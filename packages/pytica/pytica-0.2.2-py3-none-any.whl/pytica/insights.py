import pandas as pd

class Insights:
    def __init__(self, filename=None, data=None, attendance=None):
        """
        Initialize Insights.
        - filename: CSV file with grades
        - data: DataFrame of grades
        - attendance: Attendance object (optional)
        """
        if filename:
            self.data = pd.read_csv(filename)
        elif data is not None:
            self.data = data.copy()
        else:
            self.data = pd.DataFrame(columns=["Name"])

        self.attendance = attendance

        # Ensure Average column exists
        if "Average" not in self.data.columns and self.data.shape[1] > 1:
            self.data["Average"] = self.data.iloc[:, 1:].mean(axis=1)

    # ----------------------------
    # Analytics
    # ----------------------------
    def struggling_students(self, threshold=60):
        """
        Return list of students with average below threshold.
        """
        if "Average" not in self.data.columns:
            return []
        return self.data[self.data["Average"] < threshold]["Name"].tolist()

    def improving_students(self):
        """
        Return list of students whose scores improved over time.
        """
        improving = []
        for _, row in self.data.iterrows():
            scores = row.drop(labels=["Name", "Average"], errors="ignore").dropna()
            if len(scores) >= 2 and scores.iloc[-1] > scores.iloc[0]:
                improving.append(row["Name"])
        return improving

    def declining_students(self):
        """
        Return list of students whose scores declined over time.
        """
        declining = []
        for _, row in self.data.iterrows():
            scores = row.drop(labels=["Name", "Average"], errors="ignore").dropna()
            if len(scores) >= 2 and scores.iloc[-1] < scores.iloc[0]:
                declining.append(row["Name"])
        return declining

    def attendance_summary(self):
        """
        Optional: return a summary dict of attendance if provided.
        Format: {student_name: {"present": X, "absent": Y}}
        """
        summary = {}
        if not self.attendance:
            return summary

        for _, row in self.attendance.data.iterrows():
            name = row["Name"]
            present = (row == "P").sum()
            absent = (row == "A").sum()
            summary[name] = {"present": present, "absent": absent}
        return summary

    # ----------------------------
    # Save / Load CSV
    # ----------------------------
    def save_csv(self, filename):
        """
        Save insights to CSV.
        """
        self.data.to_csv(filename, index=False)
        print(f"Insights saved to {filename}")

    def load_csv(self, filename):
        """
        Load insights from CSV.
        """
        self.data = pd.read_csv(filename)
        print(f"Insights loaded from {filename}")
