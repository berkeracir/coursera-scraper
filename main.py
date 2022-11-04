import pandas as pd
import os
import pickle
import math
import time

import scraping
import server

ALL_COURSES_FILE = "all_courses.csv"
ALL_COURSES_INFORMATION_FILE = "all_courses_information.csv"
CATEGORIES_FILE = "categories.pkl"
CSV_FOLDER = "csv_files/"

if __name__ == "__main__":
	update = False

	# scrape Coursera courses into csv file
	if not os.path.exists(ALL_COURSES_FILE) or update:
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

	# scrape all Coursera course information into csv file
	if not os.path.exists(ALL_COURSES_INFORMATION_FILE) or update:
		update = True
		all_course_information = scraping.scrape_course_information_concurrently(
		 all_courses)
		df_all_course_information = pd.DataFrame(data=all_course_information)
		df_all_course_information.to_csv(ALL_COURSES_INFORMATION_FILE,
		                                 index=False,
		                                 header=True)
	else:
		# TODO: If the file is updated long ago, it may be better to update course information.
		df_all_course_information = pd.read_csv(ALL_COURSES_INFORMATION_FILE)
		all_course_information = df_all_course_information.to_dict()

	if all(
	  len(column) == len(all_course_information['name'])
	  for column in all_course_information):
		raise Exception("Incorrect Course Information Data")

	# save category information
	if not os.path.exists(CATEGORIES_FILE) or update:
		update = True
		categories = {}

		for i in range(len(all_course_information['category'])):
			category = all_course_information['category'][i]
			subcategory = all_course_information['subcategory'][i]

			if category and subcategory and isinstance(category, str) and isinstance(
			  subcategory, str):
				if category in categories:
					categories[category].add(subcategory)
				else:
					categories[category] = {subcategory}

		sorted_categories = {}
		for category in sorted(categories.keys()):
			sorted_categories[category] = sorted(categories[category])
		categories = sorted_categories

		with open(CATEGORIES_FILE, 'wb') as f:
			pickle.dump(categories, f)
	else:
		# TODO: If the file is updated long ago, it may be better to update categories.
		with open(CATEGORIES_FILE, 'rb') as f:
			categories = pickle.load(f)

	# create CSV_FOLDER if it doesn't exist
	if not os.path.exists(CSV_FOLDER):
		os.makedirs(CSV_FOLDER)

	# create sorted csv file for whole data
	csv_filepath = os.path.join(CSV_FOLDER, "all_courses.csv")
	if not os.path.exists(csv_filepath) or update:
		df_sorted_all_course_information = df_all_course_information.sort_values(
		 by=['name'])
		df_sorted_all_course_information.to_csv(csv_filepath,
		                                        index=False,
		                                        header=True)
	else:
		df_sorted_all_course_information = pd.read_csv(csv_filepath)

	# obtain category and subcategories while creating csv files
	for category in categories:
		df_category = df_sorted_all_course_information[(
		 df_sorted_all_course_information['category'] == category)]
		csv_filepath = os.path.join(CSV_FOLDER, f"{category}.csv")
		if not os.path.exists(csv_filepath) or update:
			df_category.to_csv(csv_filepath, index=False, header=True)

		for subcategory in categories[category]:
			df_category_subcategory = df_sorted_all_course_information[
			 (df_sorted_all_course_information['category'] == category)
			 & (df_sorted_all_course_information['subcategory'] == subcategory)]
			csv_filepath = os.path.join(CSV_FOLDER, f"{category}-{subcategory}.csv")
			if not os.path.exists(csv_filepath) or update:
				df_category_subcategory.to_csv(csv_filepath, index=False, header=True)

	server.start(categories)

	while True:
		print("Alive...")
		time.sleep(10)
