import json
from inventory import update_inventory, check_inventory
from receipt import print_cart, print_menu

# Load the price data from the JSON file
with open("products.json", "r") as f:
    price_data = json.load(f)

# Load inventory
with open("inventory.json", "r") as t:
    inventory_data = json.load(t)

def ask_first_time(title="Welcome to Grand Hotdog of Ghaz"):
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
    print(f"""
    Anything else?
    Please select your order by entering the corresponding number. Press 'n' to finish your order.
    """)
    add_order = input("Enter your order: ")
    return add_order


def main():

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

    print_cart(cart, price_data)
    update_inventory(cart, price_data, inventory_data)

if __name__ == "__main__":
    main()