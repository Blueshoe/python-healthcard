# -*- coding: utf-8 -*-
import json
import zlib
from datetime import datetime
from json import JSONEncoder

from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.System import readers

from healthcard.address import ResidenceAddress
from healthcard.exceptions import HealthCardException, HealthCardReadException
from healthcard.insurance import Insurance
from healthcard.patient import Patient
from healthcard.utils import unpack_bcd, decode_bcd

COMMANDS = {
    'SELECT_MF': [0x00, 0xA4, 0x04, 0x0C, 0x07, 0xD2, 0x76, 0x00, 0x01, 0x44, 0x80, 0x00],
    'SELECT_HCA': [0x00, 0xA4, 0x04, 0x0C, 0x06, 0xD2, 0x76, 0x00, 0x00, 0x01, 0x02],
    'EF_GDO': [0x00, 0xB0, 0x82, 0x00, 0x00],
    'EF_VERSION_1': [0x00, 0xB2, 0x01, 0x84, 0x00],
    'EF_VERSION_2': [0x00, 0xB2, 0x02, 0x84, 0x00],
    'EF_VERSION_3': [0x00, 0xB2, 0x03, 0x84, 0x00],
    'SELECT_FILE_PD': [0x00, 0xB0, 0x81, 0x00, 0x02],
    'SELECT_FILE_VD': [0x00, 0xB0, 0x82, 0x00, 0x08],
    'RESET_CARD_TERMINAL': [0x20, 0x11, 0x00, 0x00, 0x00],
    'GET_CARD': [0x20, 0x12, 0x01, 0x00, 0x01, 0x05],
    'EJECT_CARD': [0x20, 0x15, 0x01, 0x00, 0x01, 0x01]
}

# SFID - Short file identifier. These are only valid in conjunction with the Parent-Directory (DF)
SFID = {
    'EF.ATR': 0x1D,  # in MF
    'EF.GDO': 0x02,  # in MF
    'EF.Version': 0x10,  # in MF
    'EF.StatusVD': 0x0C,  # in MF
    'EF.PD': 0x01,  # in HCA
    'EF.VD': 0x02,  # in HCA
}


class HealthCard(object):

    def __init__(self, generation, patient, insurance):
        self.patient = patient
        self.insurance = insurance
        self.version = generation

    def to_json(self):
        return HealthCardJSONEncoder().encode(self)

    def to_flattened_json(self):
        return json.dumps({
            'firstName': self.patient.first_name,
            'lastName': self.patient.last_name,
            'gender': self.patient.gender.lower(),
            'insuranceId': self.patient.insurant_id,
            'prefix': self.patient.prefix,
            'title': self.patient.title,
            'birthday': self.patient.birthdate.strftime('%d.%m.%Y'),
            'nameAddition': self.patient.name_addition,
            'city': self.patient.address.city,
            'zipCode': self.patient.address.zip_code,
            'country': self.patient.address.country_code,
            'street': self.patient.address.street,
            'streetNumber': self.patient.address.street_number,
            'addressAddition': self.patient.address.address_addition,
        })


class HealthCardReader(object):

    def __init__(self, index=0, cardservice=None):
        try:
            if cardservice:
                self.connection = cardservice.connection
            else:
                r = readers()
                if len(r) < 1:
                    raise HealthCardException('No reader found.')
                self.reader = r[index]
                self.connection = self.reader.createConnection()

            self.connection.connect()
        except (NoCardException, CardConnectionException):
            print('No card inserted for reader: {}'.format(self.reader))

    def create_read_command(self, pos, length):
        bpos = [pos >> 8 & 0xFF, pos & 0xFF]
        return [0x00, 0xB0, bpos[0], bpos[1], length]

    def run_command(self, adpu):
        data, sw1, sw2 = self.connection.transmit(adpu)
        if (sw1, sw2) != (0x90, 0x00):
            if (sw1, sw2) == (0x62, 0x83):
                raise HealthCardException('File deactivated.')
            elif (sw1, sw2) == (0x6A, 0x82):
                raise HealthCardException('File not found.')
            elif (sw1, sw2) == (0x69, 0x00):
                raise HealthCardException('Command is not allowed.')
            elif (sw1, sw2) == (0x62, 0x82):
                raise HealthCardReadException('End Of File Reached Warning.')
            elif (sw1, sw2) == (0x62, 0x81):
                raise HealthCardReadException('Corrupted Data Warning.')
            elif (sw1, sw2) == (0x69, 0x86):
                raise HealthCardReadException('No current EF.')
            elif (sw1, sw2) == (0x69, 0x82):
                raise HealthCardReadException('Security Status not satisfied.')
            elif (sw1, sw2) == (0x69, 0x81):
                raise HealthCardReadException('Wrong File Type.')
            elif (sw1, sw2) == (0x6B, 0x00):
                raise HealthCardReadException('Offset too big.')
        return data

    def read_file(self, offset, length):
        data = []
        max_read = 0xFC
        pointer = offset
        while len(data) < length:
            bytes_left = length - len(data)
            readlen = bytes_left if bytes_left < max_read else max_read
            data_chunk = self.run_command(self.create_read_command(pointer, readlen))
            pointer += readlen
            data.extend(data_chunk)
        return data

    def get_version(self, adpu):
        data = self.run_command(adpu)
        hdata = unpack_bcd(data)
        version = "%i.%i.%i" % (
            decode_bcd(hdata[0:3]),
            decode_bcd(hdata[3:6]),
            decode_bcd(hdata[6:10])
        )
        return version

    def get_card_generation(self):
        ef_version_1 = self.get_version(COMMANDS['EF_VERSION_1'])
        ef_version_2 = self.get_version(COMMANDS['EF_VERSION_2'])
        ef_version_3 = self.get_version(COMMANDS['EF_VERSION_3'])

        if ef_version_1 == '3.0.0' and ef_version_2 == '3.0.0' and ef_version_3 == '3.0.2':
            generation = 'G1'
        elif ef_version_1 == '3.0.0' and ef_version_2 == '3.0.1' and ef_version_3 == '3.0.3':
            generation = 'G1 plus'
        elif ef_version_1 == '4.0.0' and ef_version_2 == '4.0.0' and ef_version_3 == '4.0.2':
            generation = 'G2'
        else:
            generation = 'unknown'
        return generation

    def get_health_card(self):

        # Select Masterfile (root)
        self.run_command(COMMANDS['SELECT_MF'])

        card_generation = self.get_card_generation()
        # Select Health Care Application
        self.run_command(COMMANDS['SELECT_HCA'])
        # Select file containing patient data
        self.run_command(COMMANDS['SELECT_FILE_PD'])

        # Create read command for the first two bytes of patient file.
        # Read first two byte of patient data. These contain the length of the PD file.
        data = self.run_command(self.create_read_command(0x00, 0x02))
        pd_length = (data[0] << 8) + data[1]
        # Since the two bytes are included themselves those two bytes are subtracted from the length.
        pd_length -= 0x02

        self.run_command(COMMANDS['SELECT_MF'])
        self.run_command(COMMANDS['SELECT_HCA'])
        # print('select pd')
        self.run_command(COMMANDS['SELECT_FILE_PD'])

        patient_data_compressed = self.read_file(0x02, pd_length)

        self.run_command(COMMANDS['SELECT_MF'])
        self.run_command(COMMANDS['SELECT_HCA'])
        # Select file containing insurance data
        self.run_command(COMMANDS['SELECT_FILE_VD'])

        # Read the first 8 byte of the EF.VD
        # The first two bytes contain the offset of the start of the unprotected insurance data.
        # The bytes 3 and 4 contain the offset of the end of the unprotected insurance data.
        # The bytes 5 and 6 contain the offset of the start of the protected insurance data.
        # The bytes 7 and 8 contain the offset of the end of the protected insurance data.
        data = self.run_command(self.create_read_command(0x00, 0x08))

        # Calculate the length of the unprotected insurance data.
        # Since we have zero based counting we need to subtract 1.
        vd_start = (data[0] << 8) + data[1]
        vd_end = (data[2] << 8) + data[3]
        vd_length = vd_end - (vd_start - 1)

        self.run_command(COMMANDS['SELECT_MF'])
        self.run_command(COMMANDS['SELECT_HCA'])
        self.run_command(COMMANDS['SELECT_FILE_VD'])

        insurance_data_compressed = self.read_file(vd_start, vd_length)

        patient_data_compressed.extend([0x00] * 16)
        patient_data_compressed = bytearray(patient_data_compressed)
        patient_data_compressed = bytes(patient_data_compressed)
        patient_data_xml = zlib.decompress(patient_data_compressed, 15 + 16)
        print(patient_data_xml)

        insurance_data_compressed.extend([0x00] * 16)
        insurance_data_compressed = bytearray(insurance_data_compressed)
        insurance_data_compressed = bytes(insurance_data_compressed)
        insurance_data_xml = zlib.decompress(insurance_data_compressed, 15 + 16)
        print(insurance_data_xml)

        patient = Patient(patient_data_xml)
        insurance = Insurance(insurance_data_xml)

        self.connection.disconnect()

        return HealthCard(generation=card_generation, patient=patient, insurance=insurance)


class HealthCardJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (HealthCard, Insurance, Patient, ResidenceAddress)):
            return o.__dict__
        if type(o) is datetime:
            return o.strftime('%d.%m.%Y')
        if type(o) is bytes:
            try:
                return o.decode('iso-8859-15')
            except AttributeError:
                raise TypeError(repr(o) + " is not JSON serializable")
        raise TypeError(repr(o) + " is not JSON serializable")
