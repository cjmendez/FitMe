import requests
from django.shortcuts import render, redirect
from .api_client import search_food, get_nutrient_values
from .models import WeightEntry
from .forms import WeightEntryForm
from datetime import date

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
        # Fetch additional details about the food item
        selected_food_details = search_food(api_key, fdc_id)
        
        if selected_food_details:
            selected_food = selected_food_details['foods'][0]

            # Fetch serving size
            serving_size = None
            serving_size_unit = None
            if 'servingSize' in selected_food and 'servingSizeUnit' in selected_food:
                serving_size = selected_food['servingSize']
                serving_size_unit = selected_food['servingSizeUnit']

            # Iterate over the nutrient values and update them with proper titles and measurements
            for nutrient in nutrient_values:
                nutrient_id = nutrient['nutrient']['id']
                if nutrient_id in nutrient_mapping:
                    nutrient_info = nutrient_mapping[nutrient_id]
                    nutrient['name'] = nutrient_info['name']
                    nutrient['unit'] = nutrient_info['unit']

            return render(request, 'food_detail.html', {'selected_food': selected_food, 'nutrient_values': nutrient_values, 'serving_size': serving_size, 'serving_size_unit': serving_size_unit})
        else:
            error_message = 'Failed to fetch food details. Please try again later.'
            return render(request, 'food_detail.html', {'error_message': error_message})
    else:
        error_message = 'Failed to fetch nutrient values. Please try again later.'
        return render(request, 'food_detail.html', {'error_message': error_message})

def add_weight_entry(request):
    if request.method == 'POST':
        form = WeightEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('weight_tracker')
    else:
        form = WeightEntryForm()
    return render(request, 'add_weight_entry.html', {'form': form})

def weight_tracker(request):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            try:
                entry = WeightEntry.objects.get(id=entry_id)
                entry.delete()
            except WeightEntry.DoesNotExist:
                pass  # Handle the case where entry doesn't exist
        return redirect('weight_tracker')  # Redirect to the same page after removal

    today_date = date.today().strftime("%Y-%m-%d")  # Get today's date in the required format
    selected_date = request.GET.get('selected_date', today_date)  # Get selected date from query parameters
    weight_entries = WeightEntry.objects.filter(date=selected_date)  # Filter weight entries for the selected date

    context = {
        'today_date': today_date,
        'selected_date': selected_date,
        'weight_entries': weight_entries,
    }
    return render(request, 'weight_tracker.html', context)
