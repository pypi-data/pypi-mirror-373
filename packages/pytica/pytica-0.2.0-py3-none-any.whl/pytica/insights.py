import pandas as pd

class Insights:
    def __init__(self, filename=None, data=None):
        if filename:
            self.data = pd.read_csv(filename)
        elif data is not None:
            self.data = data.copy()
        else:
            self.data = pd.DataFrame(columns=["Name"])
        
        if "Average" not in self.data.columns and self.data.shape[1] > 1:
            self.data["Average"] = self.data.iloc[:, 1:].mean(axis=1)

    def struggling_students(self, threshold=60):
        if "Average" not in self.data.columns:
            return []
        return self.data[self.data["Average"] < threshold]["Name"].tolist()

    def improving_students(self):
        improving = []
        for _, row in self.data.iterrows():
            scores = row.drop(labels=["Name", "Average"], errors="ignore").dropna()
            if len(scores) >= 2 and scores.iloc[-1] > scores.iloc[0]:
                improving.append(row["Name"])
        return improving

    def declining_students(self):
        declining = []
        for _, row in self.data.iterrows():
            scores = row.drop(labels=["Name", "Average"], errors="ignore").dropna()
            if len(scores) >= 2 and scores.iloc[-1] < scores.iloc[0]:
                declining.append(row["Name"])
        return declining
