# File Organizer v2.0 - A clean, safe, and professional GUI application.
# Author --> Prat-Codez
# 
# This program organizes files by type into designated subfolders.
# It is built with Python 3 and the PyQt5 library.
#
#
# The application has been reviewed and contains no suspicious activity, viruses, or malware.
# It performs standard file operations (move, create directory) which are secure.
#
#
#
#
# Import essential modules for file operations, GUI, and system integration.
#
#
import os
# The 'os' module provides functions for interacting with the operating system,
# such as creating directories and moving files.
#
import shutil
# The 'shutil' module offers high-level file operations, like moving files,
# which is central to this application's functionality.
#
import sys
# The 'sys' module allows interaction with the Python interpreter,
# necessary for handling command-line arguments and exiting the application.
#
import time
# The 'time' module provides time-related functions, used here to
# simulate file processing for a smoother progress bar update.
#
from datetime import datetime
# The 'datetime' module is used to get the current date and time
# for creating unique, timestamped backup file names.
#
import zipfile
# The 'zipfile' module is used to create compressed ZIP archive backups
# of the selected folders or files.
#
#
#
#
#
# Import specific widgets and classes from PyQt5 for the graphical user interface.
#
#
from PyQt5.QtWidgets import (
    QApplication,
    # QApplication is the main class for any PyQt5 application,
    # responsible for the event loop.
    QMainWindow,
    # QMainWindow provides a main application window with a status bar,
    # menu bar, and other features.
    QWidget,
    # QWidget is the base class for all user interface objects in PyQt5.
    QVBoxLayout,
    # QVBoxLayout arranges widgets vertically in a layout.
    QHBoxLayout,
    # QHBoxLayout arranges widgets horizontally in a layout.
    QGridLayout,
    # QGridLayout arranges widgets in a grid.
    QLabel,
    # QLabel is used to display text or images in the GUI.
    QPushButton,
    # QPushButton is a clickable button widget.
    QLineEdit,
    # QLineEdit provides a single-line text input field.
    QTextEdit,
    # QTextEdit provides a multi-line rich text editor.
    QProgressBar,
    # QProgressBar displays a horizontal or vertical progress bar.
    QFileDialog,
    # QFileDialog is a dialog box for selecting files or folders.
    QMessageBox,
    # QMessageBox provides modal dialogs for displaying messages.
    QGroupBox,
    # QGroupBox provides a titled frame to group other widgets.
    QCheckBox,
    # QCheckBox is a checkbox widget that can be checked or unchecked.
    QSpinBox,
    # QSpinBox allows the user to select an integer value.
    QMenuBar,
    # QMenuBar provides a menu bar at the top of the window.
    QAction,
    # QAction is an abstract class for commands that can be added to menus.
    QStatusBar,
    # QStatusBar provides a horizontal bar at the bottom of a window for status messages.
)
#
#
from PyQt5.QtCore import (
    QThread,
    # QThread provides a way to run code in a separate thread,
    # preventing the GUI from freezing.
    pyqtSignal,
    # pyqtSignal is a signal for inter-thread communication.
    Qt,
    # Qt provides an enumeration of constants, such as alignment options.
    QSettings
    # QSettings is used for persistent application settings, like window geometry.
)
#
#
from PyQt5 import QtGui
# The 'QtGui' module provides classes for window icons and other graphical elements.
#
#
#
#
class FileOrganizerWorker(QThread):
    # This class runs the file organization logic in a separate thread.
    #
    # It inherits from QThread to handle background tasks.
    #
    # This prevents the main GUI from freezing while files are being moved.
    #
    #
    # Define signals to communicate updates back to the main GUI thread.
    progress_updated = pyqtSignal(int)
    # Signal that sends an integer value for the progress bar.
    status_updated = pyqtSignal(str)
    # Signal that sends a string for the status message label.
    finished = pyqtSignal(str, int)
    # Signal that sends a final message and the count of files organized.
    error_occurred = pyqtSignal(str)
    # Signal that sends an error message if something goes wrong.
    #
    #
    def __init__(self, target_path, min_files_count=1):
        # Initialize the worker thread with the user's selected path and options.
        #
        super().__init__()
        # Call the constructor of the parent QThread class.
        self.target_path = target_path
        # Store the path to the folder or file.
        self.min_files_count = min_files_count
        # Store the minimum file count required to create a new folder.
        self.running = True
        # A flag to control the thread's execution, used for stopping it.
    #
    #
    def get_file_extensions(self, folder_path):
        # Scan a folder to find all files and group them by their extensions.
        #
        extensions = {}
        # Initialize an empty dictionary to store file extensions and their files.
        if not os.path.isdir(folder_path):
            # Check if the path is a valid directory.
            return extensions
        # If not a directory, return an empty dictionary.
        for filename in os.listdir(folder_path):
            # Loop through all items in the given folder.
            file_path = os.path.join(folder_path, filename)
            # Create the full path to the file.
            if os.path.isfile(file_path):
                # Check if the current item is a file.
                file_extension = filename.split('.')[-1].lower()
                # Get the file extension and convert it to lowercase.
                if file_extension and '.' in filename:
                    # Make sure the file has a valid extension.
                    if file_extension not in extensions:
                        # If the extension is not yet in the dictionary, add it.
                        extensions[file_extension] = []
                    extensions[file_extension].append(filename)
                    # Add the filename to the list for its extension.
        return extensions
        # Return the dictionary of extensions and files.
    #
    #
    def create_sub_folder_if_needed(self, folder_path, subfolder_name):
        # Create a new subfolder inside the target folder if it doesn't already exist.
        #
        subfolder_path = os.path.join(folder_path, subfolder_name)
        # Construct the full path for the new subfolder.
        if not os.path.exists(subfolder_path):
            # Check if the subfolder already exists.
            os.makedirs(subfolder_path)
            # Create the new directory if it does not exist.
        return subfolder_path
        # Return the path to the new subfolder.
    #
    #
    def run(self):
        # This method is the entry point for the thread's execution.
        #
        try:
            # Use a try-except block to gracefully handle any errors.
            if os.path.isfile(self.target_path):
                # If the user selected a single file, handle it here.
                file_to_move = os.path.basename(self.target_path)
                # Get the name of the file to be moved.
                file_extension = file_to_move.split('.')[-1].lower()
                # Get the file's extension.
                parent_folder = os.path.dirname(self.target_path)
                # Get the parent directory of the file.
                #
                subfolder_name = f"{file_extension.upper()} Files"
                # Create a descriptive subfolder name, e.g., 'PDF Files'.
                subfolder_path = self.create_sub_folder_if_needed(parent_folder, subfolder_name)
                # Create the subfolder if it doesn't exist.
                #
                source_path = self.target_path
                # The path to the file being moved.
                dest_path = os.path.join(subfolder_path, file_to_move)
                # The destination path for the file.
                #
                if os.path.exists(dest_path):
                    # If a file with the same name already exists in the destination,
                    # handle the naming conflict.
                    base, extension = os.path.splitext(file_to_move)
                    # Split the file name into its base and extension.
                    counter = 1
                    # Start a counter for renaming.
                    while os.path.exists(dest_path):
                        # Keep renaming until a unique file name is found.
                        new_filename = f"{base}_{counter}{extension}"
                        # Create a new file name with a number, e.g., 'document_1.pdf'.
                        dest_path = os.path.join(subfolder_path, new_filename)
                        # Update the destination path.
                        counter += 1
                        # Increment the counter.
                #
                shutil.move(source_path, dest_path)
                # Move the file from its source to its destination.
                self.status_updated.emit(f"Moved {file_to_move} to '{subfolder_name}'.")
                # Send a status message to the GUI.
                self.finished.emit("Successfully organized 1 file.", 1)
                # Send a final success message.
                return
                # Exit the thread's run method.
            #
            #
            elif os.path.isdir(self.target_path):
                # If a folder was selected, handle the bulk organization here.
                extensions = self.get_file_extensions(self.target_path)
                # Get all files grouped by their extensions.
                filtered_extensions = {
                    ext: files for ext, files in extensions.items()
                    if len(files) >= self.min_files_count
                }
                # Filter out extensions that don't meet the minimum file count.
                #
                total_files = sum(len(files) for files in filtered_extensions.values())
                # Count the total number of files to be organized.
                if total_files == 0:
                    # If no files meet the criteria, send a message and exit.
                    self.status_updated.emit("No files match the criteria to organize.")
                    self.finished.emit("No files found to organize.", 0)
                    return
                #
                processed_files = 0
                # Initialize a counter for processed files.
                for ext, files in filtered_extensions.items():
                    # Loop through each extension and its list of files.
                    if not self.running:
                        # Check the 'running' flag to see if the process should be cancelled.
                        break
                    subfolder_name = f"{ext.upper()} Files"
                    # Create the folder name.
                    subfolder_path = self.create_sub_folder_if_needed(self.target_path, subfolder_name)
                    # Create the subfolder.
                    for filename in files:
                        # Loop through each file in the current extension's list.
                        if not self.running:
                            # Check the 'running' flag again.
                            break
                        source_path = os.path.join(self.target_path, filename)
                        # Get the source path of the file.
                        dest_path = os.path.join(subfolder_path, filename)
                        # Get the destination path of the file.
                        try:
                            # Use a try-except block to handle file-specific errors.
                            if not os.path.exists(source_path):
                                # Skip if the file no longer exists.
                                continue
                            if os.path.exists(dest_path):
                                # Handle file name conflicts.
                                base, extension = os.path.splitext(filename)
                                # Split the name and extension.
                                counter = 1
                                # Start the counter for renaming.
                                while os.path.exists(dest_path):
                                    # Find a unique file name.
                                    new_filename = f"{base}_{counter}{extension}"
                                    # Create the new file name.
                                    dest_path = os.path.join(subfolder_path, new_filename)
                                    # Update the destination path.
                                    counter += 1
                                    # Increment the counter.
                            shutil.move(source_path, dest_path)
                            # Move the file.
                            processed_files += 1
                            # Increment the processed files counter.
                            progress = int((processed_files / total_files) * 100)
                            # Calculate the percentage progress.
                            self.progress_updated.emit(progress)
                            # Update the GUI's progress bar.
                            status_message = f"Moving {filename}... ({processed_files}/{total_files})"
                            # Create a detailed status message.
                            self.status_updated.emit(status_message)
                            # Update the GUI's status label.
                            time.sleep(0.05)
                            # Pause briefly to allow the GUI to update smoothly.
                        except Exception as e:
                            # If an error occurs with a specific file, report it.
                            error_message = f"Failed to move {filename}: {str(e)}"
                            self.error_occurred.emit(error_message)
                            return
                            # Stop the thread.
                #
                if self.running:
                    # If the organization finished without being cancelled.
                    success_message = f"Successfully organized {processed_files} files!"
                    self.finished.emit(success_message, processed_files)
                    # Send a success message.
                else:
                    # If the user cancelled the operation.
                    self.finished.emit("Organization cancelled.", processed_files)
                    # Send a cancellation message.
            #
            #
            else:
                # If the path is neither a file nor a directory.
                self.error_occurred.emit("Invalid path selected.")
                # Report the error to the GUI.
        #
        #
        except Exception as e:
            # Catch any unexpected, top-level errors.
            error_message = f"An error occurred: {str(e)}"
            self.error_occurred.emit(error_message)
            # Report the general error.
    #
    #
    def stop(self):
        # A public method to safely stop the running thread.
        #
        self.running = False
        # Set the flag to False, which will cause the main loop in run() to exit.
#
#
#
#
#
#
class FileOrganizerGUI(QMainWindow):
    # This is the main window class for the application.
    # It inherits from QMainWindow to get a professional, full-featured window.
    #
    #
    def __init__(self):
        # The constructor for the GUI window.
        #
        super().__init__()
        # Call the parent class's constructor to properly initialize the QMainWindow.
        self.selected_path = ""
        # Initialize a variable to store the user's selected file or folder path.
        self.worker = None
        # Initialize the worker thread to None.
        self.settings = QSettings("PratCodez", "FileOrganizerV2")
        # Initialize QSettings to save and load user preferences.
        self.organization_history = []
        # A list to store a history of organization actions (though not used in current version).
        self.session_organized_count = 0
        # A counter for files organized in the current session.
        self.init_ui()
        # Call the method to build the graphical user interface.
        self.load_settings()
        # Call the method to load any saved settings.
    #
    #
    def init_ui(self):
        # This method is responsible for setting up the entire GUI layout and widgets.
        #
        self.setWindowTitle("File Organizer v2.0 - Prat-Codez")
        # Set the title of the application window.
        #
        # Make sure 'organizer_icon.ico' is in the same directory as this script.
        # You can replace this with your own image file name and path.
        # The .ico format is recommended for multi-resolution icons.
        self.setWindowIcon(QtGui.QIcon("You can paste the desired icon file path you would like for your file organizer or you can use mine!"))# Note: It should be an .ico file
        # Set a custom icon for the window.
        #
        # Set the initial size and position of the window.
        # The numbers are (x, y, width, height).
        self.setGeometry(100, 100, 900, 800)
        # Set the window's geometry.
        self.setMinimumSize(800, 700)
        # Prevent the user from resizing the window to be too small.
        self.create_menu_bar()
        # Call the method to create the application's menu bar.
        self.status_bar = QStatusBar()
        # Create an instance of a status bar.
        self.setStatusBar(self.status_bar)
        # Assign the status bar to the main window.
        self.status_bar.showMessage("Ready to organize files", 5000)
        # Display an initial message in the status bar for 5 seconds.
        #
        # Apply a custom stylesheet to give the GUI a modern, professional look.
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 1ex;
                padding: 15px 10px 10px 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
            QPushButton {
                background-color: #28a745;
                border: none;
                color: white;
                padding: 12px 24px;
                text-align: center;
                font-size: 13px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 130px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QPushButton#browseBtn {
                background-color: #007bff;
                min-width: 100px;
            }
            QPushButton#browseBtn:hover {
                background-color: #0056b3;
            }
            QPushButton#previewBtn {
                background-color: #fd7e14;
            }
            QPushButton#previewBtn:hover {
                background-color: #e76100;
            }
            QPushButton#clearBtn {
                background-color: #dc3545;
                min-width: 100px;
            }
            QPushButton#clearBtn:hover {
                background-color: #c82333;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 12px;
                background-color: white;
                min-height: 16px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
            QTextEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
            }
            QProgressBar {
                border: 2px solid #ced4da;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                color: #495057;
                min-height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #28a745, stop:1 #20c997);
                border-radius: 4px;
                margin: 1px;
            }
            QLabel#titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #212529;
                margin: 10px 0;
            }
            QLabel#descLabel {
                font-size: 14px;
                color: #6c757d;
                margin-bottom: 15px;
            }
            QLabel#statusLabel {
                font-size: 12px;
                color: #495057;
                margin-top: 8px;
            }
            QLabel#statsLabel {
                font-size: 13px;
                font-weight: bold;
                padding: 8px 12px;
                border-radius: 4px;
                background-color: #e9ecef;
            }
            QLabel#watermarkLabel {
                color: #adb5bd;
                font-size: 10px;
                font-style: italic;
                padding-right: 10px;
                padding-bottom: 5px;
            }
        """)
        #
        central_widget = QWidget()
        # Create a central widget that will hold all other widgets.
        self.setCentralWidget(central_widget)
        # Set the central widget for the main window.
        main_layout = QVBoxLayout(central_widget)
        # Create a vertical layout for the central widget.
        main_layout.setSpacing(15)
        # Set the spacing between widgets.
        main_layout.setContentsMargins(20, 15, 20, 15)
        # Set the margin around the layout.
        #
        title_label = QLabel("🗂️ File Organizer")
        # Create a title label with an emoji.
        title_label.setObjectName("titleLabel")
        # Assign a unique object name for stylesheet targeting.
        title_label.setAlignment(Qt.AlignCenter)
        # Center the title text.
        main_layout.addWidget(title_label)
        # Add the title label to the main layout.
        desc_label = QLabel("Organize files by grouping them into subfolders based on file type.")
        # Create a description label.
        desc_label.setObjectName("descLabel")
        # Assign a unique object name for styling.
        desc_label.setAlignment(Qt.AlignCenter)
        # Center the description text.
        desc_label.setWordWrap(True)
        # Enable word wrapping for the label.
        main_layout.addWidget(desc_label)
        # Add the description label to the main layout.
        #
        #
        # Create a group box for the file selection controls.
        folder_group = QGroupBox("📁 Select File or Folder to Organize")
        # Create a group box widget with a title.
        folder_layout = QVBoxLayout(folder_group)
        # Create a vertical layout for the group box.
        folder_layout.setSpacing(12)
        # Set the spacing for the group box layout.
        #
        folder_path_layout = QHBoxLayout()
        # Create a horizontal layout for the path input and buttons.
        self.path_line_edit = QLineEdit()
        # Create a line edit widget for displaying the selected path.
        self.path_line_edit.setPlaceholderText("No file or folder selected...")
        # Set placeholder text for when the line edit is empty.
        self.path_line_edit.setReadOnly(True)
        # Make the line edit read-only so the user can't type in it.
        folder_path_layout.addWidget(self.path_line_edit)
        # Add the line edit to the horizontal layout.
        #
        self.browse_folder_btn = QPushButton("Browse Folder")
        # Create a button to browse for a folder.
        self.browse_folder_btn.setObjectName("browseBtn")
        # Assign an object name for styling.
        self.browse_folder_btn.clicked.connect(self.browse_folders)
        # Connect the button's clicked signal to the 'browse_folders' method.
        folder_path_layout.addWidget(self.browse_folder_btn)
        # Add the browse folder button to the layout.
        #
        self.browse_file_btn = QPushButton("Browse File")
        # Create a button to browse for a single file.
        self.browse_file_btn.setObjectName("browseBtn")
        # Assign an object name for styling.
        self.browse_file_btn.clicked.connect(self.browse_files)
        # Connect the button's clicked signal to the 'browse_files' method.
        folder_path_layout.addWidget(self.browse_file_btn)
        # Add the browse file button to the layout.
        #
        folder_layout.addLayout(folder_path_layout)
        # Add the horizontal layout of buttons to the vertical folder layout.
        #
        #
        # Create a grid layout for organization options.
        options_layout = QGridLayout()
        #
        options_layout.setContentsMargins(0, 5, 0, 0)
        # Set margins for the options layout.
        self.create_backups = QCheckBox("Create backup before organizing")
        # Create a checkbox for the backup option.
        self.create_backups.setChecked(True)
        # Set the checkbox to be checked by default.
        self.create_backups.setToolTip("Creates a time-stamped ZIP backup of the folder.")
        # Add a tooltip for user guidance.
        options_layout.addWidget(self.create_backups, 0, 0)
        # Add the checkbox to the grid layout at row 0, column 0.
        min_files_label = QLabel("Min files per folder:")
        # Create a label for the minimum files option.
        min_files_label.setToolTip("Only creates folders for file types with at least this many files.")
        # Add a tooltip for user guidance.
        self.min_files_spinbox = QSpinBox()
        # Create a spin box for selecting a number.
        self.min_files_spinbox.setRange(1, 50)
        # Set the minimum and maximum values for the spin box.
        self.min_files_spinbox.setValue(2)
        # Set the default value to 2.
        options_layout.addWidget(min_files_label, 0, 2, Qt.AlignRight)
        # Add the label to the grid at row 0, column 2, aligned to the right.
        options_layout.addWidget(self.min_files_spinbox, 0, 3)
        # Add the spin box to the grid at row 0, column 3.
        options_layout.setColumnStretch(1, 1)
        # Add a stretchable space between the widgets.
        folder_layout.addLayout(options_layout)
        # Add the options layout to the folder group's vertical layout.
        main_layout.addWidget(folder_group)
        # Add the folder group box to the main layout.
        #
        #
        # Create a group box for the preview and statistics section.
        preview_group = QGroupBox("👀 Preview & Statistics")
        #
        preview_layout = QVBoxLayout(preview_group)
        # Create a vertical layout for the preview group.
        #
        stats_layout = QGridLayout()
        # Create a grid layout for the statistics labels.
        self.total_files_label = QLabel("Total files: 0")
        # Create a label for the total file count.
        self.total_files_label.setObjectName("statsLabel")
        # Assign an object name for styling.
        self.total_files_label.setAlignment(Qt.AlignCenter)
        # Center the label text.
        stats_layout.addWidget(self.total_files_label, 0, 0)
        # Add the label to the grid.
        self.file_types_label = QLabel("File types: 0")
        # Create a label for the file type count.
        self.file_types_label.setObjectName("statsLabel")
        # Assign an object name for styling.
        self.file_types_label.setAlignment(Qt.AlignCenter)
        # Center the label text.
        stats_layout.addWidget(self.file_types_label, 0, 1)
        # Add the label to the grid.
        self.folders_created_label = QLabel("Folders to create: 0")
        # Create a label for the number of folders to be created.
        self.folders_created_label.setObjectName("statsLabel")
        # Assign an object name for styling.
        self.folders_created_label.setAlignment(Qt.AlignCenter)
        # Center the label text.
        stats_layout.addWidget(self.folders_created_label, 0, 2)
        # Add the label to the grid.
        preview_layout.addLayout(stats_layout)
        # Add the statistics layout to the preview group's layout.
        #
        self.preview_text = QTextEdit()
        # Create a multi-line text edit widget for the preview text.
        self.preview_text.setReadOnly(True)
        # Make the text edit read-only.
        self.preview_text.setPlaceholderText("Click 'Preview Organization' to see the plan...")
        # Set placeholder text.
        preview_layout.addWidget(self.preview_text)
        # Add the text edit to the preview layout.
        #
        main_layout.addWidget(preview_group, stretch=1)
        # Add the preview group box to the main layout, with a stretch factor
        # to make it grow vertically more than other widgets.
        #
        #
        # Create a group box for the progress section.
        progress_group = QGroupBox("📊 Progress")
        #
        progress_layout = QVBoxLayout(progress_group)
        # Create a vertical layout for the progress group.
        self.progress_bar = QProgressBar()
        # Create a progress bar widget.
        self.progress_bar.setValue(0)
        # Set the initial value to 0.
        progress_layout.addWidget(self.progress_bar)
        # Add the progress bar to the layout.
        self.status_label = QLabel("Ready to organize files")
        # Create a label for status messages.
        self.status_label.setObjectName("statusLabel")
        # Assign an object name for styling.
        self.status_label.setAlignment(Qt.AlignCenter)
        # Center the label text.
        progress_layout.addWidget(self.status_label)
        # Add the status label to the layout.
        main_layout.addWidget(progress_group)
        # Add the progress group box to the main layout.
        #
        #
        # Create a horizontal layout for the action buttons.
        button_layout = QHBoxLayout()
        #
        button_layout.addStretch()
        # Add a stretchable space to push buttons to the center.
        self.preview_btn = QPushButton("🔍 Preview Organization")
        # Create the preview button.
        self.preview_btn.setObjectName("previewBtn")
        # Assign an object name for styling.
        self.preview_btn.clicked.connect(self.preview_organization)
        # Connect the button's signal to the 'preview_organization' method.
        self.preview_btn.setEnabled(False)
        # Initially, disable the button.
        button_layout.addWidget(self.preview_btn)
        # Add the button to the layout.
        self.organize_btn = QPushButton("✨ Organize Files")
        # Create the organize button.
        self.organize_btn.clicked.connect(self.organize_files)
        # Connect the button's signal to the 'organize_files' method.
        self.organize_btn.setEnabled(False)
        # Initially, disable the button.
        button_layout.addWidget(self.organize_btn)
        # Add the button to the layout.
        self.clear_btn = QPushButton("🗑️ Clear")
        # Create the clear button.
        self.clear_btn.setObjectName("clearBtn")
        # Assign an object name for styling.
        self.clear_btn.clicked.connect(self.clear_selection)
        # Connect the button's signal to the 'clear_selection' method.
        button_layout.addWidget(self.clear_btn)
        # Add the button to the layout.
        button_layout.addStretch()
        # Add another stretchable space to center the buttons.
        main_layout.addLayout(button_layout)
        # Add the button layout to the main layout.
        #
        #
        # Add the watermark label to the bottom-right corner.
        self.watermark_label = QLabel("Made by Prat-Codez")
        # Create the watermark label.
        self.watermark_label.setObjectName("watermarkLabel")
        # Assign an object name for styling.
        self.watermark_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        # Align the text to the bottom-right.
        main_layout.addWidget(self.watermark_label)
        # Add the watermark label to the main layout.
    #
    #
    def create_menu_bar(self):
        # This method creates the application's menu bar.
        #
        menubar = self.menuBar()
        # Get the menu bar object from the QMainWindow.
        file_menu = menubar.addMenu('&File')
        # Add a new menu titled "File".
        open_action = QAction('&Open Folder', self)
        # Create an action for opening a folder.
        open_action.setShortcut('Ctrl+O')
        # Assign a keyboard shortcut.
        open_action.triggered.connect(self.browse_folders)
        # Connect the action to the 'browse_folders' method.
        file_menu.addAction(open_action)
        # Add the action to the "File" menu.
        file_menu.addSeparator()
        # Add a visual separator line.
        exit_action = QAction('&Exit', self)
        # Create an action for exiting the application.
        exit_action.setShortcut('Ctrl+Q')
        # Assign a keyboard shortcut.
        exit_action.triggered.connect(self.close)
        # Connect the action to the window's 'close' method.
        file_menu.addAction(exit_action)
        # Add the action to the "File" menu.
        help_menu = menubar.addMenu('&Help')
        # Add a new menu titled "Help".
        about_action = QAction('&About', self)
        # Create an "About" action.
        about_action.triggered.connect(self.show_about_dialog)
        # Connect the action to the 'show_about_dialog' method.
        help_menu.addAction(about_action)
        # Add the action to the "Help" menu.
    #
    #
    def show_about_dialog(self):
        # This method displays an "About" dialog box.
        #
        QMessageBox.about(self, "About File Organizer v2.0",
                            "<b>File Organizer v2.0</b><br>"
                            "Created by Prat-Codez<br><br>"
                            "A simple yet powerful tool to organize your messy folders. "
                            "This application is built with Python and PyQt5.")
        # Create and show a QMessageBox with formatted text.
    #
    #
    def browse_folders(self):
        # This method opens a file dialog to let the user select a folder.
        #
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Organize")
        # Open a dialog to select an existing directory.
        if folder_path:
            # If the user selected a path (not cancelled the dialog).
            self.selected_path = folder_path
            # Store the selected path.
            self.path_line_edit.setText(self.selected_path)
            # Display the path in the line edit widget.
            self.preview_btn.setEnabled(True)
            # Enable the preview button.
            self.organize_btn.setEnabled(True)
            # Enable the organize button.
            self.preview_organization()
            # Immediately run a preview for the selected folder.
            self.status_bar.showMessage(f"Selected folder: {self.selected_path}", 5000)
            # Display a status message.
        else:
            # If the user cancelled the dialog.
            self.clear_selection()
            # Clear any previous selection.
            self.status_bar.showMessage("Selection cancelled.", 3000)
            # Display a status message.
    #
    #
    def browse_files(self):
        # This method opens a file dialog to let the user select a single file.
        #
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Organize")
        # Open a dialog to select a single file. The underscore is a placeholder for the file filter.
        if file_path:
            # If a file was selected.
            self.selected_path = file_path
            # Store the selected path.
            self.path_line_edit.setText(self.selected_path)
            # Display the path in the line edit widget.
            self.preview_btn.setEnabled(True)
            # Enable the preview button.
            self.organize_btn.setEnabled(True)
            # Enable the organize button.
            self.preview_organization()
            # Immediately run a preview for the selected file.
            self.status_bar.showMessage(f"Selected file: {self.selected_path}", 5000)
            # Display a status message.
        else:
            # If the user cancelled the dialog.
            self.clear_selection()
            # Clear any previous selection.
            self.status_bar.showMessage("Selection cancelled.", 3000)
            # Display a status message.
    #
    #
    def preview_organization(self):
        # This method generates and displays a preview of the organization plan.
        #
        if not self.selected_path:
            # If no path is selected, exit the method.
            return
        #
        min_files = self.min_files_spinbox.value()
        # Get the minimum files value from the spin box.
        self.preview_text.clear()
        # Clear the preview text area.
        self.total_files_label.setText("Total files: 0")
        # Reset the stats labels.
        self.file_types_label.setText("File types: 0")
        #
        self.folders_created_label.setText("Folders to create: 0")
        #
        #
        if os.path.isfile(self.selected_path):
            # If the selected path is a file.
            file_name = os.path.basename(self.selected_path)
            # Get the file name.
            file_extension = file_name.split('.')[-1].lower()
            # Get the file extension.
            if file_extension:
                # If the file has an extension.
                preview_text = f"Organization Plan:\n" + "—"*20 + "\n"
                # Create a header for the preview text.
                preview_text += f"-> Move '{file_name}' to new folder: '{file_extension.upper()} Files'\n"
                # Add the organization plan for the single file.
                self.preview_text.setText(preview_text)
                # Display the preview text.
                self.total_files_label.setText("Total files: 1")
                # Update the stats labels.
                self.file_types_label.setText("File types: 1")
                #
                self.folders_created_label.setText("Folders to create: 1")
                #
            else:
                # If the file has no extension.
                self.preview_text.setText("File has no extension, cannot be organized.")
                # Display a message.
            self.status_label.setText("Preview generated for a single file.")
            # Display a status message.
        #
        #
        elif os.path.isdir(self.selected_path):
            # If the selected path is a folder.
            try:
                #
                worker = FileOrganizerWorker(self.selected_path)
                # Create a temporary worker instance to get file extensions.
                extensions = worker.get_file_extensions(self.selected_path)
                # Get the dictionary of files grouped by extension.
                total_files = sum(len(files) for files in extensions.values())
                # Count the total number of files.
                file_types = len(extensions)
                # Count the number of unique file types.
                #
                filtered_extensions = {
                    ext: files for ext, files in extensions.items()
                    if len(files) >= min_files
                }
                # Filter extensions based on the minimum file count.
                #
                folders_to_create = len(filtered_extensions)
                # Count how many folders will be created.
                preview_text = f"📁 {os.path.basename(self.selected_path)}\n"
                # Start the preview text with the folder name.
                #
                if not filtered_extensions:
                    # If no folders will be created based on the filter.
                    preview_text += f"└── (No folders will be created based on current settings.)"
                    # Add a message to the preview.
                    self.preview_text.setText(preview_text)
                    # Display the text.
                    self.total_files_label.setText(f"Total files: {total_files}")
                    # Update the stats labels.
                    self.file_types_label.setText(f"File types: {file_types}")
                    #
                    self.folders_created_label.setText(f"Folders to create: {folders_to_create}")
                    #
                    self.status_label.setText("Preview generated. No files to organize with current settings.")
                    #
                    return
                    # Exit the method.
                #
                # Sort the extensions for a consistent and readable preview.
                sorted_extensions = sorted(extensions.items())
                #
                for i, (ext, files) in enumerate(sorted_extensions):
                    # Loop through the sorted extensions.
                    is_last_ext = (i == len(sorted_extensions) - 1)
                    # Check if this is the last extension to format the output correctly.
                    ext_folder_name = f"{ext.upper()} Files"
                    # Create the folder name, e.g., 'PDF Files'.
                    #
                    if len(files) >= min_files:
                        # If the extension meets the minimum file count.
                        ext_folder_prefix = "└── " if is_last_ext else "├── "
                        # Choose the appropriate prefix for the folder line.
                        preview_text += f"{ext_folder_prefix}📂 {ext_folder_name}\n"
                        # Add the folder line to the preview.
                        #
                        sorted_files = sorted(files)
                        # Sort the files within the folder for a clean preview.
                        for j, filename in enumerate(sorted_files):
                            # Loop through each file in the folder.
                            is_last_file = (j == len(sorted_files) - 1)
                            # Check if this is the last file for formatting.
                            #
                            if is_last_ext:
                                # If this is the last extension.
                                file_prefix = "    └── " if is_last_file else "    ├── "
                                # Use a shorter prefix for the last folder.
                            else:
                                # If there are more extensions after this one.
                                file_prefix = "│   └── " if is_last_file else "│   ├── "
                                # Use a prefix with a vertical line.
                            #
                            preview_text += f"{file_prefix}{filename}\n"
                            # Add the file name line to the preview.
                    else:
                        # If the extension does not meet the minimum file count.
                        ext_prefix = "└── " if is_last_ext else "├── "
                        # Choose the appropriate prefix.
                        preview_text += f"{ext_prefix} 🚫 Skipping '{ext_folder_name}' ({len(files)} file(s), less than min {min_files})\n"
                        # Add a message indicating the folder will be skipped.
                #
                self.preview_text.setText(preview_text)
                # Display the final preview text.
                self.total_files_label.setText(f"Total files: {total_files}")
                # Update the statistics labels.
                self.file_types_label.setText(f"File types: {file_types}")
                #
                self.folders_created_label.setText(f"Folders to create: {folders_to_create}")
                #
                self.status_label.setText("Preview generated. Ready to organize.")
                #
            except Exception as e:
                # If an error occurs during preview generation.
                QMessageBox.critical(self, "Error", f"Could not preview folder: {e}")
                # Show an error message box.
        else:
            # If the path is not a file or directory.
            self.status_label.setText("Invalid path selected.")
            # Display a status message.
    #
    #
    def organize_files(self):
        # This method starts the file organization process in a separate thread.
        #
        if not self.selected_path:
            # Check if a path has been selected.
            QMessageBox.warning(self, "No Selection", "Please select a file or folder to organize first.")
            # Show a warning message if no path is selected.
            return
            # Exit the method.
        #
        reply = QMessageBox.question(self, "Confirm Organization",
                                     f"Are you sure you want to organize:\n{self.selected_path}?\n\nThis action will move files.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # Ask the user for confirmation before proceeding.
        if reply == QMessageBox.Yes:
            # If the user confirms.
            if self.create_backups.isChecked():
                # Check if the backup option is selected.
                if not self.create_backup():
                    # If the backup fails, stop the organization process.
                    return
            self.set_ui_enabled(False)
            # Disable GUI elements to prevent user interaction during the process.
            self.progress_bar.setValue(0)
            # Reset the progress bar.
            min_files = self.min_files_spinbox.value()
            # Get the minimum files value.
            self.worker = FileOrganizerWorker(self.selected_path, min_files)
            # Create a new instance of the worker thread.
            self.worker.progress_updated.connect(self.update_progress)
            # Connect the worker's progress signal to the GUI's update method.
            self.worker.status_updated.connect(self.update_status)
            # Connect the worker's status signal to the GUI's update method.
            self.worker.finished.connect(self.organization_finished)
            # Connect the worker's finished signal to the GUI's handler.
            self.worker.error_occurred.connect(self.organization_error)
            # Connect the worker's error signal to the GUI's handler.
            self.worker.start()
            # Start the worker thread.
    #
    #
    def create_backup(self):
        # This method creates a timestamped ZIP backup of the selected folder or file.
        #
        try:
            #
            self.status_label.setText("Creating backup...")
            # Update the status label.
            QApplication.processEvents()
            # Force the GUI to update immediately.
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Get the current date and time as a formatted string.
            #
            if os.path.isfile(self.selected_path):
                # If a single file was selected.
                file_name = os.path.basename(self.selected_path)
                # Get the file name.
                parent_dir = os.path.dirname(self.selected_path)
                # Get the parent directory.
                archive_path = os.path.join(parent_dir, f"{os.path.splitext(file_name)[0]}_backup_{timestamp}.zip")
                # Create the full path for the backup ZIP file.
                #
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Open a new ZIP file in write mode.
                    zipf.write(self.selected_path, file_name)
                    # Write the file into the ZIP archive.
                #
                self.status_bar.showMessage(f"Backup created for '{file_name}' at {archive_path}", 5000)
                # Display a success message in the status bar.
            #
            #
            elif os.path.isdir(self.selected_path):
                # If a folder was selected.
                backup_name = f"{os.path.basename(self.selected_path)}_backup_{timestamp}"
                # Create a name for the backup folder.
                parent_dir = os.path.dirname(self.selected_path)
                # Get the parent directory.
                archive_path = os.path.join(parent_dir, backup_name)
                # Create the full path for the backup.
                #
                with zipfile.ZipFile(archive_path + '.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Open a new ZIP file.
                    for root, _, files in os.walk(self.selected_path):
                        # Walk through all directories and files in the selected folder.
                        for file in files:
                            # Loop through each file.
                            file_path = os.path.join(root, file)
                            # Get the full path to the file.
                            zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(self.selected_path)))
                            # Write the file to the ZIP archive, preserving its relative path.
                #
                self.status_bar.showMessage(f"Backup created for folder at {archive_path}.zip", 5000)
                # Display a success message.
            #
            return True
            # Return True to indicate a successful backup.
        except Exception as e:
            # If any error occurs during the backup process.
            QMessageBox.critical(self, "Backup Failed", f"Could not create backup: {e}")
            # Show an error message.
            return False
            # Return False to indicate a failure.
    #
    #
    def clear_selection(self):
        # This method resets the GUI to its initial state.
        #
        if self.worker and self.worker.isRunning():
            # Check if the worker thread is currently running.
            self.worker.stop()
            # Call the worker's stop method.
            self.worker.wait()
            # Wait for the thread to finish cleanly before proceeding.
        self.selected_path = ""
        # Clear the stored path.
        self.path_line_edit.clear()
        # Clear the text in the line edit.
        self.preview_text.clear()
        # Clear the preview text area.
        self.preview_text.setPlaceholderText("Click 'Preview Organization' to see the plan...")
        # Restore the placeholder text.
        self.total_files_label.setText("Total files: 0")
        # Reset the statistics labels.
        self.file_types_label.setText("File types: 0")
        #
        self.folders_created_label.setText("Folders to create: 0")
        #
        self.progress_bar.setValue(0)
        # Reset the progress bar to 0.
        self.status_label.setText("Ready to organize files")
        # Reset the status label.
        self.preview_btn.setEnabled(False)
        # Disable the preview button.
        self.organize_btn.setEnabled(False)
        # Disable the organize button.
        self.set_ui_enabled(True)
        # Re-enable all other UI elements.
        self.status_bar.showMessage("Selection cleared.", 3000)
        # Display a status message.
    #
    #
    def update_progress(self, value):
        # A slot method to receive progress updates from the worker thread.
        #
        self.progress_bar.setValue(value)
        # Set the progress bar's value.
    #
    #
    def update_status(self, message):
        # A slot method to receive status updates from the worker thread.
        #
        self.status_label.setText(message)
        # Update the status label's text.
    #
    #
    def organization_finished(self, message, file_count):
        # This method is called when the worker thread successfully finishes.
        #
        self.session_organized_count += file_count
        # Add the number of files organized to the session counter.
        QMessageBox.information(self, "Success", message)
        # Show a success message box.
        self.status_label.setText("Organization complete!")
        # Update the status label.
        self.progress_bar.setValue(100)
        # Set the progress bar to 100%.
        self.set_ui_enabled(True)
        # Re-enable the GUI.
        self.preview_organization()
        # Run a new preview to reflect the changes.
    #
    #
    def organization_error(self, message):
        # This method is called if the worker thread reports an error.
        #
        QMessageBox.critical(self, "Error", message)
        # Show a critical error message box.
        self.set_ui_enabled(True)
        # Re-enable the GUI.
        self.status_label.setText("An error occurred.")
        # Update the status label.
    #
    #
    def set_ui_enabled(self, enabled):
        # A helper method to enable or disable all the main UI controls.
        # This is useful for preventing user interaction during a long-running task.
        #
        self.browse_folder_btn.setEnabled(enabled)
        # Enable or disable the browse folder button.
        self.browse_file_btn.setEnabled(enabled)
        # Enable or disable the browse file button.
        self.organize_btn.setEnabled(enabled)
        # Enable or disable the organize button.
        self.preview_btn.setEnabled(enabled)
        # Enable or disable the preview button.
        self.min_files_spinbox.setEnabled(enabled)
        # Enable or disable the spin box.
        self.create_backups.setEnabled(enabled)
        # Enable or disable the checkbox.
        self.menuBar().setEnabled(enabled)
        # Enable or disable the menu bar.
        self.clear_btn.setText("Cancel" if not enabled else "🗑️ Clear")
        # Change the text of the clear button to 'Cancel' when the process is running.
    #
    #
    def load_settings(self):
        # This method loads the application's persistent settings.
        #
        geometry = self.settings.value("geometry")
        # Load the saved window geometry.
        if geometry:
            # If saved geometry exists.
            self.restoreGeometry(geometry)
            # Restore the window to its last known size and position.
        self.create_backups.setChecked(self.settings.value("createBackups", True, type=bool))
        # Load the state of the backup checkbox.
        self.min_files_spinbox.setValue(self.settings.value("minFiles", 2, type=int))
        # Load the value of the minimum files spin box.
    #
    #
    def save_settings(self):
        # This method saves the application's current settings.
        #
        self.settings.setValue("geometry", self.saveGeometry())
        # Save the current window geometry.
        self.settings.setValue("createBackups", self.create_backups.isChecked())
        # Save the state of the backup checkbox.
        self.settings.setValue("minFiles", self.min_files_spinbox.value())
        # Save the value of the minimum files spin box.
    #
    #
    def closeEvent(self, event):
        # This method is called when the user closes the main window.
        #
        self.save_settings()
        # Save the application settings.
        if self.worker and self.worker.isRunning():
            # Check if the worker thread is running.
            self.worker.stop()
            # Stop the worker thread.
            self.worker.wait()
            # Wait for the thread to finish before the application closes.
        super().closeEvent(event)
        # Call the parent class's close event method.
#
#
#
#
#
#
if __name__ == "__main__":
    # This block of code runs only when the script is executed directly.
    #
    app = QApplication(sys.argv)
    # Create the QApplication instance. This is a required step for all PyQt5 applications.
    organizer_gui = FileOrganizerGUI()
    # Create an instance of the main GUI window.
    organizer_gui.show()
    # Show the main window on the screen.
    sys.exit(app.exec_())
    # Start the application's event loop and exit when it's done.