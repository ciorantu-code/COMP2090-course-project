"""
data_manager.py - Persistence Layer for Student Lifeline

WHAT: Handles all file read/write operations for the application,
      providing CRUD (Create, Read, Update, Delete) methods for every
      data type: dates, grades, lost items, ratings, and office hours.
HOW:  Centralises file I/O in a single DataManager class.  Each data
      type has its own text file inside a "data/" directory.  Records
      are stored as pipe-separated strings produced by each model's
      serialize() method and rebuilt by deserialize().

OOP concepts demonstrated:
  Encapsulation → All file paths are private (double-underscore) so
                  external code cannot change them.  Access is only
                  through public CRUD methods.
"""

import os
import datetime
from models import (
    ImportantDate, GradeRecord, LostFoundItem,
    CourseRating, OfficeHours
)


class DataManager:
    """
    WHAT: Centralised file-based persistence manager.
    HOW:  Stores one text file per data type.  Provides load/save/remove
          methods that internally call _read_lines() and _write_lines()
          to handle raw file I/O.
    """

    def __init__(self, data_dir: str = "data"):
        """
        WHAT: Initialise the DataManager and create the data directory.
        HOW:  Stores the directory path as a private attribute, calls
              os.makedirs(exist_ok=True) to create it if missing, and
              builds a private file path for each data type using
              os.path.join().
        """
        self.__data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # Private file paths — one per data type
        self.__dates_file = os.path.join(data_dir, "important_dates.txt")
        self.__settings_file = os.path.join(data_dir, "reminder_settings.txt")
        self.__grade_file = os.path.join(data_dir, "grade_records.txt")
        self.__lost_found_file = os.path.join(data_dir, "lost_found_items.txt")
        self.__rating_file = os.path.join(data_dir, "course_ratings.txt")
        self.__office_file = os.path.join(data_dir, "office_hours.txt")

    # ----------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------
    def _read_lines(self, path: str) -> list[str]:
        """
        WHAT: Read all non-empty lines from a text file.
        HOW:  Checks existence and size with os.path.exists() and
              os.path.getsize().  Opens with encoding="utf-8" and
              filters out blank lines using a list comprehension
              with str.strip() as the truthy test.  Returns [] if
              the file does not exist.
        """
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "r", encoding="utf-8") as f:
                return [l for l in f.readlines() if l.strip()]
        return []

    def _write_lines(self, path: str, lines: list[str]):
        """
        WHAT: Overwrite a text file with the given lines.
        HOW:  Opens the file in write mode ("w"), which replaces all
              existing content, then calls f.writelines(lines).
        """
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # ================================================================
    # Important Dates
    # ================================================================
    def load_dates(self) -> list[ImportantDate]:
        """
        WHAT: Load all important dates, auto-removing expired ones.
        HOW:  Reads each line with _read_lines(), deserializes with
              ImportantDate.deserialize(), keeps only dates where
              days_left >= 0, then rewrites the file with
              _write_lines() to clean out expired entries.
        """
        results = []
        valid_lines = []
        for line in self._read_lines(self.__dates_file):
            obj = ImportantDate.deserialize(line)
            if obj and obj.days_left >= 0:
                results.append(obj)
                valid_lines.append(obj.serialize() + "\n")
        self._write_lines(self.__dates_file, valid_lines)
        return results

    def save_date(self, date: ImportantDate):
        """
        WHAT: Append a new important date to the file.
        HOW:  Opens in append mode ("a") and writes the serialized
              string followed by a newline.
        """
        with open(self.__dates_file, "a", encoding="utf-8") as f:
            f.write(date.serialize() + "\n")

    def remove_date(self, index: int):
        """
        WHAT: Remove an important date by its line index.
        HOW:  Reads all lines with _read_lines(), removes the line
              at the given index with list.pop(), rewrites with
              _write_lines().
        """
        lines = self._read_lines(self.__dates_file)
        if 0 <= index < len(lines):
            lines.pop(index)
            self._write_lines(self.__dates_file, lines)

    # ---- Reminder days ----
    def get_reminder_days(self) -> int:
        """
        WHAT: Read the user's reminder-window setting in days.
        HOW:  Reads the first line of the settings file, converts to
              int with int(), clamps to at least 1 with max().
              Returns 7 as default if the file is empty or malformed.
        """
        try:
            lines = self._read_lines(self.__settings_file)
            if lines:
                return max(1, int(lines[0].strip()))
        except (ValueError, IndexError):
            pass
        return 7

    def save_reminder_days(self, days: int):
        """
        WHAT: Save the reminder-window setting.
        HOW:  Opens in write mode ("w") and writes the clamped value
              as a string using max(1, days).
        """
        with open(self.__settings_file, "w", encoding="utf-8") as f:
            f.write(str(max(1, days)))

    # ================================================================
    # Grade Monitor
    # ================================================================
    def load_grade(self) -> GradeRecord | None:
        """
        WHAT: Load the student's saved CGPA.
        HOW:  Reads the first line with _read_lines() and passes it
              to GradeRecord.deserialize().  Returns None if empty.
        """
        lines = self._read_lines(self.__grade_file)
        if lines:
            return GradeRecord.deserialize(lines[0])
        return None

    def save_grade(self, record: GradeRecord):
        """
        WHAT: Save (overwrite) the student's CGPA.
        HOW:  Opens in write mode ("w") to replace any previous value,
              writes the serialized string.
        """
        with open(self.__grade_file, "w", encoding="utf-8") as f:
            f.write(record.serialize())

    # ================================================================
    # Lost & Found
    # ================================================================
    def load_lost_found(self) -> list[LostFoundItem]:
        """
        WHAT: Load all lost-and-found reports.
        HOW:  Reads each line, deserializes with LostFoundItem.deserialize(),
              appends valid objects to a list.  Skips malformed lines.
        """
        items = []
        for line in self._read_lines(self.__lost_found_file):
            obj = LostFoundItem.deserialize(line)
            if obj:
                items.append(obj)
        return items

    def save_lost_found_item(self, item: LostFoundItem):
        """
        WHAT: Append a new lost/found report.
        HOW:  Opens in append mode ("a"), writes serialized string.
        """
        with open(self.__lost_found_file, "a", encoding="utf-8") as f:
            f.write(item.serialize() + "\n")

    def remove_lost_found(self, record_id: str):
        """
        WHAT: Remove a lost/found report by its record_id.
        HOW:  Loads all items, filters out the matching record_id
              with a list comprehension, rewrites the entire file.
        """
        items = [i for i in self.load_lost_found()
                 if i.record_id != record_id]
        with open(self.__lost_found_file, "w", encoding="utf-8") as f:
            for item in items:
                f.write(item.serialize() + "\n")

    # ================================================================
    # Course Ratings
    # ================================================================
    def load_ratings(self) -> list[CourseRating]:
        """
        WHAT: Load all course ratings.
        HOW:  Reads each line, deserializes with CourseRating.deserialize(),
              appends valid objects.
        """
        ratings = []
        for line in self._read_lines(self.__rating_file):
            obj = CourseRating.deserialize(line)
            if obj:
                ratings.append(obj)
        return ratings

    def save_rating(self, rating: CourseRating):
        """
        WHAT: Append a new course rating.
        HOW:  Opens in append mode ("a"), writes serialized string.
        """
        with open(self.__rating_file, "a", encoding="utf-8") as f:
            f.write(rating.serialize() + "\n")

    def remove_rating(self, record_id: str):
        """
        WHAT: Remove a course rating by its record_id.
        HOW:  Loads all ratings, filters with list comprehension,
              rewrites the file.
        """
        ratings = [r for r in self.load_ratings()
                   if r.record_id != record_id]
        with open(self.__rating_file, "w", encoding="utf-8") as f:
            for r in ratings:
                f.write(r.serialize() + "\n")

    # ================================================================
    # Office Hours
    # ================================================================
    def load_office_hours(self) -> list:
        """
        WHAT: Load all office-hour entries.
        HOW:  Reads each line, deserializes with OfficeHours.deserialize(),
              appends valid objects.
        """
        entries = []
        for line in self._read_lines(self.__office_file):
            obj = OfficeHours.deserialize(line)
            if obj:
                entries.append(obj)
        return entries

    def save_office_hour(self, entry: "OfficeHours"):
        """
        WHAT: Append a new office-hour entry.
        HOW:  Opens in append mode ("a"), writes serialized string.
        """
        with open(self.__office_file, "a", encoding="utf-8") as f:
            f.write(entry.serialize() + "\n")

    def remove_office_hour(self, record_id: str):
        """
        WHAT: Remove an office-hour entry by its record_id.
        HOW:  Loads all entries, filters with list comprehension,
              rewrites the file.
        """
        entries = [e for e in self.load_office_hours()
                   if e.record_id != record_id]
        with open(self.__office_file, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(e.serialize() + "\n")
