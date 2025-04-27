import argparse
import json
import sys
from dictionary_api import word_data as wd


VERSION = "1.0.0"
# Dictionary of available functions and their corresponding implementations
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
	"""Runs the dictionary tool in interactive mode."""
	options = list(options_mapping.keys())
	options_str = ", ".join(options)
	print("Running in interactive mode.")
	print(f"Available functions: {options_str}")
	print()
	selection = menu("Select an option: ", options)
	option = options[selection]
	word = input("Enter a word: ")
	return (option, word)


def define(option, word, as_json=False):
	"""Retrieves the requested information about the word."""
	result = options_mapping[option](word)
	
	if as_json:
		return json.dumps(result, indent=4)
	
	if option != "plain":
		if isinstance(result, list):
			result = "\n".join([i.capitalize() for i in result])
		elif isinstance(result, dict):
			result = json.dumps(result, indent=4)
	
	return result


def parse_args():
	"""Parse command line arguments using argparse."""
	parser = argparse.ArgumentParser(
		description="Dictionary tool to look up words and their properties.",
		epilog="Example usage: dict.py happy --definitions"
	)
	parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
	parser.add_argument('word', nargs='?', help='Word to look up')
	function_group = parser.add_argument_group('word functions')
	function_group.add_argument('-p', '--plain', action='store_const', const='plain', dest='function',
							help='Get plain word data (default)')
	function_group.add_argument('-d', '--data', action='store_const', const='data', dest='function',
							help='Get full word data')
	function_group.add_argument('--pos', action='store_const', const='pos', dest='function',
							help='Get parts of speech')
	function_group.add_argument('-s', '--synonyms', action='store_const', const='synonyms', dest='function',
							help='Get synonyms')
	function_group.add_argument('-a', '--antonyms', action='store_const', const='antonyms', dest='function',
							help='Get antonyms')
	function_group.add_argument('-D', '--definitions', action='store_const', const='definitions', dest='function',
							help='Get definitions')
	function_group.add_argument('-e', '--examples', action='store_const', const='examples', dest='function',
							help='Get examples')
	function_group.add_argument('--hypernyms', action='store_const', const='hypernyms', dest='function',
							help='Get hypernyms')
	function_group.add_argument('--hyponyms', action='store_const', const='hyponyms', dest='function',
							help='Get hyponyms')
	parser.add_argument('-j', '--json', action='store_true', help='Force JSON output format')
	# Add interactive mode
	parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
	return parser.parse_args()


def main():
	"""Main entry point for the dictionary tool."""
	args = parse_args()
	if args.interactive or not args.word:
		function, word = run_interactively()
	else:
		word = args.word
		# Default to 'plain' if no function is specified
		function = args.function if args.function else 'plain'
	result = define(function, word, args.json)
	print(result)


if __name__ == "__main__":
	main()
