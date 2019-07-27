import requests
from bs4 import BeautifulSoup, Tag
import timeit
import re
import multiprocessing
import time
import timeit
import csv
import os
import xlsxwriter
from multiprocessing import Pool
from fake_useragent import UserAgent
from selenium import webdriver
from phantomjs_bin import executable_path
from unidecode import unidecode
from selenium.common.exceptions import *

# Setup Chrome display
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")

#  Change according to the homepage of the site
Homepage = 'https://www.tripadvisor.com.my'

user = UserAgent().random
print(user)
headers = {'User-Agent': user}


# import methods from previous version of code
class Methods:
    # Check if the variable data type is None
    def CheckNone(link):
        if link != None:
            return True
        else:
            return False

    # Check if the passed string contains http or https
    def HttpCheck(link):
        if Methods.CheckNone(link):
            if ('https://' in link) or ('http://' in link):
                return True
            else:
                return False
        else:
            return False

    # Check if link is Unique
    def Unique(link):
        with open('E:/Scrape/TripAdvisor Australia/UniqueLinkList_.csv', 'rt',
                  encoding='utf-8') as Linklist:
            reader = csv.reader(Linklist)
            for url in reader:
                if Methods.CheckNone(link) & Methods.CheckNone(url):
                    if link == str(url).replace('[', '').replace("'", '').replace(']', ''):
                        Linklist.close()
                        return False
                else:
                    Linklist.close()
                    return False
            return True


def get_text_with_br(tag, result=''):
    for x in tag.contents:
        if isinstance(x, Tag):  # check if content is a tag
            if x.name == 'br':  # if tag is <br> append it as string
                result += str(x)
            else:  # for any other tag, recurse
                result = get_text_with_br(x, result)
        else:  # if content is NavigableString (string), append
            result += x

    return result


def collect_data(link, category, country, process_num):

    # Only change the executable_path to your path. Leave the chrome_options. NOT NEEDED
    # user = ua.random
    # print(user)
    # headers = {'User-Agent': user}
    # options.add_argument('user-agent={user}')
    # Only change the executable_path to your path. Leave the chrome_options.

    options.add_argument(f'user-agent={user}')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path=r'E:\Scrape\chromedriver.exe')
    driver.get(str(link))  # This will open the page using the URL
    content = driver.page_source.encode('utf-8').strip()
    # driver_soup = BeautifulSoup(content, "html.parser")

    page = requests.get(link, timeout=10, headers=headers)
    soup = BeautifulSoup(page.text, "lxml")

    # req = requests.get(str(link), headers=headers)
    # reqsoup = BeautifulSoup(req.content, 'lxml')

    key_url_list = []
    # Get all the activity links

    num = 0
    # we only want to click on the "limit search" once for smaller cities,
    # clicking more than once will result in an endless loop in some pages

    counter_limit_search = 0

    while True:
        time.sleep(2)
        try:
            driver.find_element_by_class_name('ui_tab_bar').find_elements_by_css_selector('li')[1].click()
            print("Locating ui_tab_bar for url " + driver.current_url)
        except:
            print("Error locating ui_tab_bar for url " + driver.current_url)
            pass

        # check for the "Limit search to X" button
        # note: this button appears when the city has few activities or the "outdoor activities" and "tours" page
        try:
            if counter_limit_search < 1:
                driver.find_element_by_id("secondaryText").click()
                print("Limiting search within " + 'city_of_country' + " for url " + driver.current_url)
                # allow website to update itself
                time.sleep(5)
                counter_limit_search += 1

        # pass ElementNotVisibleException
        except:
            print("Limit search button not visible for url " + driver.current_url)
            pass

        for div in driver.find_elements_by_class_name("attraction_clarity_cell"):
            for b in div.find_elements_by_class_name('listing_title'):
                if b.find_element_by_css_selector('a').get_attribute("href") is not None:
                    activity_link = b.find_element_by_css_selector('a').get_attribute("href")
                    if Methods.CheckNone(activity_link):
                        if Methods.HttpCheck(activity_link) & Methods.Unique(activity_link):
                            with open('E:/Scrape/TripAdvisor Australia/UniqueLinkList_.csv', 'at',
                                      encoding='utf-8', newline='') as Linklist:
                                writer = csv.writer(Linklist)
                                u = (str(activity_link).split('\n'))
                                writer.writerow(u)
                            Linklist.close()
                            key_url_list.append(activity_link)
                            num += 1
                else:
                    c = b.find_element_by_css_selector('a').get_attribute("onclick")
                    d = c.split(", ")[1]
                    d = d.replace("'", "")
                    activity_link = Ext + d
                    if Methods.CheckNone(activity_link):
                        if Methods.HttpCheck(activity_link) & Methods.Unique(activity_link):
                            with open('E:/Scrape/TripAdvisor Australia/UniqueLinkList_.csv', 'at',
                                      encoding='utf-8', newline='') as Linklist:
                                writer = csv.writer(Linklist)
                                u = (str(activity_link).split('\n'))
                                writer.writerow(u)
                            Linklist.close()
                            key_url_list.append(activity_link)
                            num += 1

        # Click the 'X' button on the survey banner.
        # try:
        #     driver.find_element_by_class_name('sbx_align_right_wrapper').find_element_by_class_name('sbx_close').click()
        #     # print("Closing the survey banner for url " + driver.current_url)
        # except NoSuchElementException:
        #     # print("No survey banner for url " + driver.current_url)
        #     pass
        #
        # # Click on the 'X' button on the sign in banner.
        # try:
        #     driver.find_element_by_id('component_27').find_element_by_class_name(
        #         'overlays-pieces-CloseX__close--7erra').click()
        #     # print("Closing the sign in banner for url " + driver.current_url)
        # except NoSuchElementException:
        #     # print("No sign in banner for url " + driver.current_url)
        #     pass

        # Click on the 'Not right now, thanks' button.
        # try:
        #     if driver.find_element_by_class_name('QSISlider'):
        #         container = driver.find_element_by_class_name('QSISlider')
        #         for a in container.find_elements_by_css_selector('div'):
        #             if 'position: absolute; top: 0px; left: 0px; width: 224px; height: 40px; overflow: hidden; display: block;' in a.get_attribute(
        #                     'style'):
        #                 a.click()
        #                 # print("clicking on the not right now button for url " + driver.current_url)
        # except (NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException) as error:
        #     # print("No not right now button for url " + driver.current_url)
        #     pass

        # Clicking on the Next Page
        try:
            if 'Next' in driver.find_element_by_class_name("disabled").text:
                raise Exception
            else:
                currentlink = driver.current_url
                driver.find_element_by_class_name("next").click()
                time.sleep(5)
                nextlink = driver.current_url
                if currentlink == nextlink:
                    driver.find_element_by_link_text("3").click()
                    time.sleep(2)
                    driver.find_element_by_class_name("previous").click()
                    time.sleep(2)
                continue
        except:
            break

    print("================================\nAll " + str(num) + " the links have been collected")
    print("Link collected: " + str(key_url_list))

    with open('E:/Scrape/TripAdvisor Australia/ExtractedData.csv', 'at', encoding="utf-8", newline='') as website:
        writer = csv.writer(website)

        num_loop = 0
        finished = 0
        retry_count = 0
        while True:
            for element in key_url_list:
                while finished != 1:
                    try:
                        if retry_count == 5:  # If except: No connection, up to 5 times then loop will break
                            print('This link cannot be opened ' + element)
                            num_loop += 1
                            break
                        else:
                            time.sleep(1)  # buffer period
                            print('OPENING ' + element)
                            response = requests.get(str(element), headers=headers, timeout=10)  # finds a response from the link to see if it's working
                            if response:
                                finished = 1
                    except requests.exceptions.ConnectionError as e:  # Multi Pool does not work without defining this
                        print(e)
                        print('No connection, Retrying...' + element)
                        retry_count += 1
                        continue
                    except requests.exceptions.ReadTimeout as e:
                        print(e)
                        print('Timeout Error.  ' + element)
                        retry_count += 1
                        continue

                soup = BeautifulSoup(response.content, "lxml")

                if soup.find_all('div', {'class': 'attractions-price-block-FromPriceBlock__mainPrice--2XwLZ'}):
                    print('Skipping...' + element + '. Not an attraction. ')
                    continue
                else:
                    details = ['', '', '', '', '', '', '']
                    # Name || from 3 layouts of TripAdvisor
                    for a in soup.find_all('div', {'id': 'photo-and-header-product-title'}):
                        for b in a.find_all('h1', {'class': 'ui_header h1 attractions-product-info-ProductTitle__title--1qM0o'}):
                            b = b.get_text()
                            b = unidecode(b)
                            details[0] = b.title()

                    if details[0] == '':
                        for a in soup.find_all('div', {'id': 'taplc_attraction_company_details_acr_responsive_0'}):
                            for b in a.find_all('h1', {'id': 'HEADING'}):
                                b = b.get_text()
                                b = unidecode(b)
                                details[0] = b.title()

                    if details[0] == '':
                        for a in soup.find_all('div', {'class': 'attractionsHeader'}):
                            for b in a.find_all('h1', {'id': 'HEADING'}):
                                b = b.get_text()
                                b = unidecode(b)
                                details[0] = b.title()

                    # City Name
                    if soup.find('div', {'class': 'global-nav-links-container'}) is not None:
                        navigation_container = soup.find('div', {'class': 'global-nav-links-container'}).find(
                            'li').find('span')
                        city_text = navigation_container.get_text()
                        city_text = " ".join(city_text.split())
                    details[1] = city_text

                    # Country Name
                    if soup.find('div', {'class': 'attractionsBLInfo'}) is not None:
                        country_text = soup.find('div', {'class': 'attractionsBLInfo'}).find('span', {
                            'class': 'country-name'}).get_text()
                        details[2] = country_text

                    details[2] = country

                    # Location || from 3 layouts of TripAdvisor
                    location = ''
                    for a in soup.find_all('ul', {'class': 'list'}):
                        for b in a.find_all('li', {'class': 'pois'}):
                            for c in b.find_all('span', {'class': 'poi_links'}):
                                for d in c.find_all('a'):
                                    if 'and' not in d.get_text():
                                        location = location + d.get_text() + ', '
                                    else:
                                        location = location + d.get_text()

                    details[3] = location

                    if details[3] == '':
                        for a in soup.find_all('div',
                                               {
                                                   'class': 'attractions-contact-card-ContactCard__contactRow--3Ih6v'}):
                            details[3] = a.get_text()
                            break

                    if details[3] == '':
                        for a in soup.find_all('div', {'class': 'address'}):
                            for b in a.find_all('span', {'class': 'detail'}):
                                details[3] = b.get_text()

                    # Overview || from 3 layouts of TripAdvisor
                    for a in soup.find_all('div',
                                           {'class': 'attractions-product-details-Overview__textWrapper--1fTL6'}):
                        for b in a.find_all('span'):
                            c = get_text_with_br(b)
                            c = c.replace('<br>', ' ')
                            c = c.replace('\n', '').replace('\t', '')
                            c = unidecode(c)
                            c = c.replace('...more', ' ').replace('Read more', ' ')
                            details[4] = c
                            break

                    if details[4] == '':
                        for a in soup.find_all('div',
                                               {'class': 'attractions-supplier-profile-SupplierAbout__about--1HdOk'}):
                            for b in a.find_all('div', {'class': 'attractions-supplier-profile-SupplierDescription__description--lzIK9'}):
                                c = get_text_with_br(b)
                                c = c.replace('<br>', ' ').replace('<br/>', ' ')
                                c = c.replace('\n', '').replace('\t', '')
                                c = unidecode(c)
                                c = c.replace('...more', ' ').replace('Read more', ' ')
                                details[4] = c
                                break

                    if details[4] == '':
                        for a in soup.find_all('div', {'class', 'ppr_rup ppr_priv_location_detail_about_card'}):
                            # print(a)
                            c = get_text_with_br(a)
                            c = c.replace('<br>', ' ').replace('<br/>', ' ').replace('About', '')
                            c = c.replace('\n', '').replace('\t', '')
                            c = unidecode(c)
                            c = c.replace('...more', ' ').replace('Read more', ' ')
                            if 'UndergroundF' in c:
                                c = c.split('Fdeg')[0]
                                if 'Local WeatherPowered by  Weather Underground' == c:
                                    details[4] = ''
                                else:
                                    details[4] = c.replace('Local WeatherPowered by  Weather Underground', '')
                            else:
                                details[4] = c
                            break

                    # URL Link of the Attraction page.
                    try:
                        details[5] = response.url  # Gets URL of the link
                    except:
                        continue

                    # Category of the Attraction.
                    details[6] = category

                    writer.writerow(details)  # Writes data in csv file
                    # print('Adding item no.' + str(num_loop) + ' to list')
                    print(details)
                    num_loop += 1
                    time.sleep(3)
            # print("\n" + str(len(key_url_list)) + " in the queue of " + '' + city + '')
            driver.quit()
            break


# end of import from previous code


def parsing_script_input(line):
    line_split = line.split(',')
    string_1, string_2, string_3 = line_split[0], line_split[1], line_split[2]
    return string_1, string_2, string_3


# input: user provided TripAdvisor url
# output: dictionary containing key = category type; value = category type url
def collect_category_link(url):
    dictionary_category_link = {}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "lxml")

    # look for the FIRST container - types of things to do; use "find" not "findall"; this also takes care of the occurence of the "see all" button
    types_of_things_todo = soup.find(class_='attractions-attraction-overview-pills-PillShelf__pillShelf--3uaz2')

    for link in types_of_things_todo.find_all('a', href=True):
        key = re.sub(r" ?\([^)]+\)", "", link.text)
        value = Homepage + link['href']
        dictionary_category_link[key] = value

    return dictionary_category_link


def main():

    start = timeit.default_timer()

    with open('E:/Scrape/TripAdvisor Australia/UniqueLinkList_.csv', 'wt') as Linklist:
        Linklist.close()

    # activity_url_list = [], if global have to collect all url links for every city in the country

    with open('E:/Scrape/TripAdvisor Australia/ExtractedData.csv', 'wt', encoding="utf-8", newline='') as website:
        writer = csv.writer(website)
        writer.writerow(['Name', 'City', 'Country', 'Location', 'Overview', 'URL Link', 'Category'])

    with open("scriptInput.txt", "rt") as input_lines:
        for index, line in enumerate(input_lines):
            country_name, city_name, city_link = parsing_script_input(line)
            dictionary = collect_category_link(city_link)
            activity_url_list = list(dictionary.values())   # within function, all collected activity links for the particular city
            category_list = list(dictionary.keys())
            print(len(activity_url_list))

            # multiprocessing stuff
            num_process = 4  # Number of processes running at one time. Change this to 1 for testing.
            all_process = len(activity_url_list)  # Total number of processes that should run. Change this according to uni. Change this to 1 for testing.
            num_finish_process = 0  # Count for finished process
            count_process = 0  # Count number of processes running
            process_num = 0  # This is for the course type in collect_data function
            process = []
            values = []

            def create_process(process_num, count_process):  # Function to create and start process
                process_num = process_num + 1  # This is for the course type in collect_data function
                new_process = multiprocessing.Process(target=collect_data, args=(activity_url_list.pop(), category_list.pop(), country_name, process_num))
                process.append(new_process)
                new_process.start()
                count_process += 1

                return [process_num, count_process]

            def start_process():  # Function that will call the create process function.
                nonlocal process_num, count_process, all_process
                nonlocal values

                values = create_process(process_num, count_process)

                process_num = values[0]
                count_process = values[1]

            while True:
                if count_process < num_process and process_num < all_process:  # Check if there is still processes left to be run, create new process if needed
                    start_process()
                    print("Starting process")

                for proc in process:  # Loop that will check for status of process
                    proc.join(timeout=0)
                    if not proc.is_alive():
                        process.remove(proc)  # Remove the finished process from the list
                        print("Process Ended!")
                        num_finish_process += 1
                        print('Completed Processes:')
                        print(num_finish_process)
                        remain_proc = int(all_process) - int(num_finish_process)
                        print('Remaining Processes:')
                        print(remain_proc)
                        count_process -= 1
                        break

                if count_process == 0 and num_finish_process == all_process:
                    print("All is done" + "\t\tTotal finished process " + str(num_finish_process))
                    break

        # with open('scriptOutput_' + country_name + '_' + '.csv', 'at', encoding="utf-8", newline='') as output_lines:
        #    writer = csv.writer(output_lines)
        #    writer.writerow(
        #       ['Name', 'City', 'Country', 'Location', 'Overview', 'Link'])

    stop = timeit.default_timer()
    time_sec = stop - start
    time_min = int(time_sec / 60)
    time_hour = int(time_min / 60)

    time_run = str(format(time_hour, "02.0f")) + ':' + str(
        format((time_min - time_hour * 60), "02.0f") + ':' + str(format(time_sec - (time_min * 60), "^-05.1f")))
    print("This code has completed running in: " + time_run)

if __name__ == '__main__':
    main()