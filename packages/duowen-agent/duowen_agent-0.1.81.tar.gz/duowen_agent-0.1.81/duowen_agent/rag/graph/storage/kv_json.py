import logging
import os
import threading

import jsonlines

from ..base import BaseKVStorage
from ..utils import create_file_dir


class JsonKVStorage(BaseKVStorage):

    def __init__(self, namespace: str, working_dir: str = "./duowen_graph_data"):
        super().__init__(namespace=namespace)
        self._file_name = os.path.join(working_dir, f"kv_store_{self.namespace}.jsonl")
        create_file_dir(self._file_name)
        self._data = {}
        if os.path.exists(self._file_name):
            with jsonlines.open(self._file_name, "r") as reader:
                for line in reader:
                    self._data[line["key"]] = line["value"]
        logging.info(f"Load KV {self.namespace} with {len(self._data)} data")
        self._buffer = []
        self._lock = threading.Lock()

    def all_keys(self) -> list[str]:
        return list(self._data.keys())

    def index_done_callback(self):
        with self._lock:
            with jsonlines.open(self._file_name, "a") as writer:
                for i in self._buffer:
                    if i["key"] in self._data:
                        writer.write(i)
                self._buffer = []

    def get_by_id(self, id):
        return self._data.get(id, None)

    def get_by_ids(self, ids, fields=None):
        if fields is None:
            return [self._data.get(id, None) for id in ids]
        return [
            (
                {k: v for k, v in self._data[id].items() if k in fields}
                if self._data.get(id, None)
                else None
            )
            for id in ids
        ]

    def filter_keys(self, data: list[str]) -> set[str]:
        return set([s for s in data if s not in self._data])

    def upsert(self, data: dict[str, dict]):
        with self._lock:
            self._data.update(data)
            for k, v in data.items():
                self._buffer.append({"value": v, "key": k})

    def drop(self):
        with self._lock:
            self._data = {}

    def delete_by_ids(self, ids: list[str]):
        with self._lock:
            for id in ids:
                self._data.pop(id, None)

    def query_done_callback(self):
        pass

    def index_start_callback(self):
        pass
