import sys
import json
from dictionary_api import word_data as wd


options_mapping = {
	"plain": wd.get_word_data_plain,
	"data": wd.get_word_data,
	"pos": wd.get_pos,
	"synonyms": wd.get_synonyms,
	"antonyms": wd.get_antonyms,
	"definitions": wd.get_definitions,
	"examples": wd.get_examples,
	"hypernyms": wd.get_hypernyms,
	"hyponyms": wd.get_hyponyms
}


def menu(prompt, items, default=0):
	"""Constructs and shows a simple commandline menu.
	Returns an index of the provided items sequence."""
	for index, item in enumerate(items):
		print(f"{index}: {item}")
	result = None
	while True:
		result = input(prompt)
		if result == "" and default is not None:
			result = default
			break
		try:
			result = int(result)
		except ValueError:
			print("error: Input must be a number. Please try again.")
			continue
		if result >= len(items) or result < 0:
			print("error: Provided option not in range. Please try again.")
			continue
		print(result)
		return result


def run_interactively():
	options = list(options_mapping.keys())
	options_str = ", ".join(options_mapping)
	print("Running in interactive mode.")
	print(f"Typical usage: {sys.argv[0]} [function] <word>")
	print(
		"Available functions: {options_str}"
	)
	print()
	print(f"Example: {sys.argv[0]} game")
	print(f"Or {sys.argv[0]} definitions opportunity")
	print()
	selection = menu("Select an option: ", options)
	option = options[selection]
	word = input("Enter a word: ")
	return (option, word)


def define(option, word):
	result = options_mapping[option](word)
	if option != "plain":
		if isinstance(result, list):
			result = "\n".join([i.capitalize() for i in result])
		else:
			result = json.dumps(result, indent=4)
	return result


def main():
	if len(sys.argv) < 2:
		function, word = run_interactively()
	elif len(sys.argv) == 2:
		function = "plain"
		word = sys.argv[1]
	elif len(sys.argv) == 3:
			function = sys.argv[1]
			word = sys.argv[2]
	print(define(function, word))


if __name__ == "__main__":
	main()
