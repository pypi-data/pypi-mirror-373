from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QScrollArea
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QMessageBox

from biosynth.data.app_data import InputData
from biosynth.executions.controllers.ui.window_utils import FloatingScrollIndicator, add_button, add_text_edit_html, \
    add_text_edit, \
    adjust_text_edit_height, adjust_scroll_area_height, create_scroll_area
from biosynth.utils.display_utils import SequenceUtils
from biosynth.utils.dna_utils import DNAUtils


class SettingsWindow(QWidget):
    def __init__(self, switch_to_eliminate_callback, back_to_upload_callback):
        super().__init__()
        self.floating_btn = None
        self.switch_to_eliminate_callback = switch_to_eliminate_callback

        self.scroll_area = None
        self.next_button = None
        self.yes_button = None
        self.no_button = None
        self.region_selector = None
        self.submit_button = None

        self.content_widget = None

        self.init_ui(back_to_upload_callback)

    def init_ui(self, callback):
        layout = QVBoxLayout(self)
        add_button(layout, 'Back', Qt.AlignLeft, callback, ())
        self.display_info(layout)

    def display_info(self, layout):
        middle_layout = QVBoxLayout()
        middle_layout.setContentsMargins(20, 10, 20, 10)
        layout.addLayout(middle_layout)

        self.scroll_area, content_widget, content_layout = create_scroll_area(middle_layout)

        # Adding formatted text to QLabel
        label_html = f"""
            <h2>Input</h2>
            <h3>Target Sequence:</h3>
        """
        label = QLabel(label_html)
        content_layout.addWidget(label)

        content = f'{InputData.dna_sequence}'
        text_edit = add_text_edit(content_layout, "", content)
        adjust_text_edit_height(text_edit)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: 1px solid lightgray;
                margin-right: 25px;
            }
        """)

        label_html = f"""
            <h3>Unwanted Patterns:</h3>
        """
        label = QLabel(label_html)
        content_layout.addWidget(label)

        content = f'{SequenceUtils.get_patterns(InputData.unwanted_patterns)}'
        text_edit = add_text_edit(content_layout, "", content)
        adjust_text_edit_height(text_edit)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: 1px solid lightgray;
                margin-right: 25px;
            }
        """)

        # Extract coding regions
        InputData.coding_positions, InputData.coding_indexes = DNAUtils.get_coding_and_non_coding_regions_positions(
            InputData.dna_sequence)
        highlighted_sequence = f"<pre>{SequenceUtils.highlight_sequences_to_html(InputData.dna_sequence, InputData.coding_indexes, line_length=96, returnBr=True)}</pre>"

        # Handle elimination of coding regions if the user chooses to
        InputData.coding_regions_list = DNAUtils.get_coding_regions_list(InputData.coding_indexes,
                                                                         InputData.dna_sequence)

        # Adding formatted text to QLabel
        label_html = None

        if len(InputData.coding_regions_list) > 0:
            label_html = f"""
                <br>
                <h2>Elimination</h2>
                <h3>Coding Regions:</h3>
                <p>The following ORFs were identified in the target sequence:
            """
        else:
            label_html = f"""
                <br>
                <h2>Elimination</h2>
                <h3>Coding Regions:</h3>
            """

        label = QLabel(label_html)
        content_layout.addWidget(label)

        text_edit = add_text_edit_html(content_layout, "", highlighted_sequence)
        adjust_text_edit_height(text_edit)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: 1px solid lightgray;
                margin-right: 25px;
            }
        """)

        label = QLabel()
        content_layout.addWidget(label)
        self.next_button = add_button(layout, 'Next', Qt.AlignRight)

        if len(InputData.coding_regions_list) > 0:
            label_html = f"""
                <p>A total of {len(InputData.coding_regions_list)} ORFs have been identified.</p>
            """

            label.setText(label_html)

            if len(InputData.coding_regions_list) > 0:
                self.prompt_coding_regions_decision(content_layout)
        else:
            label_html = f"""
                <p>No ORFs were identified in the provided target sequence</p>
            """

            label.setText(label_html)
            self.next_button.clicked.connect(
                lambda: self.switch_to_eliminate_callback(InputData.coding_positions))

        # Add a stretch to push all content to the top
        content_layout.addStretch(1)
        self.next_button.setEnabled(len(InputData.coding_regions_list) == 0)

        # Add floating button
        self.floating_btn = FloatingScrollIndicator(parent=self, scroll_area=self.scroll_area)
        self.scroll_area.verticalScrollBar().rangeChanged.connect(
            lambda min_val, max_val: self.floating_btn.on_scroll(self.scroll_area.verticalScrollBar().value())
        )

    def resizeEvent(self, event):
        self.floating_btn.raise_()  # Bring to front
        self.floating_btn.reposition()

    def prompt_coding_regions_decision(self, layout):
        # Create a horizontal layout for the entire prompt
        prompt_layout = QHBoxLayout()
        container_widget = QWidget()
        prompt_layout.setContentsMargins(0, 0, 0, 0)

        container_widget.setLayout(prompt_layout)
        layout.addWidget(container_widget, alignment=Qt.AlignTop)

        question_label = QLabel("Would you like to proceed with all detected ORFs as coding regions?")
        prompt_layout.addWidget(question_label)

        # Create the 'Yes' button
        self.yes_button = add_button(prompt_layout, 'Yes', Qt.AlignLeft, self.select_all_regions)

        # Create the 'No' button
        self.no_button = add_button(prompt_layout, 'No', Qt.AlignLeft, self.select_regions_to_exclude, (layout,))

        # Add a spacer to push the buttons to the left
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        prompt_layout.addItem(spacer)

    def select_all_regions(self):
        if not self.no_button.isEnabled() or self.next_button.isEnabled():
            return

        self.no_button.setEnabled(False)
        self.next_button.clicked.connect(lambda: self.switch_to_eliminate_callback(InputData.coding_positions))
        self.next_button.setEnabled(True)

    def select_regions_to_exclude(self, layout):

        if not self.yes_button.isEnabled() or self.next_button.isEnabled():
            return

        container_widget = QWidget()
        layout.addWidget(container_widget, alignment=Qt.AlignTop)

        self.yes_button.setEnabled(False)
        self.region_selector = RegionSelector(container_widget, self.handle_results)

    def handle_results(self, layout):
        self.region_selector.setEnabled(False)
        self.next_button.clicked.connect(
            lambda: self.switch_to_eliminate_callback(InputData.excluded_coding_positions))
        self.next_button.setEnabled(True)

        label = QLabel(f"\nDesignated ORFs for Exclusion:")
        layout.addWidget(label, alignment=Qt.AlignTop)

        # Create a new QVBoxLayout for the content of this section
        scroll_area = QScrollArea()  # Create a scroll area
        scroll_area.setAlignment(Qt.AlignTop)
        scroll_area.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        scroll_content = QWidget()  # Create a widget to hold the content

        exclude_layout = QVBoxLayout(scroll_content)  # Layout for the content widget

        for key, value in InputData.excluded_regions_list.items():
            exclude = QLabel(f"[{key}]: {value}")
            exclude_layout.addWidget(exclude, alignment=Qt.AlignTop)

        # Set the content widget for the scroll area
        scroll_area.setWidget(scroll_content)
        adjust_scroll_area_height(scroll_area)

        # Add the scroll area to the parent widget
        layout.addWidget(scroll_area)

        label = QLabel(f"\nThese coding regions will be classified as non-coding areas.\n")
        layout.addWidget(label, alignment=Qt.AlignTop)

        # Adding formatted text to QLabel
        label_html = '''
        <p>The modified target sequence, reflecting your selections, is shown below:
        </p>'''

        label = QLabel(label_html)
        layout.addWidget(label)

        # Adding formatted text to QLabel
        label_html = f"<pre>{SequenceUtils.highlight_sequences_to_html(InputData.dna_sequence, InputData.excluded_coding_indexes, line_length=96, returnBr=True)}</pre>"

        text_edit = add_text_edit_html(layout, "", label_html)
        adjust_text_edit_height(text_edit)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: 1px solid lightgray;
            }
        """)

        # Install an event filter for the scroll area's viewport.
        self.scroll_area.viewport().installEventFilter(self)


class RegionSelector(QWidget):
    def __init__(self, layout, result_callback):
        super().__init__()
        self.result_callback = result_callback

        self.checkboxes = []
        self.submit_button = None
        self.init_ui(layout)

    def init_ui(self, parent_widget):
        # Create a new QVBoxLayout for the parent widget
        parent_layout = QVBoxLayout(parent_widget)  # Assuming parent_widget already has a QVBoxLayout

        # Create the instructions label and add it to the parent layout
        instructions_label = QLabel("Please review and select the ORFs you wish to exclude:")
        parent_layout.addWidget(instructions_label, alignment=Qt.AlignTop)

        # Create a new QVBoxLayout for the content of this section
        scroll_area = QScrollArea()  # Create a scroll area
        scroll_area.setAlignment(Qt.AlignTop)
        scroll_area.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

        scroll_content = QWidget()  # Create a widget to hold the content

        layout = QVBoxLayout(scroll_content)  # Layout for the content widget

        for index, region in InputData.coding_regions_list.items():
            checkbox = QCheckBox(f"[{index}]: {region}")
            layout.addWidget(checkbox, alignment=Qt.AlignTop)
            self.checkboxes.append((checkbox, region))

        # Set the content widget for the scroll area
        scroll_area.setWidget(scroll_content)
        adjust_scroll_area_height(scroll_area)

        # Add the scroll area to the parent widget
        parent_layout.addWidget(scroll_area)

        self.submit_button = add_button(parent_layout, 'Submit Exclusions', Qt.AlignLeft, self.submit_exclusions,
                                        (parent_layout,), size=(200, 30))

    def submit_exclusions(self, layout):
        checked_indices = [index for index, (checkbox, region) in enumerate(self.checkboxes) if checkbox.isChecked()]
        if len(checked_indices) <= 0:
            QMessageBox.question(self, 'Error',
                                 'You need to choose one coding region at least to continue',
                                 QMessageBox.Ok)
            return

        # Prompt the user for confirmation
        reply = QMessageBox.question(self, 'Confirm',
                                     'Do you want to eliminate selected coding regions?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.submit_button.setEnabled(False)
            self.disable_checkboxes()
            self.handle_coding_region_checkboxes()
            self.result_callback(layout)

    def handle_coding_region_checkboxes(self):
        InputData.excluded_regions_list = dict()
        InputData.excluded_coding_positions = InputData.coding_positions.copy()  # Create a copy to avoid modifying the original
        InputData.excluded_coding_indexes = InputData.coding_indexes.copy()  # Create a copy to avoid modifying the original

        # Implementation of the exclusion logic
        for index, (checkbox, region) in enumerate(self.checkboxes):
            if checkbox.isChecked():
                InputData.excluded_regions_list[f'{index + 1}'] = region
                start, end = InputData.coding_indexes[index]
                InputData.excluded_coding_positions[start:end] = [0] * (end - start)
                InputData.excluded_coding_indexes.remove((start, end))

    def disable_checkboxes(self):
        for checkbox, region in self.checkboxes:
            checkbox.setEnabled(False)
