from flask import Flask, jsonify, render_template, request

from dictionary_api import word_data as wd


app = Flask(__name__)


@app.route("/api/health")
def health():
	"""Health check endpoint."""
	return jsonify({"status": "ok", "error": None})


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/api/word")
@app.route("/api/word/<string:word>")
def word_lookup(word=None):
	"""Looks up word data."""
	word = word or request.args.get("word")
	pos_str = request.args.get("pos") # Part of speech filter (comma-separated)
	if not word:
		return jsonify({"data": None, "error": "Missing 'word' query parameter"}), 400
	pos_filter = None
	if pos_str:
		# Split by comma and remove any leading/trailing whitespace
		pos_filter = [p.strip() for p in pos_str.split(',')]
	try:
		word_data = wd.get_word_data(word, pos_filter=pos_filter)
		if word_data and word_data.get("num_senses", 0) > 0:
			return jsonify({"data": word_data, "error": None}), 200
		else:
			return jsonify({"data": None, "error": f"No definitions found for '{word}'"}), 404
	except Exception as e:
		app.logger.error(f"Error processing word '{word}': {e}")
		return jsonify({"data": None, "error": "An internal server error occurred"}), 500


if __name__ == "__main__":
	# Ensure NLTK data is downloaded (run this once manually or in setup)
	# import nltk
	# try:
	#	 nltk.data.find('corpora/wordnet')
	# except nltk.downloader.DownloadError:
	#	 nltk.download('wordnet')
	# try:
	#	 nltk.data.find('corpora/omw-1.4')
	# except nltk.downloader.DownloadError:
	#	 nltk.download('omw-1.4') # Needed for multilingual support later and lemmatization

	app.run(debug=True)
