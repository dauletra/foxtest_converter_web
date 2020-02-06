import time
import os
import json
from datetime import datetime

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

    @property
    def min(self):
        return min([q['number'] for q in self.quizes])

    @property
    def max(self):
        return max([q['number'] for q in self.quizes])

    @property
    def not_found_question_numbers(self):
        missed_numbers = []
        real_numbers = [q['number'] for q in self.quizes]
        for i in range(min(real_numbers), max(real_numbers)):
            if i not in real_numbers:
                missed_numbers.append(str(i))
        return ','.join(missed_numbers)

    @property
    def readable_date(self):
        d = datetime.fromtimestamp(self.created)
        return d.strftime('%d-%m-%Y')

    def get_readable_dict(self):
        return {
            '_v': self._v,
            'name': self.name,
            'mode': self.mode,
            'created': self.readable_date,
            'comment': self.comment,
            'quizes': self.quizes,
            'quizes_length': len(self.quizes),
            'questions_range': f'{self.min}-{self.max}',
            'not_found_question_numbers': self.not_found_question_numbers
        }

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