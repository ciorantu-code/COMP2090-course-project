# system.py
from models import Course, Exam, Student

class UniversitySystem:
    def __init__(self):
        # System-wide storage for objects
        self.courses_catalog = {}
        self.exam_schedule = []
        self.campus_map = {
            "Main Library ": "Central Campus. 4 floors of quiet study spaces and archives.",
            "Science Building ": "North Campus. Houses the physics, chemistry, and biology labs.",
            "Arts & Humanities Hall ": "South Campus. Features historical archives and language departments.",
            "Student Union ": "West Campus. Cafeteria, club rooms, and IT support."
        }

    def add_course_to_catalog(self, course: Course):
        self.courses_catalog[course.course_code] = course

    def add_exam(self, exam: Exam):
        self.exam_schedule.append(exam)

    def get_student_exams(self, student: Student):
        # Filter the system's exam schedule to only show exams for courses the student is enrolled in
        enrolled_codes = [course.course_code for course in student.get_enrolled_courses()]
        return [exam for exam in self.exam_schedule if exam.course_code in enrolled_codes]
