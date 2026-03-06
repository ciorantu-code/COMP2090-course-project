# main.py
import sys
from models import Course, Exam, Student
from system import UniversitySystem

def display_menu():
    print("\n" + "="*45)
    print("🎓 UNIVERSITY STUDENT ASSISTANT APP 🎓")
    print("="*45)
    print("1. Create a New Course (Catalog)")
    print("2. Enroll in a Course")
    print("3. View Enrolled Courses")
    print("4. Record a Grade")
    print("5. View Academic Grades & Average")
    print("6. View Campus Map Summaries")
    print("7. Exit")
    print("="*45)

def main():
    # Initialize the core system
    app_system = UniversitySystem()
    
    # Dynamically create the student at startup
    print("--- Welcome to the Student Portal ---")
    student_name = input("Please enter your name: ").strip()
    student_id = input("Please enter your Student ID: ").strip()
    active_student = Student(student_name, student_id)
    
    print(f"\nWelcome, {active_student.name} ({active_student.get_role()})!")

    while True:
        display_menu()
        choice = input("Please select an option (1-7): ").strip()

        if choice == '1':
            print("\n--- Create a New Course ---")
            code = input("Course Code (e.g., MATH301): ").strip()
            title_en = input("English Title: ").strip()
            title_zh = input("Chinese Title (optional): ").strip()
            try:
                credits = int(input("Credits (integer): ").strip())
                new_course = Course(code, title_en, title_zh, credits)
                app_system.add_course_to_catalog(new_course)
                print(f"✅ Success! {code} has been added to the university catalog.")
            except ValueError:
                print("❌ Invalid input for credits. Please enter a whole number.")

        elif choice == '2':
            print("\n--- Enroll in a Course ---")
            if not app_system.courses_catalog:
                print("The catalog is empty. Please create a course first (Option 1).")
                continue
            
            print("Available Courses:")
            for code, course in app_system.courses_catalog.items():
                print(f" - {code}: {course.title_en}")
            
            enroll_code = input("\nEnter the Course Code you wish to enroll in: ").strip()
            if enroll_code in app_system.courses_catalog:
                course_obj = app_system.courses_catalog[enroll_code]
                active_student.enroll(course_obj)
                print(f"✅ Successfully enrolled in {enroll_code}.")
            else:
                print("❌ Course not found in catalog.")

        elif choice == '3':
            print("\n--- Enrolled Courses ---")
            courses = active_student.get_enrolled_courses()
            if not courses:
                print("You are not enrolled in any courses.")
            else:
                for course in courses:
                    print(course.display_info())

        elif choice == '4':
            print("\n--- Record a Grade ---")
            courses = active_student.get_enrolled_courses()
            if not courses:
                print("You must enroll in a course before recording a grade.")
                continue
                
            course_code = input("Enter the Course Code to grade: ").strip()
            # Verify the student is actually enrolled in this course
            enrolled_codes = [c.course_code for c in courses]
            
            if course_code in enrolled_codes:
                try:
                    grade = float(input("Enter percentage grade (0-100): ").strip())
                    active_student.set_grade(course_code, grade)
                    print(f"✅ Grade of {grade}% recorded for {course_code}.")
                except ValueError as e:
                    # This catches both non-numbers and the 0-100 validation from models.py
                    print(f"❌ Error: Invalid grade input. {e}")
            else:
                print("❌ You are not enrolled in that course.")

        elif choice == '5':
            print("\n--- Academic Grades ---")
            grades = active_student.get_grades()
            if not grades:
                print("No grades recorded yet.")
            else:
                for code, grade in grades.items():
                    print(f"Course: {code} | Current Grade: {grade}%")
                
                avg = active_student.calculate_average_grade()
                print(f"\n>> Overall Average Percentage: {avg:.2f}%")

        elif choice == '6':
            print("\n--- Campus Map & Locations ---")
            for location, desc in app_system.campus_map.items():
                print(f"📍 {location}:")
                print(f"   {desc}")

        elif choice == '7':
            print("\nLogging out. Have a great day!")
            sys.exit(0)

        else:
            print("\n❌ Invalid selection. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()
