# COMP2090-course-project
# University Student Assistant App

## Overview
The University Student Assistant App is a terminal-based student portal built in Python. It helps university students manage their academic life by providing a consolidated interface to view enrolled courses (with bilingual support), track exam schedules, calculate academic grades, and navigate the campus via map summaries. 

## Core Functions
* **Course Management:** View enrolled courses with descriptions in English and Chinese.
* **Exam Tracking:** Automatically maps a student's enrolled courses to the university's master exam schedule to provide personalized exam dates and locations.
* **Grade Calculation:** Tracks percentage grades for individual classes and calculates the overall academic average.
* **Campus Navigation:** Provides a text-based summary of essential campus buildings and their functions.

## Technical Summary & Modular Architecture
The application is strictly separated into three modules to enforce the Separation of Concerns principle:
1. `models.py`: Contains the data structures and domain entities.
2. `system.py`: Acts as the system manager/business logic layer.
3. `main.py`: Houses the interactive Command Line Interface (CLI) and entry point.

## Object-Oriented Programming (OOP) Implementation
This project rigorously applies the four pillars of OOP:

### 1. Abstraction
* **How it is used:** The `abc` module is used to create Abstract Base Classes (`AcademicItem` and `Person`). 
* **Where it is used (`models.py`):** The `AcademicItem` class defines a contract with the `@abstractmethod` `display_info()`. It hides the implementation details and forces any academic item (like courses or exams) to implement their own display logic.

### 2. Inheritance
* **How it is used:** Child classes inherit attributes and behaviors from parent classes to promote code reuse and establish hierarchical relationships.
* **Where it is used (`models.py`):** `Course` and `Exam` both inherit from `AcademicItem`, gaining the bilingual title attributes. Similarly, `Student` inherits from `Person`, gaining the `name` and `_student_id` attributes.

### 3. Encapsulation
* **How it is used:** Sensitive data is hidden within classes using private (double underscore `__`) and protected (single underscore `_`) prefixes. Access to this data is mediated through public getter and setter methods.
* **Where it is used (`models.py`):** In the `Student` class, `__enrolled_courses` and `__grades` are strictly private. The `set_grade()` method encapsulates the validation logic to ensure a grade cannot be set outside the 0-100% range, protecting the integrity of the data. 

### 4. Polymorphism
* **How it is used:** Methods with the same name behave differently depending on the object they are called on (Method Overriding).
* **Where it is used (`models.py` & `main.py`):** Both `Course` and `Exam` implement the `display_info()` method inherited from `AcademicItem`. However, a `Course` formats this as a single string with credits, while an `Exam` formats it as a multi-line string with dates and locations. In `main.py`, the menu calls `.display_info()` without needing to know if the object is a Course or an Exam.
