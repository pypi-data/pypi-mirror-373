from .utils import html_get
from .parser import parse_scholar_profile, parse_publication_details

GOOGLE_SCHOLAR_URL = "https://scholar.google.com/citations?user="

def get_scholar_profile(user_id: str) -> dict:
    """
    Fetch the Google Scholar profile information for a given user ID.

    :param user_id: The user ID of the Google Scholar profile.
    :return: A dictionary containing the user's profile information.
    """
    profile_info = None
    all_pubs = []
    start = 0 

    while True:
        url = f"{GOOGLE_SCHOLAR_URL}{user_id}&cstart={start}&pagesize=100&hl=en&view_op=list_works"
        html = html_get(url)
        if not html or "Please show you're not a robot" in html:
            print("Blocked by Google Scholar or empty page")
            break

        page_info = parse_scholar_profile(html)

        if profile_info is None:
            profile_info = {k: v for k, v in page_info.items() if k != "publications"}

        pubs = page_info.get("publications", [])
        if len(pubs) == 1:
            break
        all_pubs.extend(pubs)
        start += 100

    profile_info["publications"] = all_pubs

    return profile_info

def get_publication_details(publication_url: str) -> dict:
    """
    Fetch the details of a specific publication from Google Scholar.

    :param publication_url: The URL of the publication on Google Scholar.
    :return: A dictionary containing the publication details.
    """
    html = html_get(publication_url)
    if not html or "Please show you're not a robot" in html:
        print("Blocked by Google Scholar or empty page")
        return {}

    publication_details = parse_publication_details(html)

    return publication_details