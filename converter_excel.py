import os
import json
import win32com.client
from pprint import pprint
from foxtest.Subject import Subject, SubjectEncoder

_v = 0.3
name = "ШСҮК"
mode = 1
comment = "Тесттердің дұрыс жауабын Excel-мен тексеріп шығыңыз, дұрыс көрсетпеген сұрақтарды айтыңыз"

file_name = 'shsuk.xlsx'
json_name = 'shsuk.json'

full_path = os.path.join(os.path.abspath('excel'), file_name)
quiz_json_path = os.path.join(os.path.abspath('excel'), json_name)

print('exists' if os.path.exists(full_path) else 'does not exist')

excel = win32com.client.Dispatch('Excel.Application')
excel.Visible = True
wb = excel.WorkBooks.Open(full_path)
sheet = wb.ActiveSheet

quizes = []
for row in range(2, 102):
    quiz = dict()
    quiz['id'] = row
    quiz['number'] = int(float(sheet.Cells(row, 1).text))
    quiz['question'] = sheet.Cells(row, 2).text.strip()
    quiz['answers'] = []
    answer = sheet.Cells(row, 3).text
    try:
        answer = int(float(answer))
    except ValueError:
        pass
    quiz['answers'].append([
        'A)',
        answer
    ])
    fake_answers = []
    for n in [(4,"B) "), (5, "C) "), (6, "D) "), (7, "E) ")]:
        fake_answer = sheet.Cells(row, n[0]).text
        try:
            fake_answer = int(float(fake_answer))
        except ValueError:
            pass
        fake_answers.append([n[1], fake_answer])
    quiz['fake_answers'] = fake_answers

    quizes.append(quiz)

# pprint(quizes)

subject = Subject.create(name=name, mode=mode, comment=comment, quizes=quizes)

with open(quiz_json_path, 'w', encoding='utf8') as file:
    json.dump(subject, file, cls=SubjectEncoder, ensure_ascii=False)

wb.Close()
excel.Quit()