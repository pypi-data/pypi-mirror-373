from metaboatrace.scrapers.official.website.v1707 import BASE_URL


def create_monthly_schedule_page_url(year: int, month: int) -> str:
    formatted_date = f"{year:04d}{month:02d}"
    return f"{BASE_URL}/owpc/pc/race/monthlyschedule?ym={formatted_date}"
