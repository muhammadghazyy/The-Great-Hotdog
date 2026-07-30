from datetime import datetime
import pytz
import json
import tkinter as tk
import tkinter as tk
import qrcode
from PIL import Image, ImageTk

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


def convert_static_to_dynamic_qris(static_qris_str: str, amount: int) -> str:
    """Converts a static QRIS payload string to dynamic by injecting Tag 54 (Amount)

    and updating CRC16.
    """
    # 1. Change Point of Initiation Method from Static (010211) to Dynamic (010212)
    qris = static_qris_str.replace("010211", "010212")

    # 2. Strip existing trailing CRC (Tag 63: "6304XXXX")
    if "6304" in qris:
        qris = qris[: qris.rfind("6304")]

    # 3. Format Tag 54 (Amount) -> Tag 54 + Length (2 digits) + Amount Value
    amt_str = str(int(amount))
    tag_54 = f"54{len(amt_str):02d}{amt_str}"

    # Inject Tag 54 before Currency Code (Tag 53)
    idx_53 = qris.find("5303360")  # 360 is IDR
    if idx_53 != -1:
        qris = qris[: idx_53 + 7] + tag_54 + qris[idx_53 + 7 :]

    # 4. Append Tag 63 header for CRC calculation
    qris += "6304"

    # 5. Calculate CRC16-CCITT (0xFFFF)
    crc = 0xFFFF
    for char in qris.encode("utf-8"):
        crc ^= char << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    return qris + f"{crc:04X}"


def qris_payment(total_price):
    root = tk.Tk()
    root.title("QRIS Payment")

    window_width, window_height = 400, 600
    screen_width, screen_height = (
        root.winfo_screenwidth(),
        root.winfo_screenheight(),
    )
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    tk.Label(root, text="QRIS Payment", font=("Arial", 16, "bold")).pack(
        pady=10
    )
    tk.Label(
        root,
        text=f"Total Price: Rp {round(total_price):,}",
        font=("Arial", 14),
    ).pack(pady=5)

    # RAW STATIC QRIS payload string (Obtain this by scanning your static QRIS once)
    STATIC_QRIS_DATA = "00020101021126710019ID.CO.BANKJATIM.WWW01189360011400000062670215ID20200000592050303UME51440014ID.CO.QRIS.WWW0215ID20200435487890303UME5204866153033605802ID5919INFAQ LAZISMU JATIM6008SURABAYA61056023462070703A016304DEAE"

    # Generate Dynamic Payload
    dynamic_payload = convert_static_to_dynamic_qris(
        STATIC_QRIS_DATA, round(total_price)
    )

    # Generate QR Code image in memory
    qr_img = qrcode.make(dynamic_payload).resize((250, 250))
    photo = ImageTk.PhotoImage(qr_img)

    photo_label = tk.Label(root, image=photo)
    photo_label.image = photo  # Keep reference
    photo_label.pack(pady=10)

    tk.Label(
        root, text="Please scan the QR code above", font=("Arial", 12)
    ).pack(pady=5)

    def payment_received():
        root.destroy()

    tk.Button(
        root,
        text="Payment Received",
        command=payment_received,
        font=("Arial", 12),
    ).pack(pady=15)

    root.mainloop()
    return total_price, 0
