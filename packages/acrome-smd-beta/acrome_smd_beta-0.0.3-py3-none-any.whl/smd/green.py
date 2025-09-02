import struct
from crccheck.crc import Crc32Mpeg2 as CRC32
import serial
import time
from packaging.version import parse as parse_version
import requests
import hashlib
import tempfile
from stm32loader.main import main as stm32loader_main
import enum
from smd.SMD_device import *


# enter here for extra commands: 
#class Device_ExtraCommands(enum.IntEnum):
	# .......... start with 11
	# .......... end of extra commmands max: 39


Index_Green = enum.IntEnum('Index', [
	'Header',
	'DeviceID',
	'DeviceFamily',
	'PackageSize',
	'Command',
	'Status',
	'HardwareVersion',
	'SoftwareVersion',
	'Baudrate', #'WritableStart' = iBaudrate
	# user parameter start
	'OperationMode',
	'Enable',
	'Vbus_read',
	'Temprature_read',
	'currentId_loop_kp',
	'currentId_loop_ki',
	'currentId_loop_kd',
	'currentIq_loop_kp',
	'currentIq_loop_ki',
	'currentIq_loop_kd',
	'velocity_loop_kp',
	'velocity_loop_ki',
	'velocity_loop_kd',
	'position_loop_kp',
	'position_loop_ki',
	'position_loop_kd',
	'max_position',
	'min_position',
	'max_velocity',
	'max_current',
	'current_Va',
	'current_Vb',
	'current_Vc',
	'current_Ia',
	'current_Ib',
	'current_Ic',
	'current_Id',
	'current_Iq',
	'current_velocity',
	'current_position',
	'current_electrical_degree',
	'current_electrical_radian',
	'setpoint_current',
	'setpoint_velocity',
	'setpoint_position',
	'openloop_voltage_size',
	'openloop_angle_degree',
	'current_lock_angle_degree',
	# user parameter end
	'Config_TimeStamp',
	'Config_Description',
	'CRCValue',
], start=0)



def scan_blue_devices(port:SerialPort):
	device = Blue(0, port)
	available_devices = []

	for id in range(0,255):
		device._id = id
		if(device.ping()):
			available_devices.append(id)

	return available_devices


class Green(SMD_Device):
	_PRODUCT_TYPE = 0xDA
	_PACKAGE_ESSENTIAL_SIZE = 6
	_STATUS_KEY_LIST = ['EEPROM', 'Software Version', 'Hardware Version']
	__RELEASE_URL = "https://api.github.com/repos/AAcrome-Smart-Motion-Devices/SMD-Blue-Firmware/releases/{version}"

	class Operation_Mode():
		OPERATION_OPENLOOP = 0
		OPERATION_CURRENT_LOCK = 1
		OPERATION_FOC_TORQUE = 2
		OPERATION_FOC_VELOCITY = 3
		OPERATION_FOC_POSITION = 4

	def __init__(self, ID, port:SerialPort) -> bool:
		self.__ack_size = 0
		if ID > 254 or ID < 0:
			raise ValueError("Device ID can not be higher than 254 or lower than 0!")
		device_special_data = [
            Data_(Index_Green.Header, 'B', False, 0x55),
            Data_(Index_Green.DeviceID, 'B'),
			Data_(Index_Green.DeviceFamily, 'B'),
            Data_(Index_Green.PackageSize, 'B'),
            Data_(Index_Green.Command, 'B'),
			Data_(Index_Green.Status, 'B'),
            Data_(Index_Green.HardwareVersion, 'I'),
            Data_(Index_Green.SoftwareVersion, 'I'),
            Data_(Index_Green.Baudrate, 'I'),
			# user parameter starts
			Data_(Index_Green.OperationMode, 'B'),
			Data_(Index_Green.Enable, 'B'),
			Data_(Index_Green.Vbus_read, 'f'),
			Data_(Index_Green.Temprature_read, 'f'),
			Data_(Index_Green.currentId_loop_kp, 'f'),
			Data_(Index_Green.currentId_loop_ki, 'f'),
			Data_(Index_Green.currentId_loop_kd, 'f'),
			Data_(Index_Green.currentIq_loop_kp, 'f'),
			Data_(Index_Green.currentIq_loop_ki, 'f'),
			Data_(Index_Green.currentIq_loop_kd, 'f'),
			Data_(Index_Green.velocity_loop_kp, 'f'),
			Data_(Index_Green.velocity_loop_ki, 'f'),
			Data_(Index_Green.velocity_loop_kd, 'f'),
			Data_(Index_Green.position_loop_kp, 'f'),
			Data_(Index_Green.position_loop_ki, 'f'),
			Data_(Index_Green.position_loop_kd, 'f'),
			Data_(Index_Green.max_position, 'i'),
			Data_(Index_Green.min_position, 'i'),
			Data_(Index_Green.max_velocity, 'f'),
			Data_(Index_Green.max_current, 'f'),
			Data_(Index_Green.current_Va, 'f'),
			Data_(Index_Green.current_Vb, 'f'),
			Data_(Index_Green.current_Vc, 'f'),
			Data_(Index_Green.current_Ia, 'f'),
			Data_(Index_Green.current_Ib, 'f'),
			Data_(Index_Green.current_Ic, 'f'),
			Data_(Index_Green.current_Id, 'f'),
			Data_(Index_Green.current_Iq, 'f'),
			Data_(Index_Green.current_velocity, 'f'),
			Data_(Index_Green.current_position, 'i'),
			Data_(Index_Green.current_electrical_degree, 'f'),
			Data_(Index_Green.current_electrical_radian, 'f'),
			Data_(Index_Green.setpoint_current, 'f'),
			Data_(Index_Green.setpoint_velocity, 'f'),
			Data_(Index_Green.setpoint_position, 'f'),
			Data_(Index_Green.openloop_voltage_size, 'f'),
			Data_(Index_Green.openloop_angle_degree, 'f'),
			Data_(Index_Green.current_lock_angle_degree, 'f'),
			# user parameter end
			Data_(Index_Green.Config_TimeStamp, 'Q'),
			Data_(Index_Green.Config_Description, '100s'),
            Data_(Index_Green.CRCValue, 'I'),
        ]
		super().__init__(ID, self._PRODUCT_TYPE, device_special_data, port)
		self._vars[Index_Green.DeviceID].value(ID)

	# user start for extra commands.
	#def command(self): 

	def __del__(self):
		pass

	def get_latest_fw_version(self):
		""" Get the latest firmware version from the Github servers.

		Returns:
			String: Latest firmware version
		"""
		response = requests.get(url=self.__class__.__RELEASE_URL.format(version='latest'))
		if (response.status_code in [200, 302]):
			return (response.json()['tag_name'])

	def update_fw_version(self, version=''):
		""" Update firmware version with respect to given version string.

		Args:
			id (int): The device ID of the driver
			version (str, optional): Desired firmware version. Defaults to ''.

		Returns:
			Bool: True if the firmware is updated
		"""

		fw_file = tempfile.NamedTemporaryFile("wb+",delete=False)
		if version == '':
			version = 'latest'
		else:
			version = 'tags/' + version

		response = requests.get(url=self.__class__.__RELEASE_URL.format(version=version))
		if response.status_code in [200, 302]:
			assets = response.json()['assets']

			fw_dl_url = None
			md5_dl_url = None
			for asset in assets:
				if '.bin' in asset['name']:
					fw_dl_url = asset['browser_download_url']
				elif '.md5' in asset['name']:
					md5_dl_url = asset['browser_download_url']

			if None in [fw_dl_url, md5_dl_url]:
				raise Exception("Could not found requested firmware file! Check your connection to GitHub.")

			#  Get binary firmware file
			md5_fw = None
			response = requests.get(fw_dl_url, stream=True)
			if (response.status_code in [200, 302]):
				fw_file.write(response.content)
				md5_fw = hashlib.md5(response.content).hexdigest()
			else:
				raise Exception("Could not fetch requested binary file! Check your connection to GitHub.")

			#  Get MD5 file
			response = requests.get(md5_dl_url, stream=True)
			if (response.status_code in [200, 302]):
				md5_retreived = response.text.split(' ')[0]
				if (md5_fw == md5_retreived):

					# Put the driver in to bootloader mode
					self.enter_bootloader()
					time.sleep(0.1)

					# Close serial port
					serial_settings = self._port._ph.get_settings()
					self._port._ph.close()

					# Upload binary
					args = ['-p', self._port._ph.portstr, '-b', str(115200), '-e', '-w', '-v', fw_file.name]
					stm32loader_main(*args)

					# Delete uploaded binary
					if (not fw_file.closed):
						fw_file.close()

					# Re open port to the user with saved settings
					self._port._ph.apply_settings(serial_settings)
					self._port._ph.open()
					return True

				else:
					raise Exception("MD5 Mismatch!")
			else:
				raise Exception("Could not fetch requested MD5 file! Check your connection to GitHub.")
		else:
			raise Exception("Could not found requested firmware files list! Check your connection to GitHub.")
		
	def enable_torque(self, en: bool):
		""" Enable power to the motor of the driver.

    	Args:
    	    id (int): The device ID of the driver
    	    en (bool): Enable. True enables the torque.
    	"""

		self.set_variables([Index_Green.Enable, en])
		self._post_sleep()

	def set_config_timeStamp(self):
		epoch_seconds = int(time.time())
		self.set_variables([Index_Green.Config_TimeStamp, epoch_seconds])
		self._post_sleep()
		
	def set_config_description(self, description:str):
		if len(description) >= 100:
			text = description[:99] + '\0'
		else:
			text = description + '\0'
			text = text.ljust(100, ' ')
		text = text.encode('ascii')  # veya utf-8 eğer uyumluysa

		self.set_variables([Index_Green.Config_Description, text])
		self._post_sleep()



	def get_FOC_parameters(self, package_number:int):
		if package_number >= 3:
			raise "invalid package number ex: 0, 1, 2"
		classic_package = [
			Index_Green.Enable,
			Index_Green.current_Id, Index_Green.current_Iq,
			Index_Green.current_velocity, Index_Green.current_position,
			Index_Green.Temprature_read,
		]
		package_0 = [
			Index_Green.currentId_loop_kp, 
			Index_Green.currentId_loop_ki, 
			Index_Green.currentId_loop_kd, 
			Index_Green.currentIq_loop_kp, 
			Index_Green.currentIq_loop_ki, 
			Index_Green.currentIq_loop_kd, 
		]
		package_1 = [
			Index_Green.velocity_loop_kp,
			Index_Green.velocity_loop_ki,
			Index_Green.velocity_loop_kd,
		]
		package_2 = [
			Index_Green.position_loop_kp,
			Index_Green.position_loop_ki,
			Index_Green.position_loop_kd,
		]

		if package_number == 0:
			return self.get_variables(*classic_package , *package_0)
			
		elif package_number == 1:
			return self.get_variables(*classic_package , *package_1)
			
		elif package_number == 2:
			return self.get_variables(*classic_package , *package_2)