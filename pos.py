import json
from modules.inventory import update_inventory, check_inventory
from modules.receipt import print_cart, print_menu, total_price_generator
from modules.payment import process_payment, transaction_id_creation, save_transaction
from modules.qris import qris_payment

# Load the price data from the JSON file
with open("data/products.json", "r") as f:
    price_data = json.load(f)

# Load inventory
with open("data/inventory.json", "r") as t:
    inventory_data = json.load(t)

def ask_first_time(title="Welcome to Grand Hotdog of Ghaz"):
    """ Asking the user for their first order. """

    while True:
        print(title)
        print_menu(price_data)
        print(f"""Please select your order by entering the corresponding number.""")
        
        input_order = input("Enter your order: ")

        if input_order in price_data.keys():
            return input_order
        else:
            print("Invalid order. Please try again.")


def ask_repeat_order():
    """ Asking the user for their next order. This function called again and again until the user press n"""

    print(f"""
    Anything else?
    Please select your order by entering the corresponding number. Press 'n' to finish your order.
    """)
    add_order = input("Enter your order: ")
    return add_order


def main():

    store_location  = "GHZJKT1"
    store_timezone  = "Asia/Jakarta"
    vat             = 0.12

    transaction_id = transaction_id_creation(store_location)

    cart = []
    cart.append(str(ask_first_time()))
    add_order = ask_repeat_order()

    while True:
        if add_order.lower() == "n":
            break
        if add_order in price_data.keys():
            cart.append(str(add_order))
            add_order = ask_repeat_order()
        else:
            print("Invalid order. Please try again.")
            add_order = ask_repeat_order()

    if not check_inventory(cart, price_data, inventory_data):
        print("Sorry, we don't have enough ingredients to fulfill your order.")
        return

    print_cart(cart, price_data, transaction_id, vat=vat)
    total_price, subtotal, vat_service = total_price_generator(cart, price_data, vat)

    while True:
        try:
            payment_choice = input(f"Please select payment method \n1. Cash \n2. QRIS \nEnter your choice:")
            if payment_choice == "1":
                pay_amount, change_final = process_payment(total_price)
                print_cart(cart, price_data,  transaction_id, pay_amount, change_final, vat)
                save_transaction(cart, total_price, pay_amount, change_final, transaction_id, store_timezone, price_data, payment_choice)
                break
            elif payment_choice == "2":
                qris_payment(total_price)
                print_cart(cart, price_data, transaction_id, total_price, 0, vat)
                save_transaction(cart, total_price, total_price, 0, transaction_id, store_timezone, price_data, payment_choice)
                break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue

    update_inventory(cart, price_data, inventory_data)

if __name__ == "__main__":
    main()