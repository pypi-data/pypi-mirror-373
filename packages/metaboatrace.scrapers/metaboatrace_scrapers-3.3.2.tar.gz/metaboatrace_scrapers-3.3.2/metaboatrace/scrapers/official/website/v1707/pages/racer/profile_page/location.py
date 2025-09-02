import urllib.parse

from metaboatrace.scrapers.official.website.v1707 import BASE_URL


def create_racer_profile_page_url(racer_registration_number: int) -> str:
    return f"{BASE_URL}/owpc/pc/data/racersearch/profile?{urllib.parse.urlencode({'toban': racer_registration_number})}"
