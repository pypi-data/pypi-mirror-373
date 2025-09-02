import json
import os
import re
from copy import deepcopy
from typing import List

from .model import TrieNode
from .. import LexSynth

# 匹配换行符
PATTERN_NEWLINE = re.compile(r"[\r\n]+")

# 匹配空格或制表符
PATTERN_SPACE_TAB = re.compile(r"[ \t]+")

# 匹配包含各种标点符号（中英文）和特殊字符的字符串
PATTERN_PUNCTUATION_AND_SPECIAL_CHARS = re.compile(
    r"[ ,\./;'\[\]\\`~!@#$%\^&\*\(\)=\+_<>\?:\"\{\}\|，。；‘’【】、！￥……（）——《》？：“”-]+"
)


_curr_dir = os.path.dirname(os.path.abspath(__file__))

with open(f"{_curr_dir}/../dictionary/stopwords.json", encoding="utf-8") as f:
    STOPWORDS = set(json.loads(f.read())["STOPWORDS"])


def generate_ngram(input_list, n):
    result = []
    for i in range(1, n + 1):
        result.extend(zip(*[input_list[j:] for j in range(i)]))
    return result


class NewWordDetection:
    def __init__(self, nlp: LexSynth):
        self.nlp = nlp
        self.word_freq = deepcopy(self.nlp.tokenizer.tokenizer.FREQ)
        self.ori_root = TrieNode("*", self.word_freq)

    @staticmethod
    def split_text(text) -> List[str]:

        sentences = PATTERN_PUNCTUATION_AND_SPECIAL_CHARS.split(text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def generate_ngram(input_list, n):
        result = []
        for i in range(1, n + 1):
            result.extend(zip(*[input_list[j:] for j in range(i)]))
        return result

    def split_sentences_word(self, text: str) -> List[List[str]]:
        _data = []
        for i in self.split_text(text):
            _data.append(
                [j for j in self.nlp.content_sm_cut(i).split() if j not in STOPWORDS]
            )
        return _data

    @staticmethod
    def dynamic_threshold(N, base_threshold=5, ref_length=10000, alpha=0.5):
        return int(max(2, base_threshold * (ref_length / N) ** alpha))

    def find_word(self, text: str, ngram=3, top_n=None):
        _root = deepcopy(self.ori_root)
        _N = 0

        for word_list in self.split_sentences_word(text):
            _N += len("".join(word_list))
            ngrams = self.generate_ngram(word_list, ngram)
            for d in ngrams:
                _root.add(d)
        return _root.find_word(top_n or self.dynamic_threshold(_N))
