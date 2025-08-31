import pandas as pd

class Attendance:
    def __init__(self, filename=None, data=None):
        if filename:
            self.data = pd.read_csv(filename)
        elif data is not None:
            self.data = data.copy()
        else:
            self.data = pd.DataFrame(columns=["Name"])

    def add_student(self, name):
        if name not in self.data["Name"].values:
            new_row = pd.DataFrame({"Name": [name]})
            self.data = pd.concat([self.data, new_row], ignore_index=True)

    def mark_present(self, student_name, date):
        if student_name not in self.data["Name"].values:
            self.add_student(student_name)
        if date not in self.data.columns:
            self.data[date] = None
        self.data.loc[self.data["Name"] == student_name, date] = "P"

    def mark_absent(self, student_name, date):
        if student_name not in self.data["Name"].values:
            self.add_student(student_name)
        if date not in self.data.columns:
            self.data[date] = None
        self.data.loc[self.data["Name"] == student_name, date] = "A"

    def absent_report(self, student_name):
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return f"{student_name} not found"
        absent_days = row.iloc[0, 1:].eq("A").sum()
        return f"{student_name} was absent {absent_days} times"
