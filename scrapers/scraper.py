# This script aims to scrape the detailed economic forecast data from the OBR website. 

import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd

# Set the url and headers
url = "https://obr.uk/efo"
headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"}


# Create function to send GET requests to URLs and create soup
def get_url_soup(url: str, headers:str) -> BeautifulSoup:
    """
    This function sends GET requests to given URLs for web scraping purposes. 

    Args:
        url (string): URL in string format to pass through the function

    Returns:
        BeautifulSoup object: parsed URL from bs4 
    """

    # The url rejects GET requests that do not specify a user agent. As a result, it returns 403 forbidden. 
    # # Fetching user agent from developer tools from browser. F12 -> network -> click on first one listed -> look for user agent under headers. 

    # Set up the session
    session = requests.Session()

    try:
        response = session.get(url, headers = headers) # Get response
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")

    return BeautifulSoup(response.text, "html.parser")


soup = get_url_soup(url, headers = headers)

def extract_urls(url:str, soup: BeautifulSoup) -> list:
    """
    This function takes a BeautifulSoup as an input.
    It's tailored to specifically look at the OBR's Economic Forecast Outlook page
    and extract all the links of past EFO publications. 
    Main reason for doing this is that we want all the pages that contain data we're interested in. 

    Args:
        url (string): include the initial url to add to the final list. 
        soup (BeautifulSoup): BeatifulSoup for the url supplied.

    Returns:
        list: list of all URLs that contain data of interest. 
    """

    # Set the set to add the URLs to. Creating a set to ensure no dupes. Will turn into list later. 
    URLs = set()

    options = soup.find_all("option")

    # May contain None so adding all of them first
    for option in options:
        URLs.add(option.get("value"))

    # Now removing None and keeping only the URLs I am interested in. 
    return [URL for URL in list(URLs) if URL is not None and "economic-and-fiscal-outlook" in URL]

urls = extract_urls(url = url, soup = soup)













# After some inspection, I am interested in the detailed forecasts for the economy
# Only need to extract the urls associated with a download link. 
links_to_docs = soup.find_all("a", class_ = "download-link")

# Create a set to store unique urls
link_of_interest = set()

# Loop over link to find the href
for link in links_to_docs:
    # only interested in hrefs with the following string in them 
    if "economic-and-fiscal-outlook-detailed-forecast-tables-economy" in link.get("href"):
        # Save those to the set created earlier
        link_of_interest.add(link.get("href"))










# Path to save the data to
path = os.getcwd() + "\\data"

# Download file
for link in link_of_interest:
    file_response = requests.get(link, headers = headers)
    print("Status code:", file_response.status_code)
    print("Final URL:", file_response.url)
    print("Content-Type:", file_response.headers.get("Content-Type"))
    print("Content length:", len(file_response.content))

        # Save if it's a file
    if "application" in file_response.headers.get("Content-Type", ""):
        with open("downloaded_file.xlsx", "wb") as f:
            f.write(file_response.content)
            print("File saved.")
    else:
        # Maybe it's still an HTML page
        print("Looks like this is still a webpage, not a file.")

