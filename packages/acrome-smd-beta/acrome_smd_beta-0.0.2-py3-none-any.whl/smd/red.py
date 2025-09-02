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

class InvalidIndexError(BaseException):
    pass

class UnsupportedHardware(BaseException):
    pass

class UnsupportedFirmware(BaseException):
    pass

# enter here for extra commands: 
class ExtraCommands_Red(enum.IntEnum):
    RESET_ENC = 0x06
    TUNE = 0x07
    ERROR_CLEAR = 0x18
    SYNC_WRITE = 0x40 | 0x01


Index_Red = enum.IntEnum('Index', [
	'Header',
	'DeviceID',
	'DeviceFamily',
	'PackageSize',
	'Command',
	'Status',
	'HardwareVersion',
	'SoftwareVersion',
	'Baudrate',
	# user parameter start
    'OperationMode',
    'TorqueEnable',
    'OutputShaftCPR',
    'OutputShaftRPM',
    'UserIndicator',
    'MinimumPositionLimit',
    'MaximumPositionLimit',
    'TorqueLimit',
    'VelocityLimit',
    'PositionFF',
    'VelocityFF',
    'TorqueFF',
    'PositionDeadband',
    'VelocityDeadband',
    'TorqueDeadband',
    'PositionOutputLimit',
    'VelocityOutputLimit',
    'TorqueOutputLimit',
    'PositionScalerGain',
    'PositionPGain',
    'PositionIGain',
    'PositionDGain',
    'VelocityScalerGain',
    'VelocityPGain',
    'VelocityIGain',
    'VelocityDGain',
    'TorqueScalerGain',
    'TorquePGain',
    'TorqueIGain',
    'TorqueDGain',
    'SetPosition',
    'PositionControlMode',
	'SCurveSetpoint',
	'ScurveAccel',
	'SCurveMaxVelocity',
	'SCurveTime',
    'SetVelocity',
    'SetVelocityAcceleration',
    'SetTorque',
    'SetDutyCycle',
    'PresentPosition',              
    'PresentVelocity',
    'MotorCurrent',
    'AnalogPort',
	# user parameter end
	'CRCValue',
], start=0)

class OperationMode_Red():
    PWM = 0
    Position = 1
    Velocity = 2
    Torque = 3


class Red(SMD_Device):
    _PRODUCT_TYPE = 0xBA
    _PACKAGE_ESSENTIAL_SIZE = 6
    _STATUS_KEY_LIST = ['EEPROM', 'Software Version', 'Hardware Version']
    __RELEASE_URL = "https://api.github.com/repos/Acrome-Smart-Motion-Devices/SMD-Red-Firmware/releases/{version}"

    def __init__(self, ID, port:SerialPort) -> bool:
		
        self.__ack_size = 0
        self._config = None
        self._fw_file = None
        if ID > 254 or ID < 0:
            raise ValueError("Device ID can not be higher than 254 or lower than 0!")
        device_special_data = [
            Data_(Index_Red.Header, 'B', False, 0x55),
            Data_(Index_Red.DeviceID, 'B'),
            Data_(Index_Red.DeviceFamily, 'B', False, self.__class__._PRODUCT_TYPE),
            Data_(Index_Red.PackageSize, 'B'),
            Data_(Index_Red.Command, 'B'),
            Data_(Index_Red.Status, 'B'),
            Data_(Index_Red.HardwareVersion, 'I'),
            Data_(Index_Red.SoftwareVersion, 'I'),
            Data_(Index_Red.Baudrate, 'I'),
            # user parameter starts
            Data_(Index_Red.OperationMode, 'B'),
            Data_(Index_Red.TorqueEnable, 'B'),
            Data_(Index_Red.OutputShaftCPR, 'f'),
            Data_(Index_Red.OutputShaftRPM, 'f'),
            Data_(Index_Red.UserIndicator, 'B'),
            Data_(Index_Red.MinimumPositionLimit, 'i'),
            Data_(Index_Red.MaximumPositionLimit, 'i'),
            Data_(Index_Red.TorqueLimit, 'H'),
            Data_(Index_Red.VelocityLimit, 'H'),
            Data_(Index_Red.PositionFF, 'f'),
            Data_(Index_Red.VelocityFF, 'f'),
            Data_(Index_Red.TorqueFF, 'f'),
            Data_(Index_Red.PositionDeadband, 'f'),
            Data_(Index_Red.VelocityDeadband, 'f'),
            Data_(Index_Red.TorqueDeadband, 'f'),
            Data_(Index_Red.PositionOutputLimit, 'f'),
            Data_(Index_Red.VelocityOutputLimit, 'f'),
            Data_(Index_Red.TorqueOutputLimit, 'f'),
            Data_(Index_Red.PositionScalerGain, 'f'),
            Data_(Index_Red.PositionPGain, 'f'),
            Data_(Index_Red.PositionIGain, 'f'),
            Data_(Index_Red.PositionDGain, 'f'),
            Data_(Index_Red.VelocityScalerGain, 'f'),
            Data_(Index_Red.VelocityPGain, 'f'),
            Data_(Index_Red.VelocityIGain, 'f'),
            Data_(Index_Red.VelocityDGain, 'f'),
            Data_(Index_Red.TorqueScalerGain, 'f'),
            Data_(Index_Red.TorquePGain, 'f'),
            Data_(Index_Red.TorqueIGain, 'f'),
            Data_(Index_Red.TorqueDGain, 'f'),
            Data_(Index_Red.SetPosition, 'f'),
            Data_(Index_Red.PositionControlMode, 'B'),      # S Curve Position Control / 1 is SCurve(goTo function) 0 is direct control.
            Data_(Index_Red.SCurveSetpoint, 'f'),
            Data_(Index_Red.ScurveAccel, 'f'),
            Data_(Index_Red.SCurveMaxVelocity, 'f'),
            Data_(Index_Red.SCurveTime, 'f'),
            Data_(Index_Red.SetVelocity, 'f'),
            Data_(Index_Red.SetVelocityAcceleration, 'f'),
            Data_(Index_Red.SetTorque, 'f'),
            Data_(Index_Red.SetDutyCycle, 'f'),
            Data_(Index_Red.PresentPosition, 'f'),
            Data_(Index_Red.PresentVelocity, 'f'),
            Data_(Index_Red.MotorCurrent, 'f'),
            Data_(Index_Red.AnalogPort, 'H'),
            # user parameter end			
            Data_(Index_Red.CRCValue, 'I'),
        ]
        super().__init__(ID, self._PRODUCT_TYPE, device_special_data, port)
        self._vars[Index_Red.DeviceID].value(ID)

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
                    serial_settings = self.__ph.get_settings()
                    self.__ph.close()

                    # Upload binary
                    args = ['-p', self.__ph.portstr, '-b', str(115200), '-e', '-w', '-v', fw_file.name]
                    stm32loader_main(*args)

                    # Delete uploaded binary
                    if (not fw_file.closed):
                        fw_file.close()

                    # Re open port to the user with saved settings
                    self.__ph.apply_settings(serial_settings)
                    self.__ph.open()
                    return True

                else:
                    raise Exception("MD5 Mismatch!")
            else:
                raise Exception("Could not fetch requested MD5 file! Check your connection to GitHub.")
        else:
            raise Exception("Could not found requested firmware files list! Check your connection to GitHub.")

    def update_driver_baudrate(self, br: int):
        """Update the baudrate of the driver with
        given device ID. Following the method, the master
        baudrate must be updated accordingly to initiate a
        communication line with the board.

        Args:
            id (int): The device ID of the driver
            br (int): New baudrate value

        Raises:
            ValueError: Baudrate is not valid
        """

        if (br < 3053) or (br > 12500000):
            raise ValueError("{br} is not in acceptable range!")

        self.set_variables([Index_Red.Baudrate, br])
        self._post_sleep()
        self.eeprom_save()
        self._post_sleep()
        self.reboot(id)
        self._init_sleep()

    def get_driver_baudrate(self):
        """ Get the current baudrate from the driver.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the baudrate, otherwise None.
        """
        return self.get_variables(Index_Red.Baudrate)[0]
    
    def reset_encoder(self): #burayi kontrol et.
        """ Reset the encoder.

        Args:
            id (int): The device ID of the driver.
        """
        self.pureCommand(command_number= ExtraCommands_Red.RESET_ENC)
        self._post_sleep()

    def enable_torque(self, en: bool):
        """ Enable power to the motor of the driver.

        Args:
            id (int): The device ID of the driver
            en (bool): Enable. True enables the torque.
        """

        self.set_variables([Index_Red.TorqueEnable, en])
        self._post_sleep()

    def pid_tuner(self):
        """ Start PID auto-tuning routine. This routine will estimate
        PID coefficients for position and velocity control operation modes.

        Args:
            id (int): The device ID of the driver.
        """
        self.pureCommand(command_number= ExtraCommands_Red.TUNE)
        self._post_sleep()

    def set_operation_mode(self, mode:OperationMode_Red):
        """ Set the operation mode of the driver.

        Args:
            id (int): The device ID of the driver.
            mode (OperationMode): One of the PWM, Position, Velocity, Torque modes.
        """

        self.set_variables([Index_Red.OperationMode, mode])
        self._post_sleep()

    def get_operation_mode(self):
        """ Get the current operation mode from the driver.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the operation mode, otherwise None.
        """
        return self.get_variables(Index_Red.OperationMode)[0]

    def set_shaft_cpr(self, cpr: float):
        """ Set the count per revolution (CPR) of the motor output shaft.

        Args:
            id (int): The device ID of the driver.
            cpr (float): The CPR value of the output shaft/
        """
        self.set_variables([Index_Red.OutputShaftCPR, cpr])
        self._post_sleep()

    def get_shaft_cpr(self):
        """ Get the count per revolution (CPR) of the motor output shaft.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the output shaft CPR, otherwise None.
        """
        return self.get_variables(Index_Red.OutputShaftCPR)[0]

    def set_shaft_rpm(self, rpm: float):
        """ Set the revolution per minute (RPM) value of the output shaft at 12V rating.

        Args:
            id (int): The device ID of the driver.
            rpm (float): The RPM value of the output shaft at 12V
        """
        self.set_variables([Index_Red.OutputShaftRPM, rpm])
        self._post_sleep()

    def get_shaft_rpm(self):
        """ Get the revolution per minute (RPM) value of the output shaft at 12V rating.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the output shaft RPM characteristics, otherwise None.
        """
        return self.get_variables(Index_Red.OutputShaftRPM)

    def set_user_indicator(self):
        """ Set the user indicator color for 5 seconds. The user indicator color is cyan.

        Args:
            id (int): The device ID of the driver.
        """
        self.set_variables([Index_Red.UserIndicator, 1])
        self._post_sleep()

    def set_position_limits(self, plmin: int, plmax: int):
        """ Set the position limits of the motor in terms of encoder ticks.
        Default for min is -2,147,483,648 and for max is 2,147,483,647.
        The torque ise disabled if the value is exceeded so a tolerence
        factor should be taken into consideration when setting this values. 

        Args:
            id (int): The device ID of the driver.
            plmin (int): The minimum position limit.
            plmax (int): The maximum position limit.
        """
        self.set_variables([Index_Red.MinimumPositionLimit, plmin], [Index_Red.MaximumPositionLimit, plmax])
        self._post_sleep()

    def get_position_limits(self):
        """ Get the position limits of the motor in terms of encoder ticks.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the position limits, otherwise None.
        """
        return self.get_variables(Index_Red.MinimumPositionLimit, Index_Red.MaximumPositionLimit)

    def set_torque_limit(self, tl: int):
        """ Set the torque limit of the driver in terms of milliamps (mA).
        Torque is disabled after a timeout if the current drawn is over the
        given torque limit. Default torque limit is 65535.

        Args:
            id (int): The device ID of the driver.
            tl (int): New torque limit (mA)
        """
        self.set_variables([Index_Red.TorqueLimit, tl])
        self._post_sleep()

    def get_torque_limit(self):
        """ Get the torque limit from the driver in terms of milliamps (mA).

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the torque limit, otherwise None.
        """
        return self.get_variables(Index_Red.TorqueLimit)[0]

    def set_velocity_limit(self, vl: int):
        """ Set the velocity limit for the motor output shaft in terms of RPM. The velocity limit
        applies only in velocity mode. Default velocity limit is 65535.

        Args:
            id (int): The device ID of the driver.
            vl (int): New velocity limit (RPM)
        """
        self.set_variables([Index_Red.VelocityLimit, vl])
        self._post_sleep()

    def get_velocity_limit(self):
        """ Get the velocity limit from the driver in terms of RPM.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the velocity limit, otherwise None.
        """
        return self.get_variables(Index_Red.VelocityLimit)[0]

    def set_position(self, sp: int):
        """ Set the desired setpoint for the position control in terms of encoder ticks.

        Args:
            id (int): The device ID of the driver.
            sp (int | float): Position control setpoint.
        """
        self.set_variables([Index_Red.PositionControlMode, 0],[Index_Red.SetPosition, sp])
        self._post_sleep()

    def get_position(self):
        """ Get the current position of the motor from the driver in terms of encoder ticks.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the current position, otherwise None.
        """
        return self.get_variables(Index_Red.PresentPosition)[0]
    
    def goTo(self, target_position, time_ = 0, maxSpeed = 0, accel = 0, 
             blocking: bool = False, encoder_tick_close_counter = 10):
        """
            # goTo: 

            Sets the target position in S Curve mode. Since this function controls motor in position, 
            device should be in Position Mode to use this func.

            If you just want to drive the motor to target point smoothly, you can use just the target_position parameter only.
            If other parameters are not given or they are 0 (time, maxSpeed, accel), it will use default speed and acceleration values based on the motor's RPM.
            
            If the setpoint, time, maxSpeed, and accel parameters are specified in a way that makes it impossible to reach the target in the given time, 
            the time variable will be ignored.

            If only the time is not provided, the movement will be executed according to the other given parameters.

            It is not necessary for the speed to reach the maxSpeed value during the movement. 
            The maxSpeed parameter is only a limitation. Due to the other given parameters, it might be impossible to reach the maxSpeed value during the movement. 
            Note: The motor's RPM value is defined as maxSpeed within the SMD.

            If blocking is True, the function will wait until the motor reaches the target position.
            If blocking is False, the function will return immediately.

            Args:
                id (int): The device ID of the driver.
                target_position (int | float): Position control setpoint.
                time (int | float): Time in seconds.
                maxSpeed (int | float): Maximum speed in RPM.
                accel (int | float): Acceleration in RPM/s.
                blocking (bool): If True, the function will wait until the motor reaches the target position.
                encoder_tick_close_counter (int): The number of encoder ticks that the motor should close enough to the target position to be considered reached.
        """

        self.set_variables([Index_Red.PositionControlMode, 1])
        self.set_variables([Index_Red.SCurveTime, time_],[Index_Red.SCurveMaxVelocity, maxSpeed],[Index_Red.ScurveAccel, accel])
        self.set_variables([Index_Red.SCurveSetpoint, target_position])

        self._post_sleep()

        while(blocking):
            if (abs(target_position - self.get_position(id)) <= encoder_tick_close_counter):
                break
        
    def goTo_ConstantSpeed(self, target_position, speed,
                           blocking: bool = False, encoder_tick_close_counter = 10):
        """
            # goTo_ConstantSpeed: 

            Sets the target position and sets the accel to max accel in S Curve mode. So velocity reaches given speed immediately.

            If blocking is True, the function will wait until the motor reaches the target position.
            If blocking is False, the function will return immediately.

            Args:
                id (int): The device ID of the driver.
                target_position (int | float): Position control setpoint.
                speed (int | float): Maximum speed in RPM.
                blocking (bool): If True, the function will wait until the motor reaches the target position.
                encoder_tick_close_counter (int): The number of encoder ticks that the motor should close enough to the target position to be considered reached.
        """
        
        self.set_variables([Index_Red.VelocityControlMode, 1])
        self.set_variables([Index_Red.SCurveMaxVelocity, speed],[Index_Red.ScurveAccel, MotorConstants.MAX_ACCEL])
        self.set_variables([Index_Red.SCurveSetpoint, target_position])

        self._post_sleep()

        while(blocking):
            if (abs(target_position - self.get_position()) <= encoder_tick_close_counter):
                break

    def set_velocity(self, sp: float, accel = 0):
        """ Set the desired setpoint for the velocity control in terms of RPM.

        Args:
            id (int): The device ID of the driver.
            sp (int | float): Velocity control setpoint.
            accel(float): sets the acceleration value for the velocity control in terms of (RPM/seconds). if accel is not given, it will be ignored. 
            So previously set accel value will be used.
            In initial SMD-RED Velocity Control Mode, accel will be set to MAX_ACCEL.

        Hint: 
            It can be used to set the acceleration value by "MotorConstants.MAX_ACCEL" to reach the target velocity immediately.
        """
        if accel == MotorConstants.MAX_ACCEL:
            accel = 0
            self.set_variables([Index_Red.SetVelocityAcceleration, accel])
            self.set_variables([Index_Red.SetVelocity, sp])

        elif accel == 0:
            self.set_variables([Index_Red.SetVelocity, sp])
        else:
            self.set_variables([Index_Red.SetVelocityAcceleration, accel])
            self.set_variables([Index_Red.SetVelocity, sp])
        
        self._post_sleep()

    def get_velocity(self):
        """ Get the current velocity of the motor output shaft from the driver in terms of RPM.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the current velocity, otherwise None.
        """
        return self.get_variables(Index_Red.PresentVelocity)[0]

    def set_torque(self, sp: float):
        """ Set the desired setpoint for the torque control in terms of milliamps (mA).

        Args:
            id (int): The device ID of the driver.
            sp (int | float): Torque control setpoint.
        """
        self.set_variables([Index_Red.SetTorque, sp])
        self._post_sleep()

    def get_torque(self):
        """ Get the current drawn from the motor from the driver in terms of milliamps (mA).

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the current, otherwise None.
        """
        return self.get_variables(Index_Red.MotorCurrent)[0]

    def set_duty_cycle(self, pct: float):
        """ Set the duty cycle to the motor for PWM control mode in terms of percentage.
        Negative values will change the motor direction.

        Args:
            id (int): The device ID of the driver.
            pct (int | float): Duty cycle percentage.
        """
        self.set_variables([Index_Red.SetDutyCycle, pct])
        self._post_sleep()

    def get_analog_port(self):
        """ Get the ADC values from the analog port of the device with
        10 bit resolution. The value is in range [0, 4095].

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the ADC conversion of the port, otherwise None.
        """
        return self.get_variables(Index_Red.AnalogPort)[0]

    def set_control_parameters_position(self, p=None, i=None, d=None, db=None, ff=None, ol=None):
        """ Set the control block parameters for position control mode.
        Only assigned parameters are written, None's are ignored. The default
        max output limit is 950.

        Args:
            id (int): The device ID of the driver.
            p (float): Proportional gain. Defaults to None.
            i (float): Integral gain. Defaults to None.
            d (float): Derivative gain. Defaults to None.
            db (float): Deadband (of the setpoint type). Defaults to None.
            ff (float): Feedforward. Defaults to None.
            ol (float): Maximum output limit. Defaults to None.
        """
        index_list = [Index_Red.PositionPGain, Index_Red.PositionIGain, Index_Red.PositionDGain, Index_Red.PositionDeadband, Index_Red.PositionFF, Index_Red.PositionOutputLimit]
        val_list = [p, i, d, db, ff, ol]
        self.set_variables(*[list(pair) for pair in zip(index_list, val_list) if pair[1] is not None])
        self._post_sleep()

    def get_control_parameters_position(self):
        """ Get the position control block parameters.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list [P, I, D, FF, DB, OUTPUT_LIMIT], otherwise None.
        """

        return self.get_variables(*[Index_Red.PositionPGain, Index_Red.PositionIGain, Index_Red.PositionDGain, Index_Red.PositionDeadband, Index_Red.PositionFF, Index_Red.PositionOutputLimit])

    def set_control_parameters_velocity(self, p=None, i=None, d=None, db=None, ff=None, ol=None):
        """ Set the control block parameters for velocity control mode.
        Only assigned parameters are written, None's are ignored. The default
        max output limit is 950.

        Args:
            id (int): The device ID of the driver.
            p (float): Proportional gain. Defaults to None.
            i (float): Integral gain. Defaults to None.
            d (float): Derivative gain. Defaults to None.
            db (float): Deadband (of the setpoint type). Defaults to None.
            ff (float): Feedforward. Defaults to None.
            ol (float): Maximum output limit. Defaults to None.
        """
        index_list = [Index_Red.VelocityPGain, Index_Red.VelocityIGain, Index_Red.VelocityDGain, Index_Red.VelocityDeadband, Index_Red.VelocityFF, Index_Red.VelocityOutputLimit]
        val_list = [p, i, d, db, ff, ol]

        self.set_variables(*[list(pair) for pair in zip(index_list, val_list) if pair[1] is not None])
        self._post_sleep()

    def get_control_parameters_velocity(self):
        """ Get the velocity control block parameters.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list [P, I, D, FF, DB, OUTPUT_LIMIT], otherwise None.
        """
        return self.get_variables(*[Index_Red.VelocityPGain, Index_Red.VelocityIGain, Index_Red.VelocityDGain, Index_Red.VelocityDeadband, Index_Red.VelocityFF, Index_Red.VelocityOutputLimit])

    def set_control_parameters_torque(self, p=None, i=None, d=None, db=None, ff=None, ol=None):
        """ Set the control block parameters for torque control mode.
        Only assigned parameters are written, None's are ignored. The default
        max output limit is 950.

        Args:
            id (int): The device ID of the driver.
            p (float): Proportional gain. Defaults to None.
            i (float): Integral gain. Defaults to None.
            d (float): Derivative gain. Defaults to None.
            db (float): Deadband (of the setpoint type). Defaults to None.
            ff (float): Feedforward. Defaults to None.
            ol (float): Maximum output limit. Defaults to None.
        """
        index_list = [Index_Red.TorquePGain, Index_Red.TorqueIGain, Index_Red.TorqueDGain, Index_Red.TorqueDeadband, Index_Red.TorqueFF, Index_Red.TorqueOutputLimit]
        val_list = [p, i, d, db, ff, ol]

        self.set_variables(*[list(pair) for pair in zip(index_list, val_list) if pair[1] is not None])
        self._post_sleep()

    def get_control_parameters_torque(self):
        """ Get the torque control block parameters.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list [P, I, D, FF, DB, OUTPUT_LIMIT], otherwise None.
        """
        return self.get_variables(*[Index_Red.TorquePGain, Index_Red.TorqueIGain, Index_Red.TorqueDGain, Index_Red.TorqueDeadband, Index_Red.TorqueFF, Index_Red.TorqueOutputLimit])



def scan_red_devices(port:SerialPort):
    # burada herhangi bir nesne olusturmadan ping atmasi icin yeniden duzenlenecek.
    id_list = []
    for i in range(255):
        dev = Red(i, port)
        if dev.ping()== True:
            id_list.append(i)
    return id_list


def Red_set_variables_sync(parameter_index:Index_Red, port:SerialPort, id_val_pairs=[]):
        raise NotImplementedError()
        pass
        '''
        dev = Red(self.__class__._BROADCAST_ID)
        dev.vars[Index.Command].value(Commands.SYNC_WRITE)

        fmt_str = '<' + ''.join([var.type() for var in dev.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in dev.vars[:6]]))

        fmt_str += 'B'
        struct_out += list(struct.pack('<B', int(index)))

        for pair in id_val_pairs:
            fmt_str += 'B'
            struct_out += list(struct.pack('<B', pair[0]))
            struct_out += list(struct.pack('<' + dev.vars[index].type(), pair[1]))

        struct_out[int(Index.PackageSize)] = len(struct_out) + dev.vars[Index.CRCValue].size()
        dev.vars[Index.CRCValue].value(CRC32.calc(struct_out))

        self.__write_bus(bytes(struct_out) + struct.pack('<' + dev.vars[Index.CRCValue].type(), dev.vars[Index.CRCValue].value()))
        self._post_sleep()
        '''


