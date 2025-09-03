import urllib.parse

import requests
from AcdhArcheAssets.uri_norm_rules import get_norm_id, get_normalized_uri
from typing_extensions import Self
from wikidata.client import Client

WIKIDATA_URL = "https://www.wikidata.org/wiki/"
GEONAMES_URL = "https://sws.geonames.org/"
GND_URL = "https://d-nb.info/gnd/"
IMG_EP = "https://www.wikidata.org/w/api.php?action=wbgetclaims&property=P18&entity={}&format=json"
URL_STUB = "https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/{}"
JSON_API_STUB = "https://commons.wikimedia.org/w/api.php?action=query&titles=File:{}&prop=imageinfo&iiprop=url&iiurlwidth={}&format=json"  # noqa

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
}


def fetch_image(
    wikidata_id: str, thumb_width: int = 250, headers: dict = DEFAULT_REQUEST_HEADERS
) -> str:
    """returns the URL of a wikimedia image related to the given wikidata id

    Args:
        wikidata_id (str): a wikidata id e.g. 'Q2390830'
        thumb_width (int): the requested image widh in pixels, defaults to 250
        headers (dict): optional headers to be sent with the request, defaults to DEFAULT_REQUEST_HEADERS

    Returns:
        str: the URL to the image, e.g. 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Theo._Komisarjevsky_LCCN2014715267.jpg/250px-Theo._Komisarjevsky_LCCN2014715267.jpg'
    """  # noqa
    if wikidata_id.startswith("http"):
        wikidata_id = get_norm_id(wikidata_id)
    url = IMG_EP.format(wikidata_id)
    r = requests.get(url, headers=headers)
    try:
        img_name = r.json()["claims"]["P18"][0]["mainsnak"]["datavalue"]["value"]
    except KeyError:
        return ""
    if img_name is not None:
        img = URL_STUB.format(urllib.parse.quote(img_name))
        img_name = img.split("file/")[-1]
        api_url = JSON_API_STUB.format(img_name, thumb_width)
        data = requests.get(api_url, headers=headers).json()
        try:
            thumburl = next(iter(data["query"]["pages"].values()))["imageinfo"][0][
                "thumburl"
            ]
        except (KeyError, IndexError):
            return img
        return thumburl


class NoWikiDataUrlException(Exception):
    pass


def check_url(wikidata_url):
    if "wikidata" not in wikidata_url:
        raise NoWikiDataUrlException(f"{wikidata_url} is no proper Wikidata URL")
    else:
        return get_normalized_uri(wikidata_url)


class WikiDataEntity:
    """A base class for wikidata entities"""

    def get_apis_entity(self: Self) -> dict:
        """returns a dict representing the wikidata entity

        Args:
            self (Self): A wikiDataEntity Object

        Returns:
            dict: a dict like `{"name": "some label"}
        """
        return {"name": self.label}

    def __init__(self, wikidata_url):
        self.wikidata_url = check_url(wikidata_url)
        self.wikidata_id = get_norm_id(self.wikidata_url)
        self.client = Client()
        self.client.opener.addheaders = [
            (
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            )
        ]
        self.entity = self.client.get(self.wikidata_id, load=True)
        self.label = str(self.entity.label)
        gnd_uri_property = self.client.get("P227")
        try:
            gnd_uri = self.entity[gnd_uri_property]
            self.gnd_uri = get_normalized_uri(f"{GND_URL}{gnd_uri}")
        except KeyError:
            self.gnd_uri = False


class WikiDataPlace(WikiDataEntity):
    """Class to fetch and return often used data from WikiData Person entries"""

    def get_apis_entity(self):
        return {"name": self.label, "lat": self.lat, "lng": self.lng}

    def __init__(self, wikidata_url):
        super().__init__(wikidata_url)
        coordinates_prop = self.client.get("P625")
        geonames_uri_property = self.client.get("P1566")
        try:
            coordinates = self.entity[coordinates_prop]
        except KeyError:
            coordinates = False
        if coordinates:
            self.lat = coordinates.latitude
            self.lng = coordinates.longitude
        else:
            self.lat = None
            self.lng = None
        try:
            geonames_uri = self.entity[geonames_uri_property]
            self.geonames_uri = get_normalized_uri(f"{GEONAMES_URL}{geonames_uri}")
        except KeyError:
            self.geonames_uri = False


class WikiDataPerson(WikiDataEntity):
    """Class to fetch and return often used data from WikiData Person entries"""

    def get_apis_entity(self):
        return {
            "name": self.name,
            "first_name": self.first_name,
            "start_date_written": self.date_of_birth,
            "end_date_written": self.date_of_death,
            "gender": self.sex_or_gender,
        }

    def __init__(self, wikidata_url):
        super().__init__(wikidata_url)
        date_of_birth_prop = self.client.get("P569")
        date_of_death_prop = self.client.get("P570")
        place_of_birth_prop = self.client.get("P19")
        place_of_death_prop = self.client.get("P20")
        sex_or_gender_prop = self.client.get("P21")
        first_name_prop = self.client.get("P735")
        name_prop = self.client.get("P734")
        try:
            self.first_name = str(self.entity[first_name_prop].label)
        except KeyError:
            self.first_name = None
        try:
            self.name = str(self.entity[name_prop].label)
        except KeyError:
            self.name = self.label
        if self.first_name and self.name.startswith(f"{self.first_name} "):
            self.name = self.name.replace(f"{self.first_name} ", "")

        try:
            self.date_of_birth = str(self.entity[date_of_birth_prop])
        except (KeyError, ValueError):
            self.date_of_birth = None
        try:
            self.date_of_death = str(self.entity[date_of_death_prop])
        except (KeyError, ValueError):
            self.date_of_death = None
        try:
            self.sex_or_gender = str(self.entity[sex_or_gender_prop].label)
        except KeyError:
            self.sex_or_gender = None
        try:
            place_of_birth_id = str(self.entity[place_of_birth_prop].id)
            self.place_of_birth = get_normalized_uri(
                f"{WIKIDATA_URL}{place_of_birth_id}"
            )
        except KeyError:
            self.place_of_birth = None
        try:
            place_of_death_id = str(self.entity[place_of_death_prop].id)
            self.place_of_death = get_normalized_uri(
                f"{WIKIDATA_URL}{place_of_death_id}"
            )
        except KeyError:
            self.place_of_death = None


class WikiDataOrg(WikiDataEntity):
    def get_apis_entity(self):
        return {"name": self.label, "start_date_written": self.start_date}

    def __init__(self, wikidata_url):
        super().__init__(wikidata_url)
        start_date_prop = self.client.get("P571")
        location_hq_prop = self.client.get("P159")
        location_prop = self.client.get("P276")
        try:
            self.start_date = str(self.entity[start_date_prop])
        except (KeyError, ValueError):
            self.start_date = None
        try:
            location_id = str(self.entity[location_hq_prop].id)
            self.location = get_normalized_uri(f"{WIKIDATA_URL}{location_id}")
        except KeyError:
            try:
                self.location_id = str(self.entity[location_prop].id)
                self.location = get_normalized_uri(f"{WIKIDATA_URL}{self.location_id}")
            except KeyError:
                self.location_id = None
                self.location = None
