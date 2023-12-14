from fastapi import FastAPI, HTTPException
from typing import List, Dict
import os
import json

app = FastAPI()

# Menambahkan variabel global untuk menyimpan ujian
app.state.exams = []

exams_directory = "exams"

if not os.path.exists(exams_directory):
    os.makedirs(exams_directory)

# Endpoint untuk mengatur ujian
@app.post("/post_exam")
async def post_exam(exam_data: dict):
    # Periksa keberadaan kunci "exam" dan "id" dalam JSON
    if "exam" not in exam_data or "id" not in exam_data["exam"]:
        raise HTTPException(status_code=400, detail="Data ujian tidak valid. Pastikan memiliki kunci 'exam' dan 'id'.")

    # Periksa apakah ID ujian telah digunakan oleh ujian lain
    exam_id = exam_data["exam"]["id"]
    used_ids = [existing_exam["id"] for existing_exam in app.state.exams]
    if exam_id in used_ids or any(file.startswith(f"exam_{exam_id}.json") for file in os.listdir(exams_directory)):
        raise HTTPException(status_code=400, detail=f"ID {exam_id} telah digunakan oleh ujian lain.")
    
    # Menggunakan app.state.exams untuk menyimpan ujian
    app.state.exams.append(exam_data["exam"])
    
    # Menyimpan ujian ke file JSON
    file_path = os.path.join(exams_directory, f"exam_{exam_id}.json")
    with open(file_path, "w") as file:
        json.dump(exam_data["exam"], file)
    
    return {"message": f"Ujian dengan ID {exam_id} berhasil ditambahkan"}

# Endpoint untuk mendapatkan ujian
@app.get("/get_exam/{exam_id}")
async def get_exam(exam_id: int):
    print(f"Requested exam_id: {exam_id}")

    file_path = os.path.join(exams_directory, f"exam_{exam_id}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            exam_data = json.load(file)
        return exam_data
    else:
        raise HTTPException(status_code=404, detail="Ujian tidak ditemukan")

# Endpoint untuk menghapus ujian
@app.delete("/delete_exam/{exam_id}")
async def delete_exam(exam_id: int):
    file_path = os.path.join(exams_directory, f"exam_{exam_id}.json")

    # Memeriksa apakah file ujian ada
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"Ujian dengan ID {exam_id} berhasil dihapus"}
    else:
        raise HTTPException(status_code=404, detail="Ujian tidak ditemukan")


# Endpoint untuk mengirimkan jawaban
@app.post("/post_answer/{exam_id}")
async def post_answer(exam_id: int, answers: dict):
    # Ubah "exam_15.json" ke "15.json"
    exam_filename = f"{exam_id}.json"
    
    # Periksa apakah file JSON ujian tersedia
    exam_path = os.path.join("exams", exam_filename)
    if not os.path.exists(exam_path):
        raise HTTPException(status_code=404, detail=f"Ujian dengan ID {exam_id} tidak ditemukan")

    with open(exam_path, "r", encoding="utf-8") as file:
        exam = json.load(file)
    
    # Periksa keberadaan kunci 'questions' dalam dictionary 'exam'
    if 'questions' not in exam['exam']:
        raise HTTPException(status_code=500, detail="Struktur data ujian tidak valid")

    user_answers = answers.get("answer", [])
    
    if len(user_answers) != len(exam['exam']['questions']):
        raise HTTPException(status_code=400, detail="Jumlah jawaban tidak sesuai dengan jumlah pertanyaan")
    
    score = calculate_score(exam['exam']['questions'], user_answers)
    return {"message": f"Nilai Anda: {score}"}

# Fungsi untuk menghitung nilai
def calculate_score(questions, user_answers):
    correct_count = sum(user_answer['user_answer'] == question['correct_option'] for user_answer, question_set in zip(user_answers, questions) for question in question_set['question'])
    total_questions = sum(len(question_set['question']) for question_set in questions)
    score = (correct_count / total_questions) * 100
    return score
