from selenium import webdriver
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import time
import json


def setup_driver(driver_path):
    """
    Set up the Chrome WebDriver with options and return the driver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("executable_path=" + driver_path)
    driver = webdriver.Chrome(options=options)
    return driver


def wait_for_spinner(driver):
    """
    Wait for the loading spinner to disappear.
    """
    try:
        element_present = EC.presence_of_element_located(
            (By.CLASS_NAME, 'MuiCircularProgress-root'))
        WebDriverWait(driver, 10).until_not(element_present)
    except Exception as e:
        print(f"An error occurred: {e}")


def extract_href_links(driver, base_xpath):
    """
    Extract href links from the specified base_xpath without a limit.
    """
    href_links = []
    i = 1

    while True:
        xpath = f'{base_xpath}[{i}]/div[1]/div/a'

        try:
            href_element = driver.find_element(By.XPATH, xpath)
            href_link = href_element.get_attribute("href")
            href_link = href_element.get_attribute("href")
            href_link = href_link.split('?')[0] + 'delivery/'
            href_links.append(href_link)
            i += 1
        except NoSuchElementException:
            # Break the loop when no more elements are found
            break
    return href_links


def scrape_and_write_data(driver, href_links, json_file_path):
    """
    Scrape data from each href link and write it to a JSON file.
    """
    # Initialize an empty list to store store_info dictionaries
    store_info_list = []

    # Iterate over each link
    for link in href_links:
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract store information
        store_name = soup.find('h1', class_='v2').text.strip(
        ) if soup.find('h1', class_='v2') else ""
        store_type1 = soup.find('p', class_='merchant-establishment hide-mb').text.strip(
        ) if soup.find('p', class_='merchant-establishment hide-mb') else ""
        store_type = store_type1.split('  ')[0]
        store_loc = soup.find('a', class_='merchant-locality').text.strip(
        ) if soup.find('a', class_='merchant-locality') else ""
        store_rating = soup.find(
            'p', class_='rating-desc').text.strip() if soup.find('p', class_='rating-desc') else ""

        # Append store information to the store_info_list
        store_info_list.append({
            "store_name": store_name,
            "store_type": store_type,
            "location": store_loc,
            "rating": store_rating,
            "menu": {}  # Placeholder for menu data, to be filled later
        })

        # Extract menu data
        categories = soup.find_all('article', class_='categoryListing')
        for category in categories:
            category_name = category.find(
                'h4', class_='categoryHeading').text.strip()
            items = []
            item_sections = category.find_all(
                'section', class_='categoryItemHolder')
            for item_section in item_sections:
                item_details = item_section.find('div', class_='itemDetails')
                item_info = item_details.find('article', class_='itemInfo')
                item_name_element = item_info.find('p', class_='itemName')
                item_name = item_name_element.text.strip() if item_name_element else "N/A"
                item_price_element = item_section.find(
                    'span', class_='itemPrice')
                item_price = item_price_element.text.strip().replace(
                    '₹', '') if item_price_element else "0"
                items.append({
                    "name": item_name,
                    "price": item_price
                })
                store_info_list[-1]["menu"][category_name] = items

    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(store_info_list, json_file, indent=2)


def main():
    url = "https://magicpin.in/india/New-Delhi/All/Restaurant/?sort=max_save_percent%3Adesc%3Adist&filter=all_stores&filter=city%3ANew+Delhi"
    driver_path = "C:/Users/Praveen Saharan/Downloads/chromedriver-win64/chromedriver-win64"
    base_xpath = '//*[@id="react-around-search-results"]/main/section/div[1]/article'
    json_file_path = "store6.json"

    # Set up the driver
    driver = setup_driver(driver_path)

    # Open the website and wait for spinner to disappear
    driver.get(url)
    time.sleep(60)
    wait_for_spinner(driver)

    # Extract href links
    href_links = extract_href_links(driver, base_xpath)

    # # Scrape and write data to CSV
    scrape_and_write_data(driver, href_links, json_file_path)

    # Quit the driver
    driver.quit()

    print(f"Data has been successfully stored in '{json_file_path}'.")


if __name__ == "__main__":
    main()
