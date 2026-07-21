import pandas as pd
import json

# Load the price data from the JSON file
with open("price.json", "r") as f:
    price_data = json.load(f)

def print_menu():
    print("Menu:")
    for key, item in price_data.items():
        print(f"{key}. {item['name']} - Rp {item['price']:,}")

def ask_first_time(title="Welcome to Grand Hotdog of Ghaz"):
    while True:
        print(title)
        print(f"""
        {print_menu()}
        Please select your order by entering the corresponding number.
        """)
        
        input_order = input("Enter your order: ")

        if input_order in price_data.keys():
            return input_order
        else:
            print("Invalid order. Please try again.")


def ask_repeat_order():
    print(f"""
    Anything else?

    Please select your order by entering the corresponding number.
    """)
    add_order = input("Enter your order: ")
    return add_order

def print_cart(cart):
    print("=============================== Your Order ===============================")
    print("Your order:\n")

    for item in cart:
        item_data = price_data[item]
        print(f"{item_data['name']}\nRp {item_data['price']:,}\n\n")
    total_price = sum(price_data[item]['price'] for item in cart)

    print("=============================== Total Price ===============================")
    print(f"\nRp {total_price:,}\n")
    print("==========================================================================")

def main():

    cart = []

    input_order = ask_first_time()

    if input_order not in price_data.keys():
        print("Invalid order. Please try again.")
        input_order = ask_first_time()
    else:
        cart.append(str(input_order))

    add_order = ask_repeat_order()

    while True:
        if add_order not in price_data.keys():
            print("Invalid order. Please try again.")
            add_order = ask_repeat_order()
        else:
            cart.append(str(add_order))
            break

    print_cart(cart)

if __name__ == "__main__":
    main()