# Bold Words in Text Function

This Python function allows you to bold specific words or phrases in a `.docx` document. It is designed to work with the `python-docx` library and supports flexible, case-insensitive matching to bold target phrases while respecting word boundaries.

## Features
- **Case-insensitive matching**: The function matches words regardless of casing.
- **Word boundaries**: Ensures only full words are matched, avoiding partial matches inside larger words.
- **Support for multiple phrases**: You can pass a list of phrases to be bolded in the document.


## How to install

Run the following commands:

```$ pip install docxtexthighlighter```


## Example


```
>>> from docxtexthighlighter import bold_words_in_text

>>> list_of_words_to_be_bolded = ['dogs', 'cats', 'birds']

>>> bold_words_in_text('path/to/your/docx/file', list_of_words_to_be_bolded, output_path='path/to/your/output/location')

"Document has been saved to this path: 'path/to/your/output/location'"

```

## Notes

By default, the function saves the output to your current working directory as 'output.docx'.