from bs4 import BeautifulSoup
import requests  # TODO: use/try selenium webdriver
import re
from time import sleep, time
from multiprocessing import Pool
import numpy as np

COURSERA_URL = "https://www.coursera.org"
COURSES_URL = "https://www.coursera.org/directory/courses"
COURSES_URL_WITH_PAGE = "https://www.coursera.org/directory/courses?index=prod_all_products_term_optimization&page="

ALL_COURSES_FILE = "all_courses.csv"
CATEGORIES_FILE = "categories.csv"
POOL_SIZE = 10
SLEEP_TIME = 0.0  # TODO

INSTRUCTOR_DIVIDER = " | "


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


# Scrapes all courses from Courseare together with their names and URLs
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
	print(
	 f"\n{latest_page} pages and {len(all_courses['name'])} courses are scraped in {'{:.2f}'.format(end-start)} seconds."
	)

	return all_courses


# Scrapes course information (name, instructor(s), description, # of students, # of ratings, rating) from given URL


# Returns a dictionary of courses {'names': [], 'urls': []}
def get_courses_in_page_concurrently(page) -> dict:
	print(f"Page: {page}")
	url = f"{COURSES_URL_WITH_PAGE}{page}"
	response = requests.get(url)
	html_soup = BeautifulSoup(response.content, 'html.parser')
	courses_dict = {'name': [], 'url': []}
	course_links_columns = html_soup.find_all('div',
	                                          {'data-testid': 'linksColumn'})

	for course_links_column in course_links_columns:
		course_links = course_links_column.find_all('a', href=True)
		for course_link in course_links:
			courses_dict['name'].append(course_link.get_text())
			courses_dict['url'].append(COURSERA_URL + course_link['href'])

	return courses_dict


# Concurrently scrapes all courses from Coursera together with their names and URLs
def scrape_all_courses_concurrently():
	start = time()
	response = requests.get(COURSES_URL)
	html_soup = BeautifulSoup(response.content, 'html.parser')
	latest_page = get_latest_page(html_soup)

	all_courses = {'name': [], 'url': []}
	choke = np.arange(1, latest_page + 1, POOL_SIZE)
	for i in choke:
		pool = Pool(POOL_SIZE)
		data = pool.map(get_courses_in_page_concurrently,
		                range(i, min(i + POOL_SIZE, latest_page + 1)))
		pool.terminate()
		pool.join()

		for d in data:
			all_courses['name'].extend(d['name'])
			all_courses['url'].extend(d['url'])

	end = time()
	print(
	 f"\n{latest_page} pages and {len(all_courses['name'])} courses are scraped in {'{:.2f}'.format(end-start)} seconds."
	)

	return all_courses


def get_course_name(html_soup: BeautifulSoup) -> str:
	banner_title = html_soup.find('h1', {'class': 'banner-title'})

	if banner_title:
		name = banner_title.get_text()
	else:
		programMiniModalName = html_soup.find('h1', {'id': 'programMiniModalName'})
		name = programMiniModalName.get_text()

	print(f"get_course_name: {name}")
	return name


def get_course_category(html_soup: BeautifulSoup) -> (str, str):
	navigation_categories = html_soup.find(
	 'div', {
	  'role': 'navigation',
	  'aria-label': re.compile('breadcrumbs|Breadcrumb')
	 }).find_all('a', href=True)

	category = navigation_categories[1].get_text()
	subcategory = navigation_categories[2].get_text()

	print(f"get_course_category: {category} > {subcategory}")
	return (category, subcategory)


def get_course_instructors(html_soup: BeautifulSoup) -> str:
	instructor_avatars = html_soup.find_all(
	 'a', {'data-click-key': re.compile('instructor_avatar')})

	names = []

	for instructor_avatar in instructor_avatars:
		instructor_name = instructor_avatar.find(
		 'h3', {'class': re.compile('instructor-name')})

		if instructor_name:
			names.append(instructor_name.get_text())
		else:
			instructor_name = instructor_avatar.find(
			 'h2', {'class': re.compile('cds-119|css-10vfk66|cds-121')})
			names.append(instructor_name.get_text())

	names = INSTRUCTOR_DIVIDER.join(names)
	print(f"get_course_instructors: {names}")

	return names


def get_course_description(html_soup: BeautifulSoup) -> str:
	pass


def get_course_enrollment(html_soup: BeautifulSoup) -> int:
	pass


def get_course_raters(html_soup: BeautifulSoup) -> int:
	pass


def get_course_rating(html_soup: BeautifulSoup) -> float:
	pass


def scrape_course_information(url):
	response = requests.get(url)
	html_soup = BeautifulSoup(response.content, 'html.parser')

	try:
		print(url)
		get_course_name(html_soup)
		get_course_category(html_soup)
		get_course_instructors(html_soup)
		print()
	except AttributeError:
		print(f"Skipping the broken link: {url}")
		print()
		return None
