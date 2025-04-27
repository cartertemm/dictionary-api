# Dictionary API

A straightforward dictionary API and frontend web application that provides word lookups using the WordNet lexical database. Get definitions, examples, synonyms, antonyms, hypernyms/hyponyms - all in one place.

[Demo](https://dictionary.ctemm.me)

## Background

> [WordNet®](https://wordnet.princeton.edu/) is a large lexical database of English. Nouns, verbs, adjectives, and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept.

Princeton University hosted a web interface allowing us to get basic information about words from the dataset, until it was discontinued sometime in 2024.

Projects like [PyDictionary](https://github.com/geekpradd/PyDictionary) and my own [Text Information](https://github.com/cartertemm/text_information) relied on scraping this data for rapid lookups.

This is an attempt to provide that same data in a straightforward way that can be self-hosted if needed.

## Features

- Clean, minimalist interface
- Interact with it from the command line, website, REST API, or python module
- Lightweight, accessibility-first design with screen reader announcements
- Comprehensive word lookups with commonly desired information
- Results neatly organized by part of speech
- Interactive related words - just click to explore further

## Tech Stack

- **Backend**: Flask (based on Python module)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3 - keeping it lean
- **Data Source**: WordNet via NLTK

## Using the API

### Web API

Basic word lookup:

For JSON:
```bash
curl https://dictionary.ctemm.me/api/word/computer
```

For plain text:
```bash
curl https://dictionary.ctemm.me/api/word/plain/computer
```

Or to save a little typing:
```bash
curl https://dictionary.ctemm.me/w/computer
```

### Command Line Interface

The package includes a convenient command-line tool with various options:

```bash
# Basic usage (defaults to plain output)
dict.py computer

# Get definitions
dict.py computer -D
# or
dict.py computer --definitions

# Get synonyms
dict.py computer -s
# or
dict.py computer --synonyms

# Get antonyms
dict.py computer -a
# or
dict.py computer --antonyms

# Force JSON output for any function
dict.py computer -s -j

# Run in interactive mode
dict.py -i
# or
dict.py --interactive

# Display version
dict.py --version

# Show help and all available options
dict.py --help
```

### Python Module

```python
from dictionary_api.word_data import get_word_data, get_synonyms, get_antonyms

# Get comprehensive word data
data = get_word_data("computer")

# Get just synonyms
synonyms = get_synonyms("amazing")
print(f"Synonyms for 'amazing': {', '.join(synonyms)}")

# Get antonyms
antonyms = get_antonyms("slow")
print(f"Antonyms for 'slow': {', '.join(antonyms)}")
```

## Setup

1. Clone the repository
    ```bash
    git clone https://github.com/cartertemm/dictionary-api.git
    ```

2. Create a virtual environment (optional) and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Download required NLTK data:
    ```python
    import nltk
    nltk.download('wordnet')
    # For additional languages: nltk.download('omw-1.4')
    ```

4. Either start the application using Flask or import the module and use it directly.
   A sample virtual host configuration is included for running with Apache2 and mod_wsgi.

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/word/<word>` - Retrieve detailed word information as JSON
- `GET /api/word?word=<word>` - Alternative query format
- `GET /api/word?word=<word>&pos=<pos>` - Filter results by part of speech
- `GET /api/word/plain/<word>` - Retrieve detailed word information as plain text
- `GET /w/<word>` - Shorthand for `/api/word/plain/<word>`

## How It Works

The application follows a simple workflow: users enter a word, the frontend sends a request to the backend API, which queries WordNet for relevant data. Results are returned in JSON format and displayed in a user-friendly interface. Related words are clickable for seamless navigation between terms - nothing complicated here.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.