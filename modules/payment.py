from datetime import datetime
import pytz
import json
import tkinter as tk
import tkinter as tk
import qrcode
from PIL import Image, ImageTk

def process_payment(total_price):
    """ Process the payment by asking the user for the payment amount and calculating the change. """
    while True:
        try:
            input_amount = float(input("Please enter the payment amount: "))
            if input_amount >= total_price:
                change = input_amount - total_price
                print(f"Payment successful! Your change is Rp {change:,}.")
                return input_amount, change
            else:
                print(f"Insufficient payment. You need to pay at least Rp {total_price:,}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    

def transaction_id_creation(store_location, timezone = "Asia/Jakarta"):
    """ Create a unique transaction ID based on the store location and current date and time. """

    utc7 = pytz.timezone(timezone)
    now = datetime.now(utc7)
    return f"{store_location}-{now.strftime('%Y%m%d-%H%M%S')}{now.microsecond // 1000:03d}"

def save_transaction(cart, total_price, pay_amount, change_final, transaction_id, timezone, price_data, payment_choice):
    """ Save the transaction details to a JSON file. """

    utc7 = pytz.timezone(timezone)
    now = datetime.now(utc7)

    with open("data/transactions.json", "r") as t:
        transaction_data = json.load(t)

    total_item = {}
    for item in cart:
        if item not in total_item.keys():
            total_item[item] = 1
        elif item in total_item.keys():
            total_item[item] += 1
    for item, quantity in total_item.items():
        item_data = price_data[item]
        total_item[item] = {
            "quantity": quantity,
            "price": item_data['price'] * quantity
        }
        

    to_insert_to_transaction_data = {
        "transaction_id": transaction_id,
        "cart": total_item,
        "subtotal": total_price,
        "pay_amount": pay_amount,
        "change": change_final,
        "date": f"{now.strftime('%Y-%m-%d %H:%M:%S')}",
        "payment_type": f"{'Cash' if payment_choice == '1' else 'QRIS'}"
    }

    transaction_data.append(to_insert_to_transaction_data)

    with open("data/transactions.json", "w") as t:
        json.dump(transaction_data, t, indent=4)



