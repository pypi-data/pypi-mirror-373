import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from biosynth.executions.controllers.ui.base_window import BaseWindow
from biosynth.utils.file_utils import resource_path

sys.stderr = open(os.devnull, 'w')


class GUIController:
    @staticmethod
    def execute():
        stylesheet = """

        pre {
            font-size: 15px;
            line-height: 20px;
            max-width: 90%; /* Adjust this value as needed */
            margin-right: auto;
            overflow-wrap: break-word;
        }
        
        p {
            font-size: 15px;
            line-height: 5px;
            padding: 2px; /* Top, Right, Bottom, Left */
        }
        
        QCheckBox {
            font-size: 15px;
            line-height: 5px;
            padding: 2px; /* Top, Right, Bottom, Left */
        }
        
        QLabel {
            font-size: 15px;
            line-height: 5px;
            padding: 2px; /* Top, Right, Bottom, Left */
        }
        
        QTextEdit {
            font-size: 15px;
            line-height: 5px;
            padding: 2px; /* Top, Right, Bottom, Left */
        }
        
        QScrollArea {
            border: none;
            background: white; /* This will be the color of the 'margin' */
        }

        QScrollBar:vertical {
            border: none;
            background: lightgray; /* This should match the QScrollArea background */
            width: 2px;
        }

        QScrollBar::handle:vertical {
            background: gray;
            min-height: 20px;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar:horizontal {
            border: none;
            background: lightgray; /* This should match the QScrollArea background */
            height: 6px;
            margin: 4px 0 0 0; /* Vertical margin space */

        }
    
        QScrollBar::handle:horizontal {
            background: gray;
            min-width: 20px;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            width: 0px;
        }

        
        """

        app = QApplication(sys.argv)
        ex = BaseWindow()
        ex.show()
        icon_path = resource_path('images/BioSynth.png')
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)
        app.setStyleSheet(stylesheet)
        sys.exit(app.exec_())
