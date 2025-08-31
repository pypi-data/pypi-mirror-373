import os

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainterPath, QRegion
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QFileDialog, QTextEdit, QPlainTextEdit, QToolBar, QDoubleSpinBox, QScrollArea, QWidget
from PyQt5.QtWidgets import QFrame, QPushButton, QVBoxLayout, QApplication, QLabel, QHBoxLayout, QSizePolicy, \
    QTableWidget, QHeaderView

from biosynth.utils.file_utils import resource_path, save_file


class CircularButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(CircularButton, self).__init__(*args, **kwargs)
        self.setFixedSize(20, 20)  # Set the fixed size for the button

        # Apply the stylesheet to make the button circular
        self.setStyleSheet("""
            QPushButton {
                border: 2px solid transparent;
                border-radius: 10;  /* Half of the button's size */
                background-color: #888;
                color: white;
                font-size: 15px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #aaa;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """)

    def paintEvent(self, event):
        # Create a circular clipping region
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        super(CircularButton, self).paintEvent(event)


class DropTextEdit(QTextEdit):
    def __init__(self, parent=None, drop_callback=None):
        super().__init__(parent)
        self.drop_callback = drop_callback
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.endswith('.txt'):
                if self.drop_callback:
                    self.drop_callback(file_path)  # Let callback handle reading + setting text

        event.acceptProposedAction()


class DropTableWidget(QTableWidget):
    def __init__(self, parent=None, drop_callback=None):
        super().__init__(parent)
        self.drop_callback = drop_callback
        self.setAcceptDrops(True)
        self.setDragDropMode(QTableWidget.DropOnly)
        self.viewport().setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(".txt"):
                if self.drop_callback:
                    self.drop_callback(file_path)
        event.accept()


class FloatingScrollIndicator(QPushButton):
    def __init__(self, parent=None, scroll_area=None, direction="bottom"):
        super().__init__("▼", parent)
        self.animation = None
        self.scroll_area = scroll_area
        self.direction = direction

        self.setFixedSize(20, 20)
        self.setStyleSheet("""
            QPushButton {
                background-color: gray;
                border: 1px solid lightgray;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
        """)
        self.hide()

        # Connect scroll listener
        if self.scroll_area:
            self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

        # Handle click
        self.clicked.connect(self.scroll)

    def on_scroll(self, value):
        scrollbar = self.scroll_area.verticalScrollBar()
        if scrollbar.maximum() == 0:
            self.hide()
        elif value < scrollbar.maximum() - 10:
            self.show()
        else:
            self.hide()

    def scroll(self, **kwargs):
        bar = self.scroll_area.verticalScrollBar()
        start_value = bar.value()
        if self.direction == "top":
            end_value = 0
        elif self.direction == "bottom":
            end_value = bar.maximum()
        else:
            return

        self.animation = QPropertyAnimation(bar, b"value")
        self.animation.setDuration(500)  # Duration in milliseconds
        self.animation.setStartValue(start_value)
        self.animation.setEndValue(end_value)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def reposition(self):
        """Call this on parent resize"""
        if not self.parent():
            return
        margin = 80
        x = self.parent().width() / 2
        y = self.parent().height() - self.height() - margin
        self.move(int(x), int(y))


def add_intro(layout, row=0, column=0):
    # --- Top full-width intro ---
    intro_text = (
        "Welcome to the BioSynth App!\n\n"
        "To begin, upload the following files and optionally adjust substitution costs."
    )
    intro_label = QLabel(intro_text)
    intro_label.setWordWrap(True)
    intro_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    # --- Left column: Required files ---
    required_files_text = (
        "Required files:\n"
        "• Target DNA sequence file\n"
        "• Unwanted patterns file\n"
        "• Codon usage file"
    )
    required_label = QLabel(required_files_text)
    required_label.setWordWrap(True)
    required_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    # --- Right column: Optional costs ---
    optional_costs_text = (
        "Optional substitution costs:\n"
        "• Transitions substitutions in non-coding regions (default: 1.0)\n"
        "• Transversions substitutions in non-coding regions (default: 2.0)\n"
        "• Non-synonymous substitutions in coding regions (default: 100.0)"
    )
    optional_label = QLabel(optional_costs_text)
    optional_label.setWordWrap(True)
    optional_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    # --- Bottom full-width message ---
    bottom_text = (
        "Once you're done, BioSynth will optimize your sequence.\n"
        "Let’s get started!"
    )
    bottom_label = QLabel(bottom_text)
    bottom_label.setWordWrap(True)
    bottom_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    # --- Create layouts ---
    mid_layout = QHBoxLayout()
    mid_layout.addWidget(required_label)
    mid_layout.addWidget(optional_label)

    container = QWidget()
    container_layout = QVBoxLayout(container)
    container_layout.addWidget(intro_label)
    container_layout.addLayout(mid_layout)
    container_layout.addWidget(bottom_label)

    layout.addWidget(container, row, column)

    return intro_label, required_label, optional_label, bottom_label


def add_png_logo(layout, row=0, column=0):
    # Create a frame to hold the logo
    frame = QFrame()
    frame_layout = QHBoxLayout(frame)  # Use a QHBoxLayout within the frame
    frame_layout.setContentsMargins(5, 5, 5, 5)  # Set padding: left, top, right, bottom

    # Create and set up the PNG logo widget
    image_path = resource_path("images/BioSynth.png")
    logo = QLabel()
    pixmap = QPixmap(image_path)
    logo.setPixmap(pixmap)
    logo.setFixedSize(110, 110)  # Adjust the size as needed
    logo.setScaledContents(True)  # Ensure the image scales properly within the label

    # Add the logo to the frame's layout
    frame_layout.addWidget(logo)

    # Add the frame to the main layout
    layout.addWidget(frame, row, column, alignment=Qt.AlignTop)


def add_logo_toolbar(layout):
    # Create a toolbar for the logo
    logo_toolbar = QToolBar()
    logo_toolbar.setMovable(False)

    # Create and set up the PNG logo widget
    image_path = resource_path("images/BioSynth.png")
    logo_label = QLabel()
    pixmap = QPixmap(image_path)
    logo_label.setPixmap(pixmap)
    logo_label.setFixedSize(110, 110)  # Adjust the size as needed
    logo_label.setScaledContents(True)  # Ensure the image scales properly within the label

    # Add the logo label to the toolbar
    logo_toolbar.addWidget(logo_label)

    # Add the toolbar to the main window
    layout.addToolBar(Qt.TopToolBarArea, logo_toolbar)


def add_drop_table(layout, placeholder, columns, headers, drop_callback):
    table = DropTableWidget(drop_callback=drop_callback)
    table.setColumnCount(columns)
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    layout.addWidget(table)

    # Now create placeholder overlay
    placeholder_label = QLabel(placeholder, table.viewport())
    placeholder_label.setAlignment(Qt.AlignLeft)
    placeholder_label.setStyleSheet("color: gray; font-size: 16px;")
    placeholder_label.setAttribute(Qt.WA_TransparentForMouseEvents)
    placeholder_label.show()

    # Attach placeholder label to the table instance
    table.placeholder_label = placeholder_label

    # Update placeholder visibility initially
    def update_placeholder():
        placeholder_label.setVisible(table.rowCount() == 0)

    table.update_placeholder = update_placeholder
    update_placeholder()

    # Intercept resizeEvent
    original_resize_event = table.resizeEvent

    def new_resize_event(event):
        placeholder_label.resize(table.viewport().size())
        if original_resize_event:
            original_resize_event(event)

    table.resizeEvent = new_resize_event

    return table


def add_drop_text_edit(layout, placeholder, drop_callback, wrap=None):
    text_edit = DropTextEdit(drop_callback=drop_callback)
    text_edit.setPlaceholderText(placeholder)

    if wrap is not None:
        text_edit.setLineWrapMode(wrap)
    else:
        text_edit.setLineWrapMode(QTextEdit.WidgetWidth)  # Default wrap mode

    # Set the cursor shape to the default pointer cursor for the viewport
    text_edit.viewport().setCursor(Qt.ArrowCursor)

    layout.addWidget(text_edit)

    return text_edit


def add_text_edit(layout, placeholder, content, wrap=None):
    text_edit = QTextEdit()
    text_edit.setPlaceholderText(placeholder)

    if content:
        text_edit.setPlainText(content)

    font = QFont("Menlo")  # or "Courier New" / "Monaco"
    font.setPointSize(10)
    text_edit.setFont(font)

    text_edit.setReadOnly(True)
    text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
    text_edit.viewport().setCursor(Qt.ArrowCursor)

    # Keep wrapping for multi-line display
    if wrap is not None:
        text_edit.setLineWrapMode(wrap)
    else:
        text_edit.setLineWrapMode(QTextEdit.WidgetWidth)  # Default: wrap to widget width

    layout.addWidget(text_edit)

    return text_edit


def adjust_text_edit_height(text_edit):
    text_edit.document().setTextWidth(text_edit.viewport().width())
    margins = text_edit.contentsMargins()
    height = int(text_edit.document().size().height() + margins.top() + margins.bottom() + 10)
    text_edit.setFixedHeight(height)


def adjust_scroll_area_height(scroll_area):
    # Get the widget inside the scroll area
    widget = scroll_area.widget()

    # Ensure the widget's size is recalculated
    widget.adjustSize()

    # Get the new height of the widget
    widget_height = widget.sizeHint().height()

    # Calculate the new height with a maximum limit and padding
    new_height = min(150, widget_height + 10)  # 10 pixels of padding

    # Set the fixed height of the scroll area
    scroll_area.setFixedHeight(new_height + 10)  # Additional 10 pixels padding


def add_text_edit_html(layout, placeholder, content):
    text_edit = QTextEdit()
    text_edit.setPlaceholderText(placeholder)

    if content:
        text_edit.setHtml(content)

    text_edit.setStyleSheet("""
        QTextEdit {
            background-color: transparent;
        }
    """)

    font = QFont("Menlo")  # or "Courier New" / "Monaco"
    font.setPointSize(10)
    text_edit.setFont(font)

    text_edit.setReadOnly(True)
    text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
    text_edit.viewport().setCursor(Qt.ArrowCursor)

    layout.addWidget(text_edit)
    return text_edit


def add_code_block(parent_layout, text, file_date, update_status):
    layout = QVBoxLayout()
    parent_layout.addLayout(layout)

    # Create a QPlainTextEdit to display the code
    code_display = QPlainTextEdit(text)
    code_display.setReadOnly(True)
    layout.addWidget(code_display)

    # Button layout
    button_layout = QHBoxLayout()
    layout.addLayout(button_layout)

    button_layout.addStretch(1)  # Push the button to the right

    # Download button
    add_button(button_layout, 'Download', Qt.AlignRight, download_file, (code_display, file_date, update_status,),
               size=(100, 30))

    # Save button
    add_button(button_layout, 'Save as', Qt.AlignRight, save_to_file, (code_display, update_status,), size=(100, 30))

    # Copy button
    add_button(button_layout, 'Copy', Qt.AlignRight, copy_to_clipboard, (code_display, update_status,))


def download_file(code_display, file_date, update_status):
    filename = f'Optimized Sequence - {file_date}.txt'
    text = code_display.toPlainText()
    path = save_file(text, filename)
    update_status(path)


def save_to_file(code_display, update_status):
    text = code_display.toPlainText()
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    options = QFileDialog.Options()
    filename, _ = QFileDialog.getSaveFileName(None, "Save File", download_path, "Text Files (*.txt);", options=options)

    if filename:
        try:
            with open(filename, 'w') as file:
                file.write(text)
                update_status(filename)
        except Exception as e:
            update_status(f"Failed to save file: {e}")


def add_button(layout, text, alignment=None, callback=None, args=(), size=(60, 30)):
    bottom_layout = QHBoxLayout()
    layout.addLayout(bottom_layout)

    button = QPushButton(text)
    button.setFixedSize(size[0], size[1])
    button.setFocusPolicy(Qt.NoFocus)

    # Check if 'args' is callable or not and connect accordingly
    if callback is not None:
        if callable(args):
            button.clicked.connect(lambda: callback(*args()))
        else:
            button.clicked.connect(lambda: callback(*args))

    bottom_layout.addWidget(button, alignment=alignment)

    return button


def add_spinbox(layout, default_value, step=0.01,
                alignment=None, callback=None, args=(), size=(80, 30)):
    """
    Adds a QSpinBox to the given layout with optional callback.

    If args[0] is provided, it is shown as a label before the spinbox.

    Returns:
        QSpinBox instance.
    """
    bottom_layout = QHBoxLayout()
    bottom_layout.setContentsMargins(0, 5, 0, 10)
    layout.addLayout(bottom_layout)

    # Optional label based on args[0]
    if args and isinstance(args[0], str):
        label = QLabel(str(args[0]))
        label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        bottom_layout.addWidget(label, stretch=4)

    spinbox = QDoubleSpinBox()
    spinbox.setMinimum(0.0)
    spinbox.setMaximum(2147483647.0)
    spinbox.setValue(default_value)
    spinbox.setSingleStep(step)
    spinbox.setFixedSize(size[0], size[1])
    spinbox.setFocusPolicy(Qt.StrongFocus)

    if callback is not None:
        spinbox.valueChanged.connect(lambda val: callback(val))

    bottom_layout.addWidget(spinbox, alignment=alignment, stretch=1)
    return spinbox


def copy_to_clipboard(code_display, update_status):
    text = code_display.toPlainText()
    QApplication.clipboard().setText(text)
    update_status(f"Sequence copied to clipboard")


def create_scroll_area(parent_layout):
    scroll_area = QScrollArea()
    scroll_area.setFixedHeight(550)  # Set the maximum height for scrolling to begin
    scroll_area.setWidgetResizable(True)  # Ensure the scroll area can resize to its content
    scroll_area.setStyleSheet("QScrollArea { border: none; }")
    scroll_area.setAlignment(Qt.AlignTop)

    parent_layout.addWidget(scroll_area, alignment=Qt.AlignTop)

    content_widget = QWidget()
    scroll_area.setWidget(content_widget)

    content_layout = QVBoxLayout(content_widget)
    content_layout.setAlignment(Qt.AlignTop)

    return scroll_area, content_widget, content_layout
