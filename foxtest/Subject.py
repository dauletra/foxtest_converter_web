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
    def create(_v: float = 0.2, name: str = '', code: str = '', mode: int = 0, created: float = None, comment: str = '', quizes: list = None) -> 'Subject':
        subject = Subject()
        subject._v = _v
        subject.name = name
        subject.code = code
        subject.mode = mode
        subject.created = created or time.time()
        subject.comment = comment
        subject.quizes = quizes or []
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


class SubjectEncoder(json.JSONEncoder):
    def default(self, obj: Subject):
        if isinstance(obj, Subject):
            quiz = {
                '_v': obj._v,
                'name': obj.name,
                'code': obj.code,
                'mode': obj.mode,
                'created': obj.created,
                'comment': obj.comment,
                'quizes': obj.quizes
            }
            return quiz


def decode_subject(dic):
    if dic.get('_v') == 0.2 and dic.get('quizes'):
        return Subject.create(**dic)
    else:
        return dic