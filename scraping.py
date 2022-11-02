from bs4 import BeautifulSoup
import requests  # TODO: use/try selenium webdriver
import re
from time import sleep, time

import sys

COURSERA_URL = "https://www.coursera.org"
COURSES_URL = "https://www.coursera.org/directory/courses"
COURSES_URL_WITH_PAGE = "https://www.coursera.org/directory/courses?index=prod_all_products_term_optimization&page="

ALL_COURSES_FILE = "all_courses.csv"
SLEEP_TIME = 0.0


# Returns the latest page number in "https://www.coursera.org/directory/courses" or "https://www.coursera.org/directory/courses?page=100"
def get_latest_page(html_soup: BeautifulSoup) -> int:
	page_number = html_soup.find(
	 'div', {
	  'role': 'navigation',
	  'class': 'pagination-controls-container',
	  'aria-label': 'Page Navigation'
	 }).find_all('a', {'class': re.compile('box number')},
	             href=True)[-1].get_text()

	return int(page_number)


# Returns a dictionary of courses {'names': [], 'urls': []}
def get_courses_in_page(html_soup: BeautifulSoup) -> dict:
	courses_dict = {'name': [], 'url': []}
	course_links_columns = html_soup.find_all('div',
	                                          {'data-testid': 'linksColumn'})

	for course_links_column in course_links_columns:
		course_links = course_links_column.find_all('a', href=True)
		for course_link in course_links:
			courses_dict['name'].append(course_link.get_text())
			courses_dict['url'].append(COURSERA_URL + course_link['href'])

	return courses_dict


# Scrape all courses from Courseare together with their names and URLs
def scrape_all_courses():
	start = time()
	response = requests.get(COURSES_URL)
	html_soup = BeautifulSoup(response.content, 'html.parser')
	latest_page = get_latest_page(html_soup)

	all_courses = {'name': [], 'url': []}

	for page in range(1, latest_page + 1):
		print(f"\rScraping page: {page}/{latest_page}", end='', flush=True)
		if page != 1:
			url = f"{COURSES_URL_WITH_PAGE}{page}"
			response = requests.get(url)
			html_soup = BeautifulSoup(response.content, 'html.parser')
			

		courses_in_page = get_courses_in_page(html_soup)
		all_courses['name'].extend(courses_in_page['name'])
		all_courses['url'].extend(courses_in_page['url'])
		sleep(SLEEP_TIME)
		
	end = time()
	print(f"\n{latest_page} pages and {len(all_courses['name'])} courses are scraped in {'{:.2f}'.format(end-start)} seconds.")

	return all_courses
