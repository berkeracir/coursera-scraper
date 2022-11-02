import pandas as pd
from os.path import exists

import scraping

if __name__ == "__main__":
	if not exists(scraping.ALL_COURSES_FILE):
		all_courses = scraping.scrape_all_courses_concurrently()
		pd.DataFrame(data=all_courses).to_csv(scraping.ALL_COURSES_FILE,
		                                      index=False,
		                                      header=True)
	else:
		# TODO: If the file is updated long ago, it may be better to update it together with all courses' information.
		all_courses = pd.read_csv(scraping.ALL_COURSES_FILE).to_dict()

	if len(all_courses['name']) != len(all_courses['url']):
		raise Exception("Incorrect Data of Courses")

	#if not exists(scraping.COURSES_FILE):
	for i in range(len(all_courses['name'])):
		url = all_courses['url'][i]
		scraping.scrape_course_information(url)

#keep_alive()

#while True:
#	print("Alive...")
#	time.sleep(10)
