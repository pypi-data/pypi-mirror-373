import pandas as pd

class Insights:
    def __init__(self, grades_file):
        self.data = pd.read_csv(grades_file)
        self.data["Average"] = self.data.iloc[:, 1:].mean(axis=1)

    def struggling_students(self, threshold=60):
        return self.data[self.data["Average"] < threshold]["Name"].tolist()

    def improving_students(self):
        improving = []
        for idx, row in self.data.iterrows():
            if row.iloc[-1] > row.iloc[1]:
                improving.append(row["Name"])
        return improving

    def declining_students(self):
        declining = []
        for idx, row in self.data.iterrows():
            if row.iloc[-1] < row.iloc[1]:
                declining.append(row["Name"])
        return declining
