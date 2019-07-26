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

# Setup Fake User Agent
user = UserAgent().random
print(user)
headers = {'User-Agent': user}

#  Change according to the homepage of the site
Homepage = 'https://www.tripadvisor.com.my'

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

def collect_links(link):
    options.add_argument(f'user-agent={user}')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path=r'E:\Scrape\chromedriver.exe')
    driver.get(str(link))  # This will open the page using the URL
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, "html.parser")

    # req = requests.get(str(link), headers=headers)
    # reqsoup = BeautifulSoup(req.content, 'lxml')

    key_url_list = []
    # Get all the activity links

    num = 0
    # we only want to click on the "limit search" once for smaller cities,
    # clicking more than once will result in an endless loop in some pages

    counter_limit_search = 0

    while True:
        time.sleep(4)
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
    driver.quit()

def collect_data(attraction_list):

    # Only change the executable_path to your path. Leave the chrome_options. NOT NEEDED
    # user = ua.random
    # print(user)
    # headers = {'User-Agent': user}
    # options.add_argument('user-agent={user}')
    # Only change the executable_path to your path. Leave the chrome_options.

    # req = requests.get(str(attraction_list), headers=headers)
    # soup = BeautifulSoup(req.content, 'lxml')

    with open('E:/Scrape/TripAdvisor Australia/ExtractedData_all.csv', 'at', encoding="utf-8", newline='') as website:
        writer = csv.writer(website)

        n = 0
        while True:
            num_loop = 0
            finished = 0
            retry_count = 0
            while num_loop < len(attraction_list):       # loop condition based on total number of links. num_loop will +1 every time a link is done.
                while finished != 1:
                    try:
                        if retry_count == 5:             # If except: No connection, up to 5 times then loop will break
                            print('This link cannot be opened ' + attraction_list[num_loop])
                            num_loop += 1
                            break
                        else:
                            time.sleep(1)  # buffer period
                            print('OPENING ' + attraction_list[num_loop])
                            response = requests.get(str(attraction_list[num_loop]), headers=headers, timeout=10)        # finds a response from the link to see if it's working
                            if response:
                                finished = 1
                    except requests.exceptions.ConnectionError as e:    # Multi Pool does not work without defining this
                        print(e)
                        print('No connection, Retrying...' + attraction_list[num_loop])
                        retry_count += 1
                        continue
                    except requests.exceptions.MissingSchema as e:      # When collect Links failed to store the URL
                        print(e)
                        retry_count = 5
                        continue
                    except:
                        print('Error! Found')
                        retry_count += 1
                        continue

                soup = BeautifulSoup(response.content, "lxml")

                if soup.find_all('div', {'class': 'attractions-price-block-FromPriceBlock__mainPrice--2XwLZ'}):
                    print('Skipping...' + attraction_list[num_loop] + '. Not an attraction. ')
                    continue
                else:
                    details = ['', '', '', '', '', '']
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
                        navigation_container = soup.find('div', {'class': 'global-nav-links-container'}).find('li').find('span')
                        city_text = navigation_container.get_text()
                        city_text = " ".join(city_text.split())
                    details[1] = city_text

                    # Country Name
                    if soup.find('div', {'class': 'attractionsBLInfo'}) is not None:
                        country_text = soup.find('div', {'class': 'attractionsBLInfo'}).find('span', {'class': 'country-name'}).get_text()
                        details[2] = country_text

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
                        for a in soup.find_all('div',{'class': 'attractions-supplier-profile-SupplierAbout__about--1HdOk'}):
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
                    writer.writerow(details)  # Writes data in csv file
                    n += 1
                    print('Adding item no.' + str(n) + ' to list')
                    print(details)
                    num_loop += 1
                    time.sleep(3)
            break


# end of import from previous code


def parsing_script_input(line):
    line_split = line.split(',')
    string_1, string_2, string_3 = line_split[0], line_split[1], line_split[2]      # Reading data from input file.
    return string_1, string_2, string_3


# input: user provided TripAdvisor url
# output: dictionary containing key = category type; value = category type url
def collect_category_link(url):
    dictionary_category_link = {}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "lxml")

    # look for the FIRST container - types of things to do; use "find" not "findall"; this also takes care of the occurrence of the "see all" button
    types_of_things_todo = soup.find(class_='attractions-attraction-overview-pills-PillShelf__pillShelf--3uaz2')

    for link in types_of_things_todo.find_all('a', href=True):
        key = re.sub(r" ?\([^)]+\)", "", link.text)
        value = Homepage + link['href']
        dictionary_category_link[key] = value

    return dictionary_category_link

# Define multi processing method.
# Parameters are function name, list, no. of processes
def multi_pool(func, args, procs):
    pool = multiprocessing.Pool(processes=procs)
    print('Total number of processes: ' + str(procs))
    result = pool.map(func, args)
    pool.terminate()
    pool.join()

def main():

    start = timeit.default_timer()

    with open('E:/Scrape/TripAdvisor Australia/UniqueLinkList_.csv', 'wt') as Linklist:
        Linklist.close()

    # activity_url_list = []    # if global have to collect all url links for every city in the country
    total_attraction_list = []  # This list will store all collected links

    with open('E:/Scrape/TripAdvisor Australia/ExtractedData_all.csv', 'wt', encoding="utf-8", newline='') as website:
        writer = csv.writer(website)
        writer.writerow(['Name', 'City', 'Country', 'Location', 'Overview', 'URL Link'])

    with open("scriptInput.txt", "rt") as input_lines:
        for index, line in enumerate(input_lines):
            country_name, city_name, city_link = parsing_script_input(line)
            dictionary = collect_category_link(city_link)
            activity_url_list = list(dictionary.values())   # within function, all collected activity links for the particular city
            category_list = list(dictionary.keys())
            print('Number of Category Links: ' + str(len(activity_url_list)))

            # procs is the number of processes running in parallel.
            if len(activity_url_list) < 5:
                procs = len(activity_url_list)
            else:
                procs = 4
            multi_pool(collect_links, activity_url_list, procs)     # multiprocess Collect_links method

    with open('E:/Scrape/TripAdvisor Australia/UniqueLinkList_.csv', 'rt', encoding='utf-8', newline='') as activity_link:
        reader = csv.reader(activity_link)
        data_row = []
        next(reader)
        for row in reader:
            data_row.append(row)
            total_attraction_list.append(row)

    print(len(total_attraction_list))
    print(total_attraction_list)

    # procs is the number of processes running in parallel.
    if len(total_attraction_list) < 10:
        procs = len(total_attraction_list)
    else:
        procs = 10
    multi_pool(collect_data, total_attraction_list, procs)          # Multiprocess collect_data method

    stop = timeit.default_timer()
    time_sec = stop - start
    time_min = int(time_sec / 60)
    time_hour = int(time_min / 60)

    time_run = str(format(time_hour, "02.0f")) + ':' + str(
        format((time_min - time_hour * 60), "02.0f") + ':' + str(format(time_sec - (time_min * 60), "^-05.1f")))
    print("This code has completed running in: " + time_run)

if __name__ == '__main__':
    main()