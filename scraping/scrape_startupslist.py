import os
import selenium
import selenium.webdriver
import selenium.webdriver.chrome.options
import sys
import time


BASE_URL = "http://www.startups-list.com"
DATA_FILE = "../data/from_startupslists.txt"


def scrape_geosite(driver, url):
    driver.get(url)

    wrap = driver.find_element_by_id("wrap")
    startups = wrap.find_elements_by_class_name("startup")

    result = []
    for item in startups:
        startup_name = item.get_attribute("data-name")
        result.append(startup_name)

    return result


def main():
    data_file_path = os.path.abspath(DATA_FILE)
    if os.path.exists(data_file_path):
        print("Data for {} already downloaded!".format(BASE_URL))
        sys.exit(1)

    print("Initialization...")
    options = selenium.webdriver.chrome.options.Options()
    options.add_argument("--headless")
    driver = selenium.webdriver.Chrome(options=options)
    driver.get(BASE_URL)

    header = driver.find_element_by_tag_name("header")
    links_to_geosites = header.find_elements_by_tag_name("a")
    links_to_geosites = [item.get_attribute("href") for item in links_to_geosites]

    print("Scraping {:d} geolocated sites...".format(len(links_to_geosites)))
    startups = []
    for url in links_to_geosites:
        print("Fetching {}...".format(url))
        startups_from_geosite = scrape_geosite(driver, url)
        print("+ {:d} startup names".format(len(startups_from_geosite)))
        startups.extend(startups_from_geosite)
        time.sleep(1)
    for idx, item in enumerate(startups):
        startups[idx] = item.strip()

    print("Scraped {:d} startup names".format(len(startups)))
    data_content = "\n".join(startups)
    with open(data_file_path, "w", encoding="utf-8") as fp:
        fp.write(data_content)
    print("Result saved to {}".format(data_file_path))


if __name__ == "__main__":
    main()
