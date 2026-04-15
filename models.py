"""
models.py - Data Models for Student Lifeline

WHAT: Defines data model classes for every record type stored in the app:
      ImportantDate, RecurringDate, GradeRecord, LostFoundItem,
      CourseRating, and OfficeHours.
HOW:  Uses an abstract base class (AppRecord) with @abstractmethod to
      enforce a shared interface.  Every subclass must implement
      serialize(), deserialize(), and display_summary(), ensuring
      polymorphic behaviour across different record types.

OOP concepts demonstrated:
  Abstraction   → AppRecord (ABC) cannot be instantiated directly.
  Inheritance   → Every model extends AppRecord and reuses its attributes.
  Encapsulation → Private (__) and protected (_) attributes with @property.
  Polymorphism  → Each subclass provides its own serialize/display logic.
"""

import datetime
from abc import ABC, abstractmethod


# ============================================================
# Abstract Base Class
# ============================================================
class AppRecord(ABC):
    """
    WHAT: Abstract base class shared by all persistable records.
    HOW:  Inherits from ABC; marks three methods as @abstractmethod so
          Python raises TypeError if a subclass forgets to implement them.
    """

    def __init__(self, record_id: str, timestamp: str = None):
        """
        WHAT: Initialise the shared fields every record needs.
        HOW:  Stores record_id as a private attribute via double-underscore
              name mangling.  Generates a timestamp string with
              datetime.datetime.now().strftime() if none is supplied.
        """
        self.__record_id = record_id
        self._timestamp = timestamp or datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @property
    def record_id(self) -> str:
        """
        WHAT: Provide read-only access to the private record ID.
        HOW:  Uses @property so external code reads obj.record_id
              but cannot overwrite the double-underscore attribute.
        """
        return self.__record_id

    @property
    def timestamp(self) -> str:
        """
        WHAT: Provide read-only access to the creation timestamp.
        HOW:  Returns the protected _timestamp string directly.
        """
        return self._timestamp

    @abstractmethod
    def serialize(self) -> str:
        """
        WHAT: Convert this record into a string for file storage.
        HOW:  Each subclass joins its fields with '|' and returns
              a single-line string.
        """
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, line: str):
        """
        WHAT: Reconstruct a record object from a stored string.
        HOW:  Each subclass splits the line by '|', validates the
              field count, and calls cls() to build a new instance.
        """
        pass

    @abstractmethod
    def display_summary(self) -> str:
        """
        WHAT: Return a short human-readable summary of this record.
        HOW:  Each subclass formats its own fields into a string.
        """
        pass

    def __str__(self):
        """
        WHAT: Make print(record) produce readable output.
        HOW:  Delegates to display_summary() (polymorphic dispatch).
        """
        return self.display_summary()

    def __repr__(self):
        """
        WHAT: Provide a debug-friendly representation.
        HOW:  Uses self.__class__.__name__ to show the concrete class
              name together with the record_id.
        """
        return f"<{self.__class__.__name__} id={self.record_id}>"


# ============================================================
# ImportantDate
# ============================================================
class ImportantDate(AppRecord):
    """
    WHAT: Represents a user-created calendar event with a due date.
    HOW:  Inherits from AppRecord; adds date_str and event_name fields.
          Provides a days_left property that computes the difference
          between the event date and today via datetime arithmetic.
    """

    def __init__(self, record_id, date_str, event_name, timestamp=None):
        """
        WHAT: Initialise an ImportantDate with date string and event name.
        HOW:  Calls super().__init__() to set record_id and timestamp,
              then stores date_str and event_name as protected attributes.
        """
        super().__init__(record_id, timestamp)
        self._date_str = date_str
        self._event_name = event_name

    @property
    def date_str(self):
        """WHAT: Return the date string.  HOW: Returns self._date_str."""
        return self._date_str

    @property
    def event_name(self):
        """WHAT: Return the event label.  HOW: Returns self._event_name."""
        return self._event_name

    @property
    def date_obj(self):
        """
        WHAT: Convert the date string to a Python date object.
        HOW:  Uses datetime.datetime.strptime() with format "%Y-%m-%d"
              to parse the string, then calls .date() to strip the time.
        """
        return datetime.datetime.strptime(self._date_str, "%Y-%m-%d").date()

    @property
    def days_left(self):
        """
        WHAT: Calculate how many days remain until this event.
        HOW:  Subtracts datetime.date.today() from self.date_obj;
              returns the .days attribute of the resulting timedelta.
        """
        return (self.date_obj - datetime.date.today()).days

    def serialize(self) -> str:
        """
        WHAT: Convert this date to a storable string.
        HOW:  Joins date_str and event_name with '|'.
        """
        return f"{self._date_str}|{self._event_name}"

    @classmethod
    def deserialize(cls, line: str):
        """
        WHAT: Rebuild an ImportantDate from a stored line.
        HOW:  Splits the line by '|', checks for >= 2 parts, generates
              a unique ID using datetime.datetime.now().timestamp().
        """
        parts = line.strip().split("|")
        if len(parts) >= 2:
            rid = f"date_{int(datetime.datetime.now().timestamp() * 1000)}"
            return cls(rid, parts[0], parts[1])
        return None

    def display_summary(self) -> str:
        """
        WHAT: Produce a summary showing days remaining.
        HOW:  Checks self.days_left with if/elif/else to decide between
              "TODAY!", "X day(s) left", or "past".
        """
        d = self.days_left
        if d == 0:
            return f"{self._event_name} — TODAY!"
        elif d > 0:
            return f"{self._event_name} — {d} day(s) left"
        else:
            return f"{self._event_name} — past"


# ============================================================
# RecurringDate  (Inheritance from ImportantDate)
# ============================================================
class RecurringDate(ImportantDate):
    """
    WHAT: Represents an automatically recurring academic event.
    HOW:  Inherits all behaviour from ImportantDate.  Adds a class-level
          ACADEMIC_EVENTS list and a generate_all() factory method that
          creates instances with automatic year adjustment.
    """

    ACADEMIC_EVENTS = [
        (8, 18, "Tuition Fee Payment – Autumn Term"),
        (9, 7, "Add/Drop Period – Autumn Term"),
        (12, 31, "Tuition Fee Payment – Spring Term"),
        (1, 16, "Add/Drop Period – Spring Term"),
        (9, 1, "Fall Term Starts"),
        (1, 12, "Winter Term Starts"),
    ]

    def __init__(self, record_id, date_str, event_name):
        """
        WHAT: Initialise a RecurringDate.
        HOW:  Calls super().__init__() which chains up to AppRecord.
        """
        super().__init__(record_id, date_str, event_name)

    @classmethod
    def generate_all(cls):
        """
        WHAT: Create all recurring academic dates for the upcoming cycle.
        HOW:  Iterates ACADEMIC_EVENTS with enumerate().  For each event,
              builds a datetime.date for the current year; if already past,
              bumps to next year.  Returns a list of RecurringDate instances.
        """
        today = datetime.date.today()
        results = []
        for i, (month, day, event) in enumerate(cls.ACADEMIC_EVENTS):
            this_year = datetime.date(today.year, month, day)
            chosen = (this_year if this_year >= today
                      else datetime.date(today.year + 1, month, day))
            results.append(
                cls(f"recurring_{i}", chosen.strftime("%Y-%m-%d"), event)
            )
        return results

    def display_summary(self) -> str:
        """
        WHAT: Show a summary with a recurrence icon prefix.
        HOW:  Calls super().display_summary() for the base text,
              then prepends the "🔄 " icon string.
        """
        return f"🔄 {super().display_summary()}"


# ============================================================
# GradeRecord
# ============================================================
class GradeRecord(AppRecord):
    """
    WHAT: Stores a single CGPA value with input validation.
    HOW:  Uses a private attribute (__cgpa) with @property getter/setter
          that both call _validate() to enforce the 0.0–4.0 range.
    """

    def __init__(self, cgpa: float, record_id="cgpa_0", timestamp=None):
        """
        WHAT: Initialise a GradeRecord with a validated CGPA.
        HOW:  Calls super().__init__(), then passes cgpa through
              the static _validate() method before storing.
        """
        super().__init__(record_id, timestamp)
        self.__cgpa = self._validate(cgpa)

    @staticmethod
    def _validate(value):
        """
        WHAT: Ensure the CGPA is a float within 0.0–4.0.
        HOW:  Casts to float(), checks range with chained comparison,
              raises ValueError if out of range.
        """
        v = float(value)
        if not 0.0 <= v <= 4.0:
            raise ValueError("CGPA must be between 0.0 and 4.0")
        return v

    @property
    def cgpa(self):
        """WHAT: Read the CGPA.  HOW: Returns self.__cgpa."""
        return self.__cgpa

    @cgpa.setter
    def cgpa(self, value):
        """
        WHAT: Update the CGPA with validation.
        HOW:  Passes value through _validate() before storing.
        """
        self.__cgpa = self._validate(value)

    def get_status_comment(self) -> str:
        """
        WHAT: Return a motivational comment based on CGPA range.
        HOW:  Uses if/elif/else to map ranges to message strings.
        """
        if self.__cgpa >= 3.7:
            return "Excellent! Outstanding academic performance."
        elif self.__cgpa >= 3.3:
            return "Good job! Solid academic standing."
        elif self.__cgpa >= 2.7:
            return "Meeting expectations. Room for improvement."
        else:
            return "Consider seeking academic support resources."

    def serialize(self) -> str:
        """
        WHAT: Convert CGPA to a storable string.
        HOW:  Returns str(self.__cgpa), e.g. "3.45".
        """
        return str(self.__cgpa)

    @classmethod
    def deserialize(cls, line: str):
        """
        WHAT: Rebuild a GradeRecord from a stored line.
        HOW:  Strips whitespace, converts to float via float(),
              returns None on failure via try/except.
        """
        try:
            return cls(float(line.strip()))
        except (ValueError, IndexError):
            return None

    def display_summary(self) -> str:
        """
        WHAT: Show CGPA with status comment.
        HOW:  Formats with :.2f and appends get_status_comment().
        """
        return f"CGPA: {self.__cgpa:.2f} — {self.get_status_comment()}"


# ============================================================
# LostFoundItem
# ============================================================
class LostFoundItem(AppRecord):
    """
    WHAT: Represents a lost or found item report.
    HOW:  Inherits from AppRecord.  Validates item_type against
          VALID_TYPES.  Provides matches() for keyword search.
    """

    VALID_TYPES = ("lost", "found")

    def __init__(self, record_id, item_type, name, description,
                 location, contact, timestamp=None):
        """
        WHAT: Initialise a lost/found report with all required fields.
        HOW:  Calls super().__init__(), validates item_type against
              VALID_TYPES tuple, stores each field as protected attribute.
        """
        super().__init__(record_id, timestamp)
        if item_type not in self.VALID_TYPES:
            raise ValueError(f"item_type must be one of {self.VALID_TYPES}")
        self._item_type = item_type
        self._name = name
        self._description = description
        self._location = location
        self._contact = contact

    @property
    def item_type(self):
        """WHAT: Return item type.  HOW: Returns self._item_type."""
        return self._item_type

    @property
    def name(self):
        """WHAT: Return item name.  HOW: Returns self._name."""
        return self._name

    @property
    def description(self):
        """WHAT: Return description.  HOW: Returns self._description."""
        return self._description

    @property
    def location(self):
        """WHAT: Return location.  HOW: Returns self._location."""
        return self._location

    @property
    def contact(self):
        """WHAT: Return contact info.  HOW: Returns self._contact."""
        return self._contact

    def serialize(self) -> str:
        """
        WHAT: Convert this report to a pipe-separated string.
        HOW:  Joins all 7 fields (record_id through timestamp) with '|'.
        """
        return (f"{self.record_id}|{self._item_type}|{self._name}|"
                f"{self._description}|{self._location}|{self._contact}|"
                f"{self.timestamp}")

    @classmethod
    def deserialize(cls, line: str):
        """
        WHAT: Rebuild a LostFoundItem from a stored line.
        HOW:  Splits by '|', checks for 7 parts, uses *parts unpacking.
        """
        parts = line.strip().split("|")
        if len(parts) == 7:
            return cls(*parts)
        return None

    def matches(self, term: str) -> bool:
        """
        WHAT: Check if a search keyword matches this item.
        HOW:  Lowercases and strips both the term and every searchable
              field with .lower().strip(), then checks substring
              membership with 'in' across item_type, name, description,
              location, and contact so the search is fully
              case-insensitive.
        """
        t = term.lower().strip()
        return (t in self._item_type.lower().strip()
                or t in self._name.lower().strip()
                or t in self._description.lower().strip()
                or t in self._location.lower().strip()
                or t in self._contact.lower().strip())

    def display_summary(self) -> str:
        """
        WHAT: Produce a tagged summary string.
        HOW:  Selects "🔴 LOST" or "🟢 FOUND" based on self._item_type,
              then appends name and location via f-string.
        """
        tag = "🔴 LOST" if self._item_type == "lost" else "🟢 FOUND"
        return f"{tag}: {self._name} @ {self._location}"


# ============================================================
# CourseRating
# ============================================================
class CourseRating(AppRecord):
    """
    WHAT: Represents a course evaluation with 1–5 star rating.
    HOW:  Inherits from AppRecord.  Clamps stars to [1, 5] using
          max(1, min(5, ...)).  Provides stars_display property
          that builds a visual "★★★☆☆" string.
    """

    def __init__(self, record_id, course_field, course_code,
                 stars, reason, timestamp=None):
        """
        WHAT: Initialise a course rating record.
        HOW:  Calls super().__init__(), clamps stars with max/min.
        """
        super().__init__(record_id, timestamp)
        self._course_field = course_field
        self._course_code = course_code
        self._stars = max(1, min(5, int(stars)))
        self._reason = reason

    @property
    def course_field(self):
        """WHAT: Return course field.  HOW: Returns self._course_field."""
        return self._course_field

    @property
    def course_code(self):
        """WHAT: Return course code.  HOW: Returns self._course_code."""
        return self._course_code

    @property
    def stars(self):
        """WHAT: Return star count.  HOW: Returns self._stars."""
        return self._stars

    @property
    def reason(self):
        """WHAT: Return the review text.  HOW: Returns self._reason."""
        return self._reason

    @property
    def stars_display(self):
        """
        WHAT: Build a visual star string like "★★★☆☆".
        HOW:  Uses string multiplication — "★" * self._stars for filled
              and "☆" * (5 - self._stars) for empty — then concatenates.
        """
        return "★" * self._stars + "☆" * (5 - self._stars)

    def serialize(self) -> str:
        """
        WHAT: Convert this rating to a pipe-separated string.
        HOW:  Joins all 6 fields with '|'.
        """
        return (f"{self.record_id}|{self._course_field}|{self._course_code}|"
                f"{self._stars}|{self._reason}|{self.timestamp}")

    @classmethod
    def deserialize(cls, line: str):
        """
        WHAT: Rebuild a CourseRating from a stored line.
        HOW:  Splits by '|', checks for 6 parts, uses *parts unpacking.
        """
        parts = line.strip().split("|")
        if len(parts) == 6:
            return cls(*parts)
        return None

    def matches(self, term: str) -> bool:
        """
        WHAT: Check if a search keyword matches this course.
        HOW:  Lowercases and strips both strings, checks 'in' across
              course_field, course_code, and reason so the search is
              fully case-insensitive.
        """
        t = term.lower().strip()
        return (t in self._course_field.lower().strip()
                or t in self._course_code.lower().strip()
                or t in self._reason.lower().strip())

    def display_summary(self) -> str:
        """
        WHAT: Show course name with star display.
        HOW:  Concatenates course_field, course_code, and stars_display.
        """
        return f"{self._course_field} {self._course_code} — {self.stars_display}"


# ============================================================
# OfficeHours
# ============================================================
class OfficeHours(AppRecord):
    """
    WHAT: Stores a course's office-hour schedule entry.
    HOW:  Inherits from AppRecord.  Holds course info, instructor, day,
          time range, location, and notes.  Provides matches() for search.
    """

    VALID_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday",
                  "Friday", "Saturday", "Sunday")

    def __init__(self, record_id, course_field, course_code, instructor,
                 day, start_time, end_time, location, notes="",
                 timestamp=None):
        """
        WHAT: Initialise an office-hour entry with schedule details.
        HOW:  Calls super().__init__(), stores each field as protected.
        """
        super().__init__(record_id, timestamp)
        self._course_field = course_field
        self._course_code = course_code
        self._instructor = instructor
        self._day = day
        self._start_time = start_time
        self._end_time = end_time
        self._location = location
        self._notes = notes

    @property
    def course_field(self):
        """WHAT: Return course field.  HOW: Returns self._course_field."""
        return self._course_field

    @property
    def course_code(self):
        """WHAT: Return course code.  HOW: Returns self._course_code."""
        return self._course_code

    @property
    def instructor(self):
        """WHAT: Return instructor.  HOW: Returns self._instructor."""
        return self._instructor

    @property
    def day(self):
        """WHAT: Return day of week.  HOW: Returns self._day."""
        return self._day

    @property
    def start_time(self):
        """WHAT: Return start time.  HOW: Returns self._start_time."""
        return self._start_time

    @property
    def end_time(self):
        """WHAT: Return end time.  HOW: Returns self._end_time."""
        return self._end_time

    @property
    def location(self):
        """WHAT: Return location.  HOW: Returns self._location."""
        return self._location

    @property
    def notes(self):
        """WHAT: Return notes.  HOW: Returns self._notes."""
        return self._notes

    @property
    def time_range(self):
        """
        WHAT: Return a formatted time span string.
        HOW:  Concatenates start_time and end_time with " – ".
        """
        return f"{self._start_time} – {self._end_time}"

    def serialize(self) -> str:
        """
        WHAT: Convert this entry to a pipe-separated string.
        HOW:  Joins all 10 fields with '|'.
        """
        return (f"{self.record_id}|{self._course_field}|{self._course_code}|"
                f"{self._instructor}|{self._day}|{self._start_time}|"
                f"{self._end_time}|{self._location}|{self._notes}|"
                f"{self.timestamp}")

    @classmethod
    def deserialize(cls, line: str):
        """
        WHAT: Rebuild an OfficeHours from a stored line.
        HOW:  Splits by '|', checks for 10 parts, uses *parts unpacking.
        """
        parts = line.strip().split("|")
        if len(parts) == 10:
            return cls(*parts)
        return None

    def matches(self, term: str) -> bool:
        """
        WHAT: Check if a keyword matches any field of this entry.
        HOW:  Lowercases and strips all strings, checks 'in' across
              course_field, course_code, instructor, day, and location
              so the search is fully case-insensitive.
        """
        t = term.lower().strip()
        return (t in self._course_field.lower().strip()
                or t in self._course_code.lower().strip()
                or t in self._instructor.lower().strip()
                or t in self._day.lower().strip()
                or t in self._location.lower().strip())

    def display_summary(self) -> str:
        """
        WHAT: Show a concise summary of the office-hour entry.
        HOW:  Concatenates course, instructor, day, and time_range.
        """
        return (f"{self._course_field} {self._course_code} — "
                f"{self._instructor}  ({self._day} {self.time_range})")
