=================
python healthcard
=================

This package aims to provide a simple way to read healthcards from the german health insurance system.

It is based off of this repo:
https://github.com/asdil12/python-egk/

Usage
=====

**HealthCardReader**

The usage a pretty straightforward.

.. code-block:: python

    from healthcard.reader import HealthCardReader

    reader = HealthCardReader()
    healthcard = reader.get_health_card()

    print(healthcard.patient.first_name)
    Max

The ``HealthCardReader`` object is automatically looking for a card reader. If there are multiple card readers
available it uses the first one be default. This behavior can be changed however:

.. code-block:: python

    # change the index of the used reader
    reader = HealthCardReader(index=1)

    # or instantiate a cardservice yourself
    from smartcard.CardType import ATRCardType
    from smartcard.CardRequest import CardRequest
    from smartcard.util import toHexString, toBytes
    cardtype = ATRCardType( toBytes( "3B 16 94 20 02 01 00 00 0D" ) )  # just an example APDU
    cardrequest = CardRequest( timeout=1, cardType=cardtype )
    cardservice = cardrequest.waitforcard()

    # This example code is taken from https://pyscard.sourceforge.io/user-guide.html
    reader = HealthCardReader(cardservice=cardservice)

There are currently 3 versions of healthcards defined: G1, G1plus and G2.

The package automatically detects the version and reads the data accordingly.

**HealthCard**

The HealthCard object provides a simple interface to access insurance and patient data:

.. code-block:: python

    healthcard.patient  # Patient object
    healthcard.insurance  # Insurance object
    healthcard.version  # G1, G1plus or G2

It provides 2 JSON formatted outputs - a flattened as well as a hierarchical one:

.. code-block:: python

    healthcard.to_json()
    # and
    healthcard.to_flattened_json()


**Patient**

The Patient object contains the personal data of the healthcard:

.. code-block:: python

    patient.first_name
    patient.insurant_id
    patient.birthdate
    patient.first_name
    patient.last_name
    patient.gender
    patient.prefix
    patient.name_addition
    patient.title

    # depends on version
    patient.postal_address
    # or
    patient.residential_address


**PostalAddress**

.. code-block:: python

    address.city
    address.zip_code
    address.country_code
    address.zip_code
    address.mailbox

**ResidenceAddress**

.. code-block:: python

    address.city
    address.zip_code
    address.country_code
    address.city
    address.street
    address.street_number
    address.address_addition


**Insurance**

This object only contains the name of the insurance.

.. code-block:: python

    insurance.insurance_name

