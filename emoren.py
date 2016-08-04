# -*- coding: utf-8 -*-

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hidapi

sensor_bits = {
    'F3': [10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7],
    'FC5': [28, 29, 30, 31, 16, 17, 18, 19, 20, 21, 22, 23, 8, 9],
    'AF3': [46, 47, 32, 33, 34, 35, 36, 37, 38, 39, 24, 25, 26, 27],
    'F7': [48, 49, 50, 51, 52, 53, 54, 55, 40, 41, 42, 43, 44, 45],
    'T7': [66, 67, 68, 69, 70, 71, 56, 57, 58, 59, 60, 61, 62, 63],
    'P7': [84, 85, 86, 87, 72, 73, 74, 75, 76, 77, 78, 79, 64, 65],
    'O1': [102, 103, 88, 89, 90, 91, 92, 93, 94, 95, 80, 81, 82, 83],
    'O2': [140, 141, 142, 143, 128, 129, 130, 131, 132, 133, 134, 135, 120, 121],
    'P8': [158, 159, 144, 145, 146, 147, 148, 149, 150, 151, 136, 137, 138, 139],
    'T8': [160, 161, 162, 163, 164, 165, 166, 167, 152, 153, 154, 155, 156, 157],
    'F8': [178, 179, 180, 181, 182, 183, 168, 169, 170, 171, 172, 173, 174, 175],
    'AF4': [196, 197, 198, 199, 184, 185, 186, 187, 188, 189, 190, 191, 176, 177],
    'FC6': [214, 215, 200, 201, 202, 203, 204, 205, 206, 207, 192, 193, 194, 195],
    'F4': [216, 217, 218, 219, 220, 221, 222, 223, 208, 209, 210, 211, 212, 213]
}

quality_bits = [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112]

headset_config = {
    'cipher': None,
    'device': None,
    'old_model': True,
    'device': None
}

def get_level(data, bits):
    """
    Returns sensor level value from data using sensor bit mask in micro volts (uV).
    """
    level = 0
    for i in range(13, -1, -1):
        level <<= 1
        b, o = (bits[i] // 8) + 1, bits[i] % 8
        level |= (data[b] >> o) & 1
    return level

class EmotivPacket(object):
    """
    Basic semantics for input bytes.
    """

    def __init__(self, data, model):
        """
        Initializes packet data. Sets the global battery value.
        Updates each sensor with current sensor value from the packet data.

        :param data - Values decrypted to be processed
        :param model - Is headset old model? Old is relative now I guess.
        """

        self.sensors = {
            'F3': {'value': 0, 'quality': 0},
            'FC6': {'value': 0, 'quality': 0},
            'P7': {'value': 0, 'quality': 0},
            'T8': {'value': 0, 'quality': 0},
            'F7': {'value': 0, 'quality': 0},
            'F8': {'value': 0, 'quality': 0},
            'T7': {'value': 0, 'quality': 0},
            'P8': {'value': 0, 'quality': 0},
            'AF4': {'value': 0, 'quality': 0},
            'F4': {'value': 0, 'quality': 0},
            'AF3': {'value': 0, 'quality': 0},
            'O2': {'value': 0, 'quality': 0},
            'O1': {'value': 0, 'quality': 0},
            'FC5': {'value': 0, 'quality': 0},
            'X': {'value': 0, 'quality': 0},
            'Y': {'value': 0, 'quality': 0},
            'Z': {'value': 0, 'quality': 0},
            'Unknown': {'value': 0, 'quality': 0}}

        self.raw_data = data
        self.counter = data[0]
        self.raw_battery = None
        if self.counter > 127:
            self.raw_battery = self.counter
            self.counter = 128
        self.sync = self.counter == 0xe9
        self.gyro_x = data[29] - 106
        self.gyro_y = data[30] - 105
        self.gyro_z = 0 # No idea
        self.sensors['X']['value'] = self.gyro_x
        self.sensors['Y']['value'] = self.gyro_y
        self.sensors['Z']['value'] = self.gyro_z
        for name, bits in list(sensor_bits.items()):
            # Get Level for sensors subtract 8192 to get signed value
            value = get_level(self.raw_data, bits) - 8192
            setattr(self, name, (value,))
            self.sensors[name]['value'] = value
        self.old_model = model
        self.handle_quality()


    def handle_quality(self):
        """
        Sets the quality value for the sensor from the quality bits in the packet data.
        Optionally will return the value.

        :param sensors - reference to sensors dict in Emotiv class.

        """
        if self.old_model:
            current_contact_quality = get_level(self.raw_data, quality_bits) / 540
        else:
            current_contact_quality = get_level(self.raw_data, quality_bits) / 1024
        sensor = self.raw_data[0]
        if sensor == 0 or sensor == 64:
            self.sensors['F3']['quality'] = current_contact_quality
        elif sensor == 1 or sensor == 65:
            self.sensors['FC5']['quality'] = current_contact_quality
        elif sensor == 2 or sensor == 66:
            self.sensors['AF3']['quality'] = current_contact_quality
        elif sensor == 3 or sensor == 67:
            self.sensors['F7']['quality'] = current_contact_quality
        elif sensor == 4 or sensor == 68:
            self.sensors['T7']['quality'] = current_contact_quality
        elif sensor == 5 or sensor == 69:
            self.sensors['P7']['quality'] = current_contact_quality
        elif sensor == 6 or sensor == 70:
            self.sensors['O1']['quality'] = current_contact_quality
        elif sensor == 7 or sensor == 71:
            self.sensors['O2']['quality'] = current_contact_quality
        elif sensor == 8 or sensor == 72:
            self.sensors['P8']['quality'] = current_contact_quality
        elif sensor == 9 or sensor == 73:
            self.sensors['T8']['quality'] = current_contact_quality
        elif sensor == 10 or sensor == 74:
            self.sensors['F8']['quality'] = current_contact_quality
        elif sensor == 11 or sensor == 75:
            self.sensors['AF4']['quality'] = current_contact_quality
        elif sensor == 12 or sensor == 76 or sensor == 80:
            self.sensors['FC6']['quality'] = current_contact_quality
        elif sensor == 13 or sensor == 77:
            self.sensors['F4']['quality'] = current_contact_quality
        elif sensor == 14 or sensor == 78:
            self.sensors['F8']['quality'] = current_contact_quality
        elif sensor == 15 or sensor == 79:
            self.sensors['AF4']['quality'] = current_contact_quality
        else:
            self.sensors['Unknown']['quality'] = current_contact_quality
            self.sensors['Unknown']['value'] = sensor
        return current_contact_quality


    def __repr__(self):
        """
        Returns custom string representation of the Emotiv Packet.
        """
        return 'EmotivPacket(counter=%i, gyro_x=%i, gyro_y=%i, gyro_z=%s, raw_battery=%s)' % (
            self.counter,
            self.gyro_x,
            self.gyro_y,
            self.gyro_z,
            self.raw_battery)

def is_old_model(serial_number):
    if "GM" in serial_number[-2:]:
        return False
    return True

def hid_enumerate():
    """
    Loops over all devices in the hidapi and attempts to locate the emotiv headset.
    Since hidapi ultimately uses the path there is no reason to get the vendor id or product id.
    Although, they may be useful in locating the device.

    :returns
        path - the path to the device
        serial_number - the serial number of the device
    """
    path = ""
    serial_number = ""
    devices = hidapi.hid_enumerate()
    for device in devices:
        is_emotiv = False
        try:
            if "Emotiv" in device.manufacturer_string:
                is_emotiv = True
            if "Emotiv" in device.product_string:
                is_emotiv = True
            if "EPOC" in device.product_string:
                is_emotiv = True
            if "Brain Waves" in device.product_string:
                is_emotiv = True
            if device.product_string == '00000000000':
                is_emotiv = True
            if "EEG Signals" in device.product_string:
                is_emotiv = True

            if is_emotiv:
                serial_number = device.serial_number
                path = device.path
        except:
            pass
    return path, serial_number

def print_hid_enumerate():
    """
    Loops over all devices in the hidapi and attempts prints information.

    This is a fall back method that give the user information to give the developers when opening an issue.
    """
    devices = hidapi.hid_enumerate()
    print("-------------------------")
    for device in devices:
        print((device.manufacturer_string))
        print((device.product_string))
        print((device.path))
        print((device.vendor_id))
        print((device.product_id))
        print((device.serial_number))
        print("-------------------------")
    print("Please include this information if you open a new issue.")

def handle_quality(self, sensors):
        """
        Sets the quality value for the sensor from the quality bits in the packet data.
        Optionally will return the value.

        :param sensors - reference to sensors dict in Emotiv class.

        """
        if self.old_model:
            current_contact_quality = get_level(self.raw_data, quality_bits) / 540
        else:
            current_contact_quality = get_level(self.raw_data, quality_bits) / 1024
        sensor = ord(self.raw_data[0])
        if sensor == 0 or sensor == 64:
            sensors['F3']['quality'] = current_contact_quality
        elif sensor == 1 or sensor == 65:
            sensors['FC5']['quality'] = current_contact_quality
        elif sensor == 2 or sensor == 66:
            sensors['AF3']['quality'] = current_contact_quality
        elif sensor == 3 or sensor == 67:
            sensors['F7']['quality'] = current_contact_quality
        elif sensor == 4 or sensor == 68:
            sensors['T7']['quality'] = current_contact_quality
        elif sensor == 5 or sensor == 69:
            sensors['P7']['quality'] = current_contact_quality
        elif sensor == 6 or sensor == 70:
            sensors['O1']['quality'] = current_contact_quality
        elif sensor == 7 or sensor == 71:
            sensors['O2']['quality'] = current_contact_quality
        elif sensor == 8 or sensor == 72:
            sensors['P8']['quality'] = current_contact_quality
        elif sensor == 9 or sensor == 73:
            sensors['T8']['quality'] = current_contact_quality
        elif sensor == 10 or sensor == 74:
            sensors['F8']['quality'] = current_contact_quality
        elif sensor == 11 or sensor == 75:
            sensors['AF4']['quality'] = current_contact_quality
        elif sensor == 12 or sensor == 76 or sensor == 80:
            sensors['FC6']['quality'] = current_contact_quality
        elif sensor == 13 or sensor == 77:
            sensors['F4']['quality'] = current_contact_quality
        elif sensor == 14 or sensor == 78:
            sensors['F8']['quality'] = current_contact_quality
        elif sensor == 15 or sensor == 79:
            sensors['AF4']['quality'] = current_contact_quality
        else:
            sensors['Unknown']['quality'] = current_contact_quality
            sensors['Unknown']['value'] = sensor
        return current_contact_quality

def setup(headset, is_research=True):
    '''
    `is_research` should be True if EPOC+, try False if you have an EPOC
    '''
    hidapi.hid_init()
    path, serial_number = hid_enumerate()

    if len(path) == 0:
        print("Could not find device.")
        print_hid_enumerate()
        exit()

    headset['device'] = hidapi.hid_open_path(path)

    # Setup crypto
    if is_old_model(serial_number):
        headset['old_model'] = True
    k = ['\0'] * 16
    k[0] = serial_number[-1]
    k[1] = '\0'
    k[2] = serial_number[-2]
    if is_research:
        k[3] = 'H'
        k[4] = serial_number[-1]
        k[5] = '\0'
        k[6] = serial_number[-2]
        k[7] = 'T'
        k[8] = serial_number[-3]
        k[9] = '\x10'
        k[10] = serial_number[-4]
        k[11] = 'B'
    else:
        k[3] = 'T'
        k[4] = serial_number[-3]
        k[5] = '\x10'
        k[6] = serial_number[-4]
        k[7] = 'B'
        k[8] = serial_number[-1]
        k[9] = '\0'
        k[10] = serial_number[-2]
        k[11] = 'H'
    k[12] = serial_number[-3]
    k[13] = '\0'
    k[14] = serial_number[-4]
    k[15] = 'P'
    key = ''.join(k)
    print("Decryption key: " + key)

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key.encode()), modes.ECB(), backend=backend)
    decryptor = cipher.decryptor()
    headset['decryptor'] = decryptor

def read(headset):
    
    while True:
        data = hidapi.hid_read_timeout(headset['device'], 34, 500) # Have a timeout to make things responsive to interrupts
        if len(data) > 0:
            yield data
    
def decrypt(task, headset):
    
    if len(task) == 33:
        print("33!")
        task = task[1:] 

    task = bytes(task)
    data = bytearray(headset['decryptor'].update(task)) #+ headset['decryptor'].finalize()
    p = EmotivPacket(data, headset['old_model'])
    return p

def get_packets():
    try:
        setup(headset_config)
        for data in read(headset_config):
            packet = decrypt(data, headset_config)
            yield packet
    except:
        raise
    finally:
        if headset_config['device']:
            hidapi.hid_close(headset_config['device'])
        hidapi.hid_exit()

if __name__ == '__main__':
    for packet in get_packets():
        print(packet)
