import pandas as pd

class Attendance:
    def __init__(self, filename=None, data=None):
        """
        Initialize Attendance.
        - filename: load CSV if provided
        - data: pass a DataFrame
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
        if name not in self.data["Name"].values:
            new_row = pd.DataFrame({"Name": [name]})
            self.data = pd.concat([self.data, new_row], ignore_index=True)

    def remove_student(self, name):
        self.data = self.data[self.data["Name"] != name]

    # ----------------------------
    # Attendance marking
    # ----------------------------
    def mark_present(self, student_name, date):
        self._mark(student_name, date, "P")

    def mark_absent(self, student_name, date):
        self._mark(student_name, date, "A")

    def _mark(self, student_name, date, status):
        if student_name not in self.data["Name"].values:
            self.add_student(student_name)
        if date not in self.data.columns:
            self.data[date] = None
        self.data.loc[self.data["Name"] == student_name, date] = status

    def delete_mark(self, student_name, date):
        """Remove attendance mark for a specific date."""
        if student_name in self.data["Name"].values and date in self.data.columns:
            self.data.loc[self.data["Name"] == student_name, date] = None

    # ----------------------------
    # Reports
    # ----------------------------
    def absent_report(self, student_name):
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return f"{student_name} not found"
        absent_days = row.iloc[0, 1:].eq("A").sum()
        return f"{student_name} was absent {absent_days} times"

    def present_report(self, student_name):
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return f"{student_name} not found"
        present_days = row.iloc[0, 1:].eq("P").sum()
        return f"{student_name} was present {present_days} times"

    # ----------------------------
    # Save / Load
    # ----------------------------
    def save_csv(self, filename):
        self.data.to_csv(filename, index=False)
        print(f"Attendance saved to {filename}")

    def load_csv(self, filename):
        self.data = pd.read_csv(filename)
        print(f"Attendance loaded from {filename}")
