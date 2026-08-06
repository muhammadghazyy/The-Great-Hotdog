import json

def check_inventory(cart, price_data, inventory_data):
    """ Check if there are enough ingredients in the inventory to fulfill the order in the cart. """
    used_ingredients = {}
    for item in cart:
        recipe = price_data[item]['recipe']
        for ingredient, quantity in recipe.items():
            if ingredient not in used_ingredients:
                used_ingredients[ingredient] = quantity
            else:
                used_ingredients[ingredient] += quantity

    for ingredient, quantity in used_ingredients.items():
        if inventory_data.get(ingredient, 0) < quantity:
            return False
    return True

def update_inventory(cart, price_data, inventory_data):
    """ Update the inventory by subtracting the used ingredients based on the order in the cart. """
    used_ingredients = {}
    for item in cart:
        recipe = price_data[item]['recipe']
        for ingredient, quantity in recipe.items():
            if ingredient not in used_ingredients:
                used_ingredients[ingredient] = quantity
            else:
                used_ingredients[ingredient] += quantity

    for ingredient, quantity in used_ingredients.items():
        inventory_data[ingredient] -= quantity

    with open("data/inventory.json", "w") as t:
        json.dump(inventory_data, t, indent=4)