import nltk
import numpy as np

from nltk.tokenize import RegexpTokenizer


def avg_sentence_len(text: str) -> float:
    tokenizer = RegexpTokenizer(r'\w+')
    sent_lens = [len(tokenizer.tokenize(sent)) for sent in nltk.sent_tokenize(text)]
    return np.mean(sent_lens)
