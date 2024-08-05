import os
import sys
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QFrame, \
	QButtonGroup, QRadioButton, QHBoxLayout, QComboBox, QMessageBox, QFileDialog, QSizePolicy, QAction, QSplitter, \
	QMenuBar
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt, QEventLoop
import PressureSensorReader as PSR

import numpy as np
from DataViewer import GraphWindow
from SettingsDialog import SettingsDialog

basedir = os.path.dirname(__file__)

DEBUG = False



class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.port = "COM3"
		self.baudRate = 115200
		self.pressure = []
		self.currentDataUnit = PSR.TORR
		self.timeElapsed = 0
		self.dataRecordRate = 1  # Default
		self.graph_window = None
		self.setWindowTitle("Pressure Reader")
		self.setGeometry(100, 100, 300, 300)
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
		self.setWindowIcon(QIcon(os.path.join(basedir, "icon.png")))

		instruction_text = "<span style='font-size: 10pt;'><b>Instructions</b><br>Connect the pressure reader to the computer using a USB-C to USB cable."
		self.instruction = QLabel(instruction_text, self)
		self.instruction.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

		self.start_button = QPushButton("Start", self)
		self.start_button.clicked.connect(self.startClicked)

		self.stop_button = QPushButton("Stop", self)
		self.stop_button.clicked.connect(self.stopClicked)
		self.stop_button.setEnabled(False)

		self.plot_button = QPushButton("Plot Data", self)
		self.plot_button.clicked.connect(self.plotClicked)
		# self.plot_button.setEnabled(False)

		self.export_button = QPushButton("Export Data", self)
		self.export_button.clicked.connect(self.exportClicked)
		# self.export_button.setEnabled(False)

		self.settingsButton = QPushButton("Settings", self)
		self.settingsButton.clicked.connect(self.settingsClicked)

		self.data_record_rate_label = QLabel("Data Recording Interval (min)", self)
		self.data_record_rate_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.data_record_rate_edit = QLineEdit(self)
		self.data_record_rate_edit.setText("3")
		self.data_record_rate_edit.setPlaceholderText("Enter data record interval")
		self.data_record_rate_edit.setValidator(QIntValidator())

		self.separator1 = QFrame(self)
		self.separator1.setFrameShape(QFrame.HLine)
		self.separator1.setFrameShadow(QFrame.Sunken)
		self.separator2 = QFrame(self)
		self.separator2.setFrameShape(QFrame.HLine)
		self.separator2.setFrameShadow(QFrame.Sunken)

		self.radio_mbar = QRadioButton("mbar", self)
		self.radio_torr = QRadioButton("torr", self)
		self.radio_pascal = QRadioButton("pascal", self)
		self.radio_group = QButtonGroup(self)
		self.radio_group.addButton(self.radio_mbar, id=0)
		self.radio_group.addButton(self.radio_torr, id=1)
		self.radio_group.addButton(self.radio_pascal, id=2)

		button = self.radio_group.button(self.currentDataUnit)
		if button:
			button.setChecked(True)

		hlayout = QHBoxLayout()
		hlayout.addStretch()
		hlayout.addWidget(self.radio_mbar)
		hlayout.addWidget(self.radio_torr)
		hlayout.addWidget(self.radio_pascal)
		hlayout.addStretch()
		hlayout.setContentsMargins(10, 10, 10, 10)  # Left, Top, Right, Bottom
		hlayout.setSpacing(20)  # Space between the radio buttons

		self.mainLayout = QVBoxLayout()

		self.mainLayout.addWidget(self.instruction)
		self.mainLayout.addSpacing(10)
		self.mainLayout.addWidget(self.separator1)
		self.mainLayout.addSpacing(10)
		self.mainLayout.addWidget(self.data_record_rate_label)
		self.mainLayout.addWidget(self.data_record_rate_edit)
		self.mainLayout.addLayout(hlayout)

		buttonLayoutTop = QHBoxLayout()
		buttonLayoutBottom = QHBoxLayout()
		buttonLayoutTop.addWidget(self.start_button)
		buttonLayoutTop.addWidget(self.stop_button)
		buttonLayoutBottom.addWidget(self.plot_button)
		buttonLayoutBottom.addWidget(self.export_button)

		self.mainLayout.addLayout(buttonLayoutTop)
		self.mainLayout.addLayout(buttonLayoutBottom)
		self.mainLayout.addWidget(self.settingsButton)
		self.mainLayout.addSpacing(10)
		self.mainLayout.addWidget(self.separator2)
		self.mainLayout.addSpacing(10)
		self.pressureLabel, self.pressureValueLabel = self.createPressureSection()
		self.mainLayout.addWidget(self.pressureLabel)
		self.mainLayout.addWidget(self.pressureValueLabel)

		self.container = QWidget()
		self.container.setLayout(self.mainLayout)
		self.setCentralWidget(self.container)

		QTimer.singleShot(0, self.done)

	def enableRadioButtons(self, enable):
		self.radio_mbar.setEnabled(enable)
		self.radio_pascal.setEnabled(enable)
		self.radio_torr.setEnabled(enable)

	def createPressureSection(self):
		pressureLabel = QLabel("Pressure", self)
		pressureLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		resultFont = pressureLabel.font()
		resultFont.setPointSize(10)
		pressureLabel.setFont(resultFont)
		pressureValueLabel = QLabel("", self)
		pressureValueLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		pressureValueLabel.setFont(resultFont)
		return pressureLabel, pressureValueLabel


	def setEnabled(self, enable):
		if not DEBUG:
			self.data_record_rate_edit.setEnabled(enable)
			self.data_record_rate_label.setEnabled(enable)
			self.start_button.setEnabled(enable)
			self.radio_mbar.setEnabled(enable)
			self.radio_torr.setEnabled(enable)
			self.radio_pascal.setEnabled(enable)
			self.pressureValueLabel.setEnabled(enable)
			self.pressureLabel.setEnabled(enable)
			self.export_button.setEnabled(enable)
			self.plot_button.setEnabled(enable)

	def stopClicked(self):
		print("Stop Clicked")
		self.start_button.setEnabled(True)
		self.stop_button.setEnabled(False)
		self.data_record_rate_edit.setEnabled(True)
		self.data_record_rate_label.setEnabled(True)
		self.export_button.setEnabled(True)
		self.enableRadioButtons(True)
		self.settingsButton.setEnabled(True)
		self.readerWriter.stop()

	def showWarning(self):
		reply = QMessageBox.question(self, 'Warning',
									 'Starting again will erase any previously stored data, Save before starting?',
									 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self.exportClicked()
			return True

		return False

	def startClicked(self):
		print("Start Clicked")
		self.dataRecordRate = int(self.data_record_rate_edit.text())

		if len(self.pressure) != 0:
			if self.showWarning():
				return 0



		self.pressure = []
		self.currentDataUnit = self.getCurrentPressureUnit()
		if self.graph_window is not None:
			self.graph_window.setYLabel("Pressure (" + PSR.UNIT[self.currentDataUnit] + ")")
			self.graph_window.clearGraph()


		print("Creating ReaderWriter Object")
		try:
			self.readerWriter = PSR.DataWriteRead(self.port,self.baudRate)
			self.readerWriter.setDataReadyCallback(self.updateUI)
			self.readerWriter.write({PSR.DataWriteRead.DATA_UNIT:self.currentDataUnit})
			self.readerWriter.start()

			self.start_button.setEnabled(False)
			self.data_record_rate_edit.setEnabled(False)
			self.data_record_rate_label.setEnabled(False)
			self.export_button.setEnabled(False)
			self.enableRadioButtons(False)
			self.settingsButton.setEnabled(False)
			self.stop_button.setEnabled(True)

		except ValueError as e:
			print(e)
			self.showErrorMessage(str(e))



	def plotClicked(self):
		print("Plot Clicked")
		self.graph_window = GraphWindow(self)
		self.graph_window.setYLabel("Pressure (" + PSR.UNIT[self.currentDataUnit] + ")")
		t = [i * self.dataRecordRate for i in range(1, len(self.pressure) + 1)]
		self.graph_window.plotData(t, self.pressure)
		self.graph_window.show()
		self.plot_button.setEnabled(False)

	def exportClicked(self):
		self.saveData()

	def updateUI(self, data):
		print("updateUI")
		pressure = data.get(PSR.DataWriteRead.DATA)
		self.pressureValueLabel.setText(str(pressure))
		self.timeElapsed += 1
		if (self.dataRecordRate * 1 if DEBUG else 60) / self.timeElapsed < 1:
			print("Data Recorded")
			self.timeElapsed = 0

			self.pressure.append(data.get(PSR.DataWriteRead.DATA, 0))

			if self.graph_window is not None:
				t = [i * self.dataRecordRate for i in range(1, len(self.pressure) + 1)]
				self.graph_window.clearGraph()
				self.graph_window.plotData(t, self.pressure)

	def done(self):
		self.adjustSize()

	def getCurrentPressureUnit(self):
		checked_button = self.radio_group.checkedButton()
		index = self.radio_group.id(checked_button)
		return index

	def saveData(self):
		# Create a DataFrame from the data
		t = [i * self.dataRecordRate for i in range(1, len(self.pressure) + 1)]
		dataDict = {'Time (min)': t,
					f"Pressure ({self.currentDataUnit})": self.pressure}

		data = pd.DataFrame(dataDict)

		# Open file dialog to get save location and filename
		options = QFileDialog.Options()
		file_name, _ = QFileDialog.getSaveFileName(self, "Save Data as Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options)

		if file_name:
			# Save the DataFrame to the specified Excel file
			data.to_excel(file_name, index=False)
			print(f"Data saved to {file_name}")

	def onGraphClosed(self):
		self.graph_window = None
		self.plot_button.setEnabled(True)

	def closeEvent(self, event):
		if hasattr(self,"readerWriter"):
			if self.readerWriter is not None:
				self.readerWriter.stop()
		event.accept()

	def settingsClicked(self):
		dialog = SettingsDialog()
		dialog.setValues(self.baudRate, self.port)
		dialog.settingsSaved.connect(self.saveSettings)
		dialog.exec_()

	def saveSettings(self, baudRate, port):
		self.baudRate = baudRate
		self.port = port

	def showErrorMessage(self, message):
		error_dialog = QMessageBox()
		error_dialog.setIcon(QMessageBox.Critical)
		error_dialog.setWindowTitle("Error")
		error_dialog.setText(message)
		error_dialog.setStandardButtons(QMessageBox.Ok)
		error_dialog.exec_()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())

# ToDo:
# ADD LEGEND
# SIMPLIFY PLOT DATA BY GIVING ALL THE DATA ONCE AS ARGUMENT
