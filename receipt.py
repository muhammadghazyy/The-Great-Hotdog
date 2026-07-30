def print_menu(price_data):
    print("Menu:")
    for key, item in price_data.items():
        print(f"{key}. {item['name']:<30} Rp {item['price']:,}")

def total_price_generator(cart, price_data):
    subtotal = sum(price_data[item]['price'] for item in cart)
    vat = subtotal*0.12
    total = subtotal + vat
    return total, subtotal, vat

    

def print_cart(cart, price_data, transaction_id, pay_amount=None, change=None):

    food_check = any(price_data[item]['type'] == 'food' for item in cart)
    drink_check = any(price_data[item]['type'] == 'drink' for item in cart)

    print(f"Transaction ID: {transaction_id}")
    print("=============================== Your Order ===============================")
    if food_check is True:
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
    else:
        pass

    if drink_check is True:
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
    else:
        pass

    subtotal, vat_service = total_price_generator(cart, price_data)

    print("\n=============================== Total Price ===============================")
    print(f"{'Subtotal':<50} Rp {round(subtotal):,}")
    print(f"{'VAT + Service Charge (12%)':<50} Rp {round(vat_service):,}")
    print(f"{'TOTAL':<50} Rp {round(subtotal + vat_service):,}\n")
    if pay_amount is not None:
        print(f"{'Payment':<50} Rp {round(pay_amount):,}" )
    if change is not None:
        print(f"{'Change':<50} Rp {round(float(change)):,}")
    print("==========================================================================")



