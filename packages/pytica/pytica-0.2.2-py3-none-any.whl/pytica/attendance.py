import pandas as pd

class Attendance:
    def __init__(self, filename=None, data=None):
        """
        Initialize Attendance.
        - filename: CSV file with attendance data
        - data: DataFrame of attendance
        """
        if filename:
            self.data = pd.read_csv(filename)
        elif data is not None:
            self.data = data.copy()
        else:
            self.data = pd.DataFrame(columns=["Name"])

    # ----------------------------
    # Student management
    # ----------------------------
    def add_student(self, name):
        """Add a new student if not exists."""
        if name not in self.data["Name"].values:
            new_row = pd.DataFrame({"Name": [name]})
            self.data = pd.concat([self.data, new_row], ignore_index=True)

    def remove_student(self, name):
        """Remove a student entirely."""
        self.data = self.data[self.data["Name"] != name]

    # ----------------------------
    # Attendance marking
    # ----------------------------
    def mark_present(self, student_name, date):
        """Mark a student as present."""
        self._mark(student_name, date, "P")

    def mark_absent(self, student_name, date):
        """Mark a student as absent."""
        self._mark(student_name, date, "A")

    def _mark(self, student_name, date, status):
        """Internal function to mark attendance."""
        if student_name not in self.data["Name"].values:
            self.add_student(student_name)
        if date not in self.data.columns:
            self.data[date] = None
        self.data.loc[self.data["Name"] == student_name, date] = status

    def delete_mark(self, student_name, date):
        """Delete attendance mark for a specific date."""
        if student_name in self.data["Name"].values and date in self.data.columns:
            self.data.loc[self.data["Name"] == student_name, date] = None

    # ----------------------------
    # Reports
    # ----------------------------
    def absent_report(self, student_name):
        """Return count of absences for a student."""
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return f"{student_name} not found"
        absent_days = row.iloc[0, 1:].eq("A").sum()
        return f"{student_name} was absent {absent_days} times"

    def present_report(self, student_name):
        """Return count of presences for a student."""
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return f"{student_name} not found"
        present_days = row.iloc[0, 1:].eq("P").sum()
        return f"{student_name} was present {present_days} times"

    def attendance_percentage(self, student_name):
        """Return percentage of presence for a student."""
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return None
        total_days = row.iloc[0, 1:].notna().sum()
        if total_days == 0:
            return 0
        present_days = row.iloc[0, 1:].eq("P").sum()
        return round((present_days / total_days) * 100, 2)

    # ----------------------------
    # Save / Load CSV
    # ----------------------------
    def save_csv(self, filename):
        """Save attendance to CSV."""
        self.data.to_csv(filename, index=False)
        print(f"Attendance saved to {filename}")

    def load_csv(self, filename):
        """Load attendance from CSV."""
        self.data = pd.read_csv(filename)
        print(f"Attendance loaded from {filename}")
