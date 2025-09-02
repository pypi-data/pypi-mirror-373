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
class Device_ExtraCommands(enum.IntEnum):
	# .......... 10
	EXTERNAL_TRAJECTORY_SETPOINT 	= 0x11,
	TUNE							= 0x12,
	# .......... 39


Index_Blue = enum.IntEnum('Index', [
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
	'CurrentSetting_Drive',
	'CurrentSetting_Hold',
	'Microstepping',
	'AutoStepInterpolation_enable',
	'AutoStepInterpolation_setting',
	'MaxAcceleration',
	'MaxDeceleration',
	'MaxSpeed',
	'MaxPosition',
	'MinPosition',
	'ExternalSetpoint_BufferSize',
	'ExternalSetpoint_PhaseDelay',
	'ExternalSetpoint_IntervalTime',
	'CurrentPosition',
	'CurrentSpeed',
	'CurrentAccel',
	'LimitSwitch_1',
	'LimitSwitch_2',
	'TargetVelocity',
	'TargetPosition',
	'DesiredTime',
	'DesiredAccel',
	'DesiredMaxSpeed',
	'Setpoint',
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


class Blue(SMD_Device):
	_PRODUCT_TYPE = 0xCA
	_PACKAGE_ESSENTIAL_SIZE = 6
	_STATUS_KEY_LIST = ['EEPROM', 'Software Version', 'Hardware Version']
	__RELEASE_URL = "https://api.github.com/repos/AAcrome-Smart-Motion-Devices/SMD-Blue-Firmware/releases/{version}"

	class Operation_Mode():
		Position_Internal_Trajectory = 0
		Position_External_Trajectory = 1
		Velocity = 2
	
	class microStepping():
		FULL_STEP 				= 0b0000
		FULL_STEP_71 			= 0b0001
		HALF_STEP_NON_CIRCULAR 	= 0b0010
		HALF_STEP 				= 0b0011
		_4_STEP					= 0b0100
		_8_STEP 				= 0b0101
		_16_STEP 				= 0b0110
		_32_STEP 				= 0b0111
		_64_STEP 				= 0b1000
		_128_STEP 				= 0b1001
		_256_STEP 				= 0b1010

	class autoStepInterpolation():
		_256_Interpolation 	= 0b00
		_128_Interpolation 	= 0b01
		_64_Interpolation	= 0b10
		_32_Interpolation	= 0b11


	def __init__(self, ID, port:SerialPort) -> bool:
		self.__ack_size = 0
		if ID > 254 or ID < 0:
			raise ValueError("Device ID can not be higher than 254 or lower than 0!")
		device_special_data = [
            Data_(Index_Blue.Header, 'B', False, 0x55),
            Data_(Index_Blue.DeviceID, 'B'),
			Data_(Index_Blue.DeviceFamily, 'B'),
            Data_(Index_Blue.PackageSize, 'B'),
            Data_(Index_Blue.Command, 'B'),
			Data_(Index_Blue.Status, 'B'),
            Data_(Index_Blue.HardwareVersion, 'I'),
            Data_(Index_Blue.SoftwareVersion, 'I'),
            Data_(Index_Blue.Baudrate, 'I'),
			# user parameter starts
			Data_(Index_Blue.OperationMode, 'B'),
			Data_(Index_Blue.Enable, 'B'),
			Data_(Index_Blue.CurrentSetting_Drive, 'B'),
			Data_(Index_Blue.CurrentSetting_Hold, 'B'),
			Data_(Index_Blue.Microstepping, 'B'),
			Data_(Index_Blue.AutoStepInterpolation_enable, 'B'),
			Data_(Index_Blue.AutoStepInterpolation_setting, 'B'),
			Data_(Index_Blue.MaxAcceleration, 'f'),
			Data_(Index_Blue.MaxDeceleration, 'f'),
			Data_(Index_Blue.MaxSpeed, 'f'),
			Data_(Index_Blue.MaxPosition, 'i'),
			Data_(Index_Blue.MinPosition, 'i'),
			Data_(Index_Blue.ExternalSetpoint_BufferSize, 'H'),
			Data_(Index_Blue.ExternalSetpoint_PhaseDelay, 'H'),
			Data_(Index_Blue.ExternalSetpoint_IntervalTime, 'I'),
			Data_(Index_Blue.CurrentPosition, 'd'),
			Data_(Index_Blue.CurrentSpeed, 'd'),
			Data_(Index_Blue.CurrentAccel, 'd'),
			Data_(Index_Blue.LimitSwitch_1, 'B'),
			Data_(Index_Blue.LimitSwitch_2, 'B'),
			Data_(Index_Blue.TargetVelocity, 'f'),
			Data_(Index_Blue.TargetPosition, 'i'),
			Data_(Index_Blue.DesiredTime, 'f'),
			Data_(Index_Blue.DesiredAccel, 'f'),
			Data_(Index_Blue.DesiredMaxSpeed, 'f'),
			Data_(Index_Blue.Setpoint, 'f'),
			# user parameter end
			Data_(Index_Blue.Config_TimeStamp, 'Q'),
			Data_(Index_Blue.Config_Description, '100s'),
            Data_(Index_Blue.CRCValue, 'I'),
        ]
		super().__init__(ID, self._PRODUCT_TYPE, device_special_data, port)
		self._vars[Index_Blue.DeviceID].value(ID)

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

		self.set_variables([Index_Blue.Enable, en])
		self._post_sleep()

	def set_microstepping(self, microstepping:int, auto_stepping_enable:bool = True, auto_stepping_interpolation:int= autoStepInterpolation._256_Interpolation):
		if (microstepping > self.microStepping._256_STEP or microstepping < 0):
			raise "microstepping is not valid."
		if (auto_stepping_interpolation > self.autoStepInterpolation._32_Interpolation or auto_stepping_interpolation < self.autoStepInterpolation._256_Interpolation):
			raise "auto_stepping_interpolation is not valid."
		
		self.set_variables([Index_Blue.Microstepping, microstepping], [Index_Blue.AutoStepInterpolation_enable, auto_stepping_enable], [Index_Blue.AutoStepInterpolation_setting, auto_stepping_interpolation])
		self._post_sleep()


	def set_config_timeStamp(self):
		epoch_seconds = int(time.time())
		self.set_variables([Index_Blue.Config_TimeStamp, epoch_seconds])
		self._post_sleep()
		
	def set_config_description(self, description:str):
		if len(description) >= 100:
			text = description[:99] + '\0'
		else:
			text = description + '\0'
			text = text.ljust(100, ' ')
		text = text.encode('ascii')  # veya utf-8 eğer uyumluysa

		self.set_variables([Index_Blue.Config_Description, text])
		self._post_sleep()