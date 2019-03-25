import os
import selenium
import selenium.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.common.action_chains
import selenium.webdriver.common.keys
import sys
import termcolor
import time


CITIES_URLS = [
    "https://data.mongabay.com/cities_pop_01.htm"
    #"https://data.mongabay.com/cities_pop_02.htm",
    #"https://data.mongabay.com/cities_pop_03.htm"
]
BASE_URL = "https://angel.co/companies"
DATA_FILE = "../data/from_angellists.txt"

SMALL_DELAY = 0.5


def _normalize_city_name(city_name_raw):
    bracket_pos = city_name_raw.find("(")
    if bracket_pos >= 0:
        city_name_raw = city_name_raw[:bracket_pos]
    city_name = city_name_raw.lower().strip()
    return city_name


def get_the_largest_cities(driver):
    return ["tianjin"]

    cities = []
    for page in CITIES_URLS:
        driver.get(page)
        table = driver.find_element_by_class_name("boldtable")
        trs = table.find_elements_by_tag_name("tr")
        for idx, tr in enumerate(trs):
            if idx < 2:
                continue
            first_td = tr.find_element_by_tag_name("td")
            city_plus_country = first_td.text
            city_name_raw = city_plus_country.split(",")[0]
            norm_city = _normalize_city_name(city_name_raw)
            cities.append(norm_city)
    return cities


def _hover_location_dropdown(driver):
    filters_contrainer = driver.find_element_by_class_name("dimensions")
    filters = filters_contrainer.find_elements_by_class_name("dropdown-filter")
    location_filter = None
    for item in filters:
        if item.get_attribute("data-menu") == "locations":
            location_filter = item
    hover = selenium.webdriver.common.action_chains.ActionChains(driver)
    hover.move_to_element(location_filter)
    hover.perform()
    time.sleep(SMALL_DELAY)


def _input_city(driver, city):
    search_box = driver.find_element_by_class_name("search-box")

    # Hover and click. Somehow Enter after it adds the first match as new filter.
    hover_dropdown = selenium.webdriver.common.action_chains.ActionChains(driver)
    hover_dropdown.move_to_element(search_box)
    hover_dropdown.click()
    hover_dropdown.perform()

    time.sleep(SMALL_DELAY)

    input_field = driver.find_element_by_class_name("keyword-input")
    input_field.send_keys(city)
    input_field.send_keys(selenium.webdriver.common.keys.Keys.ENTER)

    time.sleep(SMALL_DELAY)


def _tap_more_a_lot(driver):
    try:
        for _ in range(20):
            more_button = driver.find_element_by_class_name("more")
            hover = selenium.webdriver.common.action_chains.ActionChains(driver)
            hover.move_to_element(more_button)
            hover.click()
            hover.perform()
            time.sleep(SMALL_DELAY)
    except:
        return


def _collect_startups(driver):
    result = []
    startup_conts = driver.find_elements_by_class_name("startup")
    for startup_cont in startup_conts:
        pitch = startup_cont.find_elements_by_css_selector("div.pitch")
        if len(pitch) == 0:
            continue
        pitch_text = pitch[0].text.strip()
        if pitch_text == "":
            continue
        startup_links = startup_cont.find_elements_by_css_selector("a.startup-link")
        startup_name = startup_links[-1].text.strip()
        if startup_name == "":
            continue
        result.append(startup_name)
    return result


def scrape_angellist_for_the_city(driver, city):
    try:
        driver.get(BASE_URL)
        _hover_location_dropdown(driver)
        _input_city(driver, city)
        _tap_more_a_lot(driver)
        city_startups = _collect_startups(driver)
        return city_startups
    except Exception as ex:
        termcolor.cprint("- Error {}".format(str(ex)), "red")
        return []


def main():
    data_file_path = os.path.abspath(DATA_FILE)
    if os.path.exists(data_file_path):
        print("Data for {} already downloaded!".format(BASE_URL))
        sys.exit(1)

    print("Initialization...")
    driver = selenium.webdriver.Chrome()
    driver.maximize_window()
    driver.minimize_window()

    print("Fetching citites...")
    cities = get_the_largest_cities(driver)

    print("Scraping {:d} cities for startups...".format(len(cities)))
    startups = []
    for idx, city in enumerate(cities):
        print("Fetching city #{:d} - \"{}\"...".format(idx, city))

        start_time = time.time()
        city_startups = scrape_angellist_for_the_city(driver, city)
        duration_sec = time.time() - start_time
        print("+ Done in {:.2f} seconds".format(duration_sec))

        print("+ {:d} startup names!".format(len(city_startups)))
        startups.extend(city_startups)
        time.sleep(1)

    startups = list(set(startups))

    print("Scraped {:d} startup names".format(len(startups)))
    data_content = "\n".join(startups)
    with open(data_file_path, "w", encoding="utf-8") as fp:
        fp.write(data_content)
    print("Result saved to {}".format(data_file_path))


if __name__ == "__main__":
    main()