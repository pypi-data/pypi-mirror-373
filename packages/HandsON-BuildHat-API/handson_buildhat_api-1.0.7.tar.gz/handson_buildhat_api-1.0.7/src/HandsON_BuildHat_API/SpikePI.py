# Encoding      : UTF-8
# Date          : 2025-04-30
# Production    : HandsON Technology Co., Ltd
# Author        : HaNeul Jung (caffeine.reload@gmail.com)

# All rights to the code, excluding third-party libraries used herein, are reserved by HandsON Technology Co., Ltd.

from serial import Serial
import time

class _ConstButtonID:
    START = 0
    STOP = 1
    
    LEFT = 2
    RIGHT = 3

class _ConstModuleID:
    '''
    모듈 ID 모음
    '''
    COLOR = 0x3D
    DISTANCE = 0x3E
    FORCE = 0x3F

    SMALL_MOTOR = 0x41
    MEDIUM_MOTOR = 0x30
    LARGE_MOTOR = 0x31

class _ConstValue:
    '''
    기타 상수 모음
    '''
    HUB_DATA = 0b1010 << 4
    TRA_DATA = 0b1000 << 4
    GET_DATA = 0b1001 << 4

    ALL_PORT = 0b1111

    MOTOR_STOP = 0
    MOTOR_PWM = 1
    MOTOR_ABS = 2
    MOTOR_REL = 3
    MOTOR_BRAKE = 255

class _PORT:
    PORT = {
        'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5
    }

class _COLOR:
    COLOR = {
        0:'black', 1:'violet', 3:'blue', 4:'cyan', 
        5:'green', 7:'yellow', 9:'red', 10:'white',
        255:'None'
    }

class _Availability:
    '''
    내부용 시리얼 통신의 체크섬을 확인 및 체크섬을 만드는 함수를 제공합니다.
    '''
    @staticmethod
    def make_checksum(byte:bytes) -> bytes:
        '''
        입력 받은 바이트를 기반으로 체크섬을 만들고 반환합니다.
        '''
        sum = 0
        for i in byte: sum ^= i
        return bytes([sum])
    
    @staticmethod
    def checksum_check(byte:bytes) -> bool:
        '''
        바이트열의 체크섬을 확인하고 불 값을 반환합니다.
        '''
        sum = 0
        for i in byte[:-1]: sum ^= i
        try:
            if sum == byte[-1]: return True
            else: return False
        except IndexError:
            return False

class _SerialManager:
    '''
    내부용 시리얼 버스 객체, **외부 접근 절대 금지**.
    '''
    _serial_port = (
        '/dev/ttyTHS1', # Jetson Orin Nano
        '/dev/ttyAMA0', # Raspberry PI 5
        '/dev/ttyS0'    # Raspberry PI 4
    )
    serial = None

    for i in _serial_port:
        try: serial = Serial(port=i, baudrate=115200, timeout=0.02)
        except: pass
        else: break

    if serial == None:
        raise Exception('사용 가능한 시리얼 포트를 찾을 수 없습니다.')
        
class _button:
    def __init__(self, button_id = _ConstButtonID.STOP):
        self.button_id = button_id

    def is_pressed(self):
        command = b'\xa0\x00\x00\x00\x00\x00\x00'
        command += _Availability.make_checksum(command)
        while True:
            _SerialManager.serial.write(command)
            data = _SerialManager.serial.read(16)
            if _Availability.checksum_check(data): break
        result = True if data[self.button_id + 1] == 1 else False
        return result

class BuildHat:
    def __init__(self):
        self.stop_button = _button(_ConstButtonID.STOP)
        self.start_button = _button(_ConstButtonID.START)

class _ModuleParent:
    def _get_data(self, byte:bytes) -> bytes:
        while True:
            self._send_data(byte)
            data = _SerialManager.serial.read(16)

            if data == b'': continue

            if _Availability.checksum_check(data): return data
            if ((len(data) == 1) and (data[0] == 0x04)): return data

    def _send_data(self, byte:bytes) -> None:
        com = byte
        for i in range(0, 7-len(com)): com += b'\x00'
        com += _Availability.make_checksum(com)
        time.sleep(0.005)
        _SerialManager.serial.write(com)

    def _module_check(self, port:int, ID:tuple) -> None:
        command = [_ConstValue.GET_DATA + _ConstValue.ALL_PORT]
        if not self._get_data(byte=bytes(command))[port + 1] in ID:
            raise Exception('해당 포트에 연결된 모듈이 다르거나 없습니다.')

class ColorSensor(_ModuleParent):
    def __init__(self, port:str):
        self._PORT = _PORT.PORT[port]
        self._module_check(self._PORT, (_ConstModuleID.COLOR, ))
        
    def get_color(self) -> str:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return _COLOR.COLOR[data[1]]
    
    def get_reflected_light(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return data[2]
    
    def get_rgb_intensity(self) -> tuple:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return (data[3] + (data[4] << 8), data[5] + (data[6] << 8), data[7] + (data[8] << 8))

    def get_red(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return data[3] + (data[4] << 8)
    
    def get_green(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return data[5] + (data[6] << 8)
    
    def get_blue(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return data[7] + (data[8] << 8)
    
class DistanceSensor(_ModuleParent):
    def __init__(self, port:str):
        self._PORT = _PORT.PORT[port]
        self._module_check(self._PORT, (_ConstModuleID.DISTANCE, ))

    def get_distance_cm(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return (data[1] + (data[2] << 8)) // 10

class ForceSensor(_ModuleParent):
    def __init__(self, port:str):
        self._PORT = _PORT.PORT[port]
        self._module_check(self._PORT, (_ConstModuleID.FORCE, ))

    def is_pressed(self) -> bool:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        if data[2] == 1: return True
        else: return False

    def get_force_percentage(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        return data[1]

class Motor(_ModuleParent):
    def __init__(self, port:str):
        self._PORT = _PORT.PORT[port]
        self._module_check(self._PORT, (_ConstModuleID.SMALL_MOTOR, _ConstModuleID.MEDIUM_MOTOR, _ConstModuleID.LARGE_MOTOR))

    def stop(self) -> None:
        com = bytes((_ConstValue.TRA_DATA + self._PORT, _ConstValue.MOTOR_STOP, 0, 0))
        self._get_data(com)

    def start(self, speed:int) -> None:
        if not speed in range(-100, 101):
            raise Exception('모터의 속도는 ~100 ~ 100 사이의 정수만 입력 가능합니다.')
        
        if speed > 0: sw = 1
        else: sw = 0

        com = bytes((_ConstValue.TRA_DATA + self._PORT, _ConstValue.MOTOR_PWM, abs(speed), sw))
        self._get_data(com)

    def run_to_position(self, degrees, speed) -> None:
        if not speed in range(0, 101):
            raise Exception('모터의 속도는 0 ~ 100 사이의 정수만 입력 가능합니다.')
        if not degrees in range(-180, 181):
            raise Exception('모터의 절대 각도는 -180 ~ 180 사이의 정수만 입력 가능합니다.')
        
        if degrees >= 0: target = degrees
        else: target = degrees & 0xFFFF
        
        com = bytes((_ConstValue.TRA_DATA + self._PORT, _ConstValue.MOTOR_ABS, speed, (target & 0xFF), (target >> 8)))
        self._get_data(com)

    def run_for_degrees(self, degrees, speed) -> None:
        if not speed in range(0, 101):
            raise Exception('모터의 속도는 0 ~ 100 사이의 정수만 입력 가능합니다.')
        
        if not degrees in range(-2147483647, 2147483647):
            raise Exception('모터의 동작 각도는 -2147483647 ~ 2147483647 사이의 값만 입력 가능합니다.')
        
        if degrees >= 0: target = degrees
        else: target = degrees & 0xFFFFFFFF

        com = bytes((_ConstValue.TRA_DATA + self._PORT, _ConstValue.MOTOR_REL, speed, (target & 0xFF), (target >> 8) & 0xFF, (target >> 16) & 0xFF, (target >> 24) & 0xFF))
        self._get_data(com)

    def get_speed(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        if data[1] >> 7 == 0: return data[1]
        else: return -(0xFF - data[1])

    def get_position(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        if data[7] >> 7 == 0: return data[6] + (data[7] << 8)
        else: return -(0xFFFF - (data[6] + (data[7] << 8) - 1))

    def get_degrees_counted(self) -> int:
        command = [_ConstValue.GET_DATA + self._PORT]
        data = self._get_data(bytes(command))
        if data[5] >> 7 == 0: return data[2] + (data[3] << 8) + (data[4] << 16) + (data[5] << 24)
        else: return -(0xFFFFFFFF - (data[2] + (data[3] << 8) + (data[4] << 16) + (data[5] << 24) - 1))

class MotorPair(_ModuleParent):
    def __init__(self, left_motor, right_motor):
        self._PORTs = (_PORT.PORT[left_motor],  _PORT.PORT[right_motor])
        for i in self._PORTs: self._module_check(i, (_ConstModuleID.LARGE_MOTOR, _ConstModuleID.MEDIUM_MOTOR, _ConstModuleID.SMALL_MOTOR))

    def stop(self) -> None:
        for i in self._PORTs:
            com = bytes((_ConstValue.TRA_DATA + i, _ConstValue.MOTOR_PWM, 0, 0))
            self._get_data(com)

    def start(self, steering, speed) -> None:
        if not steering in range(-100, 101):
            raise Exception('조향 값은 -100 ~ 100 사이의 값만 입력 가능합니다.')
        if not speed in range(-100, 101):
            raise Exception('속도 값은 -100 ~ 100 사이의 값만 입력 가능합니다.')
        
        out = (
            int((speed + (speed * (steering / 100))) *  1),
            int((speed - (speed * (steering / 100))) * -1)
        )

        for motor, speed in zip(self._PORTs, out):
            if speed > 0: sw = 1
            else: sw = 0

            com = bytes((_ConstValue.TRA_DATA + motor, _ConstValue.MOTOR_PWM, abs(speed), sw))
            self._get_data(com)

    def move(self, degrees, steering, speed) -> None:
        if not steering in range(-100, 101):
            raise Exception('조향 값은 -100 ~ 100 사이의 값만 입력 가능합니다.')
        if not speed in range(0, 101):
            raise Exception('속도 값은 0 ~ 100 사이의 값만 입력 가능합니다.')
        if not degrees in range(-2147483647, 2147483647):
            raise Exception('모터의 동작 각도는 -2147483647 ~ 2147483647 사이의 값만 입력 가능합니다.')
        
        out = (
            int(speed + (speed * (steering / 100))),
            int(speed - (speed * (steering / 100)))
        )

        for motor, speed, count in zip(self._PORTs, out, (0, 1)):

            if degrees >= 0: target = degrees
            else: target = degrees & 0xFFFFFFFF

            if count == 1: target = ~target

            com = bytes((_ConstValue.TRA_DATA + motor, _ConstValue.MOTOR_REL, speed, (target & 0xFF), (target >> 8) & 0xFF, (target >> 16) & 0xFF, (target >> 24) & 0xFF))
            self._get_data(com)


    def move_tank(self, degrees, left_speed, right_speed) -> None:
        if not left_speed in range(-100, 101) or not right_speed in range(-100, 101):
            raise Exception('조향 값은 -100 ~ 100 사이의 값만 입력 가능합니다.')
        if not degrees in range(-2147483647, 2147483647):
            raise Exception('모터의 동작 각도는 -2147483647 ~ 2147483647 사이의 값만 입력 가능합니다.')

        out = (
            int(left_speed  *  1),
            int(right_speed * -1)
        )

        for motor, speed, count in zip(self._PORTs, out, (0, 1)):

            if degrees >= 0: target = degrees
            else: target = degrees & 0xFFFFFFFF

            if count == 1: target = ~target

            com = bytes((_ConstValue.TRA_DATA + motor, _ConstValue.MOTOR_REL, speed, (target & 0xFF), (target >> 8) & 0xFF, (target >> 16) & 0xFF, (target >> 24) & 0xFF))
            self._get_data(com)

    def start_tank(self, left_speed, right_speed) -> None:
        if not left_speed in range(-100, 101) or not right_speed in range(-100, 101):
            raise Exception('조향 값은 -100 ~ 100 사이의 값만 입력 가능합니다.')

        out = (
            int(left_speed  *  1),
            int(right_speed * -1)
        )

        for motor, speed in zip(self._PORTs, out):
            if speed > 0: sw = 1
            else: sw = 0

            com = bytes((_ConstValue.TRA_DATA + motor, _ConstValue.MOTOR_PWM, abs(speed), sw))
            self._get_data(com)
