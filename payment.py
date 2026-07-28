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
    

        

# def transaction_id_creation():
