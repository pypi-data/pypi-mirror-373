import pandas as pd
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, grades_file):
        self.data = pd.read_csv(grades_file)

    def plot_student_progress(self, student_name):
        row = self.data[self.data["Name"] == student_name].iloc[0, 1:]
        plt.plot(row.index, row.values, marker='o')
        plt.title(f"{student_name}'s Progress")
        plt.xlabel("Assessments")
        plt.ylabel("Score")
        plt.ylim(0, 100)
        plt.grid(True)
        plt.show()

    def plot_class_average(self):
        averages = self.data.iloc[:, 1:].mean()
        plt.plot(averages.index, averages.values, marker='o', color='green')
        plt.title("Class Average Progress")
        plt.xlabel("Assessments")
        plt.ylabel("Average Score")
        plt.ylim(0, 100)
        plt.grid(True)
        plt.show()
