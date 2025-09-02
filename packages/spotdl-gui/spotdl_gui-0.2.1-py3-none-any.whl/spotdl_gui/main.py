import sys
import subprocess
import threading
import os
import datetime
import configparser
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTextEdit, QProgressBar, QMessageBox, QFileDialog,
                             QGroupBox, QRadioButton, QButtonGroup, QCheckBox, QAction, QComboBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QTextCharFormat, QTextCursor

class StreamEmitter(QObject):
    new_output = pyqtSignal(str, str)  # Now accepts both text and color type

class SpotDLGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize is_bundled FIRST
        self.is_bundled = getattr(sys, 'frozen', False)
        self.process = None
        self.emitter = StreamEmitter()
        self.emitter.new_output.connect(self.append_output)
        self.download_count = 0  # Initialize download counter
        self.dark_mode = False  # Track dark mode state
        self.log_file = None  # Track current log file
        self.log_enabled = True  # Enable logging by default
        
        # Don't set log_dir to default here - let load_settings handle it
        self.log_dir = None
        self.default_music_dir = self.get_windows_music_folder()

        self.initUI()
        # Load settings before setting up logging
        self.load_settings()
        # Now connect the signals to save any FUTURE changes
        self.connect_settings_signals()
        # Apply dark mode if enabled
        if self.dark_mode:
            self.apply_dark_mode()
        # Now setup logging AFTER settings are loaded
        self.setup_logging()

    def get_config_path(self):
        """Get the path to the config file"""
        if self.is_bundled:
            # For bundled apps, use the executable directory
            base_dir = os.path.dirname(sys.executable)
        else:
            # For development, use the script directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_dir, "spotdl_gui_config.ini")

    def load_settings(self):
        """Load settings from config file"""
        config_path = self.get_config_path()
        config = configparser.ConfigParser()
        
        # Set default log directory first
        default_log_dir = os.path.join(os.getcwd(), "spotdl_gui-logs")
        self.log_dir = default_log_dir
        
        if not os.path.exists(config_path):
            self.append_output("No existing config file found. Using default settings.", "info")
            return
        
        try:
            config.read(config_path, encoding='utf-8')
            
            # General settings
            if config.has_section('General'):
                if config.has_option('General', 'dark_mode'):
                    dark_mode = config.getboolean('General', 'dark_mode')
                    self.dark_mode = dark_mode
                    if hasattr(self, 'dark_mode_action'):
                        self.dark_mode_action.setChecked(dark_mode)
                
                if config.has_option('General', 'logging_enabled'):
                    self.log_enabled = config.getboolean('General', 'logging_enabled')
                    if hasattr(self, 'logging_action'):
                        self.logging_action.setChecked(self.log_enabled)
            
            # Directory settings - THIS IS THE CRITICAL FIX
            if config.has_section('Directories'):
                if config.has_option('Directories', 'download_dir'):
                    download_dir = config.get('Directories', 'download_dir')
                    if os.path.exists(download_dir):
                        self.dir_input.setText(download_dir)
                
                if config.has_option('Directories', 'log_dir'):
                    log_dir = config.get('Directories', 'log_dir')
                    # Always use the config value if it exists, even if directory doesn't exist yet
                    self.log_dir = log_dir
            
            # Audio settings
            if config.has_section('Audio'):
                if config.has_option('Audio', 'format'):
                    format_text = config.get('Audio', 'format')
                    format_index = self.format_combo.findText(format_text)
                    if format_index >= 0:
                        self.format_combo.setCurrentIndex(format_index)
                
                if config.has_option('Audio', 'bitrate'):
                    bitrate_text = config.get('Audio', 'bitrate')
                    bitrate_index = self.bitrate_combo.findText(bitrate_text)
                    if bitrate_index >= 0:
                        self.bitrate_combo.setCurrentIndex(bitrate_index)
            
            # Folder structure
            if config.has_section('Structure'):
                if config.has_option('Structure', 'folder_structure'):
                    structure = config.get('Structure', 'folder_structure')
                    if structure == "artist_album_song":
                        self.artist_album_song.setChecked(True)
                    elif structure == "artist_song":
                        self.artist_song.setChecked(True)
                    elif structure == "song_only":
                        self.song_only.setChecked(True)
            
            # Window geometry
            if config.has_section('Window'):
                if config.has_option('Window', 'geometry'):
                    try:
                        geometry_data = json.loads(config.get('Window', 'geometry'))
                        if len(geometry_data) == 4:
                            self.setGeometry(*geometry_data)
                    except:
                        pass
            
            self.append_output("Settings loaded from config file.", "info")
            
        except Exception as e:
            self.append_output(f"Error loading settings: {str(e)}", "error")

    def save_settings(self):
        """Save settings to config file"""
        config = configparser.ConfigParser()
        
        # General settings
        config['General'] = {
            'dark_mode': str(self.dark_mode),
            'logging_enabled': str(self.log_enabled)
        }
        
        # Directory settings
        config['Directories'] = {
            'download_dir': self.dir_input.text(),
            'log_dir': self.log_dir
        }
        
        # Audio settings
        config['Audio'] = {
            'format': self.format_combo.currentText(),
            'bitrate': self.bitrate_combo.currentText()
        }
        
        # Folder structure
        structure = "artist_album_song"
        if self.artist_song.isChecked():
            structure = "artist_song"
        elif self.song_only.isChecked():
            structure = "song_only"
        
        config['Structure'] = {
            'folder_structure': structure
        }
        
        # Window geometry
        config['Window'] = {
            'geometry': json.dumps([
                self.geometry().x(),
                self.geometry().y(),
                self.geometry().width(),
                self.geometry().height()
            ])
        }
        
        try:
            config_path = self.get_config_path()
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            self.append_output("Settings saved successfully.", "info")
            
        except Exception as e:
            self.append_output(f"Error saving settings: {str(e)}", "error")

    def closeEvent(self, event):
        """Save settings when the application closes"""
        self.save_settings()
        event.accept()

    def connect_settings_signals(self):
        """Connect signals for settings that should auto-save"""
        self.format_combo.currentTextChanged.connect(self.save_settings)
        self.bitrate_combo.currentTextChanged.connect(self.save_settings)
        self.artist_album_song.toggled.connect(self.save_settings)
        self.artist_song.toggled.connect(self.save_settings)
        self.song_only.toggled.connect(self.save_settings)

    def setup_logging(self):
        """Setup logging directory and create a new log file"""
        try:
            # Debug output to see which directory is being used
            #self.append_output(f"Setting up logging in directory: {self.log_dir}", "info")
            
            # Create logs directory if it doesn't exist
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
                self.append_output(f"Created log directory: {self.log_dir}", "info")
            
            # Create a new log file with timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            log_filename = f"console-log {timestamp}.txt"
            self.log_file = os.path.join(self.log_dir, log_filename)
            
            # Write initial log header
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"console-log - {timestamp}\n")
                f.write(f"Log directory: {self.log_dir}\n")
                f.write("=" * 50 + "\n\n")
            
            self.append_output(f"Logging to: {self.log_file}", "info")
            return True
            
        except Exception as e:
            self.append_output(f"Error creating log file: {str(e)}", "error")
            self.log_enabled = False
            return False

    def select_log_directory(self):
        """Allow user to select where log files are stored"""
        directory = QFileDialog.getExistingDirectory(
            self,
            'Select Log Directory',
            self.log_dir  # Start in current log directory
        )
        if directory:
            self.log_dir = directory
            self.append_output(f"Log directory set to: {self.log_dir}", "info")
            
            # Reinitialize logging with new directory
            if self.log_enabled:
                self.setup_logging()
            
            # Save settings after directory change
            self.save_settings()

    def open_log_directory(self):
        """Open the log directory in file explorer"""
        if not os.path.exists(self.log_dir):
            QMessageBox.warning(self, 'Directory Not Found', 'The log directory does not exist.')
            self.append_output(f"Error: Log directory not found: {self.log_dir}", "error")
            return

        try:
            # Use os.startfile on Windows
            if sys.platform == "win32":
                os.startfile(self.log_dir)
            # Use 'open' on macOS
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.log_dir])
            # Use 'xdg-open' or 'gnome-open' on Linux
            else:
                try:
                    subprocess.Popen(["xdg-open", self.log_dir])
                except FileNotFoundError:
                    subprocess.Popen(["gnome-open", self.log_dir])
            
            self.append_output(f"Opened log directory: {self.log_dir}", "info")

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not open log directory: {str(e)}')
            self.append_output(f"Error: Could not open log directory: {str(e)}", "error")

    def get_icon_path(self):
        """
        Get the correct path to the icon.ico file, whether running from source,
        as an installed package, or as a bundled executable.
        """
        base_path = None
        
        # 1. First, check if we're a bundled executable (PyInstaller)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            # 2. If not bundled, we're running from source or installed via pip
            # Try to get the package directory using importlib
            try:
                import importlib.resources as pkg_resources
                with pkg_resources.path('spotdl_gui', '') as package_path:
                    base_path = str(package_path)
            except (ImportError, FileNotFoundError):
                # Fallback to current file directory
                base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the icon
        icon_path = os.path.join(base_path, 'icon.ico')
        
        # Check if the icon exists at the calculated path
        if os.path.exists(icon_path):
            return icon_path
        else:
            # Final fallback: look in the current working directory
            cwd_icon_path = os.path.join(os.getcwd(), 'icon.ico')
            if os.path.exists(cwd_icon_path):
                return cwd_icon_path
        
        # Return None if no icon found anywhere
        return None

    def initUI(self):
        self.setWindowTitle('SpotDL GUI - 0.2.0')
        self.setGeometry(100, 100, 800, 700)  # Increased height for counter

        # Set application icon if available
        try:
            icon_path = self.get_icon_path()
            if icon_path:
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Could not load icon: {e}")

        # Create menu bar
        self.create_menu()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # URL input
        url_group = QGroupBox("Spotify URL")
        url_layout = QVBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('Enter Spotify song, album, or playlist URL')
        url_layout.addWidget(self.url_input)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Output directory selection
        dir_group = QGroupBox("Output Directory")
        dir_layout = QVBoxLayout()

        dir_control_layout = QHBoxLayout()
        self.dir_input = QLineEdit()

        # Set default to Windows Music folder
        self.dir_input.setText(self.default_music_dir)
        self.dir_input.setPlaceholderText('Select download directory')

        self.dir_button = QPushButton('Browse')
        self.dir_button.clicked.connect(self.select_directory)

        # Add reset to default button
        self.reset_dir_button = QPushButton('Default')
        self.reset_dir_button.clicked.connect(self.reset_to_default_directory)
        self.reset_dir_button.setToolTip('Reset to default Windows Music folder')

        # Add open folder button
        self.open_dir_button = QPushButton('Open Folder')
        self.open_dir_button.clicked.connect(self.open_download_directory)
        self.open_dir_button.setToolTip('Open the selected download folder')

        dir_control_layout.addWidget(self.dir_input)
        dir_control_layout.addWidget(self.dir_button)
        dir_control_layout.addWidget(self.reset_dir_button)
        dir_control_layout.addWidget(self.open_dir_button)
        dir_layout.addLayout(dir_control_layout)
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)

        # Options group
        options_group = QGroupBox("Download Options")
        options_layout = QVBoxLayout()

        # Audio format and bitrate selection
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QHBoxLayout()
        
        # Format selection
        format_widget = QWidget()
        format_layout = QVBoxLayout(format_widget)
        format_label = QLabel('Format:')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['mp3', 'wav', 'flac'])
        self.format_combo.setCurrentIndex(0)  # Default to mp3
        self.format_combo.setToolTip('Select the audio format for downloaded files')
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        
        # Bitrate selection
        bitrate_widget = QWidget()
        bitrate_layout = QVBoxLayout(bitrate_widget)
        bitrate_label = QLabel('Bitrate:')
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(['auto', 'disable', '8k', '16k', '24k', '32k', '40k', '48k', '64k', '80k', '96k', '112k', '128k', '160k', '192k', '224k', '256k', '320k'])
        self.bitrate_combo.setCurrentIndex(0)
        self.bitrate_combo.setToolTip('Select the audio bitrate for downloaded files')
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bitrate_combo)
        
        # Add format and bitrate widgets side by side
        audio_layout.addWidget(format_widget)
        audio_layout.addWidget(bitrate_widget)
        audio_group.setLayout(audio_layout)
        options_layout.addWidget(audio_group)

        # Folder structure options
        structure_group = QGroupBox("Folder Structure")
        structure_layout = QVBoxLayout()

        self.structure_group = QButtonGroup(self)

        # Use forward slashes in the display text but keep the actual template with forward slashes
        self.artist_album_song = QRadioButton("Artist/Album/Song")
        self.artist_album_song.setChecked(True)
        self.structure_group.addButton(self.artist_album_song)
        structure_layout.addWidget(self.artist_album_song)

        self.artist_song = QRadioButton("Artist/Song")
        self.structure_group.addButton(self.artist_song)
        structure_layout.addWidget(self.artist_song)

        self.song_only = QRadioButton("Song Only (No Subfolders)")
        self.structure_group.addButton(self.song_only)
        structure_layout.addWidget(self.song_only)

        structure_group.setLayout(structure_layout)
        options_layout.addWidget(structure_group)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Download counter
        counter_group = QGroupBox("Download Counter")
        counter_layout = QHBoxLayout()

        counter_label = QLabel('Files Downloaded:')
        self.counter_display = QLabel('0')
        self.counter_display.setStyleSheet("font-weight: bold; font-size: 14px;")
        counter_layout.addWidget(counter_label)
        counter_layout.addWidget(self.counter_display)
        counter_layout.addStretch()  # Push to the left

        # Reset counter button
        self.reset_counter_btn = QPushButton('Reset Counter')
        self.reset_counter_btn.clicked.connect(self.reset_counter)
        counter_layout.addWidget(self.reset_counter_btn)

        counter_group.setLayout(counter_layout)
        layout.addWidget(counter_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")

        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Output console
        console_group = QGroupBox("Output Log")
        console_layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setReadOnly(True)

        # Set monospace font for console
        font = QFont("Consolas")
        font.setPointSize(12)
        self.console.setFont(font)

        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)

        # Add a note if running as bundled executable
        if self.is_bundled:
            self.append_output("Running in portable mode...", "info")

    def create_menu(self):
        """Create the menu bar with settings and help options"""
        menubar = self.menuBar()

        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        # Dark mode toggle action
        self.dark_mode_action = QAction('Dark Mode', self, checkable=True)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        settings_menu.addAction(self.dark_mode_action)

        # Logging toggle action
        self.logging_action = QAction('Enable Logging', self, checkable=True)
        self.logging_action.setChecked(self.log_enabled)
        self.logging_action.triggered.connect(self.toggle_logging)
        settings_menu.addAction(self.logging_action)
        
        # Open config location action
        open_config_action = QAction('Open Config Folder', self)
        open_config_action.triggered.connect(self.open_config_location)
        settings_menu.addAction(open_config_action)

        # Log directory selection action
        self.log_dir_action = QAction('Select Log Directory', self)
        self.log_dir_action.triggered.connect(self.select_log_directory)
        settings_menu.addAction(self.log_dir_action)

        # Open log directory action
        self.open_log_dir_action = QAction('Open Log Directory', self)
        self.open_log_dir_action.triggered.connect(self.open_log_directory)
        settings_menu.addAction(self.open_log_dir_action)

        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # Create a new menu for the 'Contact' option
        contact_menu = help_menu.addMenu('Contact')

        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # GitHub menu
        github_menu = QMenu('GitHub', self)

        # GitHub action for spotdl
        github_action_spotdl = QAction('SpotDL', self)
        github_action_spotdl.triggered.connect(self.open_github_link1)
        github_menu.addAction(github_action_spotdl)

        # GitHub action for spotdl_gui
        github_action_gui = QAction('SpotDL_GUI', self)
        github_action_gui.triggered.connect(self.open_github_link2)
        github_menu.addAction(github_action_gui)
        
        # Add the GitHub menu as a submenu of the Contact menu
        contact_menu.addMenu(github_menu)

        # Create a QAction for the original 'Contact' link
        contact_link_action = QAction('Linktree', self)
        contact_link_action.triggered.connect(self.open_contact_link)
        contact_menu.addAction(contact_link_action)

    def open_config_location(self):
        """Open the config file location in the system's file explorer"""
        config_path = self.get_config_path()
        config_dir = os.path.dirname(config_path)

        if not os.path.exists(config_dir):
            QMessageBox.warning(self, 'Directory Not Found', 'The config directory does not exist.')
            self.append_output(f"Error: Config directory not found: {config_dir}", "error")
            return

        try:
            # Use os.startfile on Windows
            if sys.platform == "win32":
                os.startfile(config_dir)
            # Use 'open' on macOS
            elif sys.platform == "darwin":
                subprocess.Popen(["open", config_dir])
            # Use 'xdg-open' or 'gnome-open' on Linux
            else:
                try:
                    subprocess.Popen(["xdg-open", config_dir])
                except FileNotFoundError:
                    subprocess.Popen(["gnome-open", config_dir])
            
            self.append_output(f"Opened config directory: {config_dir}", "info")

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not open config directory: {str(e)}')
            self.append_output(f"Error: Could not open config directory: {str(e)}", "error")

    def toggle_logging(self, checked):
        """Toggle logging on/off"""
        self.log_enabled = checked
        if checked:
            self.setup_logging()
            self.append_output("Logging enabled", "info")
        else:
            self.append_output("Logging disabled", "info")
        # Save settings immediately when toggled
        self.save_settings()

    def open_contact_link(self):
        """Open the Linktree contact page in the default browser"""
        try:
            import webbrowser
            webbrowser.open('https://linktr.ee/spotdl_gui')
            self.append_output("Opened contact link in browser", "info")
        except Exception as e:
            self.append_output(f"Could not open browser: {str(e)}", "error")

    def show_about(self):
        """Show information about the application"""
        about_text = """
        <h3>SpotDL GUI</h3>
        <p>A graphical interface for downloading Spotify songs using spotdl.</p>
        <p>Created with Python and PyQt5.</p>
        <p>For support, use the Contact option in the Help menu.</p>
        """
        QMessageBox.about(self, 'About SpotDL GUI', about_text)
        self.append_output("Displayed about information", "info")
      
    def open_github_link1(self):
        """Open the GitHub repository page in the default browser"""
        try:
            import webbrowser
            webbrowser.open('https://github.com/spotDL/spotify-downloader')
            self.append_output("Opened GitHub repository for SpotDL in browser", "info")
        except Exception as e:
            self.append_output(f"Could not open browser: {str(e)}", "error")

    def open_github_link2(self):
        """Open the GitHub repository page in the default browser"""
        try:
            import webbrowser
            webbrowser.open('https://github.com/Ye8ibp0oAa/spotdl_gui')
            self.append_output("Opened GitHub repository for SpotDL_GUI in browser", "info")
        except Exception as e:
            self.append_output(f"Could not open browser: {str(e)}", "error")
  
    def toggle_dark_mode(self, checked):
        """Toggle between light and dark mode"""
        self.dark_mode = checked
        if checked:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()
        # Save settings immediately when toggled
        self.save_settings()

    def apply_dark_mode(self):
        """Apply dark mode styling to the application"""
        # Set palette for dark mode
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Apply the dark palette to the application
        QApplication.setPalette(dark_palette)

        # Apply specific styling to widgets
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #353535;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #353535;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #FFF;
            }
            QTextEdit {
                background-color: #252525;
                color: #FFF;
                border: 1px solid #555;
            }
            QLineEdit {
                background-color: #252525;
                color: #FFF;
                border: 1px solid #555;
                padding: 5px;
            }
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #888;
            }
            QRadioButton, QCheckBox, QLabel {
                color: #FFF;
            }
            QComboBox {
                background-color: #252525;
                color: #FFF;
                border: 1px solid #555;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: #FFF;
                selection-background-color: #555;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #353535;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
            QMenuBar {
                background-color: #353535;
                color: white;
            }
            QMenuBar::item {
                background-color: transparent;
                color: white;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #353535;
                color: white;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #555;
            }
        """)

        # Reapply special button styles
        self.download_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.cancel_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")

    def apply_light_mode(self):
        """Apply light mode styling to the application"""
        # Reset to default palette
        QApplication.setPalette(QApplication.style().standardPalette())
        
        # Reset stylesheet
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #ccc;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #aaa;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)

        # Reapply special button styles
        self.download_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.cancel_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")

    def open_download_directory(self):
        """Open the selected download directory using the system's file explorer."""
        download_dir = self.dir_input.text().strip()
        if not download_dir or not os.path.exists(download_dir):
            QMessageBox.warning(self, 'Directory Not Found', 'The specified directory does not exist.')
            self.append_output(f"Error: Directory not found: {download_dir}", "error")
            return

        try:
            # Use os.startfile on Windows
            if sys.platform == "win32":
                os.startfile(download_dir)
            # Use 'open' on macOS
            elif sys.platform == "darwin":
                subprocess.Popen(["open", download_dir])
            # Use 'xdg-open' or 'gnome-open' on Linux
            else:
                try:
                    subprocess.Popen(["xdg-open", download_dir])
                except FileNotFoundError:
                    subprocess.Popen(["gnome-open", download_dir])
            
            self.append_output(f"Opened directory: {download_dir}", "info")

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not open directory: {str(e)}')
            self.append_output(f"Error: Could not open directory: {str(e)}", "error")

    def get_windows_music_folder(self):
        """
        Get the user's default Windows Music folder
        """
        try:
            # Try to get the Music folder from Windows known folders
            music_folder = os.path.join(os.path.expanduser("~"), "Music")

            # If the Music folder doesn't exist, create it
            if not os.path.exists(music_folder):
                os.makedirs(music_folder)
                self.append_output(f"Created Music folder: {music_folder}", "info")

            return music_folder

        except Exception as e:
            # Fallback to current directory if we can't access the Music folder
            self.append_output(f"Warning: Could not access Music folder: {e}", "warning")
            return os.getcwd()

    def reset_to_default_directory(self):
        """Reset the directory to the default Windows Music folder"""
        self.dir_input.setText(self.default_music_dir)
        self.append_output(f"Reset to default directory: {self.default_music_dir}", "info")
        # Save settings after reset
        self.save_settings()

    def reset_counter(self):
        """Reset the download counter to zero"""
        self.download_count = 0
        self.counter_display.setText('0')
        self.append_output("Download counter reset to 0", "info")

    def increment_counter(self):
        """Increment the download counter and update display"""
        self.download_count += 1
        self.counter_display.setText(str(self.download_count))
        self.append_output(f"✓ Download counted! Total: {self.download_count}", "success")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            'Select Download Directory',
            self.default_music_dir  # Start in Music folder by default
        )
        if directory:
            self.dir_input.setText(directory)
            self.append_output(f"Selected directory: {directory}", "info")
            # Save settings after directory change
            self.save_settings()

    def get_output_template(self):
        if self.artist_album_song.isChecked():
            return "{artist}/{album}/{title}"
        elif self.artist_song.isChecked():
            return "{artist}/{title}"
        else:
            return "{title}"

    def get_audio_flags(self):
        """Return the appropriate spotdl flags based on selected format and bitrate"""
        format_flag = ["--format", self.format_combo.currentText().strip()]
        
        bitrate_text = self.bitrate_combo.currentText().strip()
        if bitrate_text == "best":
            return format_flag  # No bitrate flag for "best"
        else:
            return format_flag + ["--bitrate", bitrate_text]

    def start_download(self):
        url = self.url_input.text().strip()
        output_dir = self.dir_input.text().strip()

        if not url:
            QMessageBox.warning(self, 'Input Error', 'Please enter a Spotify URL')
            self.append_output("Error: Please enter a Spotify URL", "error")
            return

        # Validate URL format
        if not url.startswith(('https://open.spotify.com/', 'spotify:')):
            reply = QMessageBox.question(
                self,
                'URL Validation',
                'This doesn\'t look like a standard Spotify URL. Do you want to continue anyway?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.append_output("Download cancelled: Invalid Spotify URL", "warning")
                return

        # Use default directory if none is specified
        if not output_dir:
            output_dir = self.default_music_dir
            self.dir_input.setText(output_dir)
            self.append_output(f"Using default directory: {output_dir}", "info")

        # Check if directory exists, create if not
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                self.append_output(f"Created directory: {output_dir}", "info")
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not create directory: {str(e)}')
                self.append_output(f"Error: Could not create directory: {str(e)}", "error")
                return

        output_template = self.get_output_template()
        audio_flags = self.get_audio_flags()

        # Build command using the executable name; the batch file sets the PATH
        full_output_path = os.path.join(output_dir, output_template).replace('\\', '/')
        cmd = ['spotdl.exe', url, '--output', full_output_path]
        
        # Add audio format and bitrate flags
        cmd.extend(audio_flags)

        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.console.clear()

        self.append_output(f"Starting download with folder structure: {output_template}", "info")
        
        # Show selected audio settings
        format_text = self.format_combo.currentText().strip()
        bitrate_text = self.bitrate_combo.currentText().strip()
        self.append_output(f"Selected audio format: {format_text}, bitrate: {bitrate_text}", "info")

        # Format the command for display with forward slashes
        display_cmd = ' '.join(cmd).replace('\\', '/')
        self.append_output(f"Command: {display_cmd}", "info")

        # Start the download process
        thread = threading.Thread(target=self.run_command, args=(cmd,))
        thread.daemon = True
        thread.start()

    def run_command(self, cmd):
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                shell=False,
                encoding='utf-8',
                errors='replace'
            )

            download_in_progress = False
            current_song = ""

            for line in self.process.stdout:
                # Determine color based on content
                color = "info"
                if "ERROR" in line or "Exception" in line:
                    color = "error"
                elif "WARNING" in line or "Warning" in line:
                    color = "warning"
                elif "Downloading" in line:
                    color = "download"
                elif "Downloaded" in line or "Finished downloading" in line:
                    color = "success"

                self.emitter.new_output.emit(line, color)

                # Track download progress for better counting
                if "Downloading" in line and not download_in_progress:
                    download_in_progress = True
                    current_song = line.strip()
                    self.append_output(f"Starting download: {current_song}", "download")

                # Detect successful download completion
                elif download_in_progress and ("Downloaded" in line or "Finished downloading" in line):
                    self.increment_counter()
                    download_in_progress = False
                    current_song = ""

                # Alternative detection for different spotdl output formats
                elif "http" in line and ("youtube.com" in line or "youtu.be" in line) and not download_in_progress:
                    self.increment_counter()

            self.process.wait()
            self.download_finished()

        except Exception as e:
            self.emitter.new_output.emit(f"Error: {str(e)}", "error")
            self.download_finished()

    def append_output(self, text, color_type="info"):
        """Append text to the console with specified color"""
        cursor = self.console.textCursor()
        format = QTextCharFormat()

        # Set colors based on type
        if color_type == "error":
            format.setForeground(QColor(255, 100, 100))  # Red for errors
        elif color_type == "warning":
            format.setForeground(QColor(255, 165, 0))  # Orange for warnings
        elif color_type == "success":
            format.setForeground(QColor(100, 200, 100))  # Green for success
        elif color_type == "download":
            format.setForeground(QColor(100, 150, 255))  # Blue for download status
        elif color_type == "info":
            if self.dark_mode:
                format.setForeground(QColor(200, 200, 200))  # Light gray for info in dark mode
            else:
                format.setForeground(QColor(50, 50, 50))  # Dark gray for info in light mode
        else:
            if self.dark_mode:
                format.setForeground(QColor(200, 200, 200))  # Default light gray for dark mode
            else:
                format.setForeground(QColor(0, 0, 0))  # Default black for light mode

        # Apply the format and insert text
        cursor.movePosition(QTextCursor.End)
        cursor.setCharFormat(format)
        cursor.insertText(text.strip() + "\n")

        # Write to log file (without color formatting)
        self.write_to_log(text.strip())

        # Auto-scroll to bottom
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def download_finished(self):
        self.process = None
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.append_output(f"Download process finished. Total files downloaded: {self.download_count}", "info")

    def cancel_download(self):
        if self.process:
            self.process.terminate()
            self.append_output("Download cancelled.", "warning")
        self.download_finished()

    def set_ui_enabled(self, enabled):
        self.url_input.setEnabled(enabled)
        self.dir_input.setEnabled(enabled)
        self.dir_button.setEnabled(enabled)
        self.reset_dir_button.setEnabled(enabled)
        self.open_dir_button.setEnabled(True) 
        self.format_combo.setEnabled(enabled)
        self.bitrate_combo.setEnabled(enabled)
        self.artist_album_song.setEnabled(enabled)
        self.artist_song.setEnabled(enabled)
        self.song_only.setEnabled(enabled)
        self.download_button.setEnabled(enabled)
        self.cancel_button.setEnabled(not enabled)
        self.reset_counter_btn.setEnabled(enabled)
        self.dark_mode_action.setEnabled(enabled)
        self.logging_action.setEnabled(enabled)
        self.log_dir_action.setEnabled(enabled)
        self.open_log_dir_action.setEnabled(enabled)

    def write_to_log(self, message):
        """Write a message to the current log file if logging is enabled"""
        if self.log_enabled and self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}] {message}\n")
            except Exception as e:
                # Fallback if logging fails
                self.append_output(f"Error writing to log file: {str(e)}", "error")
                self.log_enabled = False

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    
    # Set a global font size for all widgets
    font = QFont()
    font.setPointSize(9)
    app.setFont(font)
    
    window = SpotDLGUI()
    
    # Override the font size specifically for the console
    console_font = QFont("Consolas")
    console_font.setPointSize(12)
    window.console.setFont(console_font)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()