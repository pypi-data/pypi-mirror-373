#!/usr/bin/env python3

import sys
import os
import time
import sqlite3
import logging
import json
from pathlib import Path
from datetime import datetime
from .settings_manager import SettingsManager

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QMessageBox,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QStatusBar,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QToolBar,
    QToolButton,
    QMenu,
    QSystemTrayIcon,
    QStyle,
    QMenuBar,
    QSizePolicy,
    QSpacerItem,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QScrollArea,
    QInputDialog,
    QPlainTextEdit,
    QTextBrowser,
)
from PyQt6.QtCore import Qt, QTimer, QByteArray, QSettings, QThread, pyqtSignal, QObject

# Import custom components
from .menu import MenuBar
from PyQt6.QtGui import QIcon, QAction, QFont, QTextCursor, QPixmap, QColor, QPalette

# Import local modules
import sys
import os
from script.cardReader import CardReader
from script import cardReaderExceptions
from script.version import get_version, get_version_info
from script.language_manager import LanguageManager
from script.translations import LANGUAGES
from script.help import show_help
from script.logger import logger, setup_logging
from script.about import AboutDialog
from script.help import HelpDialog
from script.sponsor import SponsorDialog


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize logger
        self.logger = setup_logging()
        self.logger.info("MSR605 Application starting...")

        # Initialize connection state
        self.__connected = False
        self.__msr = None
        self.__db_conn = None
        self.__db_cursor = None
        self.__tracks = ["", "", ""]
        self.__coercivity = "hi"  # Default to high coercivity
        self.__auto_save_database = False
        self.__enable_duplicates = False
        self.settings_manager = None

        # Initialize language manager
        self.language_manager = LanguageManager()
        self.language_manager.language_changed.connect(self.retranslate_ui)

        # Load saved settings
        self.load_settings()

        # Set application icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "icon.png",
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Initialize the UI
        self.init_ui()

        try:
            # Initialize the database
            self.init_database()

            # Try to auto-connect to the MSR605
            QTimer.singleShot(100, self.auto_connect)

            # Apply initial translations
            self.retranslate_ui()

            self.logger.info("Application initialized successfully")
        except Exception as e:
            self.logger.error(f"Error during initialization: {str(e)}", exc_info=True)
            QMessageBox.critical(
                self,
                "Initialization Error",
                f"Failed to initialize application: {str(e)}\n\nCheck the logs for more details.",
            )
            sys.exit(1)

    def auto_connect(self):
        """Attempt to automatically connect to the MSR605 device on startup."""
        try:
            self.connect_to_msr605()
        except Exception as e:
            # Silently fail - we'll let the user manually connect if auto-connect fails
            pass

    def closeEvent(self, event):
        """Handle window close event."""
        if self.__connected and self.__msr:
            self.close_connection()

        # Save settings on close
        self.save_settings()
        event.accept()

    def save_settings(self):
        """Save application settings to JSON file."""
        self.logger.info("Saving application settings...")
        
        try:
            # Get the settings manager instance
            settings = self.settings_manager
            
            # Save application settings
            settings.set("auto_save", self.__auto_save_database)
            settings.set("allow_duplicates", self.__enable_duplicates)
            settings.set("coercivity", self.__coercivity)
            
            # Save window geometry and state
            if hasattr(self, "saveGeometry"):
                settings.set("geometry", self.saveGeometry().data().hex())
            if hasattr(self, "saveState"):
                settings.set("windowState", self.saveState().data().hex())
                
            # Save the settings to file
            settings.save()
            self.logger.info("Settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.warning(
                self, 
                "Settings Error",
                f"Failed to save settings: {str(e)}\n\nPlease check the logs for more details."
            )

    def load_settings(self):
        """Load application settings from JSON file."""
        self.logger.info("Loading application settings...")
        
        try:
            # Initialize settings manager
            self.settings_manager = SettingsManager()
            settings = self.settings_manager
            
            # Load application settings with defaults
            self.__auto_save_database = settings.get("auto_save", False)
            self.__enable_duplicates = settings.get("allow_duplicates", False)
            self.__coercivity = settings.get("coercivity", "hi")
            
            # Log loaded settings
            self.logger.info(
                f"Loaded settings - auto_save: {self.__auto_save_database}, "
                f"allow_duplicates: {self.__enable_duplicates}, "
                f"coercivity: {self.__coercivity}"
            )
            
            # Load window geometry and state if they exist
            if hasattr(self, "restoreGeometry"):
                geometry_hex = settings.get("geometry")
                if geometry_hex:
                    try:
                        self.restoreGeometry(QByteArray.fromHex(bytes(geometry_hex, 'utf-8')))
                        self.logger.info("Restored window geometry")
                    except Exception as e:
                        self.logger.error(f"Error restoring window geometry: {e}")
            
            if hasattr(self, "restoreState"):
                state_hex = settings.get("windowState")
                if state_hex:
                    try:
                        self.restoreState(QByteArray.fromHex(bytes(state_hex, 'utf-8')))
                        self.logger.info("Restored window state")
                    except Exception as e:
                        self.logger.error(f"Error restoring window state: {e}")
            
            self.logger.info("Settings loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}", exc_info=True)
            # Use default settings if loading fails
            self.__auto_save_database = False
            self.__enable_duplicates = False
            self.__coercivity = "hi"
            self.logger.info("Using default settings due to error")

        print(
            f"  Loaded settings - auto_save: {self.__auto_save_database}, "
            f"allow_duplicates: {self.__enable_duplicates}, "
            f"coercivity: {self.__coercivity}"
        )

        # Window geometry and state are already handled in the try block above
        # This is just for backward compatibility with old settings format
        if hasattr(self, "restoreGeometry") and settings.get("geometry"):
            try:
                geometry = QByteArray.fromHex(settings.get("geometry").encode())
                self.restoreGeometry(geometry)
                print(f"  Restored window geometry from old format")
            except Exception as e:
                self.logger.error(f"Error restoring window geometry from old format: {e}")
                
        if hasattr(self, "restoreState") and settings.get("windowState"):
            try:
                state = QByteArray.fromHex(settings.get("windowState").encode())
                self.restoreState(state)
                print(f"  Restored window state from old format")
            except Exception as e:
                self.logger.error(f"Error restoring window state from old format: {e}")

    def retranslate_ui(self):
        """Retranslate the UI elements based on the current language."""
        self.logger.info("Retranslating UI elements...")
        
        # Update window title with version
        version = get_version()
        self.setWindowTitle(self.language_manager.translate("app_title").format(version=version))
        
        # Update tab names
        if hasattr(self, 'tabs'):
            self.tabs.setTabText(0, self.language_manager.translate("tab_read"))
            self.tabs.setTabText(1, self.language_manager.translate("tab_write"))
            self.tabs.setTabText(2, self.language_manager.translate("tab_database"))
            self.tabs.setTabText(3, self.language_manager.translate("tab_settings"))
        
        # Update Read tab elements
        if hasattr(self, 'read_button'):
            self.read_button.setText(self.language_manager.translate("btn_read_card"))
        
        if hasattr(self, 'advanced_button'):
            self.advanced_button.setText(self.language_manager.translate("btn_advanced_functions"))
        
        if hasattr(self, 'status_label'):
            self.status_label.setText(self.language_manager.translate("lbl_status_ready"))
        
        # Update status bar message if connected
        if hasattr(self, 'statusBar') and hasattr(self, '_GUI__connected') and self._GUI__connected:
            port = getattr(self, 'port_combo', None)
            if port and hasattr(port, 'currentText'):
                self.statusBar().showMessage(
                    self.language_manager.translate("status_connected").format(port=port.currentText())
                )
        
        self.logger.info("UI retranslation complete")

        print(
            f"  Loaded settings - auto_save: {self.__auto_save_database}, "
            f"allow_duplicates: {self.__enable_duplicates}, "
            f"coercivity: {self.__coercivity}"
        )

        # Window geometry and state are already handled in the try block above
        # This is just for backward compatibility with old settings format
        if hasattr(self, "restoreGeometry") and settings.get("geometry"):
            try:
                geometry = QByteArray.fromHex(settings.get("geometry").encode())
                self.restoreGeometry(geometry)
                print(f"  Restored window geometry from old format")
            except Exception as e:
                self.logger.error(f"Error restoring window geometry from old format: {e}")
                
        if hasattr(self, "restoreState") and settings.get("windowState"):
            try:
                state = QByteArray.fromHex(settings.get("windowState").encode())
                self.restoreState(state)
                print(f"  Restored window state from old format")
            except Exception as e:
                self.logger.error(f"Error restoring window state from old format: {e}")

    def retranslate_ui(self):
        """Retranslate the UI elements based on the current language."""
        if not hasattr(self, "tabs"):
            return

        # Get translations using the translate method
        t = self.language_manager.translate

        # Set window title
        self.setWindowTitle(t("app_title", version=get_version()))

        # Update tab names if tabs exist
        if hasattr(self, "tabs"):
            for i in range(self.tabs.count()):
                tab_text = self.tabs.tabText(i)
                if tab_text in ["Read Card", t("tab_read")]:
                    self.tabs.setTabText(i, t("tab_read"))
                elif tab_text in ["Write Card", t("tab_write")]:
                    self.tabs.setTabText(i, t("tab_write"))
                elif tab_text in ["Database", t("tab_database")]:
                    self.tabs.setTabText(i, t("tab_database"))
                elif tab_text in ["Settings", t("tab_settings")]:
                    self.tabs.setTabText(i, t("tab_settings"))

        # Update status bar
        if hasattr(self, "statusBar") and self.statusBar():
            self.statusBar().showMessage(t("lbl_status_ready"))

        # Update buttons if they exist
        if hasattr(self, "read_button"):
            self.read_button.setText(t("btn_read_card"))
        if hasattr(self, "write_button"):
            self.write_button.setText(t("btn_write_card"))
        if hasattr(self, "clear_button"):
            self.clear_button.setText(t("btn_clear_tracks"))
        if hasattr(self, "refresh_button"):
            self.refresh_button.setText(t("btn_refresh"))
        if hasattr(self, "export_button"):
            self.export_button.setText(t("menu_export_csv"))
        if hasattr(self, "connect_button"):
            self.connect_button.setText(t("btn_connect"))

        # Update menu bar
        if hasattr(self, "menuBar") and self.menuBar():
            self.menuBar().update_menu_states()

    def reset(self):
        """Reset the MSR605 device."""
        if not self.__connected or self.__msr is None:
            return

        try:
            self.__msr.reset()
            # Set the coercivity after reset
            if self.__coercivity == "hi":
                self.__msr.set_hi_coercivity()
            else:
                self.__msr.set_lo_coercivity()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset MSR605: {str(e)}")

    def show_sponsor(self):
        """Show the sponsor dialog."""
        try:
            sponsor_dialog = SponsorDialog(self, self.language_manager)
            sponsor_dialog.exec()
        except ImportError:
            QMessageBox.critical(
                self,
                "Import Error",
                "Failed to import the sponsor module. Make sure it's installed correctly.",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to show sponsor dialog: {str(e)}"
            )

    def check_for_updates(self):
        """Check for application updates."""
        try:
            from script.updates import check_for_updates

            check_for_updates(self)
        except ImportError:
            QMessageBox.critical(
                self,
                "Import Error",
                "Failed to import the updates module. Make sure it's installed correctly.",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to check for updates: {str(e)}"
            )

    def init_ui(self):
        """Initialize the main UI components."""
        # Set window properties
        self.setWindowTitle(f"MSR605 Card Reader/Writer {get_version()}")
        self.setMinimumSize(800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.statusBar().showMessage("Ready")

        # Create main tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Add tabs
        self.setup_read_tab()
        self.setup_write_tab()
        self.setup_database_tab()
        self.setup_settings_tab()

    def view_database(self):
        """Display the card database in a new window."""
        # Create a new window
        self.db_window = QDialog(self)
        self.db_window.setWindowTitle("Card Database")
        self.db_window.setMinimumSize(800, 600)

        # Create a table widget to display the database
        layout = QVBoxLayout()
        self.db_table = QTableWidget()
        self.db_table.setColumnCount(6)
        self.db_table.setHorizontalHeaderLabels(
            ["ID", "Date", "Track 1", "Track 2", "Track 3", "Notes"]
        )

        # Set column widths
        self.db_table.setColumnWidth(0, 50)  # ID
        self.db_table.setColumnWidth(1, 150)  # Date
        self.db_table.setColumnWidth(2, 150)  # Track 1
        self.db_table.setColumnWidth(3, 150)  # Track 2
        self.db_table.setColumnWidth(4, 150)  # Track 3
        self.db_table.setColumnWidth(5, 100)  # Notes

        # Populate the table with data from the database
        try:
            self.__db_cursor.execute(
                """
                SELECT id, datetime(timestamp, 'localtime') as date, 
                       track1, track2, track3, notes 
                FROM cards 
                ORDER BY timestamp DESC
            """
            )

            rows = self.__db_cursor.fetchall()
            self.db_table.setRowCount(len(rows))

            for row_idx, row in enumerate(rows):
                for col_idx, col in enumerate(row):
                    item = QTableWidgetItem(str(col) if col is not None else "")
                    item.setFlags(
                        item.flags() & ~Qt.ItemFlag.ItemIsEditable
                    )  # Make cells read-only
                    self.db_table.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.critical(
                self, "Database Error", f"Failed to load database: {str(e)}"
            )
            return

        # Add search functionality
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in all fields...")
        self.search_input.textChanged.connect(self.filter_database)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.db_window.reject)

        # Add widgets to layout
        layout.addLayout(search_layout)
        layout.addWidget(self.db_table)
        layout.addWidget(button_box)

        self.db_window.setLayout(layout)
        self.db_window.exec()

    def filter_database(self):
        """Filter the database table based on search text."""
        if not hasattr(self, "db_table") or not hasattr(self, "search_input"):
            return

        search_text = self.search_input.text().lower()

        for row in range(self.db_table.rowCount()):
            row_matches = False
            for col in range(self.db_table.columnCount()):
                item = self.db_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_matches = True
                    break

            self.db_table.setRowHidden(row, not row_matches)

    def export_database_to_csv(self):
        """Export the card database to a CSV file."""
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Database to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return  # User cancelled

        # Ensure the file has a .csv extension
        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        try:
            # Get all records from the database
            self.__db_cursor.execute(
                """
                SELECT datetime(timestamp, 'localtime') as date, 
                       track1, track2, track3, notes 
                FROM cards 
                ORDER BY timestamp DESC
            """
            )

            records = self.__db_cursor.fetchall()

            # Write to CSV file
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(["Date", "Track 1", "Track 2", "Track 3", "Notes"])
                # Write data
                writer.writerows(records)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Successfully exported {len(records)} records to:\n{file_path}",
            )

        except Exception as e:
            QMessageBox.critical(
                "Export Failed", f"Failed to export database: {str(e)}"
            )

    def show_about(self):
        """Show the About dialog with application information."""
        about_dialog = AboutDialog(self, self.language_manager)
        about_dialog.exec()

    def show_help(self):
        """Display help information in a dialog using HelpDialog."""
        help_dialog = HelpDialog(self, self.language_manager)
        help_dialog.exec()

    def setup_write_tab(self):
        """Set up the Write tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add track inputs
        tracks_group = QGroupBox("Track Data")
        tracks_layout = QVBoxLayout()

        self.track_inputs = []
        for i in range(3):
            group = QGroupBox(f"Track {i+1}")
            group_layout = QVBoxLayout()

            text_edit = QTextEdit()
            text_edit.setMaximumHeight(60)
            self.track_inputs.append(text_edit)

            group_layout.addWidget(text_edit)
            group.setLayout(group_layout)
            tracks_layout.addWidget(group)

        tracks_group.setLayout(tracks_layout)
        layout.addWidget(tracks_group)

        # Add buttons
        button_layout = QHBoxLayout()

        self.write_button = QPushButton("Write Card")
        self.write_button.clicked.connect(self.write_card)
        button_layout.addWidget(self.write_button)

        self.clear_button = QPushButton("Clear Tracks")
        self.clear_button.clicked.connect(self.clear_tracks)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Add status label
        self.write_status_label = QLabel("Ready to write card...")
        layout.addWidget(self.write_status_label)

        self.tabs.addTab(tab, "Write Card")

    def setup_database_tab(self):
        """Set up the Database tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add database table
        self.db_table = QTableWidget()
        self.db_table.setColumnCount(5)
        self.db_table.setHorizontalHeaderLabels(
            ["Date", "Track 1", "Track 2", "Track 3", "Notes"]
        )
        self.db_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.db_search = QLineEdit()
        self.db_search.setPlaceholderText("Search database...")
        self.db_search.textChanged.connect(self.filter_database)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.db_search)

        # Add buttons
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_database)
        button_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_database_to_csv)
        button_layout.addWidget(self.export_button)

        # Add widgets to layout
        layout.addLayout(search_layout)
        layout.addWidget(self.db_table)
        layout.addLayout(button_layout)

        self.tabs.addTab(tab, "Database")

        # Load initial data
        self.refresh_database()

    def setup_settings_tab(self):
        """Set up the Settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Connection settings
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QFormLayout()

        self.port_combo = QComboBox()
        self.refresh_ports()

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)

        conn_layout.addRow("Port:", self.port_combo)
        conn_layout.addRow(self.connect_button)
        conn_group.setLayout(conn_layout)

        # Coercivity settings
        coercivity_group = QGroupBox("Coercivity")
        coercivity_layout = QVBoxLayout()

        self.hi_coercivity = QRadioButton("High Coercivity (300 Oe)")
        self.lo_coercivity = QRadioButton("Low Coercivity (300 Oe)")

        # Default to high coercivity
        self.hi_coercivity.setChecked(True)

        self.hi_coercivity.toggled.connect(
            lambda: self.set_coercivity(
                "hi" if self.hi_coercivity.isChecked() else "lo"
            )
        )

        coercivity_layout.addWidget(self.hi_coercivity)
        coercivity_layout.addWidget(self.lo_coercivity)
        coercivity_group.setLayout(coercivity_layout)

        # Database settings
        db_group = QGroupBox("Database Settings")
        db_layout = QVBoxLayout()

        self.auto_save = QCheckBox("Auto-save read cards to database")
        self.auto_save.setChecked(self.__auto_save_database)
        self.auto_save.toggled.connect(
            lambda checked: setattr(self, "_GUI__auto_save_database", checked)
        )

        self.allow_duplicates = QCheckBox("Allow duplicate cards in database")
        self.allow_duplicates.setChecked(self.__enable_duplicates)
        self.allow_duplicates.toggled.connect(
            lambda checked: setattr(self, "_GUI__enable_duplicates", checked)
        )

        db_layout.addWidget(self.auto_save)
        db_layout.addWidget(self.allow_duplicates)
        db_group.setLayout(db_layout)

        # Add all groups to main layout
        layout.addWidget(conn_group)
        layout.addWidget(coercivity_group)
        layout.addWidget(db_group)
        layout.addStretch()

        self.tabs.addTab(tab, "Settings")

    def setup_read_tab(self):
        """Set up the Read tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add track displays
        tracks_group = QGroupBox("Track Data")
        tracks_layout = QVBoxLayout()

        self.track_displays = []
        for i in range(3):
            group = QGroupBox(f"Track {i+1}")
            group_layout = QVBoxLayout()

            text_edit = QPlainTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setMaximumHeight(60)
            self.track_displays.append(text_edit)

            group_layout.addWidget(text_edit)
            group.setLayout(group_layout)
            tracks_layout.addWidget(group)

        tracks_group.setLayout(tracks_layout)
        layout.addWidget(tracks_group)

        # Add buttons layout
        button_layout = QHBoxLayout()

        # Add read button
        self.read_button = QPushButton(self.language_manager.translate("btn_read_card"))
        self.read_button.clicked.connect(self.read_card)
        button_layout.addWidget(self.read_button)

        # Add Advanced Functions button
        self.advanced_button = QPushButton(self.language_manager.translate("btn_advanced_functions"))
        self.advanced_button.clicked.connect(self.show_advanced_functions)
        button_layout.addWidget(self.advanced_button)

        layout.addLayout(button_layout)

        # Add status label
        self.status_label = QLabel("Ready to read card...")
        layout.addWidget(self.status_label)

        self.tabs.addTab(tab, "Read Card")

    def create_menu_bar(self):
        """Create the application menu bar using the custom MenuBar class."""
        # Create and set the custom menu bar
        menubar = MenuBar(self)
        self.setMenuBar(menubar)
        return menubar

    def refresh_ports(self):
        """Refresh the list of available COM ports."""
        self.port_combo.clear()
        ports = self.get_available_ports()
        if ports:
            self.port_combo.addItems(ports)
        else:
            self.port_combo.addItem("No ports found")

    def get_available_ports(self):
        """Get a list of available COM ports."""
        import serial.tools.list_ports

        return [port.device for port in serial.tools.list_ports.comports()]

    def toggle_connection(self):
        """Toggle connection to the MSR605 device."""
        if self.__connected:
            self.close_connection()
        else:
            self.connect_to_msr605()

    def connect_to_msr605(self):
        """Connect to the MSR605 device."""
        if self.__connected:
            return

        port = self.port_combo.currentText()
        if not port or port == "No ports found":
            QMessageBox.critical(
                self, "Error", "No port selected or no ports available"
            )
            return

        try:
            self.__msr = CardReader(port)
            self.__msr.connect()
            self.__connected = True
            self.connect_button.setText("Disconnect")
            self.statusBar().showMessage(f"Connected to {port}")

            # Set the coercivity
            if self.__coercivity == "hi":
                self.__msr.set_hi_co()
            else:
                self.__msr.set_lo_co()

        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", f"Failed to connect to {port}: {str(e)}"
            )

    def close_connection(self):
        """Close the connection to the MSR605 device."""
        if not self.__connected or self.__msr is None:
            return

        try:
            self.__msr.disconnect()
        except:
            pass

        self.__connected = False
        self.connect_button.setText("Connect")
        self.statusBar().showMessage("Disconnected")

    def set_coercivity(self, coercivity):
        """Set the coercivity of the MSR605 device."""
        if not self.__connected or self.__msr is None:
            return

        try:
            if coercivity == "hi":
                self.__msr.set_hi_coercivity()
            else:
                self.__msr.set_lo_coercivity()

            self.__coercivity = coercivity
            self.statusBar().showMessage(f"Set to {coercivity} coercivity")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set coercivity: {str(e)}")

    def show_advanced_functions(self):
        """Show the advanced functions dialog."""
        try:
            from .advanced_functions import AdvancedFunctionsWidget
            
            # Create and show the advanced functions dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Advanced Functions")
            dialog.setMinimumSize(800, 600)
            
            # Create the advanced functions widget with language manager
            advanced_widget = AdvancedFunctionsWidget(
                parent=dialog, 
                tracks=self.__tracks,
                language_manager=self.language_manager
            )
            
            # Connect the read_card_requested signal to the read_card method
            advanced_widget.read_card_requested.connect(self.read_card)
            
            # Set up the layout
            layout = QVBoxLayout(dialog)
            layout.addWidget(advanced_widget)
            
            # Add close button
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec()
            
        except ImportError as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to load advanced functions: {str(e)}\n\nMake sure all required dependencies are installed."
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"An error occurred: {str(e)}"
            )

    def read_card(self):
        """Read data from a magnetic stripe card."""
        if not self.__connected or self.__msr is None:
            QMessageBox.warning(
                self, "Not Connected", "Please connect to the MSR605 first"
            )
            return

        self.status_label.setText("Reading card...")
        QApplication.processEvents()  # Update the UI

        try:
            # Read the card using the correct method
            result = self.__msr.read_card()
            tracks = result.get('tracks', ["", "", ""])

            # Update the track displays
            for i in range(3):
                if i < len(tracks) and tracks[i]:
                    self.track_displays[i].setPlainText(tracks[i])
                    self.__tracks[i] = tracks[i]
                else:
                    self.track_displays[i].clear()
                    self.__tracks[i] = ""

            # Auto-save to database if enabled
            if self.__auto_save_database and any(self.__tracks):
                self.save_to_database()

            self.status_label.setText("Card read successfully!")

        except Exception as e:
            self.status_label.setText("Error reading card")
            QMessageBox.critical(self, "Read Error", f"Failed to read card: {str(e)}")
            self.logger.error(f"Error reading card: {str(e)}", exc_info=True)

    def write_card(self):
        """Write data to a magnetic stripe card."""
        if not self.__connected or self.__msr is None:
            QMessageBox.warning(
                self, "Not Connected", "Please connect to the MSR605 first"
            )
            return

        # Get track data from input fields
        tracks = [text_edit.toPlainText() for text_edit in self.track_inputs]

        if not any(tracks):
            QMessageBox.warning(
                self, "No Data", "Please enter data for at least one track"
            )
            return

        self.write_status_label.setText("Writing to card...")
        QApplication.processEvents()  # Update the UI

        try:
            # Write to the card
            self.__msr.write_tracks(*tracks)

            # Update the track displays to show what was written
            for i in range(3):
                if i < len(tracks) and tracks[i]:
                    self.track_displays[i].setPlainText(tracks[i])
                    self.__tracks[i] = tracks[i]

            self.write_status_label.setText("Card written successfully!")

        except Exception as e:
            self.write_status_label.setText("Error writing to card")
            QMessageBox.critical(
                self, "Write Error", f"Failed to write to card: {str(e)}"
            )

    def clear_tracks(self):
        """Clear all track input fields."""
        for text_edit in self.track_inputs:
            text_edit.clear()

        for text_edit in self.track_displays:
            text_edit.clear()

        self.__tracks = ["", "", ""]
        self.write_status_label.setText("Tracks cleared")

    def save_to_database(self):
        """Save the current track data to the database."""
        # Check if there's any track data to save
        if not any(self.__tracks):
            print("No track data to save")
            return False

        # Ensure database is initialized
        if not hasattr(self, "_GUI__db_cursor") or self.__db_cursor is None:
            print("Database not initialized. Initializing...")
            if not self.init_database():
                QMessageBox.critical(
                    self,
                    "Database Error",
                    "Failed to initialize database. Cannot save card data.",
                )
                return False

        try:
            # Check for duplicates if needed
            if not self.__enable_duplicates:
                try:
                    self.__db_cursor.execute(
                        "SELECT COUNT(*) FROM cards WHERE track1=? AND track2=? AND track3=?",
                        (
                            self.__tracks[0] or None,
                            self.__tracks[1] or None,
                            self.__tracks[2] or None,
                        ),
                    )
                    if self.__db_cursor.fetchone()[0] > 0:
                        print("Duplicate card found and duplicates are not allowed")
                        return False  # Duplicate found and not allowed
                except sqlite3.Error as e:
                    print(f"Error checking for duplicates: {e}")
                    # Continue with save even if duplicate check fails

            # Insert the new record
            try:
                self.__db_cursor.execute(
                    """
                    INSERT INTO cards (track1, track2, track3, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                    """,
                    (
                        self.__tracks[0] or None,
                        self.__tracks[1] or None,
                        self.__tracks[2] or None,
                    ),
                )
                self.__db_conn.commit()
                print("Successfully saved card data to database")

                # Refresh the database view if it's open
                if (
                    hasattr(self, "db_table")
                    and hasattr(self.db_table, "isVisible")
                    and self.db_table.isVisible()
                ):
                    self.refresh_database()

                return True

            except sqlite3.Error as e:
                error_msg = f"Failed to save to database: {str(e)}"
                print(error_msg)
                QMessageBox.critical(self, "Database Error", error_msg)
                return False

        except Exception as e:
            error_msg = f"Unexpected error saving to database: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            return False

    def refresh_database(self):
        """Refresh the database table with current data."""
        if not hasattr(self, "_GUI__db_cursor") or self.__db_cursor is None:
            print("Database cursor not available. Reinitializing database...")
            if not self.init_database():
                QMessageBox.critical(
                    self,
                    "Database Error",
                    "Failed to initialize database. Please check the logs for details.",
                )
                return

        try:
            # Get the search text
            search_text = (
                self.db_search.text().lower() if hasattr(self, "db_search") else ""
            )

            # Build the query
            query = """
                SELECT 
                    datetime(timestamp, 'localtime') as date,
                    track1, track2, track3, notes 
                FROM cards
            """

            params = []

            if search_text:
                query += " WHERE "
                conditions = []
                for col in ["track1", "track2", "track3", "notes"]:
                    conditions.append(f"{col} LIKE ?")
                    params.append(f"%{search_text}%")
                query += " OR ".join(conditions)

            query += " ORDER BY timestamp DESC"

            # Execute the query
            try:
                self.__db_cursor.execute(query, params)
                rows = self.__db_cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Database query error: {e}")
                QMessageBox.critical(
                    self, "Database Error", f"Failed to execute query: {str(e)}"
                )
                return

            # Update the table if it exists
            if not hasattr(self, "db_table"):
                print("db_table not found. Database tab may not be initialized.")
                return

            try:
                self.db_table.setRowCount(len(rows))
                for row_idx, row in enumerate(rows):
                    for col_idx, col in enumerate(row):
                        item = QTableWidgetItem(str(col) if col is not None else "")
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.db_table.setItem(row_idx, col_idx, item)

                # Resize columns to fit content
                self.db_table.resizeColumnsToContents()

            except Exception as e:
                print(f"Error updating table: {e}")
                QMessageBox.critical(
                    self, "UI Error", f"Failed to update database view: {str(e)}"
                )

        except Exception as e:
            error_msg = f"Unexpected error refreshing database: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def init_database(self):
        """Initialize the SQLite database."""
        try:
            # Create or connect to the database
            db_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "card_database.db")
            )
            print(f"Initializing database at: {db_path}")

            # Ensure the directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            self.__db_conn = sqlite3.connect(db_path)
            self.__db_cursor = self.__db_conn.cursor()

            # Enable foreign key support
            self.__db_cursor.execute("PRAGMA foreign_keys = ON")

            # Create the cards table if it doesn't exist
            self.__db_cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track1 TEXT,
                    track2 TEXT,
                    track3 TEXT,
                    notes TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            self.__db_conn.commit()
            print("Database initialized successfully")
            return True

        except Exception as e:
            error_msg = f"Failed to initialize database: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Database Error", error_msg)
            self.__db_conn = None
            self.__db_cursor = None
            return False
