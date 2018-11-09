# -*- coding: utf-8 -*-
from smartcard.CardRequest import CardRequest
from smartcard.CardType import AnyCardType

from healthcard.reader import HealthCardReader

cardtype = AnyCardType()
cardrequest = CardRequest( timeout=None, cardType=cardtype )
cardservice = cardrequest.waitforcard()
reader = HealthCardReader(cardservice=cardservice)
healthcard = reader.get_health_card()
print(healthcard.patient.to_json())