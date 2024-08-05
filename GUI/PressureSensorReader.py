import json
import serial
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np

MBAR = 0
TORR = 1
PA = 2
D = [11.33, 11.46, 9.33]
UNIT = ["mbar", "torr", "pa"]
DEBUG = False

class DataWriteRead(QThread):

	data_received = pyqtSignal(dict)
	DATA_UNIT = "Unit"
	DATA = "Data"
	def __init__(self, Port = "COM3", BaudRate = 115200):
		super().__init__()
		self.setCOMPort(Port, BaudRate)

	def setCOMPort(self, Port = "COM3", BaudRate = 115200):
		try:
			self.ser = serial.Serial(Port, BaudRate)
		except serial.serialutil.SerialException as e:
			raise ValueError(f"No port named {Port} found") from e

	def setDataReadyCallback(self, callback):
		self.data_received.connect(callback)

	def run(self):
		while True:
			if not DEBUG:
				try:
					data = json.loads(self.ser.readline().decode('utf-8').strip())
				except json.JSONDecodeError:
					pass
			else:
				data = {self.DATA_UNIT : MBAR,
						self.DATA : np.random.randint(1,11)}

			self.data_received.emit(data)

	def stop(self):
		self.terminate()
		self.ser.close()

	def write(self, data):
		data = json.dumps(data)
		self.ser.write((data + "\n").encode('utf-8'))

