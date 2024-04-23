import requests, openai
from django.shortcuts import render, redirect
from .api_client import search_food, get_nutrient_values, CustomChatGPT
from .models import WeightEntry, FoodEntry
from .forms import WeightEntryForm
from datetime import date, datetime
from django.http import JsonResponse

def home(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')
        meal_type = request.POST.get('meal_type')
        calories = float(request.POST.get('calories'))
        protein = float(request.POST.get('protein'))
        carbs = float(request.POST.get('carbs'))
        fat = float(request.POST.get('fat'))
        water = float(request.POST.get('water'))

        FoodEntry.objects.create(
            food_name=food_name,
            meal_type=meal_type,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            water=water
        )

    # Get today's date
    today = datetime.now().date()

    # Filter food entries for today
    food_entries = FoodEntry.objects.filter(created_at__date=today)
    food_entries = FoodEntry.objects.all()
    total_calories = sum(entry.calories for entry in food_entries)
    total_protein = sum(entry.protein for entry in food_entries)
    total_carbs = sum(entry.carbs for entry in food_entries)
    total_fat = sum(entry.fat for entry in food_entries)

    context = {
        'food_entries': food_entries,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat,
    }

    return render(request, "home.html", context)


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

def chatbot(request):
    if request.method == 'POST':
        input_text = request.POST.get('input_text', '')
        output_text = CustomChatGPT(input_text)
        return render(request, 'chatbot.html', {'input_text': input_text, 'output_text': output_text})
    else:
        return render(request, 'chatbot.html')

def macro_calculator(request):
    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')
        activity_level = float(request.POST.get('activity_level'))

        # Calculate BMR based on gender
        if gender == 'male':
            bmr = 66 + (6.2 * weight) + (12.7 * height) - (6.76 * age)
        else:
            bmr = 655.1 + (4.35 * weight) + (4.7 * height) - (4.7 * age)
        
        # Adjust BMR based on activity level
        tdee = bmr * activity_level
        
        # Calculate macros based on TDEE and user's goals
        # For example, you can use percentages of calories for each macro
        
        # Assuming a typical ratio for macronutrients
        protein_ratio = 0.3
        carbs_ratio = 0.5
        fat_ratio = 0.2
        
        protein_calories = tdee * protein_ratio
        carbs_calories = tdee * carbs_ratio
        fat_calories = tdee * fat_ratio
        
        protein_grams = protein_calories / 4  # 4 calories per gram of protein
        carbs_grams = carbs_calories / 4      # 4 calories per gram of carbs
        fat_grams = fat_calories / 9          # 9 calories per gram of fat

        context = {
            'bmr': bmr,
            'tdee': tdee,
            'protein_grams': protein_grams,
            'carbs_grams': carbs_grams,
            'fat_grams': fat_grams,
        }

        return render(request, "macro_calculator_result.html", context)

    return render(request, "macro_calculator.html")
