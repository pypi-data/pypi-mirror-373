from bs4 import BeautifulSoup

def parse_scholar_profile(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    profile_info = {}

     # Extracting the name
    name_tag = soup.find('div', id='gsc_prf_in')
    if name_tag:
        profile_info['name'] = name_tag.text.strip()
    else:
        print("Profile not found")
        exit(1)

    # Extracting the affiliation
    affiliation_tag = soup.find('div', class_='gsc_prf_il')
    if affiliation_tag:
        profile_info['affiliation'] = affiliation_tag.text.strip()

    # Extracting the research interests
    interests = [a.text for a in soup.select('#gsc_prf_int a')]
    profile_info['interests'] = interests

    # Extracting the profile photo URL
    photo_tag = soup.find('img', id='gsc_prf_pup-img')
    if photo_tag and photo_tag.get('src'):
        profile_info['photo_url'] = photo_tag['src']

    # Extracting the statistics
    stats = soup.select('table#gsc_rsb_st td.gsc_rsb_std')
    if len(stats) >= 6:
        profile_info['citations_all'] = stats[0].text
        profile_info['citations_since_2019'] = stats[1].text
        profile_info['h_index_all'] = stats[2].text
        profile_info['h_index_since_2019'] = stats[3].text
        profile_info['i10_index_all'] = stats[4].text
        profile_info['i10_index_since_2019'] = stats[5].text

    # Extracting the publications
    publications = []
    rows = soup.select('tr.gsc_a_tr')
    for row in rows:
        title_tag = row.select_one('.gsc_a_at')
        title = title_tag.text if title_tag else ""
        citations_tag = row.select_one('.gsc_a_c a')
        url = "https://scholar.google.com" + title_tag['href'] if title_tag and title_tag.get('href') else None

        publications.append({
            "title": title,
            "citations": citations_tag.text if citations_tag else "0",
            "url": url,
        })

    profile_info["publications"] = publications

    return profile_info

def parse_publication_details(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    publication_info = {}

    # Extracting the title
    title_tag = soup.find('a', class_='gsc_oci_title_link')
    publication_info['title'] = title_tag.text.strip() if title_tag else "No Title"

    rows = soup.select('#gsc_oci_table .gs_scl')
    if len(rows) >= 9:
        # Extracting the date
        publication_info['date'] = rows[1].select_one('.gsc_oci_value').text.strip()
        
        # Extracting the citations
        citations_tag = rows[8].select_one('.gsc_oci_value a')
        publication_info['citations'] = citations_tag.text.strip() if citations_tag else "0"

    publication_info['url'] = title_tag['href'] if title_tag else None

    return publication_info