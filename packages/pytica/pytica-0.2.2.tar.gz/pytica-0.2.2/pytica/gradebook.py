import pandas as pd

class Gradebook:
    def __init__(self, filename=None, data=None):
        """
        Initialize Gradebook.
        - filename: CSV file with grades
        - data: DataFrame of grades
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
        """Remove student entirely from the gradebook."""
        self.data = self.data[self.data["Name"] != name]

    # ----------------------------
    # Grade management
    # ----------------------------
    def add_grade(self, student_name, subject, grade):
        """Add a grade for a student and subject."""
        if student_name not in self.data["Name"].values:
            self.add_student(student_name)
        if subject not in self.data.columns:
            self.data[subject] = None
        self.data.loc[self.data["Name"] == student_name, subject] = grade

    def update_grade(self, student_name, subject, grade):
        """Update existing grade; create student/subject if needed."""
        if student_name not in self.data["Name"].values:
            self.add_student(student_name)
        if subject not in self.data.columns:
            self.data[subject] = None
        self.data.loc[self.data["Name"] == student_name, subject] = grade

    def delete_grade(self, student_name, subject):
        """Delete a grade by setting it to None."""
        if student_name in self.data["Name"].values and subject in self.data.columns:
            self.data.loc[self.data["Name"] == student_name, subject] = None

    # ----------------------------
    # Data retrieval
    # ----------------------------
    def get_students(self):
        """Return list of student names."""
        return self.data["Name"].tolist()

    def get_grades(self, student_name):
        """Return a dict of subject:grade for a student."""
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return {}
        return row.drop(columns=["Name"]).iloc[0].dropna().to_dict()

    def get_average(self, student_name):
        """Return average grade of a student."""
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return None
        return row.drop(columns=["Name"]).mean(axis=1).iloc[0]

    def class_average(self):
        """Return overall class average."""
        if self.data.shape[1] <= 1:
            return None
        return self.data.drop(columns=["Name"]).mean().mean()

    def top_students(self, n=3):
        """Return top N students based on average."""
        if self.data.shape[1] <= 1:
            return []
        self.data["Average"] = self.data.drop(columns=["Name"]).mean(axis=1)
        return self.data.sort_values("Average", ascending=False).head(n)["Name"].tolist()

    def student_progress(self, student_name):
        """Return trend and improvement for a student."""
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return None
        row = row.drop(columns=["Name"]).iloc[0].dropna()
        if len(row) < 2:
            return {"trend": "flat", "improvement": "+0"}
        trend = "upward" if row.iloc[-1] > row.iloc[0] else "downward"
        improvement = f"{int(row.iloc[-1] - row.iloc[0]):+d}"
        return {"trend": trend, "improvement": improvement}

    # ----------------------------
    # Save / Load CSV
    # ----------------------------
    def save_csv(self, filename):
        """Save gradebook to CSV."""
        self.data.to_csv(filename, index=False)
        print(f"Gradebook saved to {filename}")

    def load_csv(self, filename):
        """Load gradebook from CSV."""
        self.data = pd.read_csv(filename)
        print(f"Gradebook loaded from {filename}")
