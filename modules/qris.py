import re
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import easyocr
import qrcode


# --- QRIS Helper Functions ---
def convert_static_to_dynamic_qris(static_qris_str: str, amount: int) -> str:
    """Converts a static QRIS payload string to dynamic by injecting Tag 54 (Amount)

    and updating CRC16.
    """
    qris = static_qris_str.replace("010211", "010212")

    if "6304" in qris:
        qris = qris[: qris.rfind("6304")]

    amt_str = str(int(amount))
    tag_54 = f"54{len(amt_str):02d}{amt_str}"

    idx_53 = qris.find("5303360")  # 360 is IDR
    if idx_53 != -1:
        qris = qris[: idx_53 + 7] + tag_54 + qris[idx_53 + 7 :]

    qris += "6304"

    crc = 0xFFFF
    for char in qris.encode("utf-8"):
        crc ^= char << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    return qris + f"{crc:04X}"


# --- OCR & Verification Helper Functions ---
def check_amount_match(detected_text: str, target_amount: int) -> bool:
    """Matches any variation of number strings against target integer."""
    raw_numbers = re.findall(r"\b\d+(?:[\.,]\d+)*\b", detected_text)

    for match in raw_numbers:
        parts = re.split(r"[\.,]", match)

        # Ignore trailing cents (.00 or ,00)
        if len(parts) > 1 and parts[-1] == "00":
            parts = parts[:-1]

        cleaned_num_str = "".join(parts)

        try:
            if int(cleaned_num_str) == int(target_amount):
                return True
        except ValueError:
            continue

    return False


def verify_qris_screen(reader, frame, target_amount=25000):
    # Grayscale for OCR efficiency
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Read text
    results = reader.readtext(gray)
    detected_text = " ".join([res[1].lower() for res in results])

    # Check 1: Success Keywords
    success_keywords = ["berhasil", "success", "transaksi", "selesai", "paid"]
    has_success = any(keyword in detected_text for keyword in success_keywords)

    # Check 2: Flexible Amount Matching
    has_amount = check_amount_match(detected_text, target_amount)

    if has_success and has_amount:
        return True, detected_text

    return False, detected_text


# --- Unified GUI & Camera Scanner ---
def qris_payment(total_price):
    root = tk.Tk()
    root.title("QRIS Payment & Verification")

    # Set Window Size and Position to Center
    window_width, window_height = 850, 520
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.resizable(False, False)

    # --- UI LAYOUT: Left (QRIS) | Right (Webcam) ---
    left_frame = tk.Frame(root, width=400)
    left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)

    right_frame = tk.Frame(root, width=400)
    right_frame.pack(side="right", fill="both", expand=True, padx=15, pady=10)

    # --- LEFT FRAME: Dynamic QRIS Code ---
    tk.Label(
        left_frame, text="QRIS Payment", font=("Arial", 16, "bold")
    ).pack(pady=5)
    tk.Label(
        left_frame,
        text=f"Total Price: Rp {round(total_price):,}",
        font=("Arial", 13, "bold"),
        fg="#2e7d32",
    ).pack(pady=5)

    # RAW STATIC QRIS payload string
    STATIC_QRIS_DATA = "00020101021126610014COM.GO-JEK.WWW01189360091437022285980210G7022285980303UMI51440014ID.CO.QRIS.WWW0215ID10265321540140303UMI5204839853033605802ID5925SYAFIRA TASYA, Organisasi6013JAKARTA TIMUR61051343062070703A016304FD50"

    dynamic_payload = convert_static_to_dynamic_qris(
        STATIC_QRIS_DATA, round(total_price)
    )

    qr_img = qrcode.make(dynamic_payload).resize((230, 230))
    photo = ImageTk.PhotoImage(qr_img)
    qr_label = tk.Label(left_frame, image=photo)
    qr_label.image = photo  # Keep reference
    qr_label.pack(pady=10)

    tk.Label(
        left_frame, text="Scan with any banking or e-wallet app", font=("Arial", 10)
    ).pack(pady=2)

    # --- RIGHT FRAME: Camera Scanner ---
    tk.Label(
        right_frame, text="Payment Scanner", font=("Arial", 16, "bold")
    ).pack(pady=5)

    cam_label = tk.Label(right_frame, bg="black")
    cam_label.pack(pady=5)

    status_label = tk.Label(
        right_frame,
        text="Scanning for payment receipt screen...",
        font=("Arial", 11, "italic"),
        fg="#f76f00",
    )
    status_label.pack(pady=8)

    # --- Initialize Vision & Camera ---
    try:
        reader = easyocr.Reader(["en", "id"], gpu=True)
    except Exception:
        # Fallback to CPU if GPU fails
        reader = easyocr.Reader(["en", "id"], gpu=False)

    cap = cv2.VideoCapture(0)

    state = {
        "frame_count": 0,
        "is_verified": False,
    }

    # Video Loop Callback
    def update_camera_feed():
        if state["is_verified"]:
            return

        ret, frame = cap.read()
        if not ret:
            root.after(30, update_camera_feed)
            return

        # Frame Dimensions
        h, w, _ = frame.shape

        # Run EasyOCR every 12 frames to preserve video smoothness
        state["frame_count"] += 1
        if state["frame_count"] % 12 == 0:
            is_valid, _ = verify_qris_screen(
                reader, frame, target_amount=round(total_price)
            )
            if is_valid:
                state["is_verified"] = True
                status_label.config(
                    text="✓ PAYMENT VERIFIED!", fg="#2e7d32", font=("Arial", 12, "bold")
                )

        # Draw Target Bounding Box
        box_color = (0, 255, 0) if state["is_verified"] else (0, 165, 255)
        cv2.rectangle(
            frame, (w // 6, h // 6), (5 * w // 6, 5 * h // 6), box_color, 2
        )

        if state["is_verified"]:
            cv2.putText(
                frame,
                "PAYMENT VERIFIED!",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                3,
            )

        # Convert OpenCV BGR to Tkinter RGB PhotoImage
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (380, 280))
        img_pil = Image.fromarray(frame_resized)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        cam_label.img_tk = img_tk  # Keep reference
        cam_label.config(image=img_tk)

        # Schedule Next Loop Execution
        if state["is_verified"]:
            # Hold verified state for 2 seconds, then clean up and exit
            root.after(2000, close_app)
        else:
            root.after(20, update_camera_feed)

    # Cleanup logic on window close or payment completion
    def close_app():
        if cap.isOpened():
            cap.release()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_app)

    # Start Camera Loop
    update_camera_feed()

    root.mainloop()
    return total_price, 0