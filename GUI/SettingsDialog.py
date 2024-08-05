from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
	settingsSaved = pyqtSignal(int, str)

	def __init__(self):
		super().__init__()

		self.setWindowTitle("Settings")
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
		self.init_ui()

	def init_ui(self):
		layout = QVBoxLayout()

		# Textbox for entering the baud rate
		self.baudrate_label = QLabel("Baud Rate:")
		layout.addWidget(self.baudrate_label)
		self.baudrate_input = QLineEdit()
		layout.addWidget(self.baudrate_input)

		# Textbox for entering the port
		self.port_label = QLabel("Port:")
		layout.addWidget(self.port_label)
		self.port_input = QLineEdit()
		layout.addWidget(self.port_input)

		# Save button
		self.save_button = QPushButton("Save")
		self.save_button.clicked.connect(self.saveSettings)
		layout.addWidget(self.save_button)

		self.setLayout(layout)

	def saveSettings(self):
		baudRate = self.baudrate_input.text()
		try:
			baudRate = int(baudRate)
		except ValueError:
			# If not an integer, show an error message and return without emitting the signal
			QMessageBox.critical(self, "Error", "Baud rate must be an integer.")
			return
		self.settingsSaved.emit(baudRate, self.port_input.text())

		self.accept()  # Close the dialog

	def setValues(self, baudRate, port):
		self.baudrate_input.setText(str(baudRate))
		self.port_input.setText(port)
