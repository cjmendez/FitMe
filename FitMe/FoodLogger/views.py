import requests, openai
from django.shortcuts import render, redirect
from .api_client import search_food, get_nutrient_values, CustomChatGPT
from .models import WeightEntry, FoodEntry
from .forms import WeightEntryForm
from datetime import date, datetime
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce

def home(request):
    return render(request, 'home.html')

def diary(request):
    today = datetime.now().date()

    # Handling form submissions
    if request.method == 'POST':
        if 'caloric_limit' in request.POST:
            request.session['caloric_limit'] = float(request.POST.get('caloric_limit'))
            request.session['protein_limit'] = float(request.POST.get('protein_limit'))
            request.session['carbs_limit'] = float(request.POST.get('carbs_limit'))
            request.session['fat_limit'] = float(request.POST.get('fat_limit'))
        elif 'food_name' in request.POST:
            FoodEntry.objects.create(
                food_name=request.POST.get('food_name'),
                meal_type=request.POST.get('meal_type'),
                log_date=request.POST.get('log_date', today),
                calories=float(request.POST.get('calories')),
                protein=float(request.POST.get('protein')),
                carbs=float(request.POST.get('carbs')),
                fat=float(request.POST.get('fat')),
                water=float(request.POST.get('water', 0))  # Assuming water is optional
            )

    # Retrieve food entries and calculate totals
    food_entries = FoodEntry.objects.filter(log_date=today)
    totals = food_entries.aggregate(
        total_calories=Coalesce(Sum('calories', output_field=FloatField()), 0.0),
        total_protein=Coalesce(Sum('protein', output_field=FloatField()), 0.0),
        total_carbs=Coalesce(Sum('carbs', output_field=FloatField()), 0.0),
        total_fat=Coalesce(Sum('fat', output_field=FloatField()), 0.0)
    )

    # Retrieve session values or set defaults
    caloric_limit = int(request.session.get('caloric_limit', 2000))
    protein_limit = int(request.session.get('protein_limit', 50))
    carbs_limit = int(request.session.get('carbs_limit', 225))
    fat_limit = int(request.session.get('fat_limit', 78))

    # Calculate remaining nutrients and percentages
    remaining_calories = caloric_limit - totals['total_calories']
    remaining_protein = protein_limit - totals['total_protein']
    remaining_carbs = carbs_limit - totals['total_carbs']
    remaining_fat = fat_limit - totals['total_fat']

    protein_percentage = (totals['total_protein'] / protein_limit * 100) if protein_limit else 0
    carbs_percentage = (totals['total_carbs'] / carbs_limit * 100) if carbs_limit else 0
    fat_percentage = (totals['total_fat'] / fat_limit * 100) if fat_limit else 0
    calories_percentage = (totals['total_calories'] / caloric_limit * 100) if caloric_limit else 0

    context = {
        'food_entries': food_entries,
        'total_calories': totals['total_calories'],
        'caloric_limit': caloric_limit,
        'remaining_calories': remaining_calories,
        'remaining_protein': remaining_protein,
        'remaining_carbs': remaining_carbs,
        'remaining_fat': remaining_fat,
        'protein_limit': protein_limit,
        'carbs_limit': carbs_limit,
        'fat_limit': fat_limit,
        'protein_percentage': int(protein_percentage),
        'carbs_percentage': int(carbs_percentage),
        'fat_percentage': int(fat_percentage),
        'calories_percentage': int(calories_percentage),
        'selected_date': today.strftime('%m/%d/%Y'),
    }

    return render(request, 'diary.html', context)

def food_search(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        api_key = 'lwalpcTrahR9d5sAfz7T4rRQHLkhUBOt59H68pc9'  # Replace with your actual API key

        # Perform food search
        search_results = search_food(api_key, search_query)
        filtered_results = []

        if search_results:
            print("API returned foods:", search_results['foods'])  # Debugging line
            # Filter results based on serving size being a valid number greater than zero
            for food in search_results['foods']:
                if has_valid_serving_size(food):
                    filtered_results.append(food)
                else:
                    print("Filtered out:", food['description'], food.get('servingSize'))  # Debugging line

            print("Filtered foods:", filtered_results)  # Debugging line
            if filtered_results:
                return render(request, 'food_search_results.html', {'search_results': filtered_results})
            else:
                return render(request, 'food_search_results.html', {'error_message': 'No foods found with valid serving sizes.'})
        else:
            error_message = 'Failed to fetch search results. Please try again later.'
            return render(request, 'food_search_results.html', {'error_message': error_message})
    else:
        return render(request, 'food_search_results.html')

def has_valid_serving_size(food):
    """Check if the serving size is a valid number greater than zero."""
    serving_size = food.get('servingSize')
    try:
        valid = float(serving_size) > 0
        print("Checking serving size:", serving_size, "Valid:", valid)  # Debugging line
        return valid
    except (TypeError, ValueError):
        return False

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
        1092: {'name': 'Potassium', 'unit': 'mg'},
        1090: {'name': 'Magnesium', 'unit': 'mg'},
        1085: {'name': 'Zinc', 'unit': 'mg'},
        1110: {'name': 'Vitamin D', 'unit': 'IU'},
        1175: {'name': 'Vitamin B12', 'unit': 'µg'},
        1109: {'name': 'Vitamin E', 'unit': 'mg'},
        1177: {'name': 'Folate', 'unit': 'µg'},
        1185: {'name': 'Niacin (Vitamin B3)', 'unit': 'mg'},
        1183: {'name': 'Vitamin K', 'unit': 'µg'}
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
    # Check if the 'clear' button has been pressed
    if request.GET.get('clear', '') == 'true':
        request.session['conversation'] = []  # Reset conversation
        request.session.modified = 'true'
        return redirect('/chatbot/')  # Redirect to clean the URL

    if 'conversation' not in request.session:
        request.session['conversation'] = []

    if request.method == 'POST':
        input_text = request.POST.get('input_text', '')
        output_text = CustomChatGPT(input_text)
        request.session['conversation'].append({'sender': 'User', 'text': input_text, 'type': 'chat-text'})
        request.session['conversation'].append({'sender': 'Nute', 'text': output_text, 'type': 'chat-response'})
        request.session.modified = True
        return redirect('/chatbot/')

    conversation = request.session.get('conversation', [])
    return render(request, 'chatbot.html', {'conversation': conversation})

def macro_calculator(request):
    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height_feet = int(request.POST.get('height_feet'))
        height_inches = int(request.POST.get('height_inches'))
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')
        activity_level = float(request.POST.get('activity'))
        goal = request.POST.get('goal')
        diet_type = request.POST.get('diet_type', 'balanced')  # Default to balanced

        # Convert height to inches
        height = (height_feet * 12) + height_inches

        # Calculate BMR based on gender
        if gender == 'male':
            bmr = 66 + (6.23 * weight) + (12.7 * height) - (6.76 * age)
        else:
            bmr = 655 + (4.35 * weight) + (4.7 * height) - (4.7 * age)

        # Adjust BMR based on activity level
        tdee = bmr * activity_level

        # Adjust TDEE based on goal
        if goal == 'lose':
            tdee -= 500  # Create a calorie deficit for weight loss
        elif goal == 'gain':
            tdee += 500  # Add a calorie surplus for weight gain

        # Define macro ratios based on diet type
        if diet_type == 'high protein':
            protein_ratio = 0.40
            carbs_ratio = 0.30
            fat_ratio = 0.30
        elif diet_type == 'low carb':
            protein_ratio = 0.30
            carbs_ratio = 0.20
            fat_ratio = 0.50
        elif diet_type == 'low fat':
            protein_ratio = 0.35
            carbs_ratio = 0.45
            fat_ratio = 0.20
        else:  # Balanced or any other types
            protein_ratio = 0.30
            carbs_ratio = 0.40
            fat_ratio = 0.30

        # Calculate macros based on TDEE and ratios
        protein_calories = tdee * protein_ratio
        carbs_calories = tdee * carbs_ratio
        fat_calories = tdee * fat_ratio

        protein_grams = protein_calories / 4  # 4 calories per gram of protein
        carbs_grams = carbs_calories / 4      # 4 calories per gram of carbs
        fat_grams = fat_calories / 9          # 9 calories per gram of fat

        context = {
            'protein_grams': protein_grams,
            'carbs_grams': carbs_grams,
            'fat_grams': fat_grams,
            'tdee': tdee,
            'diet_type': diet_type,
            # Add other context variables if necessary
        }

        return render(request, "macro_calculator_result.html", context)
    else:
        # For a GET request, just render the form page.
        return render(request, "macro_calculator.html")

