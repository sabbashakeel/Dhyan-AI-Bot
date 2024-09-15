from fuzzywuzzy import fuzz, process

def preprocess(text):
    return text.strip()

def get_best_match(question, qa_dict):
    question = preprocess(question)
    choices = {preprocess(k): k for k in qa_dict.keys()}
    best_match, score = process.extractOne(question, choices.keys(), scorer=fuzz.ratio)
    return choices[best_match] if score > 60 else None