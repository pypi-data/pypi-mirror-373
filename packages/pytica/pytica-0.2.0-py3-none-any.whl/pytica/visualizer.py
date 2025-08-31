import pandas as pd
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, filename=None, data=None):
        if filename:
            self.data = pd.read_csv(filename)
        elif data is not None:
            self.data = data.copy()
        else:
            self.data = pd.DataFrame(columns=["Name"])

    def plot_student_progress(self, student_name):
        row = self.data[self.data["Name"] == student_name]
        if row.empty:
            print(f"{student_name} not found")
            return
        row = row.drop(columns=["Name"]).iloc[0].dropna()
        plt.plot(row.index, row.values, marker='o')
        plt.title(f"{student_name}'s Progress")
        plt.xlabel("Assessments")
        plt.ylabel("Score")
        plt.ylim(0, 100)
        plt.grid(True)
        plt.show()

    def plot_class_average(self):
        if self.data.shape[1] <= 1:
            print("No grade data available")
            return
        averages = self.data.drop(columns=["Name"]).mean()
        plt.plot(averages.index, averages.values, marker='o', color='green')
        plt.title("Class Average Progress")
        plt.xlabel("Assessments")
        plt.ylabel("Average Score")
        plt.ylim(0, 100)
        plt.grid(True)
        plt.show()
