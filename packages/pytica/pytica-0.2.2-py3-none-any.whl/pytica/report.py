import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pytica.visualizer import Visualizer
import os

class Report:
    def __init__(self, filename=None, data=None, attendance=None, image_folder="images"):
        """
        Initialize Report.
        - filename: CSV file with grades
        - data: DataFrame with grades
        - attendance: Attendance object (optional)
        - image_folder: folder to save PNG charts
        """
        if filename:
            self.data = pd.read_csv(filename)
            self.visualizer = Visualizer(filename=filename)
        elif data is not None:
            self.data = data.copy()
            self.visualizer = Visualizer(data=data)
        else:
            self.data = pd.DataFrame(columns=["Name"])
            self.visualizer = Visualizer(data=self.data)

        self.attendance = attendance

        # Ensure Average column exists
        if "Average" not in self.data.columns and self.data.shape[1] > 1:
            self.data["Average"] = self.data.iloc[:, 1:].mean(axis=1)

        # Create folder for images
        self.image_folder = image_folder
        os.makedirs(self.image_folder, exist_ok=True)

    # ----------------------------
    # Excel Report
    # ----------------------------
    def generate_excel(self, output_file="report.xlsx"):
        df = self.data.copy()
        if self.attendance:
            att_df = self.attendance.data.copy()
            df = pd.merge(df, att_df, on="Name", how="left")
        df.to_excel(output_file, index=False)
        print(f"Excel report saved to {output_file}")

    # ----------------------------
    # PDF Report
    # ----------------------------
    def generate_pdf(self, output_file="report.pdf"):
        with PdfPages(output_file) as pdf:
            # Class Average plot
            if self.data.shape[1] > 1:
                self.visualizer.plot_class_average()
                pdf.savefig()
                plt.close()

            # Student progress plots
            for student in self.data["Name"]:
                self.visualizer.plot_student_progress(student)
                pdf.savefig()
                plt.close()

        print(f"PDF report saved to {output_file}")

    # ----------------------------
    # Image-Only Report
    # ----------------------------
    def generate_images(self):
        # Class Average
        if self.data.shape[1] > 1:
            averages = self.data.drop(columns=["Name"]).mean()
            plt.plot(averages.index, averages.values, marker='o', color='green')
            plt.title("Class Average Progress")
            plt.xlabel("Assessments")
            plt.ylabel("Average Score")
            plt.ylim(0, 100)
            plt.grid(True)
            class_file = os.path.join(self.image_folder, "class_average.png")
            plt.savefig(class_file)
            plt.close()
            print(f"Class average chart saved to {class_file}")

        # Student charts
        for student in self.data["Name"]:
            row = self.data[self.data["Name"] == student].drop(columns=["Name"]).iloc[0].dropna()
            plt.plot(row.index, row.values, marker='o')
            plt.title(f"{student}'s Progress")
            plt.xlabel("Assessments")
            plt.ylabel("Score")
            plt.ylim(0, 100)
            plt.grid(True)
            student_file = os.path.join(self.image_folder, f"{student}_progress.png")
            plt.savefig(student_file)
            plt.close()
            print(f"{student}'s chart saved to {student_file}")
