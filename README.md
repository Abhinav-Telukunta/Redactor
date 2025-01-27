Name: Vijay Abhinav Telukunta

## Project Description 

This project implements a text redaction tool that identifies and redacts sensitive information from textual data. Utilizing the Google Cloud Natural Language API and NLTK, the tool processes text to detect and redact various types of sensitive entities, including names, addresses, dates, phone numbers, and specific concepts.

## How to install
 - Install pipenv using sudo apt install pipenv

 - Then, it would create a virtual environment in the current directory.

 - Activate the virtual environment using pipenv shell.

 - Install spacy using command pipenv install spacy

 - Install spacy en_core_web_trf module using command python -m spacy download en_core_web_trf

 - Install google-cloud-language using command pipenv install google-cloud-language

 - Install nltk using command pipenv install nltk

 - Install pytest using command pipenv install pytest

 - Make sure python is also installed

## How to run

 - Open Terminal in the project root directory

 - Activate virtual environment using command pipenv shell

 - Then run command for example: pipenv run python redactor.py --input *.txt --names --dates --concepts --output 'files/' --stats 'stat_file.txt' 

 - For running tests, run command pipenv run python -m pytest


## Functions

### redactor.py

The redactor.py file provides functions for redacting various censor flags such as names, dates, phones, address and concepts. Below is a description of each function:

 - redact_concepts(concept_list, text): The redact_concepts function is designed to identify and redact sentences containing specified concepts or their synonyms from a given text. It utilizes the NLTK library to tokenize the input text into sentences and the WordNet lexical database to retrieve synonyms for each concept and redacts that whole sentence.

 - redact_phone_numbers(text, type_map): The redact_phone_numbers function is designed to identify and redact phone numbers from a given text while keeping track of the count of phone numbers detected. This function is useful for sanitizing sensitive information in documents or data sets.

 - redact_addresses(text, type_map): The redact_addresses function is designed to identify and redact addresses and location entities from a given text, enhancing data privacy and security by removing sensitive information. This function utilizes Google's Natural Language API for address recognition.

 - filter_dates(ents): Removes unnecessary categorization of dates like week, past day, days of week

 - redact_names(text, type_map, sorted_ents): This redacts all names present in text using spacy en_core_web_trf

 - redact_dates(text, type_map, sorted_ents): This redacts all dates present in text using spacy en_core_web_trf

 - redact(text, flags): Main pipeline function which carries redaction in sequence calling all required functions

 - enableRequiredFlags(args): Checking all user input flags passed through command line

 - write_to_file(redacted_content, args, input_file_path): Writes the final redacted content to output file path specified.

 - get_files(args): Fetches all input files which match given pattern using glob

 - write_summary(summary, output): Writing stats data to stdout or stderr or filename

 - main(): Handles total logic of redaction

### tests functions

The tests directory contains unit tests for various functions within the redactor.py file. The tests ensure that the functions are working as expected. Here's a description of each test:

 - test_dates.py: Tests whether dates are correctly redacted
 - test_names.py: Tests whether names are correctly redacted
 - test_phones.py: Tests whether names are correctly redacted

These tests use pytest and unittest.mock to simulate real scenarios and validate the functionality of the project code.

## Bugs and Assumptions

 - The code wouldn't work accurately and it won't be successful in redacting the addresses correctly. I have experimented with various libraries such as usaddress, spacy, google api etc. among which no library was accurate in handling addresses properly. The best address redaction among these was with google api. So, I used it.
 - I am assuming phone numbers would be of format 3 digits-4 digits-4 digits or +country code 3d-4d-4d. Apart from these patterns, regex fails to correctly identify phone number.
 - For dates, I am assuming to take day of week as well for redaction. For example, the total string : Tue 27th Dec 2001 would be redacted including Tue.
 - For concepts, I have used NLTK to capture synonyms of given concept word and redacting sentences. There might be issues in properly capturing all synonyms of a given word.
 - For testing address and concepts, since google api and nltk are involved, there is no straight forward way to test it in pytest. But, I have tested those functions from command line and its working correctly.

 ## Resources for help

  - Google API - https://cloud.google.com/natural-language/docs/reference/libraries#setting_up_authentication
  - NLTK - https://www.nltk.org/


## Keys

I am using My google cloud service account key to access google api's. 