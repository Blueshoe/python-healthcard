# -*- coding: utf-8 -*-
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType
from time import sleep
from healthcard.reader import HealthCardReader


reader = HealthCardReader()
print('Trying to fetch card data...')
sleep(0.5)
healthcard = reader.get_health_card()
print(healthcard.patient.to_json())