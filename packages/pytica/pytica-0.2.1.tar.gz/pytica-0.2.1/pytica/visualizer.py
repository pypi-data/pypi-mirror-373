import pandas as pd
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, filename=None, data=None, attendance=None):
        """
        Initialize Visualizer
        - filename: CSV file with grades
        - data: DataFrame with grades
        - attendance: Attendance object (optional) for plotting
        """
        if filename:
            self.data = pd.read_csv(filename)
        elif data is not None:
            self.data = data.copy()
        else:
            self.data = pd.DataFrame(columns=["Name"])
        self.attendance = attendance

    # ----------------------------
    # Plot individual student progress
    # ----------------------------
    def plot_student_progress(self, student_name):
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            print(f"{student_name} not found")
            return
        row = row.drop(columns=["Name"]).iloc[0].dropna()
        if row.empty:
            print(f"No grades for {student_name}")
            return

        plt.figure(figsize=(6, 4))
        plt.plot(row.index, row.values, marker='o', color='blue')
        plt.title(f"{student_name}'s Progress")
        plt.xlabel("Assessments")
        plt.ylabel("Score")
        plt.ylim(0, 100)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # ----------------------------
    # Plot class average
    # ----------------------------
    def plot_class_average(self):
        if self.data.shape[1] <= 1:
            print("No grade data available")
            return

        averages = self.data.drop(columns=["Name"]).mean()
        plt.figure(figsize=(6, 4))
        plt.plot(averages.index, averages.values, marker='o', color='green')
        plt.title("Class Average Progress")
        plt.xlabel("Assessments")
        plt.ylabel("Average Score")
        plt.ylim(0, 100)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # ----------------------------
    # Optional: Plot attendance
    # ----------------------------
    def plot_attendance(self, student_name):
        if not self.attendance:
            print("Attendance data not provided")
            return
        row = self.attendance.data[self.attendance.data["Name"] == student_name]
        if row.empty:
            print(f"{student_name} not found in attendance")
            return
        row = row.drop(columns=["Name"]).iloc[0].dropna()
        status_numeric = row.apply(lambda x: 1 if x == "P" else 0)  # P=1, A=0

        plt.figure(figsize=(6, 4))
        plt.bar(status_numeric.index, status_numeric.values, color='orange')
        plt.title(f"{student_name}'s Attendance")
        plt.xlabel("Date")
        plt.ylabel("Presence (1=Present, 0=Absent)")
        plt.ylim(0, 1.2)
        plt.grid(axis='y')
        plt.tight_layout()
        plt.show()
