#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json
import logging
import os
import re
import time

from nltk.corpus import wordnet

_curr_dir = os.path.dirname(os.path.abspath(__file__))


class SynonymDealer:
    def __init__(self):
        self.lookup_num = 100000000
        self.load_tm = time.time() - 1000000
        self.dictionary = {}
        self.init_word()

    def init_word(self) -> None:
        path = f"{_curr_dir}/dictionary/synonym.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.dictionary = json.load(f)
            except Exception:
                logging.warning("Missing synonym.json")
                self.dictionary = {}
        else:
            logging.warning("Missing synonym.json")

    def del_word(self, word: str) -> None:
        if word in self.dictionary:
            _ = self.dictionary.pop(word)

    def set_word(self, word: str, alias: str) -> None:
        self.dictionary[word] = alias.split("|")

    def lookup(self, tk, topn=8):
        if re.match(r"[a-z]+$", tk):
            res = list(
                set(
                    [
                        re.sub("_", " ", syn.name().split(".")[0])
                        for syn in wordnet.synsets(tk)
                    ]
                )
                - set([tk])
            )
            return [t for t in res if t]

        self.lookup_num += 1
        res = self.dictionary.get(re.sub(r"[ \t]+", " ", tk.lower()), [])
        if isinstance(res, str):
            res = [res]
        return res[:topn]


if __name__ == "__main__":
    dl = Dealer()
    print(dl.dictionary)
