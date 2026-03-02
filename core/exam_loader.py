import json
import os

def load_exam(exam_file):
    path = os.path.join("data", "exams", exam_file)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
