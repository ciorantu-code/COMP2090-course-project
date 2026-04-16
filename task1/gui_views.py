"""
gui_views.py - GUI Views for Student Lifeline

WHAT: Defines the visual pages (views) displayed in the main content area
      when the user clicks a sidebar button: Dashboard, Important Dates,
      Grade Monitor, Lost & Found, Course Ratings, and Office Hours.
HOW:  All views inherit from BaseView (which inherits ctk.CTkFrame).
      Each view overrides build_content() to set up widgets and refresh()
      to reload data.  This is polymorphism — the main app can call
      refresh() on any view without knowing its concrete class.

OOP concepts demonstrated:
  Inheritance   → Every view extends BaseView extends ctk.CTkFrame.
  Polymorphism  → Each view has its own build_content() and refresh().
  Encapsulation → Internal widgets stored as protected attributes.
"""

import customtkinter as ctk
from tkinter import messagebox
import datetime
from models import (
    ImportantDate, RecurringDate, GradeRecord,
    LostFoundItem, CourseRating, OfficeHours
)
from data_manager import DataManager

# ============================================================
# Colour palette constants
# ============================================================
CARDINAL_RED = "#8C1515"
CARDINAL_DARK = "#6B0F0F"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F4F4F4"
MID_GRAY = "#D1D1D1"
DARK_GRAY = "#3D3D3D"
TEXT_COLOR = "#2E2E2E"
ACCENT_GREEN = "#009B76"
ACCENT_AMBER = "#E98300"
CARD_BG = "#FFFFFF"
SIDEBAR_BG = "#1A1A1A"
SIDEBAR_TEXT = "#C8C8C8"
SIDEBAR_HOVER = "#8C1515"


# ============================================================
# BaseView (Abstract parent for all views)
# ============================================================
class BaseView(ctk.CTkFrame):
    """
    WHAT: Abstract base class for all feature views.
    HOW:  Inherits ctk.CTkFrame.  Provides shared helpers _make_header(),
          _make_card(), _clear_cards().  Calls build_content() in __init__
          so subclasses populate themselves upon creation.
    """

    def __init__(self, parent, data_manager: DataManager, **kwargs):
        """
        WHAT: Initialise the base view frame and trigger content building.
        HOW:  Calls super().__init__() to set up the CTkFrame, stores the
              DataManager reference, initialises a _cards list for tracking,
              then calls build_content().
        """
        super().__init__(parent, fg_color=LIGHT_GRAY, corner_radius=0,
                         **kwargs)
        self._dm = data_manager
        self._cards: list[ctk.CTkFrame] = []
        self.build_content()

    def build_content(self):
        """
        WHAT: Populate the view with widgets (override in subclass).
        HOW:  Raises NotImplementedError to enforce overriding.
        """
        raise NotImplementedError

    def refresh(self):
        """
        WHAT: Reload data and update displayed widgets (override in subclass).
        HOW:  Raises NotImplementedError to enforce overriding.
        """
        raise NotImplementedError

    def _make_header(self, parent, title: str, subtitle: str = ""):
        """
        WHAT: Create a styled red header banner at the top of a view.
        HOW:  Creates a CTkFrame with CARDINAL_RED background and fixed
              height of 90 px via pack_propagate(False).  Adds CTkLabel
              widgets for title and optional subtitle.
        """
        hdr = ctk.CTkFrame(parent, fg_color=CARDINAL_RED,
                            corner_radius=12, height=90)
        hdr.pack(fill="x", padx=20, pady=(20, 10))
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=title, font=("Helvetica", 22, "bold"),
                      text_color=WHITE).pack(anchor="w", padx=24,
                                              pady=(16, 0))
        if subtitle:
            ctk.CTkLabel(hdr, text=subtitle, font=("Helvetica", 13),
                          text_color="#E8CCCC").pack(anchor="w", padx=24)
        return hdr

    def _make_card(self, parent, **kwargs) -> ctk.CTkFrame:
        """
        WHAT: Create a white rounded card frame for displaying a record.
        HOW:  Creates a CTkFrame with white background, 12 px corner
              radius, and a 1 px gray border.  Appends to self._cards
              for bulk cleanup via _clear_cards().
        """
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12,
                             border_width=1, border_color=MID_GRAY,
                             **kwargs)
        self._cards.append(card)
        return card

    def _clear_cards(self):
        """
        WHAT: Destroy all cards created by _make_card().
        HOW:  Iterates self._cards, calls .destroy() on each widget,
              then calls list.clear() to empty the tracking list.
        """
        for c in self._cards:
            c.destroy()
        self._cards.clear()


# ============================================================
# DashboardView
# ============================================================
class DashboardView(BaseView):
    """
    WHAT: Home page showing summary statistics and upcoming events.
    HOW:  Loads data from DataManager in refresh(), builds four stat
          cards using a grid layout, and lists the nearest 5 events
          sorted by days_left.
    """

    def build_content(self):
        """
        WHAT: Set up the scrollable container and header.
        HOW:  Creates a CTkScrollableFrame, calls _make_header(), adds
              a content sub-frame, then calls refresh().
        """
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=LIGHT_GRAY,
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)
        self._make_header(self._scroll, "Dashboard",
                           "Welcome to Student Lifeline")
        self._content = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        self._content.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        """
        WHAT: Reload all data and rebuild the dashboard widgets.
        HOW:  Destroys existing children with winfo_children() loop,
              loads stats from DataManager, builds stat cards in a
              4-column grid, then builds event cards sorted by days_left
              using sorted() with a lambda key.
        """
        # Clear existing widgets
        for w in self._content.winfo_children():
            w.destroy()
        self._clear_cards()

        # Load summary data
        grade = self._dm.load_grade()
        cgpa_text = f"{grade.cgpa:.2f}" if grade else "—"
        dates = self._dm.load_dates()
        recurring = RecurringDate.generate_all()
        reminder_days = self._dm.get_reminder_days()
        # Count events within the reminder window using sum() with generator
        upcoming_count = sum(
            1 for d in dates + recurring
            if 0 <= d.days_left <= reminder_days
        )
        lf_count = len(self._dm.load_lost_found())
        rating_count = len(self._dm.load_ratings())

        # Build stat cards row using grid layout
        stats_row = ctk.CTkFrame(self._content, fg_color=LIGHT_GRAY)
        stats_row.pack(fill="x", pady=(0, 12))
        stats_row.columnconfigure((0, 1, 2, 3), weight=1)

        stat_data = [
            ("CGPA", cgpa_text, CARDINAL_RED),
            ("Upcoming Events", str(upcoming_count), ACCENT_AMBER),
            ("Lost & Found", str(lf_count), "#4A90D9"),
            ("Ratings", str(rating_count), ACCENT_GREEN),
        ]
        for col, (label, value, color) in enumerate(stat_data):
            card = self._make_card(stats_row)
            card.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")
            ctk.CTkLabel(card, text=value,
                          font=("Helvetica", 32, "bold"),
                          text_color=color).pack(padx=16, pady=(16, 0))
            ctk.CTkLabel(card, text=label, font=("Helvetica", 12),
                          text_color=DARK_GRAY).pack(padx=16, pady=(0, 16))

        # Build upcoming events list
        ctk.CTkLabel(self._content, text="Upcoming Events",
                      font=("Helvetica", 16, "bold"),
                      text_color=TEXT_COLOR, anchor="w").pack(fill="x",
                                                              pady=(8, 4))
        # Sort all dates by days_left using sorted() with lambda
        all_dates = sorted(dates + recurring, key=lambda d: d.days_left)
        shown = 0
        for d in all_dates:
            if d.days_left < 0:
                continue
            if shown >= 5:
                break
            card = self._make_card(self._content)
            card.pack(fill="x", pady=3)
            row = ctk.CTkFrame(card, fg_color=CARD_BG)
            row.pack(fill="x", padx=16, pady=10)
            # Days-left badge: RED if within reminder window, GRAY if outside
            days_txt = "TODAY" if d.days_left == 0 else f"{d.days_left}d"
            badge_color = (CARDINAL_RED if d.days_left <= reminder_days
                           else MID_GRAY)
            ctk.CTkLabel(row, text=days_txt, width=52,
                          font=("Helvetica", 13, "bold"),
                          text_color=WHITE, fg_color=badge_color,
                          corner_radius=6).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(row, text=d.event_name,
                          font=("Helvetica", 13),
                          text_color=TEXT_COLOR).pack(side="left")
            ctk.CTkLabel(row, text=d.date_str,
                          font=("Helvetica", 11),
                          text_color=DARK_GRAY).pack(side="right")
            shown += 1

        if shown == 0:
            ctk.CTkLabel(self._content, text="No upcoming events.",
                          font=("Helvetica", 13),
                          text_color=DARK_GRAY).pack(pady=8)


# ============================================================
# ImportantDatesView
# ============================================================
class ImportantDatesView(BaseView):
    """
    WHAT: View for managing important dates with add and delete.
    HOW:  Provides toolbar buttons for Add Date and Reminder Days.
          Lists all dates (custom + recurring) sorted by days_left.  Delete buttons use lambda with default argument
          to capture the correct index.
    """

    def build_content(self):
        """
        WHAT: Set up header, toolbar buttons, and list frame.
        HOW:  Creates CTkScrollableFrame, _make_header(), toolbar with
              three CTkButton widgets, and a list frame for cards.
        """
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=LIGHT_GRAY,
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)
        self._make_header(self._scroll, "Important Dates",
                           "Academic calendar & custom events")

        # Toolbar
        tb = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        tb.pack(fill="x", padx=20, pady=(4, 0))
        ctk.CTkButton(tb, text="＋  Add Date", fg_color=CARDINAL_RED,
                       hover_color=CARDINAL_DARK, corner_radius=8,
                       command=self._add_dialog).pack(side="left")
        ctk.CTkButton(tb, text="⚙  Reminder Days", fg_color=DARK_GRAY,
                       hover_color="#555", corner_radius=8,
                       command=self._reminder_dialog).pack(side="left",
                                                            padx=8)

        self._list_frame = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        """
        WHAT: Reload and display all dates sorted by days remaining.
        HOW:  Clears existing cards, loads reminder_days setting via
              _dm.get_reminder_days(), loads custom dates and recurring
              dates, merges and sorts with sorted(key=lambda).  Badge
              colour is CARDINAL_RED if days_left <= reminder_days
              (within alert window), otherwise gray.  Delete buttons
              are shown only for user-created dates (checked via
              isinstance() to exclude RecurringDate).
        """
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._clear_cards()

        # Load the user's reminder-days setting for badge colouring
        reminder_days = self._dm.get_reminder_days()

        custom = self._dm.load_dates()
        recurring = RecurringDate.generate_all()
        all_dates = sorted(custom + recurring, key=lambda d: d.days_left)

        for i, d in enumerate(all_dates):
            if d.days_left < 0:
                continue
            card = self._make_card(self._list_frame)
            card.pack(fill="x", pady=3)
            row = ctk.CTkFrame(card, fg_color=CARD_BG)
            row.pack(fill="x", padx=14, pady=10)
            days_txt = "TODAY" if d.days_left == 0 else f"{d.days_left}d"
            # RED if within the reminder window, GRAY if outside
            badge_color = (CARDINAL_RED if d.days_left <= reminder_days
                           else "#9E9E9E")
            ctk.CTkLabel(row, text=days_txt, width=52,
                          font=("Helvetica", 13, "bold"),
                          text_color=WHITE, fg_color=badge_color,
                          corner_radius=6).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(row, text=d.event_name,
                          font=("Helvetica", 13),
                          text_color=TEXT_COLOR).pack(side="left")
            ctk.CTkLabel(row, text=d.date_str,
                          font=("Helvetica", 11),
                          text_color=DARK_GRAY).pack(side="right",
                                                      padx=(0, 8))
            # Show delete button only for user-created dates
            if isinstance(d, ImportantDate) and not isinstance(d,
                                                               RecurringDate):
                idx = custom.index(d) if d in custom else -1
                if idx >= 0:
                    ctk.CTkButton(
                        row, text="✕", width=28, height=28,
                        fg_color="#D9534F", hover_color="#C9302C",
                        corner_radius=6,
                        command=lambda ix=idx: self._remove(ix)
                    ).pack(side="right", padx=4)

    def _remove(self, idx):
        """
        WHAT: Delete a user-created date and refresh the list.
        HOW:  Calls self._dm.remove_date(idx), then self.refresh().
        """
        self._dm.remove_date(idx)
        self.refresh()

    def _add_dialog(self):
        """
        WHAT: Open a pop-up dialog for adding a new important date.
        HOW:  Creates a CTkToplevel with grab_set() for modal behaviour.
              Provides CTkEntry fields for date (YYYY-MM-DD) and event
              name.  The inner save() function validates input using
              datetime.datetime.strptime(), creates an ImportantDate
              object, saves via _dm.save_date(), and refreshes.
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title("Add Important Date")
        dlg.geometry("360x280")
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="Date (YYYY-MM-DD):",
                      font=("Helvetica", 13)).pack(padx=20,
                                                    pady=(20, 4),
                                                    anchor="w")
        date_entry = ctk.CTkEntry(dlg, placeholder_text="2026-06-15")
        date_entry.pack(padx=20, fill="x")

        ctk.CTkLabel(dlg, text="Event name:",
                      font=("Helvetica", 13)).pack(padx=20,
                                                    pady=(12, 4),
                                                    anchor="w")
        event_entry = ctk.CTkEntry(dlg, placeholder_text="Final Exam")
        event_entry.pack(padx=20, fill="x")

        def save():
            """
            WHAT: Validate inputs and save the new date.
            HOW:  Gets text via .get().strip(), validates format with
                  strptime(), checks future date, creates ImportantDate,
                  calls _dm.save_date().
            """
            ds = date_entry.get().strip()
            ev = event_entry.get().strip()
            if not ds or not ev:
                messagebox.showwarning("Missing",
                                       "Please fill in both fields.")
                return
            try:
                dt = datetime.datetime.strptime(ds, "%Y-%m-%d").date()
                if dt <= datetime.date.today():
                    messagebox.showwarning("Invalid",
                                           "Date must be in the future.")
                    return
            except ValueError:
                messagebox.showwarning("Invalid",
                                       "Use YYYY-MM-DD format.")
                return
            rid = f"date_{int(datetime.datetime.now().timestamp())}"
            self._dm.save_date(ImportantDate(rid, ds, ev))
            dlg.destroy()
            self.refresh()

        ctk.CTkButton(dlg, text="Save", fg_color=CARDINAL_RED,
                       hover_color=CARDINAL_DARK, corner_radius=8,
                       command=save).pack(pady=20)

    def _reminder_dialog(self):
        """
        WHAT: Open a pop-up to change the reminder window (in days).
        HOW:  Creates a CTkToplevel, shows current setting, provides
              a CTkEntry for new value, validates with int() and range
              check, saves via _dm.save_reminder_days().
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title("Reminder Settings")
        dlg.geometry("300x180")
        dlg.grab_set()
        current = self._dm.get_reminder_days()
        ctk.CTkLabel(dlg, text=f"Current: {current} days",
                      font=("Helvetica", 13)).pack(pady=(20, 8))
        entry = ctk.CTkEntry(dlg, placeholder_text="7")
        entry.pack(padx=20, fill="x")

        def save():
            """
            WHAT: Validate and save the new reminder-days value.
            HOW:  Converts with int(), checks 1–365 range, calls
                  _dm.save_reminder_days().
            """
            try:
                v = int(entry.get())
                if 1 <= v <= 365:
                    self._dm.save_reminder_days(v)
                    dlg.destroy()
                    self.refresh()
                else:
                    messagebox.showwarning("Invalid", "Enter 1-365.")
            except ValueError:
                messagebox.showwarning("Invalid", "Enter a number.")

        ctk.CTkButton(dlg, text="Save", fg_color=CARDINAL_RED,
                       hover_color=CARDINAL_DARK, corner_radius=8,
                       command=save).pack(pady=16)


# ============================================================
# GradeMonitorView
# ============================================================
class GradeMonitorView(BaseView):
    """
    WHAT: Display and update the student's CGPA.
    HOW:  Shows a large colour-coded CGPA number (green/amber/red based
          on range), a status comment from GradeRecord.get_status_comment(),
          and a form to enter a new value.
    """

    def build_content(self):
        """
        WHAT: Set up header and content frame.
        HOW:  Creates CTkScrollableFrame, _make_header(), content frame,
              calls refresh().
        """
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=LIGHT_GRAY,
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)
        self._make_header(self._scroll, "Grade Monitor",
                           "Track your academic performance")
        self._content = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        self._content.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        """
        WHAT: Reload grade and rebuild the display.
        HOW:  Loads grade via _dm.load_grade(), displays CGPA with
              colour coding using ternary expressions, shows status
              comment, and provides an update form with validation
              via GradeRecord constructor (raises ValueError if invalid).
        """
        for w in self._content.winfo_children():
            w.destroy()
        self._clear_cards()

        grade = self._dm.load_grade()
        card = self._make_card(self._content)
        card.pack(fill="x", pady=8)

        if grade:
            cgpa_val = grade.cgpa
            color = (ACCENT_GREEN if cgpa_val >= 3.3
                     else ACCENT_AMBER if cgpa_val >= 2.7
                     else CARDINAL_RED)
            ctk.CTkLabel(card, text=f"{cgpa_val:.2f}",
                          font=("Helvetica", 56, "bold"),
                          text_color=color).pack(pady=(24, 0))
            ctk.CTkLabel(card, text="Current CGPA",
                          font=("Helvetica", 13),
                          text_color=DARK_GRAY).pack()
            ctk.CTkLabel(card, text=grade.get_status_comment(),
                          font=("Helvetica", 14),
                          text_color=TEXT_COLOR,
                          wraplength=400).pack(pady=(8, 24))
        else:
            ctk.CTkLabel(card, text="—",
                          font=("Helvetica", 56, "bold"),
                          text_color=MID_GRAY).pack(pady=(24, 0))
            ctk.CTkLabel(card, text="No CGPA recorded yet",
                          font=("Helvetica", 13),
                          text_color=DARK_GRAY).pack(pady=(0, 24))

        # Update form
        form_card = self._make_card(self._content)
        form_card.pack(fill="x", pady=8)
        ctk.CTkLabel(form_card, text="Update CGPA",
                      font=("Helvetica", 15, "bold"),
                      text_color=TEXT_COLOR).pack(padx=20, pady=(16, 4),
                                                   anchor="w")
        entry = ctk.CTkEntry(form_card, placeholder_text="e.g. 3.45")
        entry.pack(padx=20, fill="x")

        def save():
            """
            WHAT: Validate and save a new CGPA value.
            HOW:  Converts with float(), passes to GradeRecord() which
                  validates range, saves via _dm.save_grade().
            """
            try:
                v = float(entry.get())
                rec = GradeRecord(v)
                self._dm.save_grade(rec)
                self.refresh()
            except ValueError:
                messagebox.showwarning("Invalid",
                                       "Enter a number 0.0 – 4.0.")

        ctk.CTkButton(form_card, text="Save", fg_color=CARDINAL_RED,
                       hover_color=CARDINAL_DARK, corner_radius=8,
                       command=save).pack(padx=20, pady=16, anchor="w")


# ============================================================
# LostFoundView
# ============================================================
class LostFoundView(BaseView):
    """
    WHAT: Report and search for lost/found items.
    HOW:  Provides a Report Item dialog, a search bar with StringVar,
          and a list of cards showing item details with delete buttons.
    """

    def build_content(self):
        """
        WHAT: Set up header, toolbar (report + search), and list frame.
        HOW:  Creates toolbar with CTkButton and CTkEntry (bound to
              <Return> for search), and a list frame for cards.
        """
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=LIGHT_GRAY,
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)
        self._make_header(self._scroll, "Lost & Found",
                           "Report and search for items")

        tb = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        tb.pack(fill="x", padx=20, pady=(4, 0))
        ctk.CTkButton(tb, text="＋  Report Item",
                       fg_color=CARDINAL_RED, hover_color=CARDINAL_DARK,
                       corner_radius=8,
                       command=self._add_dialog).pack(side="left")
        self._search_var = ctk.StringVar()
        se = ctk.CTkEntry(tb, textvariable=self._search_var,
                           placeholder_text="Search items…", width=200)
        se.pack(side="left", padx=8)
        se.bind("<Return>", lambda e: self.refresh())
        ctk.CTkButton(tb, text="Search", width=70,
                       fg_color=DARK_GRAY, hover_color="#555",
                       corner_radius=8,
                       command=self.refresh).pack(side="left")

        self._list_frame = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        """
        WHAT: Reload items, apply search filter, and rebuild cards.
        HOW:  Loads via _dm.load_lost_found(), filters with matches()
              if a search term exists, sorts by timestamp descending
              using sorted(key=lambda, reverse=True).
        """
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._clear_cards()
        items = self._dm.load_lost_found()
        term = (self._search_var.get().strip()
                if hasattr(self, '_search_var') else "")
        if term:
            items = [i for i in items if i.matches(term)]
        items.sort(key=lambda x: x.timestamp, reverse=True)

        if not items:
            ctk.CTkLabel(self._list_frame, text="No items found.",
                          font=("Helvetica", 13),
                          text_color=DARK_GRAY).pack(pady=20)
            return

        for item in items:
            card = self._make_card(self._list_frame)
            card.pack(fill="x", pady=3)
            row = ctk.CTkFrame(card, fg_color=CARD_BG)
            row.pack(fill="x", padx=14, pady=10)
            # Colour-coded tag using ternary expression
            tag_color = (CARDINAL_RED if item.item_type == "lost"
                         else ACCENT_GREEN)
            tag_text = ("LOST" if item.item_type == "lost"
                        else "FOUND")
            ctk.CTkLabel(row, text=tag_text, width=56,
                          font=("Helvetica", 11, "bold"),
                          text_color=WHITE, fg_color=tag_color,
                          corner_radius=6).pack(side="left",
                                                 padx=(0, 10))
            info = ctk.CTkFrame(row, fg_color=CARD_BG)
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=item.name,
                          font=("Helvetica", 13, "bold"),
                          text_color=TEXT_COLOR,
                          anchor="w").pack(fill="x")
            ctk.CTkLabel(info,
                          text=f"{item.description}  •  {item.location}",
                          font=("Helvetica", 11),
                          text_color=DARK_GRAY,
                          anchor="w").pack(fill="x")
            ctk.CTkButton(
                row, text="✕", width=28, height=28,
                fg_color="#D9534F", hover_color="#C9302C",
                corner_radius=6,
                command=lambda rid=item.record_id: self._remove(rid)
            ).pack(side="right", padx=4)

    def _remove(self, record_id):
        """
        WHAT: Delete an item and refresh.
        HOW:  Calls _dm.remove_lost_found(record_id), then refresh().
        """
        self._dm.remove_lost_found(record_id)
        self.refresh()

    def _add_dialog(self):
        """
        WHAT: Open a dialog for reporting a lost/found item.
        HOW:  Creates CTkToplevel with fields for type, name, description,
              location, and contact.  Validates type against ("lost","found"),
              creates LostFoundItem, saves via _dm.save_lost_found_item().
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title("Report Item")
        dlg.geometry("400x420")
        dlg.grab_set()

        fields = {}
        for label, key, ph in [
            ("Type (lost / found)", "type", "lost"),
            ("Item Name", "name", "Blue backpack"),
            ("Description", "desc", "Nike brand, has keychain"),
            ("Location", "loc", "Library 2F"),
            ("Contact", "contact", "student@hkmu.edu.hk"),
        ]:
            ctk.CTkLabel(dlg, text=label,
                          font=("Helvetica", 13)).pack(padx=20,
                                                        pady=(10, 2),
                                                        anchor="w")
            e = ctk.CTkEntry(dlg, placeholder_text=ph)
            e.pack(padx=20, fill="x")
            fields[key] = e

        def save():
            """
            WHAT: Validate and save the new item report.
            HOW:  Reads fields via .get().strip(), validates type,
                  generates unique ID with timestamp, creates
                  LostFoundItem, calls _dm.save_lost_found_item().
            """
            t = fields["type"].get().strip().lower()
            if t not in ("lost", "found"):
                messagebox.showwarning("Invalid",
                                       "Type must be 'lost' or 'found'.")
                return
            n = fields["name"].get().strip()
            if not n:
                messagebox.showwarning("Missing",
                                       "Item name is required.")
                return
            rid = f"{t}_{int(datetime.datetime.now().timestamp())}"
            item = LostFoundItem(
                rid, t, n, fields["desc"].get().strip(),
                fields["loc"].get().strip(),
                fields["contact"].get().strip()
            )
            self._dm.save_lost_found_item(item)
            dlg.destroy()
            self.refresh()

        ctk.CTkButton(dlg, text="Save", fg_color=CARDINAL_RED,
                       hover_color=CARDINAL_DARK, corner_radius=8,
                       command=save).pack(pady=16)


# ============================================================
# CourseRatingView
# ============================================================
class CourseRatingView(BaseView):
    """
    WHAT: Rate and review courses with 1–5 stars.
    HOW:  Provides add dialog with CTkSlider for star selection,
          search bar for filtering, and card list with star display.
    """

    def build_content(self):
        """
        WHAT: Set up header, toolbar (add + search), and list frame.
        HOW:  Creates toolbar with CTkButton and CTkEntry, list frame.
        """
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=LIGHT_GRAY,
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)
        self._make_header(self._scroll, "Course Ratings",
                           "Rate and review your courses")

        tb = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        tb.pack(fill="x", padx=20, pady=(4, 0))
        ctk.CTkButton(tb, text="＋  Add Rating",
                       fg_color=CARDINAL_RED, hover_color=CARDINAL_DARK,
                       corner_radius=8,
                       command=self._add_dialog).pack(side="left")
        self._search_var = ctk.StringVar()
        se = ctk.CTkEntry(tb, textvariable=self._search_var,
                           placeholder_text="Search courses…", width=200)
        se.pack(side="left", padx=8)
        se.bind("<Return>", lambda e: self.refresh())
        ctk.CTkButton(tb, text="Search", width=70,
                       fg_color=DARK_GRAY, hover_color="#555",
                       corner_radius=8,
                       command=self.refresh).pack(side="left")

        self._list_frame = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        """
        WHAT: Reload ratings, apply search, and rebuild cards.
        HOW:  Loads via _dm.load_ratings(), filters with matches(),
              sorts newest first by timestamp, displays star string
              from stars_display property.
        """
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._clear_cards()
        ratings = self._dm.load_ratings()
        term = (self._search_var.get().strip()
                if hasattr(self, '_search_var') else "")
        if term:
            ratings = [r for r in ratings if r.matches(term)]
        ratings.sort(key=lambda x: x.timestamp, reverse=True)

        if not ratings:
            ctk.CTkLabel(self._list_frame, text="No ratings yet.",
                          font=("Helvetica", 13),
                          text_color=DARK_GRAY).pack(pady=20)
            return

        for r in ratings:
            card = self._make_card(self._list_frame)
            card.pack(fill="x", pady=3)
            row = ctk.CTkFrame(card, fg_color=CARD_BG)
            row.pack(fill="x", padx=14, pady=10)
            ctk.CTkLabel(row, text=r.stars_display,
                          font=("Helvetica", 16),
                          text_color=ACCENT_AMBER).pack(side="left",
                                                         padx=(0, 10))
            info = ctk.CTkFrame(row, fg_color=CARD_BG)
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info,
                          text=f"{r.course_field} {r.course_code}",
                          font=("Helvetica", 13, "bold"),
                          text_color=TEXT_COLOR,
                          anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=r.reason,
                          font=("Helvetica", 11),
                          text_color=DARK_GRAY, anchor="w",
                          wraplength=350).pack(fill="x")
            ctk.CTkButton(
                row, text="✕", width=28, height=28,
                fg_color="#D9534F", hover_color="#C9302C",
                corner_radius=6,
                command=lambda rid=r.record_id: self._remove(rid)
            ).pack(side="right", padx=4)

    def _remove(self, record_id):
        """
        WHAT: Delete a rating and refresh.
        HOW:  Calls _dm.remove_rating(record_id), then refresh().
        """
        self._dm.remove_rating(record_id)
        self.refresh()

    def _add_dialog(self):
        """
        WHAT: Open a dialog for adding a new course rating.
        HOW:  Creates CTkToplevel with CTkEntry for course field/code,
              CTkSlider for stars (1–5 with 4 steps), CTkEntry for
              reason.  Uses setattr() to dynamically store entry
              references.  Creates CourseRating on save.
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title("Add Rating")
        dlg.geometry("380x380")
        dlg.grab_set()

        for label, key, ph in [("Course Field", "field", "COMP"),
                                ("Course Code", "code", "2090SEF")]:
            ctk.CTkLabel(dlg, text=label,
                          font=("Helvetica", 13)).pack(padx=20,
                                                        pady=(12, 2),
                                                        anchor="w")
            e = ctk.CTkEntry(dlg, placeholder_text=ph)
            e.pack(padx=20, fill="x")
            # Store reference dynamically using setattr()
            setattr(self, f"_dlg_{key}", e)

        ctk.CTkLabel(dlg, text="Stars (1-5)",
                      font=("Helvetica", 13)).pack(padx=20, pady=(12, 2),
                                                    anchor="w")
        self._dlg_stars = ctk.CTkSlider(dlg, from_=1, to=5,
                                         number_of_steps=4, width=200)
        self._dlg_stars.set(3)
        self._dlg_stars.pack(padx=20, anchor="w")

        ctk.CTkLabel(dlg, text="Reason",
                      font=("Helvetica", 13)).pack(padx=20, pady=(12, 2),
                                                    anchor="w")
        self._dlg_reason = ctk.CTkEntry(dlg,
                                         placeholder_text="Great lecturer!")
        self._dlg_reason.pack(padx=20, fill="x")

        def save():
            """
            WHAT: Validate and save the new rating.
            HOW:  Reads fields, generates ID with timestamp,
                  creates CourseRating, calls _dm.save_rating().
            """
            f = self._dlg_field.get().strip()
            c = self._dlg_code.get().strip()
            if not f or not c:
                messagebox.showwarning("Missing",
                                       "Fill in course field and code.")
                return
            rid = f"rating_{int(datetime.datetime.now().timestamp())}"
            rating = CourseRating(rid, f, c, int(self._dlg_stars.get()),
                                  self._dlg_reason.get().strip())
            self._dm.save_rating(rating)
            dlg.destroy()
            self.refresh()

        ctk.CTkButton(dlg, text="Save", fg_color=CARDINAL_RED,
                       hover_color=CARDINAL_DARK, corner_radius=8,
                       command=save).pack(pady=16)


# ============================================================
# OfficeHoursView
# ============================================================
class OfficeHoursView(BaseView):
    """
    WHAT: Add and search course office hours.
    HOW:  Groups entries by day of the week, sorts by start time
          within each day using a custom sort key.
    """

    DAY_OPTIONS = ["Monday", "Tuesday", "Wednesday", "Thursday",
                   "Friday", "Saturday", "Sunday"]

    def build_content(self):
        """
        WHAT: Set up header, toolbar (add + search), and list frame.
        HOW:  Creates toolbar with CTkButton and CTkEntry, list frame.
        """
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=LIGHT_GRAY,
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)
        self._make_header(self._scroll, "Office Hours",
                           "Find when your instructors are available")

        tb = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        tb.pack(fill="x", padx=20, pady=(4, 0))
        ctk.CTkButton(tb, text="＋  Add Office Hour",
                       fg_color=CARDINAL_RED, hover_color=CARDINAL_DARK,
                       corner_radius=8,
                       command=self._add_dialog).pack(side="left")
        self._search_var = ctk.StringVar()
        se = ctk.CTkEntry(tb, textvariable=self._search_var,
                           placeholder_text="Search course, instructor…",
                           width=240)
        se.pack(side="left", padx=8)
        se.bind("<Return>", lambda e: self.refresh())
        ctk.CTkButton(tb, text="Search", width=70,
                       fg_color=DARK_GRAY, hover_color="#555",
                       corner_radius=8,
                       command=self.refresh).pack(side="left")

        self._list_frame = ctk.CTkFrame(self._scroll, fg_color=LIGHT_GRAY)
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh()

    def refresh(self):
        """
        WHAT: Reload entries, apply search, group by day, rebuild cards.
        HOW:  Loads via _dm.load_office_hours(), filters with matches().
              Sorts by (day_order, start_time) using a dictionary
              comprehension {day: index} and sorted() with a lambda
              that returns a tuple key.  Prints a bold day header
              whenever current_day changes.
        """
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._clear_cards()
        entries = self._dm.load_office_hours()
        term = (self._search_var.get().strip()
                if hasattr(self, '_search_var') else "")
        if term:
            entries = [e for e in entries if e.matches(term)]
        # Sort by day order then start time using dict comprehension
        day_order = {d: i for i, d in enumerate(self.DAY_OPTIONS)}
        entries.sort(
            key=lambda e: (day_order.get(e.day, 99), e.start_time)
        )

        if not entries:
            ctk.CTkLabel(self._list_frame,
                          text="No office hours recorded.",
                          font=("Helvetica", 13),
                          text_color=DARK_GRAY).pack(pady=20)
            return

        # Group by day with day-change header
        current_day = None
        for entry in entries:
            if entry.day != current_day:
                current_day = entry.day
                ctk.CTkLabel(self._list_frame, text=current_day,
                              font=("Helvetica", 14, "bold"),
                              text_color=CARDINAL_RED,
                              anchor="w").pack(fill="x", pady=(12, 2))

            card = self._make_card(self._list_frame)
            card.pack(fill="x", pady=2)
            row = ctk.CTkFrame(card, fg_color=CARD_BG)
            row.pack(fill="x", padx=14, pady=10)
            # Time badge
            ctk.CTkLabel(row, text=entry.time_range, width=120,
                          font=("Helvetica", 12, "bold"),
                          text_color=WHITE, fg_color="#4A90D9",
                          corner_radius=6).pack(side="left",
                                                 padx=(0, 10))
            info = ctk.CTkFrame(row, fg_color=CARD_BG)
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info,
                          text=f"{entry.course_field} {entry.course_code}",
                          font=("Helvetica", 13, "bold"),
                          text_color=TEXT_COLOR,
                          anchor="w").pack(fill="x")
            # Build subtitle from instructor, location, notes
            sub_parts = [entry.instructor, entry.location]
            if entry.notes:
                sub_parts.append(entry.notes)
            ctk.CTkLabel(info, text="  •  ".join(sub_parts),
                          font=("Helvetica", 11),
                          text_color=DARK_GRAY, anchor="w",
                          wraplength=380).pack(fill="x")
            ctk.CTkButton(
                row, text="✕", width=28, height=28,
                fg_color="#D9534F", hover_color="#C9302C",
                corner_radius=6,
                command=lambda rid=entry.record_id: self._remove(rid)
            ).pack(side="right", padx=4)

    def _remove(self, record_id):
        """
        WHAT: Delete an entry and refresh.
        HOW:  Calls _dm.remove_office_hour(record_id), then refresh().
        """
        self._dm.remove_office_hour(record_id)
        self.refresh()

    def _add_dialog(self):
        """
        WHAT: Open a dialog for adding an office-hour entry.
        HOW:  Creates CTkToplevel with CTkEntry fields for course,
              instructor, location, notes; CTkOptionMenu for day
              selection; CTkEntry for start/end times.  Creates
              OfficeHours object on save.
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title("Add Office Hour")
        dlg.geometry("420x520")
        dlg.grab_set()

        fields = {}
        for label, key, ph in [
            ("Course Field", "field", "COMP"),
            ("Course Code", "code", "2090SEF"),
            ("Instructor", "instructor", "Dr. Chan"),
            ("Location", "location", "Room A401"),
            ("Notes (optional)", "notes", "Bring student ID"),
        ]:
            ctk.CTkLabel(dlg, text=label,
                          font=("Helvetica", 13)).pack(padx=20,
                                                        pady=(8, 2),
                                                        anchor="w")
            e = ctk.CTkEntry(dlg, placeholder_text=ph)
            e.pack(padx=20, fill="x")
            fields[key] = e

        # Day dropdown using CTkOptionMenu with StringVar
        ctk.CTkLabel(dlg, text="Day",
                      font=("Helvetica", 13)).pack(padx=20, pady=(8, 2),
                                                    anchor="w")
        day_var = ctk.StringVar(value="Monday")
        ctk.CTkOptionMenu(dlg, variable=day_var, values=self.DAY_OPTIONS,
                           fg_color=CARDINAL_RED,
                           button_color=CARDINAL_DARK).pack(padx=20,
                                                             anchor="w")

        # Start/end time entries side by side
        time_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        time_frame.pack(fill="x", padx=20, pady=(8, 0))
        ctk.CTkLabel(time_frame, text="Start",
                      font=("Helvetica", 13)).pack(side="left")
        start_e = ctk.CTkEntry(time_frame, placeholder_text="10:00",
                                width=80)
        start_e.pack(side="left", padx=(8, 16))
        ctk.CTkLabel(time_frame, text="End",
                      font=("Helvetica", 13)).pack(side="left")
        end_e = ctk.CTkEntry(time_frame, placeholder_text="12:00",
                              width=80)
        end_e.pack(side="left", padx=8)

        def save():
            """
            WHAT: Validate and save the new office-hour entry.
            HOW:  Reads all fields, checks required fields with all(),
                  generates ID with timestamp, creates OfficeHours,
                  calls _dm.save_office_hour().
            """
            f = fields["field"].get().strip()
            c = fields["code"].get().strip()
            ins = fields["instructor"].get().strip()
            loc = fields["location"].get().strip()
            s = start_e.get().strip()
            en = end_e.get().strip()
            if not all([f, c, ins, s, en]):
                messagebox.showwarning("Missing",
                                       "Please fill in required fields.")
                return
            rid = f"office_{int(datetime.datetime.now().timestamp())}"
            entry = OfficeHours(rid, f, c, ins, day_var.get(), s, en,
                                 loc, fields["notes"].get().strip())
            self._dm.save_office_hour(entry)
            dlg.destroy()
            self.refresh()

        ctk.CTkButton(dlg, text="Save", fg_color=CARDINAL_RED,
                       hover_color=CARDINAL_DARK, corner_radius=8,
                       command=save).pack(pady=16)
