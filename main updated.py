import os
import sys
import time
import subprocess

import numpy as np
from scipy.io import loadmat

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenModelica Runner")
        self.resize(900, 700)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.path_input = QLineEdit()
        self.start_input = QLineEdit()
        self.stop_input = QLineEdit()
        self.status_label = QLabel("Ready.")

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)

        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self.run_simulation)

        layout = QVBoxLayout()

        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("Select Executable:"))
        file_row.addWidget(self.path_input)
        file_row.addWidget(browse_btn)

        start_row = QHBoxLayout()
        start_row.addWidget(QLabel("Start Time:"))
        start_row.addWidget(self.start_input)

        stop_row = QHBoxLayout()
        stop_row.addWidget(QLabel("Stop Time:"))
        stop_row.addWidget(self.stop_input)

        layout.addLayout(file_row)
        layout.addLayout(start_row)
        layout.addLayout(stop_row)
        layout.addWidget(run_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Executable",
            "",
            "Executable Files (*.exe);;All Files (*)",
        )
        if file_path:
            self.path_input.setText(file_path)

    def _clear_old_mat_files(self, folder):
        for name in os.listdir(folder):
            if name.lower().endswith(".mat"):
                try:
                    os.remove(os.path.join(folder, name))
                except OSError:
                    pass

    def run_simulation(self):
        exe = self.path_input.text().strip()
        start_text = self.start_input.text().strip()
        stop_text = self.stop_input.text().strip()

        if not exe or not os.path.isfile(exe):
            self._fail("Invalid executable file.")
            return

        if not start_text.isdigit() or not stop_text.isdigit():
            self._fail("Start and stop must be integers.")
            return

        start = int(start_text)
        stop = int(stop_text)

        if not (0 <= start < stop < 5):
            self._fail("Condition: 0 <= start < stop < 5")
            return

        exe_folder = os.path.dirname(exe)

        command = [
            exe,
            f"-startTime={start}",
            f"-stopTime={stop}",
            "-outputFormat=mat",
        ]

        try:
            self.status_label.setText("Running simulation...")
            self._clear_plot()

            print("Running:", command)

            self._clear_old_mat_files(exe_folder)

            completed = subprocess.run(
                command,
                cwd=exe_folder,
                capture_output=True,
                text=True,
            )

            if completed.stdout:
                print(completed.stdout)
            if completed.stderr:
                print(completed.stderr)

            time.sleep(1)

            mat_file = self._find_latest_mat_file(exe_folder)

            if mat_file is None:
                self._fail("No .mat file found.")
                return

            print("Simulation completed ✅")
            print("Using file:", mat_file)

            data = loadmat(mat_file)
            series = self._extract_series(data)

            if not series:
                self._fail("No plottable data found.")
                return

            self._plot_series(series, os.path.basename(mat_file))
            self.status_label.setText("Simulation completed successfully ✅")

        except Exception as e:
            self._fail(f"Error: {e}")

    def _find_latest_mat_file(self, folder):
        mat_files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(".mat")
        ]
        if not mat_files:
            return None
        return max(mat_files, key=os.path.getmtime)

    def _extract_series(self, mat_data):
        series = {}

        for key, value in mat_data.items():
            if key.startswith("__"):
                continue

            try:
                arr = np.asarray(value).squeeze()
            except Exception:
                continue

            if not np.issubdtype(arr.dtype, np.number):
                continue

            if arr.size > 1:
                series[key] = arr.astype(float).reshape(-1)

        return series

    def _plot_series(self, series, title):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        time_key = None
        for k in series:
            if "time" in k.lower():
                time_key = k
                break

        time_values = series.get(time_key) if time_key else None

        plotted = False
        for k, values in series.items():
            if k == time_key:
                continue

            if time_values is not None and len(values) == len(time_values):
                ax.plot(time_values, values, label=k)
            else:
                ax.plot(values, label=k)

            plotted = True

        ax.set_title(title)
        ax.grid(True)

        if plotted:
            ax.legend()

        self.canvas.draw()

    def _clear_plot(self):
        self.figure.clear()
        self.canvas.draw()

    def _fail(self, msg):
        self.status_label.setText(msg)
        QMessageBox.warning(self, "Error", msg)
        print(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())