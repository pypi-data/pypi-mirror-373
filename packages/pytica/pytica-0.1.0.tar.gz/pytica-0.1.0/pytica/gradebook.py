import pandas as pd

class Gradebook:
    def __init__(self, filename):
        self.data = pd.read_csv(filename)

    def class_average(self):
        return self.data.iloc[:, 1:].mean().mean()

    def top_students(self, n=3):
        self.data["Average"] = self.data.iloc[:, 1:].mean(axis=1)
        return self.data.sort_values("Average", ascending=False).head(n)["Name"].tolist()

    def student_progress(self, student_name):
        row = self.data[self.data["Name"] == student_name].iloc[0, 1:]
        trend = "upward" if row.iloc[-1] > row.iloc[0] else "downward"
        improvement = f"{row.iloc[-1] - row.iloc[0]:+d}"
        return {"trend": trend, "improvement": improvement}
