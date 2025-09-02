import json
import math
import os
import re

import numpy as np

from .rag_tokenizer import RagTokenizer
from .surname import check_surname

_curr_dir = os.path.dirname(os.path.abspath(__file__))


class TermWeightDealer:
    def __init__(self, tokenizer: RagTokenizer):
        with open(f"{_curr_dir}/dictionary/stopwords.json", encoding="utf-8") as f:
            self.stop_words = set(json.loads(f.read())["STOPWORDS"])

        with open(f"{_curr_dir}/dictionary/ner.json", encoding="utf-8") as f:
            self.ne = json.loads(f.read())

        self.df = {}

        self.tokenizer = tokenizer

        self.ner_type = {
            "toxic": 2,
            "func": 1,
            "corp": 3,
            "loca": 3,
            "sch": 3,
            "stock": 3,
            "firstnm": 1,
            "surname": 3,
        }

    def set_word(self, word: str, term_type: str) -> None:
        if term_type not in self.ner_type:
            raise ValueError(f"类型 {type} 没有定义权重")
        self.ne[word] = term_type

    def del_word(self, word: str) -> None:
        if word in self.ne:
            _ = self.ne.pop(word)

    def pretoken(self, txt, num=False, stpwd=True):
        patt = [
            r"[~—\t @#%!<>,\.\?\":;'\{\}\[\]_=\(\)\|，。？》•●○↓《；‘’：“”【¥ 】…￥！、·（）×`&\\/「」\\]"
        ]
        rewt = []
        for p, r in rewt:
            txt = re.sub(p, r, txt)

        res = []
        for t in self.tokenizer.tokenize(txt).split():
            tk = t
            if (stpwd and tk in self.stop_words) or (
                re.match(r"[0-9]$", tk) and not num
            ):
                continue
            for p in patt:
                if re.match(p, t):
                    tk = "#"
                    break
            # tk = re.sub(r"([\+\\-])", r"\\\1", tk)
            if tk != "#" and tk:
                res.append(tk)
        return res

    def tokenMerge(self, tks):
        def oneTerm(t):
            return len(t) == 1 or re.match(r"[0-9a-z]{1,2}$", t)

        res, i = [], 0
        while i < len(tks):
            j = i
            if (
                i == 0
                and oneTerm(tks[i])
                and len(tks) > 1
                and (len(tks[i + 1]) > 1 and not re.match(r"[0-9a-zA-Z]", tks[i + 1]))
            ):  # 多 工位
                res.append(" ".join(tks[0:2]))
                i = 2
                continue

            while (
                j < len(tks)
                and tks[j]
                and tks[j] not in self.stop_words
                and oneTerm(tks[j])
            ):
                j += 1
            if j - i > 1:
                if j - i < 5:
                    res.append(" ".join(tks[i:j]))
                    i = j
                else:
                    res.append(" ".join(tks[i : i + 2]))
                    i = i + 2
            else:
                if len(tks[i]) > 0:
                    res.append(tks[i])
                i += 1
        return [t for t in res if t]

    def split(self, txt):
        tks = []
        for t in re.sub(r"[ \t]+", " ", txt).split():
            if (
                tks
                and re.match(r".*[a-zA-Z]$", tks[-1])
                and re.match(r".*[a-zA-Z]$", t)
                and tks
                and self.ne.get(t, "") != "func"
                and self.ne.get(tks[-1], "") != "func"
            ):
                tks[-1] = tks[-1] + " " + t
            else:
                tks.append(t)
        return tks

    def weights(self, tks, preprocess=True):
        # def skill(t):
        #     if t not in self.sk:
        #         return 1
        #     return 6

        def ner(t):

            def _ner(word):
                res = self.ne.get(word, "")
                if res:
                    return res
                elif self.tokenizer.tag(word) == "nr":  # 词表本来就存在的人名
                    return "surname"
                elif check_surname(word):  # 算法识别的人名
                    return "surname"
                else:
                    return ""

            if re.match(r"[0-9,.]{2,}$", t):
                return 2
            if re.match(r"[a-z]{1,2}$", t):
                return 0.01

            _n = _ner(t)
            if _n not in self.ner_type:
                return 1

            return self.ner_type[_n]

        def postag(t):
            t = self.tokenizer.tag(t)
            if t in {"r", "c", "d"}:
                return 0.3
            if t in {"ns", "nt"}:
                return 3
            if t in {"nz"}:
                return 2.5
            if t in {"n"}:
                return 2
            if re.match(r"[0-9-]+", t):
                return 2
            return 1

        def freq(t):
            if re.match(r"[0-9. -]{2,}$", t):
                return 3
            s = self.tokenizer.freq(t)
            if not s and re.match(r"[a-z. -]+$", t):
                return 300
            if not s:
                s = 0

            if not s and len(t) >= 4:
                s = [
                    tt
                    for tt in self.tokenizer.fine_grained_tokenize(t).split()
                    if len(tt) > 1
                ]
                if len(s) > 1:
                    s = np.min([freq(tt) for tt in s]) / 6.0
                else:
                    s = 0

            return max(s, 10)

        def df(t):
            if re.match(r"[0-9. -]{2,}$", t):
                return 5
            if t in self.df:
                return self.df[t] + 3
            elif re.match(r"[a-z. -]+$", t):
                return 300
            elif len(t) >= 4:
                s = [
                    tt
                    for tt in self.tokenizer.fine_grained_tokenize(t).split()
                    if len(tt) > 1
                ]
                if len(s) > 1:
                    return max(3, np.min([df(tt) for tt in s]) / 6.0)

            return 3

        def idf(s, N):
            return math.log10(10 + ((N - s + 0.5) / (s + 0.5)))

        tw = []
        if not preprocess:
            idf1 = np.array([idf(freq(t), 10000000) for t in tks])
            idf2 = np.array([idf(df(t), 1000000000) for t in tks])
            wts = (0.3 * idf1 + 0.7 * idf2) * np.array(
                [ner(t) * postag(t) for t in tks]
            )
            wts = [s for s in wts]
            tw = list(zip(tks, wts))
        else:
            for tk in tks:
                tt = self.tokenMerge(self.pretoken(tk, True))
                idf1 = np.array([idf(freq(t), 10000000) for t in tt])
                idf2 = np.array([idf(df(t), 1000000000) for t in tt])
                wts = (0.3 * idf1 + 0.7 * idf2) * np.array(
                    [ner(t) * postag(t) for t in tt]
                )
                wts = [s for s in wts]
                tw.extend(zip(tt, wts))

        S = np.sum([s for _, s in tw])
        return [(t, s / S) for t, s in tw]
