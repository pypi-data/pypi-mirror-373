import logging
import math
import os
import re
import warnings

import nltk
from nltk import PorterStemmer, WordNetLemmatizer, word_tokenize
from nltk.data import find

# 忽略无效转义序列的警告
warnings.filterwarnings(
    "ignore", message=".*invalid escape sequence.*", category=DeprecationWarning
)

# 忽略pkg_resources弃用警告
warnings.filterwarnings(
    "ignore", message=".*pkg_resources is deprecated.*", category=DeprecationWarning
)


from jieba import Tokenizer, re_userdict


from .utils import (
    traditional_to_simplified,
    fullwidth_to_halfwidth,
    is_chinese,
)


def ensure_nltk_resource(resource_name):
    try:
        find(resource_name)
    except LookupError:
        logging.info(f"Resource '{resource_name}' not found. Downloading...")
        nltk.download(resource_name.split("/")[-1])


ensure_nltk_resource("tokenizers/punkt_tab")
ensure_nltk_resource("corpora/wordnet")
ensure_nltk_resource("corpora/omw-1.4")

_curr_dir = os.path.dirname(os.path.abspath(__file__))


class RagTokenizer:
    def __init__(self, user_dict=None):

        self.SPLIT_CHAR = r"([ ,\.<>/?;:'\[\]\\`!@#$%^&*\(\)\{\}\|_+=《》，。？、；‘’：“”【】~！￥%……（）——-]+|[a-zA-Z0-9,\.-]+)"
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.DENOMINATOR = 1000000
        self.tokenizer = Tokenizer()
        self.tokenizer.initialize()
        with open(f"{_curr_dir}/dictionary/jieba_ext_dict.txt", encoding="utf-8") as f:
            self.tokenizer.load_userdict(f)

        if user_dict:
            self.tokenizer.load_userdict(user_dict)
        self.pos = {}
        self.initialize_pos()

    def initialize_pos(self):
        self.pos = {}
        with self.tokenizer.get_dict_file() as f:
            for line in f:
                word, freq, tag = re_userdict.match(
                    line.strip().decode("utf-8")
                ).groups()
                self.pos[word] = tag
                if tag is not None and word is not None:
                    self.pos[word.strip()] = tag.strip()

        with open(f"{_curr_dir}/dictionary/jieba_ext_dict.txt", encoding="utf-8") as f:
            for line in f:
                word, freq, tag = re_userdict.match(line.strip()).groups()
                self.pos[word] = tag
                if tag is not None and word is not None:
                    self.pos[word.strip()] = tag.strip()

    def tok_add_word(self, word, frequency: int = None, pos: str = None):
        """添加词语到分词词典
        Example: tok_add_word("量子计算", freq=100, pos="n")
        """
        self.tokenizer.add_word(word, freq=frequency, tag=pos)
        self.pos[word] = pos

    def tok_del_word(self, word):
        """从分词词典删除词语"""
        self.tokenizer.del_word(word)
        if word in self.pos:
            del self.pos[word]

    def tok_update_word(self, word, frequency: int = None, pos: str = None):
        """更新词语信息（实际是先删除后添加）"""
        self.tokenizer.del_word(word)
        self.tokenizer.add_word(word, freq=frequency, tag=pos)
        self.pos[word] = pos

    def freq(self, tk):
        _freq = self.tokenizer.FREQ.get(tk, 0)
        if _freq:
            _freq = int(math.log(float(_freq) / self.DENOMINATOR) + 0.5)  # 对数压缩
            return int(math.exp(_freq) * self.DENOMINATOR + 0.5)  # 整数近似
        else:
            return 0

    def tag(self, tk):
        if tk in self.pos:
            return self.pos[tk]
        else:
            return ""

    def _split_by_lang(self, line):
        txt_lang_pairs = []
        arr = re.split(self.SPLIT_CHAR, line)
        for a in arr:
            if not a:
                continue
            s = 0
            e = s + 1
            zh = is_chinese(a[s])
            while e < len(a):
                _zh = is_chinese(a[e])
                if _zh == zh:
                    e += 1
                    continue
                txt_lang_pairs.append((a[s:e], zh))
                s = e
                e = s + 1
                zh = _zh
            if s >= len(a):
                continue
            txt_lang_pairs.append((a[s:e], zh))
        return txt_lang_pairs

    def merge_(self, tks):
        res = []
        tks = re.sub(r"[ ]+", " ", tks).split()
        s = 0
        while True:
            if s >= len(tks):
                break
            E = s + 1
            for e in range(s + 2, min(len(tks) + 2, s + 6)):
                tk = "".join(tks[s:e])
                if re.search(self.SPLIT_CHAR, tk) and self.tag(tk):
                    E = e
            res.append("".join(tks[s:E]))
            s = E

        return " ".join(res)

    def english_normalize_(self, tks):
        return [
            (
                self.stemmer.stem(self.lemmatizer.lemmatize(t))
                if re.match(r"[a-zA-Z_-]+$", t)
                else t
            )
            for t in tks
        ]

    def tokenize(self, line):
        line = re.sub(r"\W+", " ", line)
        line = fullwidth_to_halfwidth(line).lower()
        line = traditional_to_simplified(line)

        arr = self._split_by_lang(line)
        res = []
        for L, lang in arr:
            if not lang:
                res.extend(
                    [
                        self.stemmer.stem(self.lemmatizer.lemmatize(t))
                        for t in word_tokenize(L)
                    ]
                )
                continue
            if len(L) < 2 or re.match(r"[a-z\.-]+$", L) or re.match(r"[0-9\.-]+$", L):
                res.append(L)
                continue

            res.extend(self.tokenizer.lcut(L))
        res = " ".join(res)
        return self.merge_(res)

    def fine_grained_tokenize(self, tks):
        tks = tks.split()
        zh_num = len([1 for c in tks if c and is_chinese(c[0])])
        if zh_num < len(tks) * 0.2:
            res = []
            for tk in tks:
                res.extend(tk.split("/"))
            return " ".join(res)
        res = []
        for tk in tks:
            if len(tk) < 3 or re.match(r"[0-9,\.-]+$", tk):
                res.append(tk)
                continue
            for i in self.tokenizer.lcut_for_search(tk):
                if not i == tk:
                    res.append(i)
        return " ".join(self.english_normalize_(res))
