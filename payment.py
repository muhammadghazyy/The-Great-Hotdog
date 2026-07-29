from datetime import datetime
import pytz
import json
import tkinter as tk

def process_payment(total_price):
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
    

    utc7 = pytz.timezone(timezone)
    now = datetime.now(utc7)
    return f"{store_location}-{now.strftime('%Y%m%d-%H%M%S')}{now.microsecond // 1000:03d}"

def save_transaction(cart, total_price, pay_amount, change_final, transaction_id, timezone, price_data, payment_choice):

    utc7 = pytz.timezone(timezone)
    now = datetime.now(utc7)

    with open("transactions.json", "r") as t:
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

    with open("transactions.json", "w") as t:
        json.dump(transaction_data, t, indent=4)


def qris_payment(total_price):
    root = tk.Tk()
    root.title("QRIS Payment")
    # Set dimensions
    window_width = 600
    window_height = 650

    # Get screen dimensions and calculate center offsets
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))

    # Center the window
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    title = tk.Label(root, text="QRIS Payment", font=("Arial", 16, "bold"))
    title.pack(pady=20)

    total_price_label = tk.Label(root, text=f"Total Price: Rp {round(total_price):,}", font=("Arial", 14))
    total_price_label.pack(pady=10)

    photo = tk.PhotoImage(file = "assets/qris.png").subsample(3, 3)
    photo_label = tk.Label(root, image=photo)
    photo_label.image = photo
    photo_label.pack(pady=10)

    instruction = tk.Label(root, text="Please scan the QR code Above", font=("Arial", 12))
    instruction.pack(pady=10)

    def payment_received():
        root.destroy()
    
    button = tk.Button(root, text="OK", command=payment_received, font=("Arial", 12))
    button.pack(pady=20)

    root.mainloop()

    return total_price, 0