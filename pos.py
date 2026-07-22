import json

# Load the price data from the JSON file
with open("price.json", "r") as f:
    price_data = json.load(f)

def print_menu():
    print("Menu:")
    for key, item in price_data.items():
        print(f"{key}. {item['name']:<30} Rp {item['price']:,}")

def ask_first_time(title="Welcome to Grand Hotdog of Ghaz"):
    while True:
        print(title)
        print_menu()
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

def print_cart(cart):
    print("=============================== Your Order ===============================")
    print("Your order:\n")

    print('Foods\n--------------------------------------------------------------------------')
    food_item = {}
    for item in cart:
        if price_data[item]['type'] == 'food':
            if item not in food_item.keys():
                food_item[item] = 1
            elif item in food_item.keys():
                food_item[item] += 1
    for item, quantity in food_item.items():
        item_data = price_data[item]
        print(f"{quantity} x {item_data['name']:<46} Rp {item_data['price'] * quantity:,}")

    print('\nDrinks\n--------------------------------------------------------------------------')
    drink_item = {}
    for item in cart:
        if price_data[item]['type'] == 'drink':
            if item not in drink_item.keys():
                drink_item[item] = 1
            elif item in drink_item.keys():
                drink_item[item] += 1
    for item, quantity in drink_item.items():
        item_data = price_data[item]
        print(f"{quantity} x {item_data['name']:<46} Rp {item_data['price'] * quantity:,}")

    total_price = sum(price_data[item]['price'] for item in cart)

    print("\n=============================== Total Price ===============================")
    print(f"{'Subtotal':<50} Rp {total_price:,}")
    print(f"{'VAT + Service Charge (12%)':<50} Rp {round(total_price * 0.12):,}")
    print(f"{'TOTAL':<50} Rp {round(total_price * 1.12):,}")
    print("==========================================================================")

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

    print_cart(cart)

if __name__ == "__main__":
    main()