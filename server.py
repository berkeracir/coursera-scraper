from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from threading import Thread

app = Flask(__name__)

CATEGORIES = None


@app.route('/')
def home():
	global CATEGORIES
	return render_template('index.html', categories=CATEGORIES)


@app.route('/get-file', methods=['GET'])
def get_file():
	return redirect(
	 url_for('get_csv', filename=request.args.get('category_subcategory')))


@app.route('/csv/<filename>', methods=['GET'])
def get_csv(filename):
	try:
		download_name = filename.lower().replace(' ', '_') + ".csv"
		return send_from_directory("csv_files",
		                           filename + ".csv",
		                           as_attachment=False,
		                           download_name=download_name)
	except FileNotFoundError:
		abort(404)


def run():
	app.run(host='0.0.0.0', port=8000, threaded=True)


def start(categories):
	global CATEGORIES
	CATEGORIES = categories

	t = Thread(target=run)
	t.start()
