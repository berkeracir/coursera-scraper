import pandas as pd
from os.path import exists

from scraping import scrape_all_courses, ALL_COURSES_FILE


if __name__ == "__main__":
	if not exists(ALL_COURSES_FILE):
		all_courses = scrape_all_courses()
		pd.DataFrame(data=all_courses).to_csv(ALL_COURSES_FILE,
	                                      index=False,
	                                      header=True)
	else:
		# TODO: If the file is updated long ago, update all courses.
		pass

#keep_alive()

#while True:
#	print("Alive...")
#	time.sleep(10)
