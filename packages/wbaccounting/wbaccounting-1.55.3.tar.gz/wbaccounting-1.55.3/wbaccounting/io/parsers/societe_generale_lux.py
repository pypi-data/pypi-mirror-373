import csv
import datetime
import hashlib

from schwifty import IBAN

# Bank specific Information for Societe Generale Luxembourg
BANK_COUNTRY_CODE = "LU"
BANK_CODE = "060"


def parse(import_source):
    # Load file into a CSV DictReader
    csv_file = import_source.file.open(mode="rt")

    # Read file into a CSV Dict Reader
    csv_reader = csv.DictReader(csv_file, delimiter=";")

    # Iterate through the CSV File and parse the data into a list
    data = list()
    for transaction in csv_reader:
        if amount := transaction.get("Amount", None):
            booking_date = datetime.datetime.strptime(transaction["Accounting date"], "%Y/%m/%d").date()
            value_date = datetime.datetime.strptime(transaction["Value date"], "%Y/%m/%d").date()
            currency = transaction["Account currency"]
            value = float(amount.replace(",", "."))
            description = transaction["Transaction main description"]
            bank_account = str(
                IBAN.generate(BANK_COUNTRY_CODE, bank_code=BANK_CODE, account_code=transaction["Account number"])
            )
            item = {
                "booking_date": booking_date.strftime("%Y-%m-%d"),
                "value_date": value_date.strftime("%Y-%m-%d"),
                "currency": currency,
                "value": value,
                "description": description,
                "bank_account": bank_account,
            }
            _hash = hashlib.sha256()
            for field in item.values():
                _hash.update(str(field).encode())

            item["_hash"] = _hash.hexdigest()
            data.append(item)

    csv_file.close()
    return {
        "data": data,
    }
