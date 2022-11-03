import pandas as pd
from os.path import exists
import pickle

import scraping

ALL_COURSES_FILE = "all_courses.csv"
ALL_COURSES_INFORMATION_FILE = "all_courses_information.csv"
CATEGORIES_FILE = "categories.pkl"

if __name__ == "__main__":
	update = False

	if not exists(ALL_COURSES_FILE) or update:
		update = True
		all_courses = scraping.scrape_all_courses_concurrently()
		pd.DataFrame(data=all_courses).to_csv(ALL_COURSES_FILE,
		                                      index=False,
		                                      header=True)
	else:
		# TODO: If the file is updated long ago, it may be better to update course pages.
		all_courses = pd.read_csv(ALL_COURSES_FILE).to_dict()

	if len(all_courses['name']) != len(all_courses['url']):
		raise Exception("Incorrect Courses Data")

	if not exists(ALL_COURSES_INFORMATION_FILE) or update:
		update = True
		all_course_information = scraping.scrape_course_information_concurrently(
		 all_courses)
		pd.DataFrame(data=all_course_information).to_csv(
		 ALL_COURSES_INFORMATION_FILE, index=False, header=True)
	else:
		# TODO: If the file is updated long ago, it may be better to update course information.
		all_course_information = pd.read_csv(ALL_COURSES_INFORMATION_FILE).to_dict()

	if all(
	  len(column) == len(all_course_information['name'])
	  for column in all_course_information):
		raise Exception("Incorrect Course Information Data")

	if not exists(CATEGORIES_FILE) or update:
		update = True
		categories = {}

		for i in range(len(all_course_information['category'])):
			category = all_course_information['category'][i]
			subcategory = all_course_information['subcategory'][i]

			if category and subcategory:
				if category in categories:
					categories[category].add(subcategory)
				else:
					categories[category] = {subcategory}

		with open(CATEGORIES_FILE, 'wb') as f:
			pickle.dump(categories, f)
	else:
		# TODO: If the file is updated long ago, it may be better to update categories.
		with open(CATEGORIES_FILE, 'rb') as f:
			categories = pickle.load(f)

#keep_alive()

#while True:
#	print("Alive...")
#	time.sleep(10)
