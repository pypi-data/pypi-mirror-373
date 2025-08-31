import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pytica.visualizer import Visualizer

class Report:
    def __init__(self, filename=None, data=None):
        if filename:
            self.data = pd.read_csv(filename)
            self.visualizer = Visualizer(filename=filename)
        elif data is not None:
            self.data = data.copy()
            self.visualizer = Visualizer(data=data)
        else:
            self.data = pd.DataFrame(columns=["Name"])
            self.visualizer = Visualizer(data=self.data)

    def generate_excel(self, output_file="report.xlsx"):
        if self.data.shape[1] > 1:
            self.data["Average"] = self.data.iloc[:, 1:].mean(axis=1)
        self.data.to_excel(output_file, index=False)
        print(f"Excel report saved to {output_file}")

    def generate_pdf(self, output_file="report.pdf"):
        with PdfPages(output_file) as pdf:
            if self.data.shape[1] > 1:
                self.visualizer.plot_class_average()
                pdf.savefig()
                plt.close()
            for student in self.data["Name"]:
                self.visualizer.plot_student_progress(student)
                pdf.savefig()
                plt.close()
        print(f"PDF report saved to {output_file}")
