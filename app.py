from flask import Flask, render_template, request
from database import connect_db
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 


app = Flask(__name__)
class MissingFileOrFolderError(Exception):
    pass

# ---------------- FEE FUNCTION ----------------

def calculate_fee(tuition_fee,
                  hostel_fee=0,
                  transportation_fee=0):

    total_fee = tuition_fee + hostel_fee + transportation_fee
    return total_fee


# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('index.html')


# ---------------- STUDENT REGISTRATION ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        age = request.form['age']
        score = float(request.form['score'])

        if score >= 90:
            grade = "A"
            remark = "Excellent"

        elif score >= 75:
            grade = "B"
            remark = "Very Good"

        elif score >= 60:
            grade = "C"
            remark = "Good"

        elif score >= 40:
            grade = "D"
            remark = "Average"

        else:
            grade = "F"
            remark = "Needs Improvement"

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students(name, age, score, grade, remark)
        VALUES (?, ?, ?, ?, ?)
        """, (name, age, score, grade, remark))

        conn.commit()
        conn.close()

        return f"Student Registered Successfully! Grade = {grade}, Remark = {remark}"

    return render_template("register.html")


# ---------------- COURSE ENROLLMENT ----------------

@app.route('/courses', methods=['GET', 'POST'])
def courses():

    if request.method == 'POST':

        student_name = request.form['student_name']
        course_name = request.form['course_name']
        credits = int(request.form['credits'])

        if credits <= 0:
            return "Credits must be greater than 0"

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO courses(student_name, course_name, credits)
        VALUES (?, ?, ?)
        """, (student_name, course_name, credits))

        conn.commit()
        conn.close()

        return f"Course '{course_name}' added successfully!"

    return render_template("courses.html")


# ---------------- STUDENT RECORDS ----------------

@app.route('/records')
def records():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "records.html",
        students=students
    )


# ---------------- SEARCH & SORT ----------------

@app.route('/search', methods=['GET', 'POST'])
def search():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students")

    data = cursor.fetchall()

    conn.close()

    ids = [row[0] for row in data]

    # Bubble Sort

    n = len(ids)

    for i in range(n):
        for j in range(0, n-i-1):

            if ids[j] > ids[j+1]:

                temp = ids[j]
                ids[j] = ids[j+1]
                ids[j+1] = temp

    result = ""

    if request.method == 'POST':

        target = int(request.form['student_id'])

        if target in ids:
            result = f"Student ID {target} Found"

        else:
            result = f"Student ID {target} Not Found"

    return render_template(
        "search.html",
        ids=ids,
        result=result
    )


# ---------------- FEE CALCULATOR ----------------

@app.route('/fees', methods=['GET', 'POST'])
def fees():

    total = None

    if request.method == 'POST':

        tuition = int(request.form['tuition'])

        hostel = request.form['hostel']
        transport = request.form['transport']

        hostel = int(hostel) if hostel else 0
        transport = int(transport) if transport else 0

        total = calculate_fee(
            tuition,
            hostel,
            transport
        )

    return render_template(
        "fees.html",
        total=total
    )


# ---------------- FILE HANDLING ----------------

@app.route('/academic_records')
def academic_records():

    records = []

    with open("student_records.txt", "r") as file:

        lines = file.readlines()

        for line in lines[1:]:

            parts = line.strip().split(",")

            records.append(parts)

    total_students = len(records)

    total_marks = 0

    highest_marks = -1

    top_student = ""

    for row in records:

        marks = int(row[2])

        total_marks += marks

        if marks > highest_marks:

            highest_marks = marks

            top_student = row[1]

    average_marks = total_marks / total_students

    return render_template(
        "file_records.html",
        records=records,
        total_students=total_students,
        average_marks=average_marks,
        top_student=top_student
    )


# ---------------- DIRECTORY SCAN ----------------

@app.route('/scan', methods=['GET', 'POST'])
def scan():

    result = ""

    if request.method == 'POST':

        path = request.form['path']

        try:

            if not os.path.exists(path):
                raise FileNotFoundError("Invalid directory path")

            for root, dirs, files in os.walk(path):

                result += f"\n{root}\n"

                for file in files:
                    result += f"   {file}\n"

            if result == "":
                raise MissingFileOrFolderError(
                    "Empty Folder"
                )

        except FileNotFoundError as e:

            result = str(e)

        except MissingFileOrFolderError as e:

            result = str(e)

        except Exception as e:

            result = str(e)

    return render_template(
        "scan.html",
        result=result
    )

# ---------------- ANALYTICS ----------------

@app.route('/analytics')
def analytics():

    df = pd.read_csv("student_performance.csv")

    scores = df[["Math", "Science", "English"]].to_numpy()

    mean_scores = np.mean(scores, axis=0)

    top_math = df.loc[df["Math"].idxmax(), "Name"]
    top_science = df.loc[df["Science"].idxmax(), "Name"]
    top_english = df.loc[df["English"].idxmax(), "Name"]

    subjects = ["Math", "Science", "English"]

    plt.figure(figsize=(6,4))

    plt.bar(subjects, mean_scores)

    plt.title("Average Scores")

    plt.savefig("static/chart.png")

    plt.close()

    return render_template(
        "analytics.html",
        math_avg=round(mean_scores[0],2),
        science_avg=round(mean_scores[1],2),
        english_avg=round(mean_scores[2],2),
        top_math=top_math,
        top_science=top_science,
        top_english=top_english
    )


# ---------------- MAIN ----------------

if __name__ == '__main__':
    app.run(debug=True)