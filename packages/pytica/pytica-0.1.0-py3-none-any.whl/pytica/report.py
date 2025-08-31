import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pytica.visualizer import Visualizer

class Report:
    def __init__(self, grades_file):
        self.data = pd.read_csv(grades_file)
        self.visualizer = Visualizer(grades_file)

    def generate_excel(self, output_file="report.xlsx"):
        self.data["Average"] = self.data.iloc[:, 1:].mean(axis=1)
        self.data.to_excel(output_file, index=False)
        print(f"Excel report saved to {output_file}")

    def generate_pdf(self, output_file="report.pdf"):
        with PdfPages(output_file) as pdf:
            self.visualizer.plot_class_average()
            pdf.savefig()
            plt.close()
            for student in self.data["Name"]:
                self.visualizer.plot_student_progress(student)
                pdf.savefig()
                plt.close()
        print(f"PDF report saved to {output_file}")
