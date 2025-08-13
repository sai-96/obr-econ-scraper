# This script aims to scrape the detailed economic forecast data from the OBR website. 

import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import re

############## PARAMS ####################

# Set the url and headers
obr_efo_url = "https://obr.uk/efo"
headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"}

# Path to save the data to
# Go up one folder and then save to raw_data folder
raw_data_folder_path = os.path.dirname(os.getcwd())  + "\\raw_data\\"

# Create a list of strings that we're looking for in the href for the data we need
economy_href = [
    "economic-and-fiscal-outlook-detailed-forecast-tables-economy",
    "economy-supplementary-data-economic-and-fiscal-outlook",
    "economic-and-fiscal-outlook-supplementary-economy-table",
    "economic-fiscal-outlook-supplementary-economy-table"
]

################### FUNCTIONS FOR SCRAPING ####################

# Create function to send GET requests to URLs and create soup
def get_url_soup(url: str, headers:dict) -> BeautifulSoup:
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

# Function to extract webpage URL where the download links are
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

# Function to extract download links from each webpage
def extract_download_urls(page_urls:list, keywords: list) -> list:
    """
    This function takes the list created by the extract_urls function to point
    to the file to download in each page. 

    Args:
        page_urls (list): list of urls created by extract_urls function
        keywords (list): list of keywords to look for what we need in the page

    Returns
        list: list of URLs that point to the file to download from the pages passed through this function.

    """
    # empty set to store the links
    download_urls = set()

    # Loop through each URL to find the download link
    for url in page_urls:
        # Get soup
        soup = get_url_soup(url, headers=headers)
        # Find all the links in the page that are classed as download-links
        download_link = soup.find_all("a", class_ = "download-link")

        # Loop over each download link and find the links that we need
        for dl in download_link:
            for href in keywords:
                if href in dl.get("href"):
                    download_urls.add(dl.get("href"))

    return list(download_urls)

# Download data from download links
def download_data(download_url:list, headers:dict, local_path:str):
    """
    Pass through the download links of each file and this function will save them onto the local path

    Args:
        download_url (list): list of the download links.
        headers (dict): dictionary of headers.
        local_path (str): the folder you want to save the files to. 

    Returns:
        Files downloaded in path

    """

    session = requests.Session()

    for url in download_url:
        
        pattern = r"(?<=download/)(.*?)(?=/\?t)"
        match = re.search(pattern, url)
        match_pattern = match.group(1) if match else ""
        filename = match_pattern + ".xlsx" 

        print("Downloading:", filename)

        # Get request
        response = session.get(url, headers = headers)

        if "application" in response.headers.get("Content-Type", ""):
             with open(local_path + filename, "wb") as f:
                  f.write(response.content)
                  print("File saved at:", local_path + filename)
        else:
             # If not a file
             print("Could not retrieve file to download at:", url)

# Put it altogether
def scrape_and_download_data(url:str, headers:dict, keywords:list, local_path:str):

    soup = get_url_soup(url, headers=headers)
    page_url_list = extract_urls(url=url, soup=soup)
    download_url = extract_download_urls(page_urls=page_url_list, keywords=keywords)
    download_data(download_url=download_url, headers=headers,local_path=local_path)

    print("Downloaded all files")

################################################################

# To do:
# Ideally, before downloading, check the number of files in the raw data folder already
# If they match the number of URLs, then no need to download as there would be no new files. 
# New data only comes out every 6-7 months or so. 

# Scrape and download 
scrape_and_download_data(url=obr_efo_url, 
                         headers=headers, 
                         keywords=economy_href, 
                         local_path=raw_data_folder_path)