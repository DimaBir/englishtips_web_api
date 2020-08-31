import nltk
import numpy as np


def avg_sentence_len(text: str) -> float:
    sent_lens = [len(nltk.word_tokenize(sent)) for sent in nltk.sent_tokenize(text)]
    return np.mean(sent_lens)
