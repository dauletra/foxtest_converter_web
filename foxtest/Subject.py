import time
import os
import json


class Subject:
    _v: float = 0.2
    name: str = None
    code: str = None
    mode: int = None
    created: float = None  # 1577959078.905777
    comment: str = None
    quizes: list = None

    @staticmethod
    def create(name: str, code: str, mode: int, comment: str, quizes: list) -> 'Subject':
        subject = Subject()
        subject.name = name
        subject.code = code
        subject.mode = mode
        subject.created = time.time()
        subject.comment = comment
        subject.quizes = quizes
        return subject

    def get_dict(self):
        subject = dict()
        subject['_v'] = self._v
        subject['name'] = self.name
        subject['code'] = self.code
        subject['mode'] = self.mode
        subject['created'] = self.created
        subject['comment'] = self.comment
        subject['quizes'] = self.quizes
        return subject

    def save_json(self):
        jpath = os.path.join(os.path.abspath(''), self.code + '.json')
        with open(jpath, 'w') as jout:
            json.dump(self.get_dict(), jout)
