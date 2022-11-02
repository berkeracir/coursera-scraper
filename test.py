# Date: 02/11/2022
from bs4 import BeautifulSoup
import requests
import time

from scraping import get_latest_page, get_courses_in_page, SLEEP_TIME


def test_latest_page():
	print("test_latest_page")
	urls = [
	 "https://www.coursera.org/directory/courses",
	 "https://www.coursera.org/directory/courses?page=159",
	 "https://www.coursera.org/directory/courses?index=prod_all_products_term_optimization?page=252"
	]

	for url in urls:
		response = requests.get(url)
		html_soup = BeautifulSoup(response.content, 'html.parser')
		latest_page = get_latest_page(html_soup)

		assert latest_page == 292, "The latest page number"
		time.sleep(SLEEP_TIME)


def test_courses_in_page():
	print("test_courses_in_page")
	test_urls = [
	 ("https://www.coursera.org/directory/courses", 35,
	  "Accounting for Mergers and Acquisitions: Foundations (University of Illinois at Urbana-Champaign)",
	  "https://www.coursera.org/learn/kitabat-mujaz-ibdaie-li-tahdid-almasharih-alibdaiya-ala-mail-chimp"
	  ),
	 ("https://www.coursera.org/directory/courses?page=159", 35,
	  "Introduction to Augmented Reality and ARCore (Google AR & VR)",
	  "https://www.coursera.org/learn/introclassicalmusic"),
	 ("https://www.coursera.org/directory/courses?index=prod_all_products_term_optimization&page=292",
	  9, "Building RESTful APIs Using Node.js and Express (NIIT)",
	  "https://www.coursera.org/learn/python-social-network-analysis-ko")
	]

	for url, course_count, first_course, last_url in test_urls:
		response = requests.get(url)
		html_soup = BeautifulSoup(response.content, 'html.parser')
		courses = get_courses_in_page(html_soup)

		assert len(courses['name']) == course_count, "Course Count"
		assert len(courses['name']) == len(
		 courses['url']), "Name count equals url count"
		assert courses['name'][0] == first_course, "The first course"
		assert courses['url'][-1] == last_url, "The last course's URL"
		time.sleep(SLEEP_TIME)


if __name__ == "__main__":
	test_latest_page()
	test_courses_in_page()
	print("Everything passed!")
