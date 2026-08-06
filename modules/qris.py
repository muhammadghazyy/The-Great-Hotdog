from datetime import datetime
import pytz
import json
import tkinter as tk
import tkinter as tk
import qrcode
# import cv2
# import easyocr
import re
from PIL import Image, ImageTk


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
    STATIC_QRIS_DATA = "00020101021126610014COM.GO-JEK.WWW01189360091437022285980210G7022285980303UMI51440014ID.CO.QRIS.WWW0215ID10265321540140303UMI5204839853033605802ID5925SYAFIRA TASYA, Organisasi6013JAKARTA TIMUR61051343062070703A016304FD50"

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



# 

def verify_qris_screen(frame, target_amount=150000):
    # Convert frame to grayscale for OCR processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Perform OCR on the frame
    results = reader.readtext(gray)
    
    detected_text = " ".join([res[1].lower() for res in results])
    print(f"[OCR Raw Text]: {detected_text}")

    # Check 1: Success Keywords used by Indonesian Banks/E-Wallets
    success_keywords = ["berhasil", "success", "transaksi berhasil", "pembayaran berhasil"]
    has_success = any(keyword in detected_text for keyword in success_keywords)

    # Check 2: Match Target Amount (handling formatted numbers like 150.000 or 150000)
    target_str = f"{target_amount:,}".replace(",", ".") # "150.000"
    has_amount = target_str in detected_text or str(target_amount) in detected_text

    if has_success and has_amount:
        return True, detected_text

    return False, detected_text

# --- Camera Loop Demo ---

# Initialize EasyOCR reader (English + Indonesian)
# reader = easyocr.Reader(['en', 'id'], gpu=False)
# cap = cv2.VideoCapture(0)  # Use 0 for default webcam

# TARGET_AMOUNT = 150000

# print("Point phone screen with successful payment at the camera...")

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Optional: Draw a target bounding box guide on video stream
#     h, w, _ = frame.shape
#     cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)

#     # Run check when frame is ready
#     is_valid, raw_text = verify_qris_screen(frame, TARGET_AMOUNT)

#     if is_valid:
#         print("\n[SUCCESS] Payment screen verified! Closing window...")
#         cv2.putText(frame, "PAYMENT VERIFIED!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
#         cv2.imshow("Camera Verification", frame)
#         cv2.waitKey(2000)  # Show success state briefly
#         break

#     cv2.imshow("Camera Verification", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()