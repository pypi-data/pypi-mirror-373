import json
import logging
import re
from abc import ABC
from collections import defaultdict

import numpy as np

from duowen_agent.rag.nlp.utils import traditional_to_simplified, fullwidth_to_halfwidth
from .rag_tokenizer import RagTokenizer
from .synonym import SynonymDealer
from .term_weight import TermWeightDealer


class MatchTextExpr(ABC):
    def __init__(
        self,
        fields: list[str],
        matching_text: str,
        topn: int,
        extra_options: dict = dict(),
    ):
        self.fields = fields
        self.matching_text = matching_text
        self.topn = topn
        self.extra_options = extra_options


class FulltextQueryer:
    def __init__(
        self, tw: TermWeightDealer, syn: SynonymDealer, tokenizer: RagTokenizer
    ):
        self.tw = tw
        self.syn = syn
        self.tokenizer = tokenizer
        self.query_fields = [
            "title_tks^10",
            "title_sm_tks^5",
            "important_kwd^30",
            "important_tks^20",
            "question_tks^20",
            "content_ltks^2",
            "content_sm_ltks",
        ]

    @staticmethod
    def subSpecialChar(line):
        return re.sub(r"([:\{\}/\[\]\-\*\"\(\)\|\+~\^])", r"\\\1", line).strip()

    @staticmethod
    def isChinese(line):
        arr = re.split(r"[ \t]+", line)
        if len(arr) <= 3:
            return True
        e = 0
        for t in arr:
            if not re.match(r"[a-zA-Z]+$", t):
                e += 1
        return e * 1.0 / len(arr) >= 0.7

    @staticmethod
    def rmWWW(txt):
        patts = [
            (
                r"是*(什么样的|哪家|一下|那家|请问|啥样|咋样了|什么时候|何时|何地|何人|是否|是不是|多少|哪里|怎么|哪儿|怎么样|如何|哪些|是啥|啥是|啊|吗|呢|吧|咋|什么|有没有|呀|谁|哪位|哪个)是*",
                "",
            ),
            (r"(^| )(what|who|how|which|where|why)('re|'s)? ", " "),
            (
                r"(^| )('s|'re|is|are|were|was|do|does|did|don't|doesn't|didn't|has|have|be|there|you|me|your|my|mine|just|please|may|i|should|would|wouldn't|will|won't|done|go|for|with|so|the|a|an|by|i'm|it's|he's|she's|they|they're|you're|as|by|on|in|at|up|out|down|of|to|or|and|if) ",
                " ",
            ),
        ]
        otxt = txt
        for r, p in patts:
            txt = re.sub(r, p, txt, flags=re.IGNORECASE)
        if not txt:
            txt = otxt
        return txt

    def question(self, txt, tbl="qa", min_match: float = 0.6):
        txt = re.sub(
            r"[ :|\r\n\t,，。？?/`!！&^%%()\[\]{}<>]+",
            " ",
            traditional_to_simplified(fullwidth_to_halfwidth(txt.lower())),
        ).strip()
        txt = FulltextQueryer.rmWWW(txt)

        if not self.isChinese(txt):
            txt = FulltextQueryer.rmWWW(txt)
            tks = self.tokenizer.tokenize(txt).split()
            keywords = [t for t in tks if t]
            tks_w = self.tw.weights(tks, preprocess=False)
            tks_w = [(re.sub(r"[ \\\"'^]", "", tk), w) for tk, w in tks_w]
            tks_w = [(re.sub(r"^[a-z0-9]$", "", tk), w) for tk, w in tks_w if tk]
            tks_w = [(re.sub(r"^[\+-]", "", tk), w) for tk, w in tks_w if tk]
            tks_w = [(tk.strip(), w) for tk, w in tks_w if tk.strip()]
            syns = []
            for tk, w in tks_w[:256]:
                syn = self.syn.lookup(tk)
                syn = self.tokenizer.tokenize(" ".join(syn)).split()
                keywords.extend(syn)
                syn = ['"{}"^{:.4f}'.format(s, w / 4.0) for s in syn if s.strip()]
                syns.append(" ".join(syn))

            q = [
                "({}^{:.4f}".format(tk, w) + " {})".format(syn)
                for (tk, w), syn in zip(tks_w, syns)
                if tk and not re.match(r"[.^+\(\)-]", tk)
            ]
            for i in range(1, len(tks_w)):
                left, right = tks_w[i - 1][0].strip(), tks_w[i][0].strip()
                if not left or not right:
                    continue
                q.append(
                    '"%s %s"^%.4f'
                    % (
                        tks_w[i - 1][0],
                        tks_w[i][0],
                        max(tks_w[i - 1][1], tks_w[i][1]) * 2,
                    )
                )
            if not q:
                q.append(txt)
            query = " ".join(q)
            return MatchTextExpr(self.query_fields, query, 100), keywords

        def need_fine_grained_tokenize(tk):
            if len(tk) < 3:
                return False
            if re.match(r"[0-9a-z\.\+#_\*-]+$", tk):
                return False
            return True

        txt = FulltextQueryer.rmWWW(txt)
        qs, keywords = [], []
        for tt in self.tw.split(txt)[:256]:  # .split():
            if not tt:
                continue
            keywords.append(tt)
            twts = self.tw.weights([tt])
            syns = self.syn.lookup(tt)
            if syns and len(keywords) < 32:
                keywords.extend(syns)
            logging.debug(json.dumps(twts, ensure_ascii=False))
            tms = []
            for tk, w in sorted(twts, key=lambda x: x[1] * -1):
                sm = (
                    self.tokenizer.fine_grained_tokenize(tk).split()
                    if need_fine_grained_tokenize(tk)
                    else []
                )
                sm = [
                    re.sub(
                        r"[ ,\./;'\[\]\\`~!@#$%\^&\*\(\)=\+_<>\?:\"\{\}\|，。；‘’【】、！￥……（）——《》？：“”-]+",
                        "",
                        m,
                    )
                    for m in sm
                ]
                sm = [FulltextQueryer.subSpecialChar(m) for m in sm if len(m) > 1]
                sm = [m for m in sm if len(m) > 1]

                if len(keywords) < 32:
                    keywords.append(re.sub(r"[ \\\"']+", "", tk))
                    keywords.extend(sm)

                tk_syns = self.syn.lookup(tk)
                tk_syns = [FulltextQueryer.subSpecialChar(s) for s in tk_syns]
                if len(keywords) < 32:
                    keywords.extend([s for s in tk_syns if s])
                tk_syns = [
                    self.tokenizer.fine_grained_tokenize(s) for s in tk_syns if s
                ]
                tk_syns = [f'"{s}"' if s.find(" ") > 0 else s for s in tk_syns]

                if len(keywords) >= 32:
                    break

                tk = FulltextQueryer.subSpecialChar(tk)
                if tk.find(" ") > 0:
                    tk = '"%s"' % tk
                if tk_syns:
                    tk = f"({tk} OR (%s)^0.2)" % " ".join(tk_syns)
                if sm:
                    tk = f'{tk} OR "%s" OR ("%s"~2)^0.5' % (" ".join(sm), " ".join(sm))
                if tk.strip():
                    tms.append((tk, w))

            tms = " ".join([f"({t})^{w}" for t, w in tms])

            if len(twts) > 1:
                tms += ' ("%s"~2)^1.5' % self.tokenizer.tokenize(tt)

            syns = " OR ".join(
                [
                    '"%s"' % self.tokenizer.tokenize(FulltextQueryer.subSpecialChar(s))
                    for s in syns
                ]
            )
            if syns and tms:
                tms = f"({tms})^5 OR ({syns})^0.7"

            qs.append(tms)

        if qs:
            query = " OR ".join([f"({t})" for t in qs if t])
            return (
                MatchTextExpr(
                    self.query_fields, query, 100, {"minimum_should_match": min_match}
                ),
                keywords,
            )
        return None, keywords

    @staticmethod
    def vector_similarity(avec, bvecs):

        avec = np.asarray(avec)
        bvecs = np.asarray(bvecs)

        avec_norm = np.linalg.norm(avec)
        bvecs_norm = np.linalg.norm(bvecs, axis=1)

        sims = np.dot(bvecs, avec) / (
            bvecs_norm * avec_norm + 1e-9
        )  # 加入平滑项防止除零
        return sims

    def hybrid_similarity(self, avec, bvecs, atks, btkss, tkweight=0.3, vtweight=0.7):
        # 计算向量相似度 (cosine similarity)
        sims = self.vector_similarity(avec, bvecs)

        # 计算文本相似度
        tksim = self.token_similarity(atks, btkss)

        return np.array(sims) * vtweight + np.array(tksim) * tkweight, tksim, sims

    def token_similarity(self, atks, btkss):
        def toDict(tks):
            if isinstance(tks, str):
                tks = tks.split()
            d = defaultdict(int)
            wts = self.tw.weights(tks, preprocess=False)
            for i, (t, c) in enumerate(wts):
                d[t] += c
            return d

        atks = toDict(atks)
        btkss = [toDict(tks) for tks in btkss]
        return [self.similarity(atks, btks) for btks in btkss]

    # def similarity(self, qtwt, dtwt):
    #     if isinstance(dtwt, type("")):
    #         dtwt = {
    #             t: w for t, w in self.tw.weights(self.tw.split(dtwt), preprocess=False)
    #         }
    #     if isinstance(qtwt, type("")):
    #         qtwt = {
    #             t: w for t, w in self.tw.weights(self.tw.split(qtwt), preprocess=False)
    #         }
    #     s = 1e-9
    #     for k, v in qtwt.items():
    #         if k in dtwt:
    #             s += v * dtwt[k]
    #     q = 1e-9
    #     for k, v in qtwt.items():
    #         q += v * v
    #     return math.sqrt(3.0 * (s / q / math.log10(len(dtwt.keys()) + 512)))

    def similarity(self, qtwt, dtwt):
        if isinstance(dtwt, type("")):
            dtwt = {
                t: w for t, w in self.tw.weights(self.tw.split(dtwt), preprocess=False)
            }
        if isinstance(qtwt, type("")):
            qtwt = {
                t: w for t, w in self.tw.weights(self.tw.split(qtwt), preprocess=False)
            }
        s = 1e-9
        for k, v in qtwt.items():
            if k in dtwt:
                s += v  # * dtwt[k]
        q = 1e-9
        for k, v in qtwt.items():
            q += v  # * v
        return s / q

    def paragraph(self, content_tks: str, keywords=None, keywords_topn=30):
        if keywords is None:
            keywords = []
        if isinstance(content_tks, str):
            content_tks = [c.strip() for c in content_tks.strip() if c.strip()]
        tks_w = self.tw.weights(content_tks, preprocess=False)

        keywords = [f'"{k.strip()}"' for k in keywords]
        for tk, w in sorted(tks_w, key=lambda x: x[1] * -1)[:keywords_topn]:
            tk_syns = self.syn.lookup(tk)
            tk_syns = [FulltextQueryer.subSpecialChar(s) for s in tk_syns]
            tk_syns = [self.tokenizer.fine_grained_tokenize(s) for s in tk_syns if s]
            tk_syns = [f'"{s}"' if s.find(" ") > 0 else s for s in tk_syns]
            tk = FulltextQueryer.subSpecialChar(tk)
            if tk.find(" ") > 0:
                tk = '"%s"' % tk
            if tk_syns:
                tk = f"({tk} OR (%s)^0.2)" % " ".join(tk_syns)
            if tk:
                keywords.append(f"{tk}^{w}")

        return MatchTextExpr(
            self.query_fields,
            " ".join(keywords),
            100,
            {"minimum_should_match": min(3, len(keywords) / 10)},
        )
