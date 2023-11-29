import os
import json

from fastapi import FastAPI, HTTPException, Depends

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
    if 1 <= exam_id <= len(app.state.exams):
        return app.state.exams[exam_id - 1]
    else:
        raise HTTPException(status_code=404, detail="Ujian tidak ditemukan")

# Endpoint untuk menghapus ujian
@app.delete("/delete_exam/{exam_id}")
async def delete_exam(exam_id: int):
    file_path = os.path.join(exams_directory, f"exam_{exam_id}.json")
    
    # Memeriksa apakah file ujian ada
    if os.path.exists(file_path):
        os.remove(file_path)
        # Menggunakan app.state.exams untuk menghapus ujian dari variabel global
        app.state.exams.pop(exam_id - 1)
        return {"message": f"Ujian dengan ID {exam_id} berhasil dihapus"}
    else:
        raise HTTPException(status_code=404, detail="Ujian tidak ditemukan")

# Endpoint untuk mengirimkan jawaban
@app.post("/post_answer/{exam_id}")
async def post_answer(exam_id: int, answers: dict):
    if 1 <= exam_id <= len(app.state.exams):
        exam = app.state.exams[exam_id - 1]
        
        # Periksa keberadaan kunci 'questions' dalam dictionary 'exam'
        if 'questions' not in exam:
            raise HTTPException(status_code=500, detail="Struktur data ujian tidak valid")

        user_answers = answers.get("user_answers", [])
        
        if len(user_answers) != len(exam["questions"]):
            raise HTTPException(status_code=400, detail="Jumlah jawaban tidak sesuai dengan jumlah pertanyaan")
        
        score = calculate_score(exam["questions"], user_answers)
        return {"message": f"Nilai Anda: {score}"}
    else:
        raise HTTPException(status_code=404, detail="Ujian tidak ditemukan")
    
# Fungsi untuk menghitung nilai
def calculate_score(questions, user_answers):
    correct_count = sum(user_answer == question["correct_option"] for user_answer, question in zip(user_answers, questions))
    total_questions = len(questions)
    score = (correct_count / total_questions) * 100
    return score
