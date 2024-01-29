import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

mvp_data_url_template = \
    'https://www.basketball-reference.com/awards/awards_{}.html'

team_data_url_template = \
    'https://www.basketball-reference.com/leagues/NBA_1991_standings.html'


def make_request(url):
    """
    Make a GET request to the given URL with retries.

    :param url: The URL to send the GET request to.
    :return: Response object if successful.
    :raises InvalidURL: If the URL is unknown.
    :raises TooManyRedirects: If max retries are reached due to too many
    redirects.
    :raises RequestException: For unknown request errors.
    """
    retry_count = 3
    # Send a GET request to the URL
    while retry_count > 0:
        response = requests.get(url)
        if response.status_code in (400, 404):  # Indicates a bad request
            raise requests.exceptions.InvalidURL(f'{url} is an unknown URL')
        elif response.status_code == 429:  # Indicates too many requests
            retry_count -= 1
            # Sleep for 10 seconds before making a new request
            time.sleep(10)
        elif response.status_code != 200:  # Indicates some unknown error
            raise requests.exceptions.RequestException(
                f'Error with status code {response.status_code}encountered')
        else:  # If we are here, we made a successful request
            return response

    # If we are here, we ran out of retries
    raise requests.exceptions.TooManyRedirects(
        f'Reached maximum retries for url {url}.')


def initialize_yearly_player_data(years):
    for year in years:
        file_path = 'src/yearly_player_data/{}.html'.format(year)
        try:
            with open(file_path, 'x', encoding='utf-8') as f:
                # If we successfully created the file, write our html to it
                # Get the url corresponding to the current year
                player_per_game_url = \
                    'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'.format(
                        year)
                # Try to make a GET request to the URL
                try:
                    response = make_request(player_per_game_url)
                except (requests.exceptions.TooManyRedirects,
                        requests.exceptions.RequestException,
                        requests.exceptions.InvalidURL) as e:
                    raise RuntimeError(
                        f'Encountered {e} when making a URL request')
                # Strip the web page of unnecessary information, return the
                # relevant mvp table for the given year
                # Save the html table into a file in our yearly_mvp_data folder
                # Create the file with our new data
                player_table_html = extract_yearly_player_table_from_page(
                    year, response.text
                )
                # Write a string representation of the page's HTML for the mvp table
                f.write(str(player_table_html))
        except FileExistsError:
            # If the file already exists, we can simply continue
            continue


def initialize_yearly_team_data(years):
    pass


def initialize_yearly_mvp_data(years):
    """
    Downloads MVP for each given year and saves each into HTML files

    Iterates through the list of years provided, scrapes the
    web page from the corresponding URL for that year, extracts the relevant
    table data from the page's HTML, and saves the mvp table data into HTML
    files in the corresponding folder.
    If the file for a particular year already exists, it skips that year's data.

    :param years: List of years for which MVP data is to be downloaded.
    :return: None
    :raises RuntimeError: If encountering exceptions during URL request.

    Example:
    ```
    yrs = [2018, 2019, 2020]
    initialize_yearly_mvp_data(yrs)
    ```
    After running the function, HTML files for each year (2018.html, 2019.html,
    2020.html) will be created in the 'yearly_mvp_data' folder.
    """
    # Iterate through each year that we want to scrape data for
    # Iterate through each type of data that we want to scrape data for:
    # MVP data, player data, team data
    for year in years:
        file_path = 'src/yearly_mvp_data/{}.html'.format(year)
        try:
            with open(file_path, 'x', encoding='utf-8') as f:
                # If we successfully created the file, write our html to it
                # Get the url corresponding to the current year
                url = mvp_data_url_template.format(year)
                # Try to make a GET request to the URL
                try:
                    response = make_request(url)
                except (requests.exceptions.TooManyRedirects,
                        requests.exceptions.RequestException,
                        requests.exceptions.InvalidURL) as e:
                    raise RuntimeError(
                        f'Encountered {e} when making a URL request')
                # Strip the web page of unnecessary information, return the
                # relevant mvp table for the given year
                # Save the html table into a file in our yearly_mvp_data folder
                # Create the file with our new data
                mvp_table_html = extract_yearly_mvp_table_from_page(
                    response.text
                )
                # Write a string representation of the page's HTML for the mvp table
                f.write(str(mvp_table_html))
        except FileExistsError:
            # If the file already exists, we can simply continue
            continue


def extract_yearly_mvp_table_from_page(year, page):
    """
    Extracts the MVP table from the HTML page for a given year.

    :param year: The year for which the MVP table is being extracted.
    :param page: HTML content of the web page.
    :return: BeautifulSoup object containing the MVP table.
    """
    soup = BeautifulSoup(page, 'html.parser')
    # Remove the 0th table row - it contains unnecessary info for our data
    soup.find('tr', class_='over_header').decompose()
    # Extract the specific table containing MVP voting data
    mvp_table = soup.find(id='mvp')
    return mvp_table


def extract_yearly_player_table_from_page(year, page):
    # Create a webdriver to automate the browser
    driver = webdriver.Chrome()



def scrape_basketball_reference(years):
    """
    Scrapes MVP, player, and team data from basketball-reference.com and
    saves it into HTML files.

    :param years: List of years for which MVP data is to be scraped.
    :return: None
    """
    initialize_yearly_mvp_data(years)
    initialize_yearly_player_data(years)
    initialize_yearly_team_data(years)
