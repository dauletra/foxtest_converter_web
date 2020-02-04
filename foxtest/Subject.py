import time
import os
import json


class Subject:
    _v: float = 0.3
    name: str = None
    # code: str = None
    mode: int = None
    created: float = None  # 1577959078.905777
    comment: str = None
    quizes: list = None

    @staticmethod
    def create(_v: float = 0.3, name: str = '', mode: int = 0, created: float = None, comment: str = '', quizes: list = None) -> 'Subject':
        subject = Subject()
        subject._v = _v
        subject.name = name
        subject.mode = mode
        subject.created = created or time.time()
        subject.comment = comment
        subject.quizes = quizes or []
        return subject

    def get_dict(self):
        return {
            '_v': self._v,
            'name': self.name,
            'mode': self.mode,
            'created': self.created,
            'comment': self.comment,
            'quizes': self.quizes
        }


class SubjectEncoder(json.JSONEncoder):
    def default(self, obj: Subject):
        if isinstance(obj, Subject):
            quiz = {
                '_v': obj._v,
                'name': obj.name,
                'mode': obj.mode,
                'created': obj.created,
                'comment': obj.comment,
                'quizes': obj.quizes
            }
            return quiz


def decode_subject(dic):
    if dic.get('_v') == 0.3 and dic.get('quizes'):
        return Subject.create(**dic)
    else:
        return dic