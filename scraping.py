from bs4 import BeautifulSoup
from multiprocessing import Pool
import numpy as np
import re
import requests  # TODO: use/try selenium webdriver
from time import time  #sleep
import traceback

COURSERA_URL = "https://www.coursera.org"
COURSES_URL = "https://www.coursera.org/directory/courses"
COURSES_URL_WITH_PAGE = "https://www.coursera.org/directory/courses?index=prod_all_products_term_optimization&page="

POOL_SIZE_FOR_PAGE_SRAPING = 10
POOL_SIZE_FOR_COURSE_SRAPING = 50
SLEEP_TIME = 0.0  # TODO

INSTRUCTOR_DIVIDER = ", "
DESCRIPTION_CONNECTOR = "\n\n"


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

	end = time()
	print(
	 f"\n{latest_page} pages and {len(all_courses['name'])} courses are scraped in {'{:.2f}'.format(end-start)} seconds."
	)

	return all_courses


# Returns a dictionary of courses {'names': [], 'urls': []}
def get_courses_in_page_concurrently(page) -> dict:
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
	choke = np.arange(1, latest_page + 1, POOL_SIZE_FOR_PAGE_SRAPING)
	for i in choke:
		print(
		 f"\rScraping course pages: [{i}-{min(i + POOL_SIZE_FOR_PAGE_SRAPING - 1, latest_page)}]/{latest_page}",
		 end='',
		 flush=True)
		pool = Pool(POOL_SIZE_FOR_PAGE_SRAPING)
		data = pool.map(
		 get_courses_in_page_concurrently,
		 range(i, min(i + POOL_SIZE_FOR_PAGE_SRAPING, latest_page + 1)))
		pool.terminate()
		pool.join()

		for d in data:
			all_courses['name'].extend(d['name'])
			all_courses['url'].extend(d['url'])

	end = time()
	print(
	 f"\n{latest_page} pages and {len(all_courses['name'])} courses are scraped in {'{:.2f}'.format(end-start)} seconds.\n"
	)

	return all_courses


# Returns the course name
def get_course_name(html_soup: BeautifulSoup) -> str:
	name = None
	banner_title = html_soup.find('h1', {'class': 'banner-title'})

	if banner_title:
		name = banner_title.get_text().strip()
	else:
		programMiniModalName = html_soup.find('h1', {'id': 'programMiniModalName'})

		if programMiniModalName:
			name = programMiniModalName.get_text().strip()

	#print(f"get_course_name: {name}")
	return name


# Returns the course categories: category and subcategory
def get_course_category(html_soup: BeautifulSoup) -> (str, str):
	category = None
	subcategory = None
	breadcrumbs = html_soup.find(
	 'div', {
	  'role': 'navigation',
	  'aria-label': re.compile('breadcrumbs|Breadcrumb')
	 })

	if breadcrumbs:
		categories = breadcrumbs.find_all('a', href=True)

		if categories and len(categories) == 3:
			category = categories[1].get_text()
			subcategory = categories[2].get_text()

	#print(f"get_course_category: {category} > {subcategory}")
	return (category, subcategory)


# Returns the course instructor(s)
def get_course_instructors(html_soup: BeautifulSoup) -> str:
	names = []
	instructor_avatars = html_soup.find_all(
	 'a', {'data-click-key': re.compile('instructor_avatar')})

	for instructor_avatar in instructor_avatars:
		instructor_name = instructor_avatar.find(
		 'h3', {'class': re.compile('instructor-name')})

		if instructor_name:
			names.append(instructor_name.find_all(text=True, recursive=False)[0])
		else:
			instructor_name = instructor_avatar.find(
			 'h2', {'class': re.compile('css-10vfk66')})

			if instructor_name:
				names.append(instructor_name.get_text())

	if not names:
		instructor_avatar = html_soup.find(
		 'a', {'data-click-key': re.compile('nav_item_instructors')})

		if instructor_avatar:
			span = instructor_avatar.find('span')

			if span:
				names.append(span.get_text())

	names = INSTRUCTOR_DIVIDER.join(names) if names else None
	#print(f"get_course_instructors: {names}")
	return names


# Returns the course description
def get_course_description(html_soup: BeautifulSoup) -> str:
	description = None
	about_section = html_soup.find('div', {'class': re.compile('about-section')})

	if about_section:
		paragraphs = about_section.find_all('p')

		for paragraph in paragraphs:
			text = paragraph.get_text()
			description = text if not description else (description +
			                                            DESCRIPTION_CONNECTOR + text)

	else:
		about_section = html_soup.find('p', {'class': re.compile('css-ngtbbz')})

		if about_section:
			description = about_section.get_text()

	#print(f"get_course_description: {description}")
	return description


# Returns the course metrics: the number of already enrolled students or recent views
def get_course_metrics(html_soup: BeautifulSoup) -> (int, int):
	enrollment = None
	views = None
	product_metrics = html_soup.find_all('div', {'class': 'rc-ProductMetrics'})

	for product_metric in product_metrics:
		span = product_metric.find('span')

		if span:
			text = span.get_text()
			number = int(
			 re.findall(r'[\d]+[.,\d]+', text)[0].replace(',', '').replace('.', ''))

			if 'views' in text:
				views = number
			elif 'enroll' in text:
				enrollment = number

	#print(f"get_course_metrics: Enrolled-{enrollment}, Views-{views}")
	return (enrollment, views)


# Returns the course review summary: rating and ratings count
def get_course_reviews(html_soup: BeautifulSoup) -> int:
	rating = None
	ratings_count = None

	span_rating_text = html_soup.find(
	 'span', {'class': re.compile('rating-text number-rating')})
	if span_rating_text:
		rating = float(span_rating_text.find_all(text=True, recursive=False)[0])

	span_ratings_count = html_soup.find(
	 'span', {'data-test': re.compile('ratings-count')})
	if not span_ratings_count:
		span_ratings_count = html_soup.find(
		 'p', {'data-test': re.compile('ratings-count')})
	if span_ratings_count:
		ratings_count = int(
		 re.findall(r'[\d]+[.,\d]+',
		            span_ratings_count.get_text())[0].replace('.',
		                                                      '').replace(',', ''))

	#print(f"get_course_reviews: Rating-{rating}, Ratings Count-{ratings_count}")
	return (rating, ratings_count)


# Scrapes course information (name, url, category, subcategory, instructor(s), description, # of enrolled students, # of recent views, rating, # of ratings) from given URL
def scrape_course_information(name, url):
	response = requests.get(url)
	html_soup = BeautifulSoup(response.content, 'html.parser')

	try:
		course_name = get_course_name(html_soup)
		course_name = course_name if course_name else name
		(category, subcategory) = get_course_category(html_soup)
		instructors = get_course_instructors(html_soup)
		description = get_course_description(html_soup)
		(enrollment, views) = get_course_metrics(html_soup)
		(rating, raters) = get_course_reviews(html_soup)
		return (course_name, url, category, subcategory, instructors, description,
		        enrollment, views, rating, raters)
	except:
		print(f"\nSkipping the broken link: {url}")
		traceback.print_exc()
		return None


# Concurrently scrapes all course information from URL
def scrape_course_information_concurrently(all_courses: dict) -> dict:
	start = time()
	print("Scraping all course information...")
	all_course_information = {
	 'name': [],
	 'url': [],
	 'category': [],
	 'subcategory': [],
	 'instructors': [],
	 'description': [],
	 'enrollment': [],
	 'views': [],
	 'rating': [],
	 'raters': []
	}
	choke = np.arange(0, len(all_courses['name']), POOL_SIZE_FOR_COURSE_SRAPING)
	for i in choke:
		print(
		 f"\rScraping course information: [{i+1}-{min(i + POOL_SIZE_FOR_COURSE_SRAPING, len(all_courses['name']))}]/{len(all_courses['name'])}",
		 end='',
		 flush=True)
		pool = Pool(POOL_SIZE_FOR_COURSE_SRAPING)
		arguments = [(all_courses['name'][j], all_courses['url'][j]) for j in range(
		 i, min(i + POOL_SIZE_FOR_COURSE_SRAPING, len(all_courses['name'])))]
		data = pool.starmap(scrape_course_information, arguments)
		pool.terminate()
		pool.join()

		for d in data:
			if d is None:
				continue

			(name, url, category, subcategory, instructors, description, enrollment,
			 views, rating, raters) = d
			all_course_information['name'].append(name)
			all_course_information['url'].append(url)
			all_course_information['category'].append(category)
			all_course_information['subcategory'].append(subcategory)
			all_course_information['instructors'].append(instructors)
			all_course_information['description'].append(description)
			all_course_information['enrollment'].append(enrollment)
			all_course_information['views'].append(views)
			all_course_information['rating'].append(rating)
			all_course_information['raters'].append(raters)

	end = time()
	print(
	 f"\n{len(all_course_information['name'])} courses are scraped in {'{:.2f}'.format(end-start)} seconds.\n"
	)

	return all_course_information
