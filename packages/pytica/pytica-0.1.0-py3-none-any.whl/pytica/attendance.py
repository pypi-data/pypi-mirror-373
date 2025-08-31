import pandas as pd

class Attendance:
    def __init__(self, filename):
        self.data = pd.read_csv(filename)

    def absent_report(self, student_name):
        row = self.data[self.data["Name"] == student_name].iloc[0, 1:]
        absent_days = row[row == "A"].count()
        return f"{student_name} was absent {absent_days} times"
