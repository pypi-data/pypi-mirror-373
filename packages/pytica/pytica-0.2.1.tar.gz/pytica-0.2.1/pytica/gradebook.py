import pandas as pd

class Gradebook:
    def __init__(self, filename=None, data=None):
        """
        Initialize Gradebook.
        - filename: load CSV if provided
        - data: pass a DataFrame directly
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
    # Grade management
    # ----------------------------
    def add_grade(self, student_name, subject, grade):
        if student_name not in self.data["Name"].values:
            self.add_student(student_name)
        if subject not in self.data.columns:
            self.data[subject] = None
        self.data.loc[self.data["Name"] == student_name, subject] = grade

    def update_grade(self, student_name, subject, grade):
        if student_name in self.data["Name"].values and subject in self.data.columns:
            self.data.loc[self.data["Name"] == student_name, subject] = grade
        else:
            print(f"Student or subject not found.")

    def delete_grade(self, student_name, subject):
        if student_name in self.data["Name"].values and subject in self.data.columns:
            self.data.loc[self.data["Name"] == student_name, subject] = None
        else:
            print(f"Student or subject not found.")

    # ----------------------------
    # Data retrieval
    # ----------------------------
    def get_students(self):
        return self.data["Name"].tolist()

    def get_grades(self, student_name):
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return {}
        return row.drop(columns=["Name"]).iloc[0].dropna().to_dict()

    def get_average(self, student_name):
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            return None
        return row.drop(columns=["Name"]).mean(axis=1).iloc[0]

    def class_average(self):
        if self.data.shape[1] <= 1:
            return None
        return self.data.drop(columns=["Name"]).mean().mean()

    def top_students(self, n=3):
        if self.data.shape[1] <= 1:
            return []
        self.data["Average"] = self.data.drop(columns=["Name"]).mean(axis=1)
        return self.data.sort_values("Average", ascending=False).head(n)["Name"].tolist()

    def student_progress(self, student_name):
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
    # Save / Load
    # ----------------------------
    def save_csv(self, filename):
        self.data.to_csv(filename, index=False)
        print(f"Gradebook saved to {filename}")

    def load_csv(self, filename):
        self.data = pd.read_csv(filename)
        print(f"Gradebook loaded from {filename}")
