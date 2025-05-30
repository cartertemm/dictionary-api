document.addEventListener('DOMContentLoaded', () => {
    const wordInput = document.getElementById('word-input');
    const lookupButton = document.getElementById('lookup-button');
    const resultsSection = document.getElementById('results');
    const statusDiv = document.getElementById('status');

    const performLookup = async () => {
        const word = wordInput.value.trim();
        if (!word) {
            resultsSection.innerHTML = '';
            setStatus('Please enter a word.');
            return;
        }

        resultsSection.innerHTML = ''; // Clear previous results
        setStatus(`Looking up "${word}"...`, 'loading');

        try {
            // Use the /api/word/{word} endpoint which should return the detailed structure
            // Ensure the word is properly encoded for the URL path
            const response = await fetch(`/api/word/${encodeURIComponent(word)}`);
            const data = await response.json();

            if (!response.ok) {
                // Try to parse error from standard { "error": "message" } format
                let errorMessage = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json(); // Try parsing JSON even on error
                    errorMessage = errorData.error || errorData.message || errorMessage;
                } catch (e) {
                    // Ignore if response is not JSON
                }
                 throw new Error(errorMessage);
            }

            // Check for application-level errors within the JSON response
            if (data.error) {
                 throw new Error(data.error);
            }
             // Also check for the 'message' field often used for "not found" etc.
            if (response.status === 404 && data.message) {
                 throw new Error(data.message);
            }


            // Pass the original searched word for display purposes
            displayResults(data, word); // Assuming data structure is {  { word: ..., entries: [...] } }
            setStatus(`Results for "${word}" loaded.`);

        } catch (error) {
            console.error('Lookup failed:', error);
            // Display the error message from the caught error object
            displayError(`Error looking up "${word}": ${error.message}`);
            setStatus(`Error looking up "${word}".`);
        }
    };

    const setStatus = (message, type = '') => {
        statusDiv.textContent = message;
        statusDiv.className = type; // Add class for potential styling (e.g., 'loading', 'error')
    };

    const displayError = (errorMessage) => {
        resultsSection.innerHTML = `<p class="error">${errorMessage}</p>`;
    };

    const displayResults = (responseData, originalWord) => {
        resultsSection.innerHTML = ''; // Clear previous content
        const data = responseData.data;
        if (!data || !data.entries || data.entries.length === 0) {
             // Use message from response if available, otherwise generate one
             const message = responseData.message || `No definitions found for "${originalWord}".`;
             displayError(message);
             setStatus(message);
             return;
        }
        const resultsHeading = document.createElement('h2');
        // Use the lemmatized word from the response if available, otherwise the original
        const displayWord = data.word || originalWord;
        resultsHeading.textContent = `Results for "${displayWord}"`;
        resultsSection.appendChild(resultsHeading);
        // Group entries by part of speech
        const groupedByPos = {};
        data.entries.forEach(entry => {
            const pos = entry.pos || 'unknown'; // Default POS if missing
            if (!groupedByPos[pos]) {
                // Initialize structure for this part of speech
                groupedByPos[pos] = {
                    definitions: [],
                    examples: new Set(), // Use Sets to avoid duplicates within a POS section
                    synonyms: new Set(),
                    antonyms: new Set(),
                    hypernyms: new Set(),
                    hyponyms: new Set()
                };
            }
            // Add data from the current entry to the appropriate POS group
            if (entry.definition) {
                 // Keep definitions separate, maybe include synset_id or context if needed later
                 // For now, just list them.
                groupedByPos[pos].definitions.push(entry.definition);
            }
            (entry.examples || []).forEach(item => groupedByPos[pos].examples.add(item));
            (entry.synonyms || []).forEach(item => groupedByPos[pos].synonyms.add(item));
            (entry.antonyms || []).forEach(item => groupedByPos[pos].antonyms.add(item));
            (entry.hypernyms || []).forEach(item => groupedByPos[pos].hypernyms.add(item));
            (entry.hyponyms || []).forEach(item => groupedByPos[pos].hyponyms.add(item));
        });

        // Now render the grouped data
        const sortedPOS = Object.keys(groupedByPos).sort(); // Sort POS alphabetically
        if (sortedPOS.length === 0) {
             displayError(`No specific data found for "${displayWord}" broken down by part of speech.`);
             setStatus(`No specific data found for "${displayWord}".`);
             return;
        }
        sortedPOS.forEach(pos => {
            const posData = groupedByPos[pos];
            const posSection = document.createElement('section');
            posSection.setAttribute('aria-labelledby', `heading-${pos}`);
            const posHeading = document.createElement('h3');
            posHeading.id = `heading-${pos}`;
            posHeading.textContent = pos.replace(/_/g, ' '); // Format POS nicely
            posSection.appendChild(posHeading);
            // The lists that should have clickable words
            const clickableTitles = ['Synonyms', 'Antonyms', 'Hypernyms (more general)', 'Hyponyms (more specific)'];
            // Display definitions for this POS
            if (posData.definitions.length > 0) {
                 addList(posSection, 'Definitions', posData.definitions, clickableTitles);
            }
            // Display other lists, converting Sets back to sorted arrays
            addList(posSection, 'Examples', Array.from(posData.examples).sort(), clickableTitles);
            addList(posSection, 'Synonyms', Array.from(posData.synonyms).sort(), clickableTitles);
            addList(posSection, 'Antonyms', Array.from(posData.antonyms).sort(), clickableTitles);
            addList(posSection, 'Hypernyms (more general)', Array.from(posData.hypernyms).sort(), clickableTitles);
            addList(posSection, 'Hyponyms (more specific)', Array.from(posData.hyponyms).sort(), clickableTitles);
            // Only append the section if it contains more than just the heading
            if (posSection.childElementCount > 1) {
                resultsSection.appendChild(posSection);
            }
        });
         // Check if any sections were actually added
        if (resultsSection.querySelectorAll('section').length === 0) {
             // This might happen if all POS sections were empty after filtering/processing
             displayError(`No displayable data found for "${displayWord}" after processing.`);
             setStatus(`No displayable data found for "${displayWord}".`);
        }
    };

    const addList = (parentElement, title, items, clickableTitles = []) => {
        // Ensure items is treated as an array, even if it's a single definition string initially
        const itemsArray = Array.isArray(items) ? items : [items];
        const isClickableList = clickableTitles.includes(title);

        if (itemsArray && itemsArray.length > 0 && itemsArray.some(item => item)) { // Check if array has at least one non-empty item
            const subHeading = document.createElement('h4');
            subHeading.textContent = title;
            parentElement.appendChild(subHeading);

            const list = document.createElement('ul');
            itemsArray.forEach(item => {
                 if (item) { // Ensure item is not null/empty before creating li
                    const listItem = document.createElement('li');
                    if (isClickableList) {
                        const link = document.createElement('a');
                        link.href = '#'; // Prevent navigation, handle click via JS
                        link.textContent = item;
                        link.style.cursor = 'pointer'; // Indicate it's clickable
                        link.addEventListener('click', (event) => {
                            event.preventDefault(); // Stop link navigation
                            const clickedWord = event.target.textContent;
                            wordInput.value = clickedWord; // Update input field
                            performLookup(); // Trigger new lookup
                            wordInput.focus(); // Optional: focus input after click
                            window.scrollTo(0, 0); // Scroll to top
                        });
                        listItem.appendChild(link);
                    } else {
                        listItem.textContent = item; // For non-clickable lists (Definitions, Examples)
                    }
                    list.appendChild(listItem);
                 }
            });
             // Only append the list if it actually contains list items
            if (list.childElementCount > 0) {
                parentElement.appendChild(list);
            } else {
                 // If the list ended up empty (e.g., all items were null/empty), remove the subheading too
                 parentElement.removeChild(subHeading);
            }
        }
    };

    // Event Listeners
    lookupButton.addEventListener('click', performLookup);

    wordInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form submission if it were in a form
            performLookup();
        }
    });

     // Initial focus on input field
     wordInput.focus();
});
