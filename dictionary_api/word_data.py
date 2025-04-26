from typing import List, Optional, Dict, Any, Set, Tuple
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from functools import lru_cache


POS_MAPPING = {
	"n": "noun",
	"v": "verb",
	"a": "adjective",
	"s": "adjective",  # 's' is an adjective satellite in WordNet
	"r": "adverb",
}


@lru_cache(maxsize=5)
def normalize_pos(tag: str) -> str:
	"""
	Convert WordNet POS tag to human-readable form.

	Args:
			tag: WordNet POS tag (n, v, a, r, s)

	Returns:
			Human-readable POS (noun, verb, adjective, adverb)
	"""
	return POS_MAPPING.get(tag, tag)


def lemmatize_word(word: str) -> str:
	"""
	Lemmatize a word to its base form.

	Args:
			word: Word to lemmatize

	Returns:
			Lemmatized word
	"""
	lemmatizer = WordNetLemmatizer()
	return lemmatizer.lemmatize(word.lower())


def get_synsets(word: str, pos_filter: Optional[List[str]] = None) -> List[wn.synset]:
	"""
	Get all synsets for a word, optionally filtered by part of speech.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			List of WordNet synsets
	"""
	synsets = wn.synsets(word)
	if not pos_filter:
		return synsets
	# Convert human-readable POS to WordNet tags for filtering
	# This allows parameters like ["n", "noun", "Noun"]
	pos_filter = [pos.lower() for pos in pos_filter]
	reverse_mapping = {v: k for k, v in POS_MAPPING.items()}
	wn_pos_filter = [reverse_mapping.get(pos, pos) for pos in pos_filter]
	return [synset for synset in synsets if synset.pos() in wn_pos_filter]


def format_lemma_name(name: str) -> str:
	"""
	Format a lemma name.
	Simply replaces underscores with spaces for now.

	Args:
			name: Lemma name from WordNet

	Returns:
			Formatted name
	"""
	return name.replace("_", " ")


def get_pos(word: str) -> List[str]:
	"""
	Get all parts of speech for a word.

	Args:
			word: Word to lookup

	Returns:
			List of parts of speech
	"""
	synsets = get_synsets(lemmatize_word(word))
	pos_set = {normalize_pos(synset.pos()) for synset in synsets}
	return sorted(list(pos_set))


def get_definitions(
	word: str, pos_filter: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
	"""
	Get all definitions for a word.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			List of definitions with POS and examples
	"""
	lemmatized = lemmatize_word(word)
	synsets = get_synsets(lemmatized, pos_filter)
	definitions = []
	seen_definitions = set()
	for synset in synsets:
		definition = synset.definition()
		# Skip duplicate definitions
		if definition in seen_definitions:
			continue
		seen_definitions.add(definition)
		definitions.append(definition)
	return definitions


def get_definition(word: str, pos: Optional[str] = None) -> str:
	"""
	Get the first definition of a word, optionally filtered by part of speech.

	Args:
			word: Word to lookup
			pos: Optional part of speech filter

	Returns:
			Definition string or empty string if not found
	"""
	pos_filter = [pos] if pos else None
	definitions = get_definitions(word, pos_filter)
	return definitions[0]["definition"] if definitions else ""


def get_synonyms(word: str, pos_filter: Optional[List[str]] = None) -> List[str]:
	"""
	Get all synonyms for a word.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			List of synonyms
	"""
	lemmatized = lemmatize_word(word)
	synsets = get_synsets(lemmatized, pos_filter)
	synonyms = set()
	for synset in synsets:
		for lemma in synset.lemmas():
			synonyms.add(format_lemma_name(lemma.name()))
	# Remove the word itself from synonyms
	if lemmatized in synonyms:
		synonyms.remove(lemmatized)
	return sorted(list(synonyms))


def get_antonyms(word: str, pos_filter: Optional[List[str]] = None) -> List[str]:
	"""
	Get all antonyms for a word.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			List of antonyms
	"""
	lemmatized = lemmatize_word(word)
	synsets = get_synsets(lemmatized, pos_filter)
	antonyms = set()
	for synset in synsets:
		for lemma in synset.lemmas():
			for antonym in lemma.antonyms():
				antonyms.add(format_lemma_name(antonym.name()))
	return sorted(list(antonyms))


def get_examples(word: str, pos_filter: Optional[List[str]] = None) -> List[str]:
	"""
	Get all usage examples for a word.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			List of example sentences
	"""
	lemmatized = lemmatize_word(word)
	synsets = get_synsets(lemmatized, pos_filter)

	examples = set()

	for synset in synsets:
		examples.update(synset.examples())

	return sorted(list(examples))


def get_hypernyms(word: str, pos_filter: Optional[List[str]] = None) -> List[str]:
	"""
	Get all hypernyms (more general terms) for a word.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			List of hypernyms
	"""
	lemmatized = lemmatize_word(word)
	synsets = get_synsets(lemmatized, pos_filter)

	hypernyms = set()

	for synset in synsets:
		for hypernym in synset.hypernyms():
			for lemma in hypernym.lemmas():
				hypernyms.add(format_lemma_name(lemma.name()))

	return sorted(list(hypernyms))


def get_hyponyms(word: str, pos_filter: Optional[List[str]] = None) -> List[str]:
	"""
	Get all hyponyms (more specific terms) for a word.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			List of hyponyms
	"""
	lemmatized = lemmatize_word(word)
	synsets = get_synsets(lemmatized, pos_filter)

	hyponyms = set()

	for synset in synsets:
		for hyponym in synset.hyponyms():
			for lemma in hyponym.lemmas():
				hyponyms.add(format_lemma_name(lemma.name()))

	return sorted(list(hyponyms))


@lru_cache(maxsize=100)
def get_word_data(word: str, pos_filter: Optional[List[str]] = None) -> Dict[str, Any]:
	"""
	Get comprehensive data about a word including definitions, examples, synonyms and antonyms.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			Dictionary containing word data organized by sense
	"""
	lemmatized = lemmatize_word(word)
	synsets = get_synsets(lemmatized, pos_filter)
	entries = []

	for synset in synsets:
		pos = normalize_pos(synset.pos())

		# Get synonyms and antonyms for this specific synset
		synonyms = set()
		antonyms = set()

		for lemma in synset.lemmas():
			lemma_name = format_lemma_name(lemma.name())
			synonyms.add(lemma_name)

			for antonym in lemma.antonyms():
				antonyms.add(format_lemma_name(antonym.name()))

		# Remove the word itself from synonyms
		if lemmatized in synonyms:
			synonyms.remove(lemmatized)

		# Get hypernyms and hyponyms for this synset
		hypernyms = {
			format_lemma_name(lemma.name())
			for hypernym in synset.hypernyms()
			for lemma in hypernym.lemmas()
		}

		hyponyms = {
			format_lemma_name(lemma.name())
			for hyponym in synset.hyponyms()
			for lemma in hyponym.lemmas()
		}

		entry = {
			"word": lemmatized,
			"definition": synset.definition(),
			"pos": pos,
			"examples": synset.examples(),
			"synonyms": sorted(list(synonyms)),
			"antonyms": sorted(list(antonyms)),
			"hypernyms": sorted(list(hypernyms)),
			"hyponyms": sorted(list(hyponyms)),
			"synset_id": synset.name(),
		}
		entries.append(entry)

	return {"word": lemmatized, "entries": entries, "num_senses": len(entries)}


@lru_cache(maxsize=100)
def get_word_data_plain(word: str, pos_filter: Optional[List[str]] = None) -> Dict[str, Any]:
	"""
	Get comprehensive data about a word including definitions, examples, synonyms and antonyms.

	Args:
			word: Word to lookup
			pos_filter: Optional list of parts of speech to filter by

	Returns:
			String containing the pretty printed word data organized by sense
	"""
	wd = get_word_data(word=word, pos_filter=pos_filter)
	output = []
	for i, entry in enumerate(wd["entries"]):
		final = f"{i+1}. {entry['pos'].capitalize()}: {entry['definition']}\n"
		if len(entry["examples"]) > 0:
			final += "Examples:" + "\t" + ("\n\t".join(entry["examples"])) + "\n"
		if len(entry["synonyms"]) > 0:
			final += "Synonyms: " + ", ".join(entry["synonyms"]) + "\n"
		if len(entry["antonyms"]) > 0:
			final += "Antonyms: " + ", ".join(entry["antonyms"]) + "\n"
		if len(entry["hypernyms"]) > 0:
			final += "Hypernyms: " + ", ".join(entry["hypernyms"]) + "\n"
		if len(entry["hyponyms"]) > 0:
			final += "Hyponyms: " + ", ".join(entry["hyponyms"]) + "\n"
		output.append(final)
	return "\n".join(output)
