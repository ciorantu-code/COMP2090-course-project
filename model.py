# models.py
from abc import ABC, abstractmethod

# ABSTRACTION: AcademicItem is an Abstract Base Class (ABC). 
# It defines a blueprint for other classes but cannot be instantiated directly.
class AcademicItem(ABC):
    def __init__(self, title_en: str, title_zh: str):
        self.title_en = title_en
        self.title_zh = title_zh

    # ABSTRACTION: Abstract method that must be implemented by subclasses
    @abstractmethod
    def display_info(self) -> str:
        pass

# INHERITANCE: Course inherits from AcademicItem
class Course(AcademicItem):
    def __init__(self, course_code: str, title_en: str, title_zh: str, credits: int):
        super().__init__(title_en, title_zh)
        self.course_code = course_code
        # ENCAPSULATION: __credits is private. It can't be accessed directly from outside the class.
        self.__credits = credits 

    # ENCAPSULATION: Getter for the private __credits attribute
    def get_credits(self) -> int:
        return self.__credits

    # POLYMORPHISM: Overriding the abstract method from the parent class
    def display_info(self) -> str:
        return f"[{self.course_code}] {self.title_en} / {self.title_zh} ({self.__credits} Credits)"

# INHERITANCE: Exam inherits from AcademicItem
class Exam(AcademicItem):
    def __init__(self, course_code: str, title_en: str, title_zh: str, date: str, location: str):
        super().__init__(title_en, title_zh)
        self.course_code = course_code
        self.date = date
        self.location = location

    # POLYMORPHISM: Overriding the abstract method with exam-specific formatting
    def display_info(self) -> str:
        return f"Exam: {self.course_code} - {self.title_en}\n  Date: {self.date}\n  Location: {self.location}"

# ABSTRACTION: Another abstract base class for people in the university
class Person(ABC):
    def __init__(self, name: str, student_id: str):
        self.name = name
        # ENCAPSULATION: _student_id is protected (conventionally, accessible in subclasses)
        self._student_id = student_id

    @abstractmethod
    def get_role(self) -> str:
        pass

# INHERITANCE: Student inherits from Person
class Student(Person):
    def __init__(self, name: str, student_id: str):
        super().__init__(name, student_id)
        # ENCAPSULATION: Private lists and dictionaries to protect student data
        self.__enrolled_courses = []
        self.__grades = {} # Format: {course_code: percentage}

    # POLYMORPHISM: Implementing the abstract method from Person
    def get_role(self) -> str:
        return "Student"

    # ENCAPSULATION: Safe methods (setters/getters) to modify private data
    def enroll(self, course: Course):
        if course not in self.__enrolled_courses:
            self.__enrolled_courses.append(course)

    def get_enrolled_courses(self):
        return self.__enrolled_courses

    def set_grade(self, course_code: str, grade: float):
        # Validation logic within the setter ensures data integrity
        if 0.0 <= grade <= 100.0:
            self.__grades[course_code] = grade
        else:
            raise ValueError("Grade must be between 0 and 100.")

    def get_grades(self):
        return self.__grades

    def calculate_average_grade(self) -> float:
        if not self.__grades:
            return 0.0
        return sum(self.__grades.values()) / len(self.__grades)
