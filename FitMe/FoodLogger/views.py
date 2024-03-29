import requests
from django.shortcuts import render
from .api_client import search_food, get_nutrient_values

def home(request):
    return render(request, "home.html")


def food_search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        api_key = 'lwalpcTrahR9d5sAfz7T4rRQHLkhUBOt59H68pc9'  # Replace with your actual API key

        # Perform food search
        search_results = search_food(api_key, search_query)

        if search_results:
            return render(request, 'food_search_results.html', {'search_results': search_results})
        else:
            error_message = 'Failed to fetch search results. Please try again later.'
            return render(request, 'food_search_results.html', {'error_message': error_message})
    else:
        return render(request, 'food_search_results.html')

def food_detail(request, fdc_id):
    api_key = 'lwalpcTrahR9d5sAfz7T4rRQHLkhUBOt59H68pc9'  # Replace with your actual API key

    # Define the nutrient mapping dictionary
    nutrient_mapping = {
        1003: {'name': 'Protein', 'unit': 'grams'},
        1008: {'name': 'Calories (Energy)', 'unit': 'kcal'},
        1004: {'name': 'Total Fat', 'unit': 'grams'},
        1258: {'name': 'Saturated Fat', 'unit': 'grams'},
        1257: {'name': 'Trans Fat', 'unit': 'grams'},
        1253: {'name': 'Cholesterol', 'unit': 'mg'},
        1005: {'name': 'Carbohydrates', 'unit': 'grams'},
        1079: {'name': 'Fiber', 'unit': 'grams'},
        2000: {'name': 'Sugars', 'unit': 'grams'},
        1093: {'name': 'Sodium', 'unit': 'mg'},
        1104: {'name': 'Vitamin A', 'unit': 'IU'},
        1162: {'name': 'Vitamin C', 'unit': 'mg'},
        1087: {'name': 'Calcium', 'unit': 'mg'},
        1089: {'name': 'Iron', 'unit': 'mg'},
        # Add more mappings for other nutrients as needed
    }

    # Get nutrient values for the selected food item
    nutrient_values = get_nutrient_values(api_key, fdc_id)

    if nutrient_values:
        # Iterate over the nutrient values and update them with proper titles and measurements
        for nutrient in nutrient_values:
            nutrient_id = nutrient['nutrient']['id']
            if nutrient_id in nutrient_mapping:
                nutrient_info = nutrient_mapping[nutrient_id]
                nutrient['name'] = nutrient_info['name']
                nutrient['unit'] = nutrient_info['unit']

        return render(request, 'food_detail.html', {'nutrient_values': nutrient_values})
    else:
        error_message = 'Failed to fetch nutrient values. Please try again later.'
        return render(request, 'food_detail.html', {'error_message': error_message})
    
