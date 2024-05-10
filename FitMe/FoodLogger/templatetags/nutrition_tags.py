from django import template

register = template.Library()

@register.filter
def get_nutrient(nutrient_values, nutrient_name):
    # Correcting the expected nutrient names based on the actual data structure observed
    name_map = {
        'Calories (Energy)': 'Energy',
        'Carbohydrates': 'Carbohydrate, by difference',
        'Total Fat': 'Total lipid (fat)'
    }
    
    corrected_name = name_map.get(nutrient_name, nutrient_name)  # Get the corrected name from the map, defaulting to the provided name
    
    print(f"Searching for nutrient: {corrected_name}")
    print(f"Available nutrients: {nutrient_values}")
    for nutrient in nutrient_values:
        print(f"Checking nutrient: {nutrient['nutrient']['name']}")
        if nutrient['nutrient']['name'] == corrected_name:
            print(f"Nutrient found: {nutrient_name} with amount {nutrient['amount']}")
            return nutrient['amount']
    print(f"Nutrient {nutrient_name} not found.")
    return 0  # Return 0 if the nutrient is not found

