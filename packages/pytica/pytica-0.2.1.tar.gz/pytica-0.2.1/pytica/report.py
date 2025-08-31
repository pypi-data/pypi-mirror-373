import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pytica.visualizer import Visualizer

class Report:
    def __init__(self, filename=None, data=None, attendance=None):
        """
        Initialize Report.
        - filename: CSV file with grades
        - data: DataFrame with grades
        - attendance: Attendance object (optional)
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
