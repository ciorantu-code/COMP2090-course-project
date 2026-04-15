"""
main.py - Entry Point for Student Lifeline GUI Application

WHAT: Creates the main application window, draws the top bar and
      sidebar navigation, and handles view switching.
HOW:  Defines StudentLifelineApp which inherits from ctk.CTk (the
      customtkinter root window).  Uses a list of view classes and
      a _switch_view() method to swap content polymorphically.

Run:  pip install customtkinter   then   python main.py

Architecture (4 modules):
  main.py          → this file; entry point and navigation
  models.py        → data model classes (OOP: abstraction, inheritance,
                     encapsulation, polymorphism)
  data_manager.py  → file-based persistence (encapsulation)
  gui_views.py     → GUI view classes (inheritance, polymorphism)
"""

import customtkinter as ctk
from gui_views import (
    DashboardView, ImportantDatesView, GradeMonitorView,
    LostFoundView, CourseRatingView, OfficeHoursView,
    CARDINAL_RED, CARDINAL_DARK, WHITE, SIDEBAR_BG,
    SIDEBAR_TEXT, SIDEBAR_HOVER, LIGHT_GRAY, DARK_GRAY
)
from data_manager import DataManager


class StudentLifelineApp(ctk.CTk):
    """
    WHAT: Main application window with sidebar navigation.
    HOW:  Inherits from ctk.CTk.  Builds a top bar, a collapsible sidebar,
          and a content area.  Switches views polymorphically by indexing
          into a list of view classes and calling ViewClass(parent, dm).
    """

    # Menu items: (icon, label) — order matches the view_classes list
    MENU_ITEMS = [
        ("🏠", "Dashboard"),
        ("📅", "Important Dates"),
        ("📊", "Grade Monitor"),
        ("🔍", "Lost & Found"),
        ("⭐", "Course Ratings"),
        ("🕐", "Office Hours"),
    ]

    def __init__(self):
        """
        WHAT: Initialise the app window and data layer.
        HOW:  Calls super().__init__() for the CTk window, sets appearance
              with ctk.set_appearance_mode(), creates a DataManager (shared
              by all views), builds the layout, and opens the Dashboard.
        """
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Student Lifeline")
        self.geometry("1080x720")
        self.minsize(900, 600)

        # Shared data layer — all views read/write through this object
        self._dm = DataManager()

        # Internal state
        self._current_view = None
        self._sidebar_expanded = True
        self._nav_buttons: list[ctk.CTkButton] = []
        self._nav_labels: list[ctk.CTkLabel] = []

        self._build_layout()
        self._switch_view(0)

    # ----------------------------------------------------------------
    # Layout
    # ----------------------------------------------------------------
    def _build_layout(self):
        """
        WHAT: Build the top bar, sidebar, and content area.
        HOW:  Creates three CTkFrame sections.  The top bar uses
              pack(fill="x") with a fixed height via pack_propagate(False).
              The sidebar uses pack(side="left", fill="y") with a fixed
              width.  Sidebar buttons are created in a for-loop using
              enumerate() over MENU_ITEMS; each button's command uses
              a lambda with default argument (i=idx) to capture the
              correct index at creation time.
        """
        # Top bar
        top = ctk.CTkFrame(self, fg_color=CARDINAL_RED, height=52,
                            corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkButton(top, text="☰", width=42, height=36,
                       font=("Helvetica", 20), fg_color="transparent",
                       hover_color=CARDINAL_DARK, text_color=WHITE,
                       command=self._toggle_sidebar).pack(side="left",
                                                           padx=8)
        ctk.CTkLabel(top, text="Student Lifeline",
                      font=("Helvetica", 17, "bold"),
                      text_color=WHITE).pack(side="left", padx=4)
        ctk.CTkLabel(top, text="HKMU  •  COMP2090SEF",
                      font=("Helvetica", 11),
                      text_color="#E8CCCC").pack(side="right", padx=16)

        # Body (holds sidebar + content area)
        body = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, corner_radius=0)
        body.pack(fill="both", expand=True)

        # Sidebar
        self._sidebar = ctk.CTkFrame(body, fg_color=SIDEBAR_BG,
                                      width=220, corner_radius=0)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        for idx, (icon, label) in enumerate(self.MENU_ITEMS):
            btn_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
            btn_frame.pack(fill="x", padx=8, pady=2)
            btn = ctk.CTkButton(
                btn_frame,
                text=(f"  {icon}  {label}" if self._sidebar_expanded
                      else f"  {icon}"),
                anchor="w", fg_color="transparent",
                text_color=SIDEBAR_TEXT, hover_color=SIDEBAR_HOVER,
                font=("Helvetica", 14), height=40, corner_radius=8,
                # lambda with default arg captures current idx value
                command=lambda i=idx: self._switch_view(i)
            )
            btn.pack(fill="x")
            self._nav_buttons.append(btn)

        # Content area
        self._content_area = ctk.CTkFrame(body, fg_color=LIGHT_GRAY,
                                           corner_radius=0)
        self._content_area.pack(side="left", fill="both", expand=True)

    # ----------------------------------------------------------------
    # Navigation
    # ----------------------------------------------------------------
    def _switch_view(self, index: int):
        """
        WHAT: Switch the displayed content to the selected view.
        HOW:  Updates sidebar button colours via .configure() in a loop.
              Destroys the current view with .destroy().  Indexes into
              the view_classes list by position, instantiates the class
              with (parent, dm) arguments (polymorphic construction),
              and packs the new view.
        """
        # Highlight the active button
        for i, btn in enumerate(self._nav_buttons):
            btn.configure(
                fg_color=CARDINAL_RED if i == index else "transparent",
                text_color=WHITE if i == index else SIDEBAR_TEXT
            )

        # Destroy current view
        if self._current_view:
            self._current_view.destroy()

        # Instantiate the new view (polymorphic — any BaseView subclass)
        view_classes = [
            DashboardView, ImportantDatesView, GradeMonitorView,
            LostFoundView, CourseRatingView, OfficeHoursView,
        ]
        ViewClass = view_classes[index]
        self._current_view = ViewClass(self._content_area, self._dm)
        self._current_view.pack(fill="both", expand=True)

    def _toggle_sidebar(self):
        """
        WHAT: Collapse or expand the sidebar.
        HOW:  Flips self._sidebar_expanded, updates the sidebar width
              via .configure(width=...), and updates each button's text
              to include or exclude the label via .configure(text=...).
        """
        self._sidebar_expanded = not self._sidebar_expanded
        new_width = 220 if self._sidebar_expanded else 56
        self._sidebar.configure(width=new_width)
        for i, btn in enumerate(self._nav_buttons):
            icon, label = self.MENU_ITEMS[i]
            btn.configure(
                text=(f"  {icon}  {label}" if self._sidebar_expanded
                      else f"  {icon}")
            )


# ================================================================
# Entry point
# ================================================================
if __name__ == "__main__":
    app = StudentLifelineApp()
    app.mainloop()
