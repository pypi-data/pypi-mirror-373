import os
from datetime import datetime

import webview
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QSizePolicy, QSpacerItem, QDialog, QTextEdit, QDialogButtonBox

from biosynth.data.app_data import InputData, OutputData, EliminationData
from biosynth.executions.controllers.ui.window_utils import add_button, add_code_block, add_text_edit_html, \
    CircularButton
from biosynth.executions.execution_utils import mark_non_equal_codons, initialize_report

QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)


def quit_app():
    QApplication.instance().quit()


def show_preview_report(report_local_file_path):
    file_path = os.path.abspath(report_local_file_path)
    webview.create_window('Preview Report', url=f'file://{file_path}', width=1200, height=800, resizable=False)
    webview.start()


class ResultsWindow(QWidget):
    def __init__(self, back_to_elimination_callback, updated_coding_positions):
        super().__init__()
        self.top_layout = None
        self.middle_layout = None
        self.bottom_layout = None
        self.report = None
        self.status_label = None

        self.updated_coding_positions = updated_coding_positions
        self.init_ui(back_to_elimination_callback)

        # Timer for status label
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.clear_status)

    def init_ui(self, callback):
        layout = QVBoxLayout(self)

        callback_args = (self.updated_coding_positions,)
        add_button(layout, 'Back', Qt.AlignLeft, callback, callback_args)

        self.display_info(layout)

    def display_info(self, layout):
        self.middle_layout = QVBoxLayout()
        self.middle_layout.setContentsMargins(20, 20, 20, 20)

        layout.addLayout(self.middle_layout)

        # Adding formatted text to QLabel
        label_html = f"""
            <h2>Results:</h2>
        """

        label = QLabel(label_html)
        self.middle_layout.addWidget(label)

        info_layout = QHBoxLayout()
        self.middle_layout.addLayout(info_layout)

        # Adding formatted text to QLabel
        label_html = f"""
            <h3>DNA Sequences Difference:</h3>
        """

        label = QLabel(label_html)
        info_layout.addWidget(label)

        # Create the info button
        info_button = CircularButton('ⓘ', self)
        info_button.clicked.connect(self.show_info)
        info_layout.addWidget(info_button, alignment=Qt.AlignRight)

        # Mark non-equal codons and print the optimized sequence
        index_seq_str, marked_input_seq, marked_optimized_seq = mark_non_equal_codons(InputData.dna_sequence,
                                                                                      OutputData.optimized_sequence,
                                                                                      self.updated_coding_positions)

        content = '''<pre>''' + index_seq_str + '''<br></pre>'''
        content += '''<pre>''' + marked_input_seq + '''<br><br>''' + marked_optimized_seq + '''</pre>'''

        content = content.replace("\n", "<br>")
        content = content.replace(" ", "&nbsp;")

        text_edit = add_text_edit_html(self.middle_layout, "", content)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: 1px solid gray;
                padding: 10px; /* Top, Right, Bottom, Left */
            }
        """)
        text_edit.setFixedHeight(150)  # Set fixed height

        # Adding formatted text to QLabel
        label_html = f"""
            <br>
            <br>
            <h3>Optimized Sequence:</h3>
        """

        label = QLabel(label_html)
        self.middle_layout.addWidget(label)

        # Create a report summarizing the processing and save if the user chooses to
        file_date = datetime.today().strftime("%d-%b-%Y, %H-%M-%S")

        add_code_block(self.middle_layout, OutputData.optimized_sequence, file_date, self.update_status)

        # Spacer to push other widgets to the top
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.prompt_report(self.middle_layout, file_date)

        # Create a horizontal layout for the bottom section
        self.bottom_layout = QHBoxLayout()
        layout.addLayout(self.bottom_layout)

        # Create the status bar-like label
        self.status_label = QLabel()
        self.bottom_layout.addWidget(self.status_label)

        # Add next button to the bottom layout
        done_button = QPushButton('Done')
        done_button.setFixedSize(60, 30)
        done_button.clicked.connect(lambda: quit_app())  # Connect to quit the application
        self.bottom_layout.addWidget(done_button, alignment=Qt.AlignRight)

    def prompt_report(self, layout, file_date):
        self.report = initialize_report(self.updated_coding_positions)

        report_local_file_path = self.report.create_report(file_date)

        if report_local_file_path:
            # Create a horizontal layout for the entire prompt
            prompt_layout = QHBoxLayout()
            prompt_layout.setSpacing(10)  # Adjust spacing between elements

            # Create and add the question label to the horizontal layout
            question_label = QLabel("Elimination report is now available")
            prompt_layout.addWidget(question_label)

            # Create the 'Save' button
            download_button = QPushButton('Download')
            download_button.setFixedSize(120, 30)
            download_button.clicked.connect(
                lambda: self.download_report())

            # Create the 'Save' button
            save_as_button = QPushButton('Save as')
            save_as_button.setFixedSize(120, 30)
            save_as_button.clicked.connect(
                lambda: self.save_as_report())

            # Create the 'Preview' button
            show_preview_button = QPushButton("Show Preview")
            show_preview_button.setFixedSize(120, 30)
            show_preview_button.clicked.connect(
                lambda: show_preview_report(report_local_file_path))

            # Add the buttons to the horizontal layout
            prompt_layout.addWidget(download_button)
            prompt_layout.addWidget(save_as_button)
            prompt_layout.addWidget(show_preview_button)

            # Add a spacer to push the buttons to the left
            spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            prompt_layout.addItem(spacer)

            # Add the entire horizontal layout to the parent layout
            layout.addLayout(prompt_layout)

    def show_info(self):
        info_text = '\n'.join(EliminationData.detailed_changes) if EliminationData.detailed_changes else None

        # Create a dialog to show detailed information
        dialog = QDialog(self)
        dialog.setWindowTitle('Info')
        dialog.setFixedSize(1000, 400)

        # Set the window flags to make the dialog non-modal and always on top
        dialog.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        dialog.setWindowModality(Qt.NonModal)  # Allow interaction with the parent

        layout = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        font = QFont("Menlo")
        font.setPointSize(10)
        text_edit.setFont(font)

        text_edit.setPlainText(info_text)

        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.show()

    def download_report(self):
        report_path = self.report.download_report()
        # Update status label when the report is downloaded
        self.update_status(report_path)

    def update_status(self, message):
        self.status_label.setText(message)
        # Start the timer to clear the status after 30 seconds
        self.status_timer.start(3000)  # 30 seconds in milliseconds

    def clear_status(self):
        self.status_label.setText("")
        self.status_timer.stop()

    def save_as_report(self):
        # Get the path to the desktop directory
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

        # Show the "Save As" dialog with the desktop directory as the default location
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save As", desktop_dir, "HTML Files (*.html);",
                                                   options=options)
        if save_path:
            try:
                report_path = self.report.download_report(save_path)
                self.update_status(f"Report saved as: {report_path}")
            except Exception as e:
                self.update_status(f"Failed to save report with error: {e}")
