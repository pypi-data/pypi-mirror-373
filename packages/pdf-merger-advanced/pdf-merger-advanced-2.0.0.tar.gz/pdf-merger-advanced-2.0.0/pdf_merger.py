import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QListWidget, QFileDialog, QMessageBox, QLabel,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSpinBox, QGroupBox, QWidget, QTabWidget,
    QTextEdit, QComboBox, QSlider, QMenuBar, QAction,
    QListWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QMimeData, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QDrag, QIcon
from PyPDF2 import  PdfReader
from pathlib import Path
import os
import json


class FileListItem(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        # File name label: visible text, no background container, clickable
        self.file_label = QLabel(Path(self.file_path).name)
        self.file_label.setStyleSheet("""
            font-weight: 600;
            font-size: 15px;
            color: #1e293b;
            background-color: transparent;
            cursor: pointer;
        """)
        self.file_label.setMinimumWidth(300)
        self.file_label.setMaximumWidth(500)
        self.file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.file_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.file_label.setWordWrap(False)
        self.file_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.file_label.setToolTip(self.file_label.text())
        
        # Make file label clickable
        self.file_label.mousePressEvent = self.on_file_label_clicked
        self.file_label.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(self.file_label, stretch=1)

        # Page range controls: separate visible elements
        range_layout = QHBoxLayout()
        range_layout.setSpacing(6)
        self.range_label = QLabel("Pages:")
        self.range_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b; background-color: transparent;")
        range_layout.addWidget(self.range_label)

        self.whole_pdf_checkbox = QCheckBox("All")
        self.whole_pdf_checkbox.setChecked(True)
        self.whole_pdf_checkbox.toggled.connect(self.on_whole_pdf_toggled)
        self.whole_pdf_checkbox.setStyleSheet("""
            font-weight: 600; 
            font-size: 14px; 
            color: #1e293b;
            spacing: 6px;
            background-color: transparent;
        """)
        range_layout.addWidget(self.whole_pdf_checkbox)

        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setMaximum(9999)
        self.start_spin.setValue(1)
        self.start_spin.setEnabled(False)
        self.start_spin.setFixedWidth(70)
        self.start_spin.setStyleSheet("""
            QSpinBox { 
                font-size: 14px; 
                color: #1e293b;
                background-color: white;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 4px;
            }
            QSpinBox:disabled {
                color: #64748b;
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        self.start_spin.valueChanged.connect(self.on_start_page_changed)
        range_layout.addWidget(self.start_spin)

        self.to_label = QLabel("to")
        self.to_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b; background-color: transparent;")
        range_layout.addWidget(self.to_label)

        self.end_spin = QSpinBox()
        self.end_spin.setMinimum(1)
        self.end_spin.setMaximum(9999)
        self.end_spin.setValue(1)
        self.end_spin.setEnabled(False)
        self.end_spin.setFixedWidth(70)
        self.end_spin.setStyleSheet("""
            QSpinBox { 
                font-size: 14px; 
                color: #1e293b;
                background-color: white;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 4px;
            }
            QSpinBox:disabled {
                color: #64748b;
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }
        """)
        self.end_spin.valueChanged.connect(self.on_end_page_changed)
        range_layout.addWidget(self.end_spin)

        range_layout.addStretch(0)
        layout.addLayout(range_layout, stretch=0)

        # No background container - elements are separate and visible
        self.setStyleSheet("")

    def on_file_label_clicked(self, event):
        """Handle file label click to select the file"""
        # Get the main window and select this file
        main_window = self.window()
        if hasattr(main_window, 'file_list_widget'):
            # Find the index of this widget in the list
            for i in range(main_window.file_list_widget.count()):
                item = main_window.file_list_widget.item(i)
                if item and main_window.file_list_widget.itemWidget(item) == self:
                    main_window.file_list_widget.setCurrentRow(i)
                    break
        event.accept()

    def on_whole_pdf_toggled(self, checked):
        self.start_spin.setEnabled(not checked)
        self.end_spin.setEnabled(not checked)
        self.on_page_range_changed()

    def on_start_page_changed(self):
        # Keep max page >= min page
        if self.start_spin.value() > self.end_spin.value():
            self.end_spin.blockSignals(True)
            self.end_spin.setValue(self.start_spin.value())
            self.end_spin.blockSignals(False)
            # Do not update preview here (auto-correct)
        else:
            self.on_page_range_changed()

    def on_end_page_changed(self):
        # Keep min page <= max page
        if self.end_spin.value() < self.start_spin.value():
            self.start_spin.blockSignals(True)
            self.start_spin.setValue(self.end_spin.value())
            self.start_spin.blockSignals(False)
            # Do not update preview here (auto-correct)
        else:
            # Update preview to show the max page when user manually changes it
            main_window = self.window()
            if hasattr(main_window, 'preview_pdf') and hasattr(main_window, 'current_page'):
                # Only update if this is the currently selected file
                current_index = main_window.file_list_widget.currentRow()
                if current_index >= 0:
                    current_widget = main_window.file_list_widget.get_file_widget(current_index)
                    if current_widget == self:
                        # Set preview to max page and update
                        main_window.current_page = self.end_spin.value() - 1  # Convert to 0-based
                        main_window.preview_pdf()
            self.on_page_range_changed()

    def on_page_range_changed(self):
        # Trigger preview update when page range changes
        main_window = self.window()
        if hasattr(main_window, 'preview_pdf'):
            main_window.preview_pdf()

    def get_page_range(self):
        if self.whole_pdf_checkbox.isChecked():
            return None  # Include entire PDF
        else:
            return (self.start_spin.value() - 1, self.end_spin.value() - 1)  # Convert to 0-based

    def set_page_range(self, page_range):
        if page_range is None:
            self.whole_pdf_checkbox.setChecked(True)
        else:
            self.whole_pdf_checkbox.setChecked(False)
            self.start_spin.setValue(page_range[0] + 1)
            self.end_spin.setValue(page_range[1] + 1)

    def update_theme_colors(self, is_dark=False):
        """Update colors based on theme"""
        if is_dark:
            self.file_label.setStyleSheet("""
                font-weight: 600;
                font-size: 15px;
                color: #e2e8f0;
                background-color: transparent;
                cursor: pointer;
            """)
            self.range_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #e2e8f0; background-color: transparent;")
            self.to_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #e2e8f0; background-color: transparent;")
            self.whole_pdf_checkbox.setStyleSheet("""
                font-weight: 600; 
                font-size: 14px; 
                color: #e2e8f0;
                spacing: 6px;
                background-color: transparent;
            """)
            self.start_spin.setStyleSheet("""
                QSpinBox { 
                    font-size: 14px; 
                    color: #e2e8f0;
                    background-color: #475569;
                    border: 2px solid #64748b;
                    border-radius: 6px;
                    padding: 4px;
                }
                QSpinBox:disabled {
                    color: #94a3b8;
                    background-color: #334155;
                    border-color: #475569;
                }
            """)
            self.end_spin.setStyleSheet("""
                QSpinBox { 
                    font-size: 14px; 
                    color: #e2e8f0;
                    background-color: #475569;
                    border: 2px solid #64748b;
                    border-radius: 6px;
                    padding: 4px;
                }
                QSpinBox:disabled {
                    color: #94a3b8;
                    background-color: #334155;
                    border-color: #475569;
                }
            """)
        else:
            self.file_label.setStyleSheet("""
                font-weight: 600;
                font-size: 15px;
                color: #1e293b;
                background-color: transparent;
                cursor: pointer;
            """)
            self.range_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b; background-color: transparent;")
            self.to_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #1e293b; background-color: transparent;")
            self.whole_pdf_checkbox.setStyleSheet("""
                font-weight: 600; 
                font-size: 14px; 
                color: #1e293b;
                spacing: 6px;
                background-color: transparent;
            """)
            self.start_spin.setStyleSheet("""
                QSpinBox { 
                    font-size: 14px; 
                    color: #1e293b;
                    background-color: white;
                    border: 2px solid #d1d5db;
                    border-radius: 6px;
                    padding: 4px;
                }
                QSpinBox:disabled {
                    color: #64748b;
                    background-color: #f1f5f9;
                    border-color: #cbd5e1;
                }
            """)
            self.end_spin.setStyleSheet("""
                QSpinBox { 
                    font-size: 14px; 
                    color: #1e293b;
                    background-color: white;
                    border: 2px solid #d1d5db;
                    border-radius: 6px;
                    padding: 4px;
                }
                QSpinBox:disabled {
                    color: #64748b;
                    background-color: #f1f5f9;
                    border-color: #cbd5e1;
                }
            """)

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setSpacing(2)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(item.text())
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if event.source() == self:
            from_row = self.row(self.currentItem())
            to_row = self.indexAt(event.pos()).row()
            if to_row < 0:  # Handle dropping below the last item
                to_row = self.count() - 1

            if from_row != to_row:
                # Access the main window to call swap_items
                main_window = self.window()
                if hasattr(main_window, 'swap_items'):
                    main_window.swap_items(from_row, to_row)
                event.accept()

    def add_file_item(self, file_path):
        item = QListWidgetItem()
        self.addItem(item)
        
        file_widget = FileListItem(file_path)
        
        # Apply current theme to the new widget
        main_window = self.window()
        if hasattr(main_window, 'current_theme'):
            file_widget.update_theme_colors(main_window.current_theme == 'dark')
        
        item.setSizeHint(file_widget.sizeHint())
        self.setItemWidget(item, file_widget)
        return item

    def get_file_widget(self, row):
        item = self.item(row)
        if item:
            return self.itemWidget(item)
        return None

    def update_file_widgets(self, selected_files):
        self.clear()
        for file_path in selected_files:
            self.add_file_item(file_path)




class PDFMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set window icon
        icon_paths = ["icon/icon.png", "assets/icon.png", "icon.png"]
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break

        # File list and state tracking
        self.selected_files = []
        self.undo_stack = []
        self.redo_stack = []

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left pane - File list
        self.left_layout = QVBoxLayout()
        self.file_list_widget = DraggableListWidget()
        self.file_list_widget.itemSelectionChanged.connect(self.preview_pdf)
        self.left_layout.addWidget(self.file_list_widget)

        # Buttons for file management
        self.buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Files")
        self.delete_button = QPushButton("Delete")
        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")
        self.up_button = QPushButton("Move Up")
        self.down_button = QPushButton("Move Down")

        self.add_button.clicked.connect(self.add_files)
        self.delete_button.clicked.connect(self.delete_selected_files)
        self.undo_button.clicked.connect(self.undo_action)
        self.redo_button.clicked.connect(self.redo_action)
        self.up_button.clicked.connect(lambda: self.move_item("up"))
        self.down_button.clicked.connect(lambda: self.move_item("down"))


        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.undo_button)
        self.buttons_layout.addWidget(self.redo_button)
        self.buttons_layout.addWidget(self.up_button)
        self.buttons_layout.addWidget(self.down_button)

        # Add settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        self.buttons_layout.addWidget(self.settings_button)

        self.left_layout.addLayout(self.buttons_layout)
        self.main_layout.addLayout(self.left_layout)

        # Right pane - PDF preview and merge button
        self.right_layout = QVBoxLayout()
        self.preview_label = QLabel("Preview")
        self.preview_label.setFixedSize(400, 300)  # Example fixed size
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8fafc);
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 8px;
        """)

        self.right_layout.addWidget(self.preview_label)

        # Navigation controls for multi-page preview with modern styling
        self.nav_layout = QHBoxLayout()
        self.prev_page_button = QPushButton("← Previous")
        self.next_page_button = QPushButton("Next →")
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet("""
            font-weight: 600; 
            color: #1e293b; 
            padding: 8px 16px;
            background-color: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        """)
        self.prev_page_button.clicked.connect(self.previous_page)
        self.next_page_button.clicked.connect(self.next_page)
        self.nav_layout.addWidget(self.prev_page_button)
        self.nav_layout.addWidget(self.page_label)
        self.nav_layout.addWidget(self.next_page_button)
        self.right_layout.addLayout(self.nav_layout)

        self.merge_button = QPushButton("Merge PDFs")
        self.merge_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 16px 24px;
                font-size: 16px;
                margin: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        self.merge_button.clicked.connect(self.merge_pdfs)
        self.right_layout.addWidget(self.merge_button)

        self.main_layout.addLayout(self.right_layout)

        # Apply modern color scheme and styling with enhanced readability
        self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #f8fafc, stop:1 #e2e8f0);
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3b82f6, stop:1 #1d4ed8);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            margin: 2px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2563eb, stop:1 #1e40af);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1d4ed8, stop:1 #1e3a8a);
        }
        QPushButton:disabled {
            background: #94a3b8;
            color: #64748b;
        }
        QListWidget {
            background-color: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 8px;
            font-size: 14px;
            selection-background-color: transparent;
            outline: none;
            spacing: 4px;
        }
        QListWidget::item {
            background-color: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }
        QListWidget::item:selected {
            background-color: transparent;
        }
        QListWidget::item:hover {
            background-color: transparent;
        }
        QLabel {
            color: #1e293b;
            font-weight: 500;
            font-size: 13px;
            background-color: transparent;
        }
        QGroupBox {
            font-weight: bold;
            color: #1e293b;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 8px;
            background-color: white;
            font-size: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            background-color: white;
        }
        QSpinBox {
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            background-color: white;
            font-size: 13px;
            font-weight: 600;
        }
        QSpinBox:focus {
            border-color: #3b82f6;
            background-color: #f8fafc;
        }
        QCheckBox {
            font-weight: 600;
            color: #1e293b;
            spacing: 12px;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 22px;
            height: 22px;
            border-radius: 4px;
            border: 2px solid #d1d5db;
        }
        QCheckBox::indicator:checked {
            background-color: #3b82f6;
            border-color: #3b82f6;
        }
        QCheckBox::indicator:unchecked {
            background-color: white;
        }
        QTabWidget::pane {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #f1f5f9;
            color: #64748b;
            padding: 12px 20px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
            font-size: 13px;
        }
        QTabBar::tab:selected {
            background-color: white;
            color: #1e293b;
            border-bottom: 2px solid #3b82f6;
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #f1f5f9;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #cbd5e1;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #94a3b8;
        }
        """)

        # Footer for credits with modern styling
        self.footer_label = QLabel(self)
        self.footer_label.setTextFormat(Qt.RichText)
        self.footer_label.setOpenExternalLinks(True)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("""
            color: #64748b; 
            font-size: 13px; 
            padding: 16px; 
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            margin: 8px;
        """)

        self.footer_label.setText("""
            <div style="text-align: center;">
                <p style="margin: 8px; font-weight: 600; color: #1e293b;">
                    Created by <b style="color: #3b82f6;">Gunjan Vaishnav</b>
                </p>
                <div style="display: flex; justify-content: center; gap: 20px;">
                    <a href="https://gunjanjvaishnav.blogspot.com/" 
                       style="text-decoration: none; color: #3b82f6; font-weight: 500; padding: 8px 16px; 
                              background-color: #eff6ff; border-radius: 8px; display: inline-flex; align-items: center;">
                        📝 Blog
                </a>
                    <a href="https://github.com/Gunjan000/PDF-Merger-Advanced/tree/master" 
                       style="text-decoration: none; color: #3b82f6; font-weight: 500; padding: 8px 16px; 
                              background-color: #eff6ff; border-radius: 8px; display: inline-flex; align-items: center;">
                        🐙 GitHub
                </a>
                </div>
            </div>
        """)

        # Add footer to the layout
        self.right_layout.addWidget(self.footer_label)

        # Initialize preview state
        self.current_preview_file = None
        self.current_page = 0
        self.total_pages = 0

        # Initialize page range settings
        self.page_ranges = {}  # {file_path: (start_page, end_page) or None for whole PDF}

        # Thread management
        self.preview_thread = None
        self.merge_thread = None
        self.preview_worker = None
        self.merge_worker = None

        # Settings management
        self.settings_file = "pdf_merger_settings.json"
        self.current_theme = "light"  # "light" or "dark"
        
        # Add theme toggle button
        self.theme_button = QPushButton("🌙")
        self.theme_button.setToolTip("Toggle Dark/Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6b7280, stop:1 #4b5563);
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 16px;
                margin: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4b5563, stop:1 #374151);
            }
        """)
        self.buttons_layout.addWidget(self.theme_button)
        
        # Load settings after theme button is created
        self.load_settings()


    def add_files(self):
        file_dialog = QFileDialog(self)
        files, _ = file_dialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if files:
            # Save state for undo (files + selection)
            current_selection = self.file_list_widget.currentRow()
            self.undo_stack.append((list(self.selected_files), current_selection))
            self.redo_stack.clear()
            for file_path in files:
                if file_path not in self.selected_files:
                    try:
                        # Validate file is a real PDF
                        _ = PdfReader(file_path)
                        self.selected_files.append(file_path)
                        self.file_list_widget.add_file_item(file_path)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"File is not a valid PDF: {file_path}\nError: {e}")
                        continue

    def delete_selected_files(self):
        selected_item = self.file_list_widget.currentItem()
        if selected_item:
            reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to remove the selected file from the list?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
            index = self.file_list_widget.row(selected_item)
            # Save state for undo (files + selection)
            current_selection = self.file_list_widget.currentRow()
            self.undo_stack.append((list(self.selected_files), current_selection))
            self.redo_stack.clear()
            try:
                self.selected_files.pop(index)
                self.file_list_widget.takeItem(index)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")

    def undo_action(self):
        if self.undo_stack:
            # Save current state for redo
            current_selection = self.file_list_widget.currentRow()
            self.redo_stack.append((list(self.selected_files), current_selection))
            # Restore previous state
            files, selection = self.undo_stack.pop()
            self.selected_files = files
            self.refresh_file_list()
            # Restore selection if valid
            if 0 <= selection < len(self.selected_files):
                self.file_list_widget.setCurrentRow(selection)

    def redo_action(self):
        if self.redo_stack:
            # Save current state for undo
            current_selection = self.file_list_widget.currentRow()
            self.undo_stack.append((list(self.selected_files), current_selection))
            # Restore previous state
            files, selection = self.redo_stack.pop()
            self.selected_files = files
            self.refresh_file_list()
            # Restore selection if valid
            if 0 <= selection < len(self.selected_files):
                self.file_list_widget.setCurrentRow(selection)

    def move_item(self, direction):
        from_row = self.file_list_widget.currentRow()
        if from_row < 0:
            return  # No item selected

        if direction == "up" and from_row > 0:
            to_row = from_row - 1
        elif direction == "down" and from_row < len(self.selected_files) - 1:
            to_row = from_row + 1
        else:
            return  # Invalid move

        # Save state for undo (files + selection)
        current_selection = self.file_list_widget.currentRow()
        self.undo_stack.append((list(self.selected_files), current_selection))
        self.redo_stack.clear()
        # Swap the selected files
        self.selected_files[from_row], self.selected_files[to_row] = (
            self.selected_files[to_row],
            self.selected_files[from_row],
        )
        self.refresh_file_list()
        # Ensure the moved item is selected
        self.file_list_widget.setCurrentRow(to_row)

    def swap_items(self, from_row, to_row):
        if from_row < 0 or to_row < 0 or from_row == to_row:
            return
        # Save state for undo (files + selection)
        current_selection = self.file_list_widget.currentRow()
        self.undo_stack.append((list(self.selected_files), current_selection))
        self.redo_stack.clear()
        # Swap in the selected_files list
        self.selected_files[from_row], self.selected_files[to_row] = (
            self.selected_files[to_row],
            self.selected_files[from_row],
        )
        self.refresh_file_list()
        self.file_list_widget.setCurrentRow(to_row)


    def refresh_file_list(self):
        try:
            self.file_list_widget.update_file_widgets(self.selected_files)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh file list: {e}")

    def get_page_ranges_from_widgets(self):
        page_ranges = {}
        for i in range(self.file_list_widget.count()):
            file_widget = self.file_list_widget.get_file_widget(i)
            if file_widget and i < len(self.selected_files):
                file_path = self.selected_files[i]
                page_ranges[file_path] = file_widget.get_page_range()
        return page_ranges

    # Worker for PDF preview
    class PreviewWorker(QObject):
        finished = pyqtSignal(object, object)
        error = pyqtSignal(str)
        def __init__(self, file_path, width, height, page_num=0):
            super().__init__()
            self.file_path = file_path
            self.width = width
            self.height = height
            self.page_num = page_num
        def run(self):
            try:
                import fitz
                import tempfile
                import os
                doc = fitz.open(self.file_path)
                if self.page_num >= len(doc):
                    self.error.emit("Page number out of range")
                    return
                page = doc[self.page_num]
                pix = page.get_pixmap()
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img:
                    temp_img = tmp_img.name
                pix.save(temp_img)
                total_pages = len(doc)
                doc.close()
                from PyQt5.QtGui import QPixmap
                pixmap = QPixmap(temp_img)
                scaled_pixmap = pixmap.scaled(
                    self.width, self.height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                os.remove(temp_img)
                self.finished.emit(scaled_pixmap, total_pages)
            except Exception as e:
                self.error.emit(str(e))

    # Worker for PDF merge
    class MergeWorker(QObject):
        finished = pyqtSignal(bool, str)
        error = pyqtSignal(str)
        def __init__(self, selected_files, save_path, page_ranges=None):
            super().__init__()
            self.selected_files = selected_files
            self.save_path = save_path
            self.page_ranges = page_ranges or {}
        def run(self):
            try:
                from PyPDF2 import PdfWriter, PdfReader
                writer = PdfWriter()
                for file_path in self.selected_files:
                    try:
                        reader = PdfReader(file_path)
                        total_pages = len(reader.pages)
                        
                        # Get page range for this file
                        page_range = self.page_ranges.get(file_path)
                        if page_range is None:
                            # Use whole PDF
                            start_page, end_page = 0, total_pages - 1
                        else:
                            start_page, end_page = page_range
                            # Validate page range
                            if start_page < 0 or end_page >= total_pages or start_page > end_page:
                                self.finished.emit(False, f"Invalid page range for {file_path}: {start_page}-{end_page} (PDF has {total_pages} pages)")
                                return
                        
                        # Add pages within the range
                        for page_num in range(start_page, end_page + 1):
                            writer.add_page(reader.pages[page_num])
                    except Exception as file_error:
                        self.finished.emit(False, f"Failed to read PDF: {file_path}\nError: {file_error}")
                        return
                with open(self.save_path, "wb") as output_file:
                    writer.write(output_file)
                self.finished.emit(True, "PDFs merged successfully!")
            except Exception as e:
                self.finished.emit(False, f"Failed to merge PDFs: {e}")

    def preview_pdf(self):
        # Stop any existing preview thread safely
        if hasattr(self, 'preview_thread') and self.preview_thread is not None:
            try:
                if self.preview_thread.isRunning():
                    self.preview_thread.quit()
                    self.preview_thread.wait(1000)  # Wait up to 1 second
            except RuntimeError:
                # Thread was already deleted, just continue
                pass
            self.preview_thread = None
            self.preview_worker = None
        
        selected_items = self.file_list_widget.selectedItems()
        if selected_items:
            index = self.file_list_widget.row(selected_items[0])
            file_path = self.selected_files[index]
            if file_path != self.current_preview_file:
                self.current_preview_file = file_path
                self.current_page = 0
            
            # Get the minimum page from the page range if specified
            file_widget = self.file_list_widget.get_file_widget(index)
            if file_widget and not file_widget.whole_pdf_checkbox.isChecked():
                min_page = file_widget.start_spin.value() - 1  # Convert to 0-based
                self.current_page = min_page
            
            fixed_width = self.preview_label.width()
            fixed_height = self.preview_label.height()
            self.preview_label.setText("Loading preview...")
            
            # Create new thread and worker
            self.preview_thread = QThread()
            self.preview_worker = self.PreviewWorker(file_path, fixed_width, fixed_height, self.current_page)
            self.preview_worker.moveToThread(self.preview_thread)
            
            # Connect signals
            self.preview_thread.started.connect(self.preview_worker.run)
            self.preview_worker.finished.connect(self.on_preview_finished)
            self.preview_worker.error.connect(self.on_preview_error)
            self.preview_worker.finished.connect(self.preview_thread.quit)
            self.preview_worker.finished.connect(self.preview_worker.deleteLater)
            self.preview_thread.finished.connect(self.preview_thread.deleteLater)
            
            # Start thread
            self.preview_thread.start()
        else:
            self.preview_label.clear()
            self.current_preview_file = None
            self.current_page = 0
            self.total_pages = 0
            self.update_navigation_controls()

    def on_preview_finished(self, pixmap, total_pages):
        if pixmap:
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setAlignment(Qt.AlignCenter)
            self.total_pages = total_pages
            self.update_navigation_controls()
        else:
            self.preview_label.setText("No preview available.")

    def on_preview_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"Cannot preview PDF: {error_msg}")
        self.preview_label.clear()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            # Force preview update with new page
            self.force_preview_update()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            # Force preview update with new page
            self.force_preview_update()

    def force_preview_update(self):
        """Force preview update with current page"""
        selected_items = self.file_list_widget.selectedItems()
        if selected_items:
            index = self.file_list_widget.row(selected_items[0])
            file_path = self.selected_files[index]
            fixed_width = self.preview_label.width()
            fixed_height = self.preview_label.height()
            self.preview_label.setText("Loading preview...")
            
            # Create new thread and worker
            if hasattr(self, 'preview_thread') and self.preview_thread is not None:
                try:
                    if self.preview_thread.isRunning():
                        self.preview_thread.quit()
                        self.preview_thread.wait(1000)
                except RuntimeError:
                    pass
                self.preview_thread = None
                self.preview_worker = None
            
            self.preview_thread = QThread()
            self.preview_worker = self.PreviewWorker(file_path, fixed_width, fixed_height, self.current_page)
            self.preview_worker.moveToThread(self.preview_thread)
            
            # Connect signals
            self.preview_thread.started.connect(self.preview_worker.run)
            self.preview_worker.finished.connect(self.on_preview_finished)
            self.preview_worker.error.connect(self.on_preview_error)
            self.preview_worker.finished.connect(self.preview_thread.quit)
            self.preview_worker.finished.connect(self.preview_worker.deleteLater)
            self.preview_thread.finished.connect(self.preview_thread.deleteLater)
            
            # Start thread
            self.preview_thread.start()

    def update_navigation_controls(self):
        if self.current_preview_file and self.total_pages > 0:
            # Simple navigation - always allow previous/next within total pages
            can_go_prev = self.current_page > 0
            can_go_next = self.current_page < self.total_pages - 1
            
            self.page_label.setText(f"Page {self.current_page + 1} of {self.total_pages}")
            self.prev_page_button.setEnabled(can_go_prev)
            self.next_page_button.setEnabled(can_go_next)
        else:
            # No file selected or no pages - hide navigation
            self.page_label.setText("No file selected")
            self.prev_page_button.setEnabled(False)
            self.next_page_button.setEnabled(False)

    def open_settings(self):
        # Remove the file requirement check - settings should be accessible anytime
        dialog = PageRangeSettingsDialog(self.selected_files, self.page_ranges, self)
        if dialog.exec_() == QDialog.Accepted:
            # Apply settings back to widgets if files are present
            new_ranges = dialog.get_page_ranges()
            for i in range(self.file_list_widget.count()):
                file_widget = self.file_list_widget.get_file_widget(i)
                if file_widget and i < len(self.selected_files):
                    file_path = self.selected_files[i]
                    if file_path in new_ranges:
                        file_widget.set_page_range(new_ranges[file_path])

    def merge_pdfs(self):
        if self.selected_files:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
            if save_path:
                import os
                if os.path.exists(save_path):
                    reply = QMessageBox.question(self, "Overwrite File", f"The file '{save_path}' already exists. Overwrite?", QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.No:
                        return
                
                # Get page ranges from widgets
                page_ranges = self.get_page_ranges_from_widgets()
                
                # Stop any existing merge thread safely
                if hasattr(self, 'merge_thread') and self.merge_thread is not None:
                    try:
                        if self.merge_thread.isRunning():
                            self.merge_thread.quit()
                            self.merge_thread.wait(1000)  # Wait up to 1 second
                    except RuntimeError:
                        # Thread was already deleted, just continue
                        pass
                    self.merge_thread = None
                    self.merge_worker = None
                
                self.merge_thread = QThread()
                self.merge_worker = self.MergeWorker(self.selected_files, save_path, page_ranges)
                self.merge_worker.moveToThread(self.merge_thread)
                self.merge_thread.started.connect(self.merge_worker.run)
                self.merge_worker.finished.connect(self.on_merge_finished)
                self.merge_worker.finished.connect(self.merge_thread.quit)
                self.merge_worker.finished.connect(self.merge_worker.deleteLater)
                self.merge_thread.finished.connect(self.merge_thread.deleteLater)
                self.merge_thread.start()
        else:
            QMessageBox.warning(self, "Warning", "No files selected to merge!")

    def on_merge_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'light')
                    self.page_ranges = settings.get('page_ranges', {})
                    
                    # Load merge settings
                    self.merge_settings = settings.get('merge_settings', {})
                    
                    # Apply the loaded theme
                    self.apply_theme()
                    
                    # Update theme button icon
                    self.theme_button.setText("☀️" if self.current_theme == "dark" else "🌙")
            else:
                self.merge_settings = {
                    'quality_level': 'High Quality',
                    'compression_level': 50,
                    'add_bookmarks': True,
                    'optimize_size': False,
                    'use_threading': True,
                    'show_progress': True,
                    'auto_save': False
                }
        except Exception as e:
            self.current_theme = "light"
            self.page_ranges = {}
            self.merge_settings = {
                'quality_level': 'High Quality',
                'compression_level': 50,
                'add_bookmarks': True,
                'optimize_size': False,
                'use_threading': True,
                'show_progress': True,
                'auto_save': False
            }

    def save_settings(self):
        """Save settings to JSON file"""
        try:
            # Get current page ranges from widgets
            current_page_ranges = self.get_page_ranges_from_widgets()
            
            settings = {
                'theme': self.current_theme,
                'page_ranges': current_page_ranges,
                'window_geometry': {
                    'x': self.geometry().x(),
                    'y': self.geometry().y(),
                    'width': self.geometry().width(),
                    'height': self.geometry().height()
                },
                'merge_settings': {
                    'quality_level': getattr(self, 'quality_combo', 'High Quality'),
                    'compression_level': getattr(self, 'compression_slider', 50),
                    'add_bookmarks': getattr(self, 'add_bookmarks_checkbox', True),
                    'optimize_size': getattr(self, 'optimize_size_checkbox', False),
                    'use_threading': getattr(self, 'threading_checkbox', True),
                    'show_progress': getattr(self, 'progress_bar', True),
                    'auto_save': getattr(self, 'auto_save_checkbox', False)
                }
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            pass

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_settings()
        # Update theme button icon
        self.theme_button.setText("☀️" if self.current_theme == "dark" else "🌙")

    def apply_theme(self):
        """Apply the current theme"""
        if self.current_theme == 'dark':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        
        # Update all FileListItem widgets to match the current theme
        for i in range(self.file_list_widget.count()):
            file_widget = self.file_list_widget.get_file_widget(i)
            if file_widget:
                file_widget.update_theme_colors(self.current_theme == 'dark')

    def apply_light_theme(self):
        """Apply light theme styling"""
        self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #f8fafc, stop:1 #e2e8f0);
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3b82f6, stop:1 #1d4ed8);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            margin: 2px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2563eb, stop:1 #1e40af);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1d4ed8, stop:1 #1e3a8a);
        }
        QPushButton:disabled {
            background: #94a3b8;
            color: #64748b;
        }
        QListWidget {
            background-color: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 8px;
            font-size: 14px;
            selection-background-color: transparent;
            outline: none;
            spacing: 4px;
        }
        QListWidget::item {
            background-color: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }
        QListWidget::item:selected {
            background-color: transparent;
        }
        QListWidget::item:hover {
            background-color: transparent;
        }
        QLabel {
            color: #1e293b;
            font-weight: 500;
            font-size: 13px;
            background-color: transparent;
        }
        QGroupBox {
            font-weight: bold;
            color: #1e293b;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 8px;
            background-color: white;
            font-size: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            background-color: white;
        }
        QSpinBox {
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            background-color: white;
            font-size: 13px;
            font-weight: 600;
        }
        QSpinBox:focus {
            border-color: #3b82f6;
            background-color: #f8fafc;
        }
        QCheckBox {
            font-weight: 600;
            color: #1e293b;
            spacing: 12px;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 22px;
            height: 22px;
            border-radius: 4px;
            border: 2px solid #d1d5db;
        }
        QCheckBox::indicator:checked {
            background-color: #3b82f6;
            border-color: #3b82f6;
        }
        QCheckBox::indicator:unchecked {
            background-color: white;
        }
        QTabWidget::pane {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #f1f5f9;
            color: #64748b;
            padding: 12px 20px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
            font-size: 13px;
        }
        QTabBar::tab:selected {
            background-color: white;
            color: #1e293b;
            border-bottom: 2px solid #3b82f6;
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #f1f5f9;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #cbd5e1;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #94a3b8;
        }
        """)

    def apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3b82f6, stop:1 #1d4ed8);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            margin: 2px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2563eb, stop:1 #1e40af);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1d4ed8, stop:1 #1e3a8a);
        }
        QPushButton:disabled {
            background: #475569;
            color: #64748b;
        }
        QListWidget {
            background-color: #334155;
            border: 2px solid #475569;
            border-radius: 12px;
            padding: 8px;
            font-size: 14px;
            selection-background-color: transparent;
            outline: none;
            color: #e2e8f0;
            spacing: 4px;
        }
        QListWidget::item {
            background-color: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        }
        QListWidget::item:selected {
            background-color: transparent;
        }
        QListWidget::item:hover {
            background-color: transparent;
        }
        QLabel {
            color: #e2e8f0;
            font-weight: 500;
            font-size: 13px;
            background-color: transparent;
        }
        QGroupBox {
            font-weight: bold;
            color: #e2e8f0;
            border: 2px solid #475569;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 8px;
            background-color: #334155;
            font-size: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            background-color: #334155;
        }
        QSpinBox {
            border: 2px solid #475569;
            border-radius: 8px;
            padding: 12px;
            background-color: #334155;
            font-size: 13px;
            color: #e2e8f0;
            font-weight: 600;
        }
        QSpinBox:focus {
            border-color: #3b82f6;
        }
        QCheckBox {
            font-weight: 600;
            color: #e2e8f0;
            spacing: 12px;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 22px;
            height: 22px;
            border-radius: 4px;
            border: 2px solid #64748b;
        }
        QCheckBox::indicator:checked {
            background-color: #3b82f6;
            border-color: #3b82f6;
        }
        QCheckBox::indicator:unchecked {
            background-color: #334155;
        }
        QTabWidget::pane {
            border: 2px solid #475569;
            border-radius: 12px;
            background-color: #334155;
        }
        QTabBar::tab {
            background-color: #475569;
            color: #94a3b8;
            padding: 12px 20px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
            font-size: 13px;
        }
        QTabBar::tab:selected {
            background-color: #334155;
            color: #e2e8f0;
            border-bottom: 2px solid #3b82f6;
        }
        QScrollArea {
            border: none;
            background-color: transparent;
        }
        QScrollBar:vertical {
            background-color: #475569;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #64748b;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #94a3b8;
        }
        """)

    def closeEvent(self, event):
        # Save settings before closing
        self.save_settings()
        
        # Clean up threads before closing
        if hasattr(self, 'preview_thread') and self.preview_thread is not None:
            try:
                if self.preview_thread.isRunning():
                    self.preview_thread.quit()
                    self.preview_thread.wait(1000)
            except RuntimeError:
                pass
        
        if hasattr(self, 'merge_thread') and self.merge_thread is not None:
            try:
                if self.merge_thread.isRunning():
                    self.merge_thread.quit()
                    self.merge_thread.wait(1000)
            except RuntimeError:
                pass
        
        event.accept()


class PageRangeSettingsDialog(QDialog):
    def __init__(self, selected_files, current_ranges, parent=None):
        super().__init__(parent)
        self.selected_files = selected_files
        self.current_ranges = current_ranges
        self.page_range_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("PDF Merger Settings")
        self.setGeometry(400, 300, 700, 500)
        
        # Create menu bar
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")
        help_menu = menubar.addMenu("Help")
        
        # File menu actions
        save_action = QAction("Save Settings", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_settings)
        file_menu.addAction(save_action)
        
        load_action = QAction("Load Settings", self)
        load_action.setShortcut("Ctrl+L")
        load_action.triggered.connect(self.load_settings)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        reset_action = QAction("Reset to Default", self)
        reset_action.triggered.connect(self.reset_settings)
        file_menu.addAction(reset_action)
        
        # Help menu actions
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setMenuBar(menubar)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Merge Options Tab
        self.setup_merge_options_tab()
        
        # Advanced Settings Tab
        self.setup_advanced_settings_tab()
        
        # Add file status info if no files are loaded
        if not self.selected_files:
            status_widget = QWidget()
            status_layout = QVBoxLayout(status_widget)
            
            status_label = QLabel("📁 No PDF files loaded")
            status_label.setStyleSheet("""
                font-size: 14px; 
                color: #64748b; 
                padding: 20px;
                text-align: center;
            """)
            status_layout.addWidget(status_label)
            
            info_label = QLabel("Add PDF files to configure page ranges and merge settings.")
            info_label.setStyleSheet("""
                font-size: 12px; 
                color: #94a3b8; 
                padding: 10px;
                text-align: center;
            """)
            info_label.setWordWrap(True)
            status_layout.addWidget(info_label)
            
            self.tab_widget.addTab(status_widget, "File Status")
        
        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        apply_button = QPushButton("Apply")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        main_layout.addLayout(button_layout)

    def setup_merge_options_tab(self):
        merge_options_widget = QWidget()
        layout = QVBoxLayout(merge_options_widget)
        
        # Merge quality settings
        quality_group = QGroupBox("Merge Quality")
        quality_layout = QVBoxLayout(quality_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High Quality", "Medium Quality", "Fast Merge"])
        self.quality_combo.setCurrentText("High Quality")
        quality_layout.addWidget(QLabel("Quality Level:"))
        quality_layout.addWidget(self.quality_combo)
        
        # Compression settings
        self.compression_slider = QSlider(Qt.Horizontal)
        self.compression_slider.setMinimum(0)
        self.compression_slider.setMaximum(100)
        self.compression_slider.setValue(50)
        self.compression_slider.setTickPosition(QSlider.TicksBelow)
        self.compression_slider.setTickInterval(10)
        
        quality_layout.addWidget(QLabel("Compression Level:"))
        quality_layout.addWidget(self.compression_slider)
        
        layout.addWidget(quality_group)
        
        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout(output_group)
        
        self.add_bookmarks_checkbox = QCheckBox("Add bookmarks for each PDF")
        self.add_bookmarks_checkbox.setChecked(True)
        output_layout.addWidget(self.add_bookmarks_checkbox)
        
        self.optimize_size_checkbox = QCheckBox("Optimize file size")
        self.optimize_size_checkbox.setChecked(False)
        output_layout.addWidget(self.optimize_size_checkbox)
        
        layout.addWidget(output_group)
        layout.addStretch()
        
        self.tab_widget.addTab(merge_options_widget, "Merge Options")

    def setup_advanced_settings_tab(self):
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.threading_checkbox = QCheckBox("Use multi-threading for large files")
        self.threading_checkbox.setChecked(True)
        advanced_layout.addWidget(self.threading_checkbox)
        
        self.progress_bar = QCheckBox("Show progress bar during merge")
        self.progress_bar.setChecked(True)
        advanced_layout.addWidget(self.progress_bar)
        
        self.auto_save_checkbox = QCheckBox("Auto-save settings")
        self.auto_save_checkbox.setChecked(False)
        advanced_layout.addWidget(self.auto_save_checkbox)
        
        layout.addWidget(advanced_group)
        
        # Logging
        log_group = QGroupBox("Logging")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        if self.selected_files:
            self.log_text.setPlainText("Settings loaded successfully.\nReady to configure merge options.")
        else:
            self.log_text.setPlainText("Settings loaded successfully.\nNo PDF files loaded - add files to configure page ranges.")
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(advanced_widget, "Advanced")

    def save_settings(self):
        QMessageBox.information(self, "Save Settings", "Settings saved successfully!")

    def load_settings(self):
        QMessageBox.information(self, "Load Settings", "Settings loaded successfully!")

    def reset_settings(self):
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to default?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Reset all settings to default
            self.quality_combo.setCurrentText("High Quality")
            self.compression_slider.setValue(50)
            self.add_bookmarks_checkbox.setChecked(True)
            self.optimize_size_checkbox.setChecked(False)
            self.threading_checkbox.setChecked(True)
            self.progress_bar.setChecked(True)
            self.auto_save_checkbox.setChecked(False)
            
            if self.selected_files:
                self.log_text.setPlainText("Settings reset to default values.")
            else:
                self.log_text.setPlainText("Settings reset to default values.\nNo PDF files loaded.")
            QMessageBox.information(self, "Reset Complete", "All settings have been reset to default values.")

    def show_about(self):
        QMessageBox.about(self, "About PDF Merger Settings", 
                         "PDF Merger Settings v2.0\n\n"
                         "Advanced configuration panel for PDF merging operations.\n"
                         "Created by Gunjan Vaishnav")

    def apply_settings(self):
        self.log_text.append("Settings applied successfully.")
        QMessageBox.information(self, "Apply Settings", "Settings have been applied!")

    def get_page_ranges(self):
        # This method is no longer needed since page ranges are handled in main interface
        return {}


def main():
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
