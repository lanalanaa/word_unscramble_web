import nltk
from nltk.corpus import wordnet as wn

def get_words_by_category(category):
    words = set()
    for synset in wn.synsets(category):
        for hyponym in synset.closure(lambda s: s.hyponyms()):
            for lemma in hyponym.lemmas():
                word = lemma.name().replace('_', ' ')
                if word.isalpha():
                    words.add(word.lower())
    return words

def filter_words(category_words, valid_words):
    return [word for word in category_words if word in valid_words]

def save_words_to_file(words, filename):
    with open(filename, 'w') as f:
        for word in sorted(words):
            f.write(word + '\n')

def main():
    # Load the full word list from words_alpha.txt
    with open('words_alpha.txt', 'r') as f:
        all_words = set(line.strip().lower() for line in f if line.strip().isalpha())

    categories = ['animal', 'fruit', 'countries', 'sport', 'colour']

    for category in categories:
        print(f"Generating word list for category: {category}")
        category_words = get_words_by_category(category)
        # Filter category words to include only those present in the full word list
        valid_category_words = filter_words(category_words, all_words)
        if valid_category_words:
            filename = f'words/{category}s.txt'  # Pluralize category for filename
            save_words_to_file(valid_category_words, filename)
            print(f"Saved {len(valid_category_words)} words to {filename}")
        else:
            print(f"No valid words found for category: {category}")

if __name__ == '__main__':
    main()
