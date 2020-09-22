import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from app.utils import find_first_char_index

nltk.download('stopwords')


def word_list_to_freq_dict(wordlist):
    wordfreq = [wordlist.count(w) for w in wordlist]

    return dict(list(zip(wordlist, wordfreq)))


def sort_freq_dict(freq_dict):
    aux = [(freq_dict[key], key) for key in freq_dict]
    aux.sort()
    aux.reverse()
    return aux


def find_top_ten_words(text, top_k_elements=10):
    original_text = text

    top_k_words_result = []

    # remove punctuations from text
    clear_text = text.translate(str.maketrans('', '', string.punctuation))
    text_tokens = word_tokenize(clear_text.lower())
    stopWords = set(stopwords.words("english"))
    wordlist = [word for word in text_tokens if word not in stopWords]

    freq_dict = word_list_to_freq_dict(wordlist)
    sorted_freq = sort_freq_dict(freq_dict)
    top_k_words = [tuple[1] for tuple in sorted_freq[:top_k_elements]]

    # Now find words in text
    for word in list(set(text_tokens)):
        if word.lower() in top_k_words:
            # Finds indexes in the text
            indexes, length = find_first_char_index(original_text.lower(), word, one_based=False)
            dict = {
                "Word": word,
                "Length": length,
                "Indexes": indexes,
                "Place": top_k_words.index(word.lower())+1
            }
            top_k_words_result.append(dict)
    return top_k_words_result


if __name__ == '__main__':
    find_top_ten_words(
        "In publishing and graphic design, Lorem ipsum is a placeholder text commonly used to demonstrate the visual form of a document or a typeface without relying on meaningful content. Lorem ipsum may be used before final copy is available, but it may also be used to temporarily replace copy in a process called greeking, which allows designers to consider form without the meaning of the text influencing the design.")
