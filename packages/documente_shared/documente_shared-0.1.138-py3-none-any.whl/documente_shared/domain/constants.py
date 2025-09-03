import pytz
from os import environ


la_paz_tz = pytz.timezone("America/La_Paz")

DOCUMENTE_API_URL = environ.get("DOCUMENTE_API_URL")
DOCUMENTE_API_KEY = environ.get("DOCUMENTE_API_KEY")