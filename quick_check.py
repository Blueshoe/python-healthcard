# -*- coding: utf-8 -*-
from time import sleep
from healthcard.reader import HealthCardReader

reader = HealthCardReader()
print("Trying to fetch card data...")
sleep(0.2)
healthcard = reader.get_health_card()
print(healthcard.patient.to_json())
