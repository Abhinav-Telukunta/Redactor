import spacy
import argparse
import re
from google.cloud import language_v1
import os
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize
import ssl
import glob

ssl._create_default_https_context = ssl._create_unverified_context

nltk.download("wordnet", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Load the spaCy model
nlp = spacy.load("en_core_web_trf")

stats = []

def redact_concepts(concept_list, text):

    def get_synonyms(word):
        lemmas = set().union(*[s.lemmas() for s in wn.synsets(word)])
        return list(set(l.name().lower().replace("_", " ") for l in lemmas) - {word})

    sentences = sent_tokenize(text)
    
    # Create a set for concepts and their synonyms
    concepts_with_synonyms = set(concept_list)  # Start with the original concepts
    for concept in concept_list:
        synonyms = get_synonyms(concept)
        #print("synonyms are ", synonyms)
        concepts_with_synonyms.update(synonyms)  # Add synonyms to the set


    # Initialize a list to hold redacted sentences
    redacted_sentences = []

    concept_map = {}
    
    # Iterate over sentences and check for presence of concepts or synonyms
    for sentence in sentences:
        # Check if any concept or related term is in the sentence
        for concept in concepts_with_synonyms:
            if concept in sentence.lower():
                concept_map[concept] = concept_map.get(concept,0)+1
                redacted_sentences.append("\u2588" * len(sentence))
                break
        else:
            # Keep the original sentence
            redacted_sentences.append(sentence)
    
    # Join the sentences back into a single string
    redacted_text = ' '.join(redacted_sentences)

    for k, v in concept_map.items():
        stats.append(f"Redacted CONCEPT {k}: {v} times")
    
    return redacted_text


# Function to replace phone numbers with block unicode characters
def redact_phone_numbers(text, type_map):
    phone_regex = r"(\+?\d{1,3}[-\s])?\(?\d{3}\)?[-\s]\d{3}[-\s]\d{4}"
    matches = re.findall(phone_regex, text)
    match_count = len(matches)
    type_map['PHONE'] = type_map.get('PHONE',0)+1
    # Replace each phone number match with block characters of the same length
    redacted_text = re.sub(phone_regex, lambda match: "\u2588" * len(match.group()), text)
    return redacted_text

def redact_addresses(text, type_map):

    address = [language_v1.Entity.Type.ADDRESS, language_v1.Entity.Type.LOCATION]

    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = client.analyze_entities(document=document)

    def sort_key(entity):
        if entity.type_ == address[0]:
            return (0, entity.name)  # Addresses come first
        elif entity.type_ == address[1]:
            return (1, entity.name)  # Locations come second
        else:
            return (2, entity.name)  # Other entity types come last

    # Sort the entities based on the defined key
    sorted_entities = sorted(response.entities, key=sort_key)
    
    for entity in sorted_entities:
        if entity.type_ in address:
            type_map['ADDRESS'] = type_map.get('ADDRESS',0)+1
            pattern = r'\b' + re.escape(entity.name) + r'\b'
            text = re.sub(pattern, "\u2588" * len(entity.name), text)

    return text

def filter_dates(ents):
    # Regex pattern to match weekdays and the word "week"
    weekday_regex = r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|week)\b'
    result_ents = []
    for ent in ents:
        if ent.label_ == 'DATE' and re.search(weekday_regex, ent.text, re.IGNORECASE)!=None:
            continue
        result_ents.append(ent)

    return result_ents

def redact_names(text, type_map, sorted_ents):
    for ent in sorted_ents:
        if ent.label_ == 'PERSON':
            # Replace the name with block Unicode characters
            text = text.replace(ent.text, "\u2588" * len(ent.text))
            type_map[ent.label_] = type_map.get(ent.label_,0)+1

    email_redact_regex = r"\b[A-Za-z0-9._%+-]+(?=@enron\.com)"
    matches = re.findall(email_redact_regex, text)
    match_count = len(matches)
    type_map['PERSON'] = type_map.get('PERSON',0)+match_count
    # Redact the emails by replacing with block characters
    redacted_text = re.sub(email_redact_regex, lambda match: "\u2588" * len(match.group()), text)
    return redacted_text

def redact_dates(text, type_map, sorted_ents):
    for ent in sorted_ents:
        if ent.label_ == 'DATE':
            # Replace the name with block Unicode characters
            text = text.replace(ent.text, "\u2588" * len(ent.text))
            type_map[ent.label_] = type_map.get(ent.label_,0)+1
    return text

# Function to redact
def redact(text, flags):
    doc = nlp(text)
    redacted_text = text
    sorted_ents = sorted(doc.ents, key=lambda ent: len(ent.text), reverse=True)

    if "DATE" in flags:
        sorted_ents = filter_dates(sorted_ents)

    type_map = {}

    if "PERSON" in flags:
        redacted_text = redact_names(redacted_text, type_map, sorted_ents)
    if "DATE" in flags:
        redacted_text = redact_dates(redacted_text, type_map, sorted_ents)
    if "PHONE" in flags:
        redacted_text = redact_phone_numbers(redacted_text, type_map)

    if "ADDRESS" in flags:
        redacted_text = redact_addresses(redacted_text, type_map)

    for k, v in type_map.items():
        stats.append(f"Redacted {k}: {v} times")
    
    return redacted_text

def enableRequiredFlags(args):
    flags=[]
    if args.names:
        flags.append("PERSON")
    if args.dates:
        flags.append("DATE")
    if args.phones:
        flags.append("PHONE")
    if args.address:
        flags.append("ADDRESS")
    if args.concept is not None:
        flags.append("CONCEPT")

    return flags

def write_to_file(redacted_content, args, input_file_path):
    if args.output is not None:
        os.makedirs(args.output,exist_ok=True)

    output_file_name = input_file_path[input_file_path.rfind('/')+1:] + ".censored"
    output_file_dir = os.path.join(args.output,output_file_name)
    with open(output_file_dir, "w") as file:
        file.write(redacted_content)

def get_files(args):
    file_patterns = args.input
    files_to_read = []
    for pattern in file_patterns:
        # Use glob to find all files matching the pattern
        matched_files = glob.glob(pattern)
        files_to_read.extend(matched_files)

    return files_to_read


def write_summary(summary, output):
    if output is not None:
        summ_str = "\n".join(summary)
        if output == "stdout":
            print(summ_str)
        elif output == "stderr":
            print(summ_str, file=sys.stderr)
        else:
            with open(output, 'w') as f:
                f.write(summ_str)


def main():
    # Argument parser to handle command-line inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', action='append', required=True)
    parser.add_argument('--names', action='store_true')
    parser.add_argument('--dates', action='store_true')
    parser.add_argument('--phones', action='store_true')
    parser.add_argument('--address', action='store_true')
    parser.add_argument('--concept', action='append')
    parser.add_argument('--output')
    parser.add_argument('--stats')
    
    
    args = parser.parse_args()

    files_to_read = get_files(args)

    flags = enableRequiredFlags(args)

    for file_path in files_to_read:
        try:
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                print(f"Error: Cannot read file '{file_path}'")
                continue
            
            # Read file content
            with open(file_path, 'r') as file:
                content = file.read()
                # Process content as needed

            stats.append(f"File: {file_path[file_path.rfind('/')+1:]}")

            if "CONCEPT" in flags:
                concept_list = args.concept
                content = redact_concepts(concept_list,content)

            redacted_content = redact(content, flags)

            stats.append("-------------------------------------------------------")

            # Print or save the redacted content
            write_to_file(redacted_content, args, file_path)

        except Exception as e:
            print(f"Error: Could not read or process file '{file_path}' - {e}")

    write_summary(stats, args.stats)

if __name__ == "__main__":
    main()
