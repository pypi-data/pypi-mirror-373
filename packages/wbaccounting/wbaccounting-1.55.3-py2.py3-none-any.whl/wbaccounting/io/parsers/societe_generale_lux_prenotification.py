import hashlib
from contextlib import suppress
from datetime import datetime

import pandas as pd
from wbportfolio.models import Product


def parse(import_source):
    csv_file = import_source.file.open()
    df = pd.read_csv(csv_file)
    df = df[~df["Isin"].isnull()]
    df["Trade date"] = df["Trade date"].ffill()

    df_sub = df[
        ["Trade date", "Isin", "Quantity Sub", "Amount Sub class ccy", "Value date Sub", "Nav Class ccy", "Ccy Class"]
    ]
    df_sub = df_sub.rename(
        columns={"Quantity Sub": "quantity", "Amount Sub class ccy": "amount", "Value date Sub": "value_date"}
    )
    df_red = df[
        ["Trade date", "Isin", "Quantity Red", "Amount Red Class ccy", "Value date Red", "Nav Class ccy", "Ccy Class"]
    ]
    df_red = df_red.rename(
        columns={"Quantity Red": "quantity", "Amount Red Class ccy": "amount", "Value date Red": "value_date"}
    )
    df_red["quantity"] = df_red["quantity"] * -1
    df_red["amount"] = df_red["amount"] * -1
    df = pd.concat([df_sub, df_red])
    df["value"] = df["amount"] + (df["quantity"] * df["Nav Class ccy"])

    df = df[df["value"] != 0]

    # Iterate through the CSV File and parse the data into a list
    data = list()
    for transaction in df.to_dict(orient="records"):
        _hash = hashlib.sha256()
        for field in transaction.values():
            _hash.update(str(field).encode())

        description = f'Trade ({transaction["Isin"]}): {transaction["quantity"]} shares and {transaction["amount"]} {transaction["Ccy Class"]}.'

        with suppress(Product.DoesNotExist):
            bank_account = Product.objects.get(isin=transaction["Isin"]).bank_account.iban
            data.append(
                {
                    "booking_date": datetime.strptime(transaction["Trade date"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    "value_date": datetime.strptime(transaction["value_date"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                    "currency": transaction.get("Ccy Class"),
                    "value": float(transaction["value"]),
                    "description": description,
                    "bank_account": bank_account,
                    "prenotification": True,
                    "_hash": _hash.hexdigest(),
                }
            )

    return {
        "data": data,
    }
