from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Dictionary of common grocery categories and items
grocery_categories = {
    "veg": [
        # Fresh Vegetables
        "carrots", "tomatoes", "onions", "potatoes", "lettuce", "spinach", "broccoli", "cauliflower", "peas", "mushrooms",
        "bell peppers", "cucumber", "zucchini", "eggplant", "okra", "bitter gourd", "bottle gourd", "ridge gourd", "green beans", "corn",
        # Indian Vegetables
        "bhindi", "lauki", "karela", "tinda", "arbi", "methi leaves", "palak", "bathua", "sarson ka saag", "lotus root"
    ],
    "non-veg": [
        # Chicken
        "chicken curry cut", "chicken biryani cut", "chicken breast", "chicken wings", "chicken drumsticks",
        "chicken liver", "chicken tandoori", "chicken boneless", "chicken keema", "chicken whole",
        # Mutton
        "mutton curry cut", "mutton biryani cut", "mutton chops", "mutton keema", "mutton liver",
        "mutton ribs", "mutton leg", "mutton brain", "mutton bones", "mutton paya",
        # Fish & Seafood
        "pomfret fish", "rohu fish", "surmai fish", "bangda fish", "prawns",
        "fish fillet", "fish curry cut", "crab", "squid", "mussels",
        # Eggs & Others
        "egg tray", "quail eggs", "duck meat", "turkey meat", "rabbit meat"
    ],
    "vegan": [
        # Protein Sources
        "tofu", "tempeh", "seitan", "textured vegetable protein", "jackfruit meat",
        "soy chunks", "mushroom meat", "pea protein", "beyond meat burger", "impossible meat",
        # Dairy Alternatives
        "almond milk", "soy milk", "oat milk", "coconut milk", "cashew milk",
        "vegan cheese", "vegan butter", "vegan yogurt", "vegan cream", "vegan ice cream",
        # Other Vegan Items
        "nutritional yeast", "aquafaba", "chia seeds", "flax seeds", "hemp seeds"
    ],
    "breakfast": [
        # Hot Items
        "oatmeal", "poha", "upma", "idli", "dosa batter",
        "paratha", "bread", "pancake mix", "waffles", "french toast mix",
        # Cold Items
        "cereal", "muesli", "granola", "cornflakes", "fruit loops",
        # Beverages
        "coffee", "tea", "green tea", "milk", "juice",
        # Spreads
        "butter", "jam", "peanut butter", "honey", "nutella"
    ],
    "lunch": [
        # Main Course
        "rice", "dal", "roti", "naan", "biryani",
        "rajma", "chole", "sambar", "rasam", "curry",
        # Side Dishes
        "pickle", "papad", "chutney", "raita", "salad",
        # Quick Meals
        "sandwiches", "wraps", "pasta", "noodles", "pizza"
    ],
    "dinner": [
        # Indian Main Course
        "dal makhani", "paneer butter masala", "chicken curry", "fish curry", "mutton curry",
        "biryani", "pulao", "jeera rice", "naan", "roti",
        # International
        "pasta", "pizza", "burger", "steak", "grilled chicken",
        # Sides
        "soup", "salad", "garlic bread", "mashed potatoes", "grilled vegetables"
    ],
    "dessert": [
        # Indian Sweets
        "rasgulla", "gulab jamun", "kaju katli", "milk burfi", "jalebi",
        "rasmalai", "kheer", "gajar ka halwa", "ladoo", "barfi",
        "motichoor ladoo", "kala jamun", "rabri", "malai peda", "besan ladoo",
        # International Desserts
        "ice cream", "chocolate cake", "pastries", "cookies", "pudding",
        "brownies", "cheesecake", "tiramisu", "mousse", "pie",
        # Bengali Sweets
        "sandesh", "chamcham", "pantua", "mishti doi", "sondesh"
    ],
    "sugar": [
        # Natural Sweeteners
        "white sugar", "brown sugar", "powdered sugar", "cane sugar", "palm sugar",
        "honey", "maple syrup", "date syrup", "molasses", "jaggery",
        # Sweet Items
        "chocolate", "candy", "toffee", "caramel", "marshmallows",
        # Sweet Spreads
        "nutella", "jam", "marmalade", "golden syrup", "chocolate spread"
    ],
    "sugarless": [
        # Natural Alternatives
        "stevia", "monk fruit sweetener", "erythritol", "xylitol", "allulose",
        # Sugar-free Products
        "sugar-free chocolate", "sugar-free candy", "sugar-free ice cream", "sugar-free cookies", "sugar-free cake",
        "sugar-free jams", "sugar-free syrup", "diet soda", "sugar-free pudding", "sugar-free gum",
        # Diabetic-friendly
        "diabetic chocolate", "diabetic cookies", "diabetic ice cream", "diabetic sweets", "diabetic drinks"
    ]
}

def get_spoonacular_recommendations(query):
    api_key = os.getenv('SPOONACULAR_API_KEY')
    base_url = 'https://api.spoonacular.com/food/ingredients/search'
    
    # Parameters for the API call
    params = {
        'apiKey': api_key,
        'query': query,
        'number': 20,  # Number of results to return
        'sort': 'calories',  # Sort by calories
        'sortDirection': 'asc'  # Ascending order
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Extract ingredient names from the response
        ingredients = [item['name'] for item in data.get('results', [])]
        return ingredients
    except Exception as e:
        print(f"Error calling Spoonacular API: {str(e)}")
        return None

def is_food_related(text):
    # List of food-related keywords
    food_keywords = [
        'food', 'eat', 'meal', 'cook', 'grocery', 'shopping',
        'ingredient', 'recipe', 'diet', 'nutrition', 'healthy',
        'restaurant', 'kitchen', 'snack', 'drink', 'beverage'
    ]
    text = text.lower()
    return any(keyword in text for keyword in food_keywords)

def generate_grocery_list(user_input):
    # Convert user input to lowercase for better matching
    user_input = user_input.lower().strip()
    
    # Check if input is empty
    if not user_input:
        return {
            "success": False,
            "error": "Please enter some text to get grocery suggestions."
        }
    
    # Map common variations to category names
    category_mapping = {
        "vegetarian": "veg",
        "vegetables": "veg",
        "veggies": "veg",
        "healthy": "veg",  # Added mapping for 'healthy'
        "non vegetarian": "non-veg",
        "meat": "non-veg",
        "nonveg": "non-veg",
        "non veg": "non-veg",
        "plant based": "vegan",
        "sweet": "dessert",
        "sweets": "dessert",
        "morning": "breakfast",
        "evening": "dinner",
        "afternoon": "lunch",
        "sugary": "sugar",
        "sugar free": "sugarless",
        "no sugar": "sugarless",
        "diabetic": "sugarless"
    }
    
    # Find matching category
    matched_categories = []
    for key, category in category_mapping.items():
        if key in user_input:
            matched_categories.append(category)
    
    # Direct category matching
    for category in grocery_categories.keys():
        if category in user_input:
            matched_categories.append(category)
    
    # Remove duplicates
    matched_categories = list(set(matched_categories))
    
    # If categories found, return items from all matched categories
    if matched_categories:
        sections = []
        for category in matched_categories:
            title = category.replace("-", " ").title()
            items = grocery_categories[category]
            
            # If query contains 'healthy', prioritize healthy items
            if 'healthy' in user_input:
                if category == 'veg':
                    healthy_items = [
                        "spinach", "broccoli", "kale", "carrots", "sweet potatoes",
                        "bell peppers", "tomatoes", "cucumber", "lettuce", "peas",
                        "green beans", "asparagus", "brussels sprouts", "cauliflower", "quinoa"
                    ]
                    items = healthy_items
                elif category == 'non-veg':
                    healthy_items = [
                        "chicken breast", "salmon", "tuna", "turkey breast", "egg whites",
                        "lean beef", "cod fish", "sardines", "tilapia", "shrimp"
                    ]
                    items = healthy_items
            
            sections.append({
                "title": f"{title} Items",
                "items": items,
                "type": category
            })
            
            # If category is non-veg, add complementary vegetables
            if category == 'non-veg':
                complementary_veggies = [
                    "onions", "tomatoes", "potatoes", "garlic", "ginger",
                    "green chilies", "coriander leaves", "mint leaves", "curry leaves",
                    "bell peppers", "carrots", "lemon"
                ]
                sections.append({
                    "title": "Recommended Vegetables",
                    "items": complementary_veggies,
                    "type": "veg"
                })
        return {
            "success": True,
            "message": f"Here's your grocery list:",
            "sections": sections
        }
    
    # If no category matched but the input is 'healthy', return a healthy food list
    if 'healthy' in user_input:
        return {
            "success": True,
            "message": "Here's a list of healthy food items:",
            "sections": [
                {
                    "title": "Healthy Vegetables",
                    "items": [
                        "spinach", "broccoli", "kale", "carrots", "sweet potatoes",
                        "bell peppers", "tomatoes", "cucumber", "lettuce", "peas"
                    ],
                    "type": "veg"
                },
                {
                    "title": "Healthy Proteins",
                    "items": [
                        "chicken breast", "salmon", "tuna", "turkey breast", "egg whites",
                        "lean beef", "cod fish", "sardines", "tilapia", "shrimp"
                    ],
                    "type": "non-veg"
                },
                {
                    "title": "Healthy Grains & Seeds",
                    "items": [
                        "quinoa", "brown rice", "oats", "chia seeds", "flax seeds",
                        "whole grain bread", "buckwheat", "millet", "amaranth", "wild rice"
                    ],
                    "type": "vegan"
                }
            ]
        }
    
    # If no category matched, try to get recommendations from Spoonacular API
    api_results = get_spoonacular_recommendations(user_input)
    if api_results:
        return {
            "success": True,
            "message": f"Here are some suggested ingredients for '{user_input}':",
            "sections": [
                {
                    "title": "API Recommendations",
                    "items": api_results,
                    "type": "api"
                }
            ]
        }
    
    return {
        "success": False,
        "error": "Please ask about food-related items or use categories like: \n" +
                 "- 'veg' or 'vegetarian'\n" +
                 "- 'non-veg' or 'meat'\n" +
                 "- 'vegan' or 'plant based'\n" +
                 "- 'breakfast', 'lunch', or 'dinner'\n" +
                 "- 'dessert' or 'sweets'\n" +
                 "- 'sugar' or 'sugarless'"
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_list', methods=['POST'])
def get_grocery_list():
    try:
        # Get the raw data from the request
        data = request.get_data()
        if not data:
            return jsonify({"success": False, "error": "Empty request"}), 400

        # Try to parse as JSON
        try:
            json_data = request.get_json()
        except Exception:
            return jsonify({"success": False, "error": "Invalid JSON format"}), 400

        # Validate the message field
        if not json_data or 'message' not in json_data:
            return jsonify({"success": False, "error": "Missing message field"}), 400

        user_input = json_data['message']
        if not isinstance(user_input, str):
            return jsonify({"success": False, "error": "Message must be text"}), 400

        # Generate the grocery list
        result = generate_grocery_list(user_input)
        
        # If the result indicates an error, return it with 400 status
        if not result.get("success", True):
            return jsonify(result), 400
            
        return jsonify(result)

    except Exception as e:
        print(f"Error in get_grocery_list: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "An error occurred while processing your request. Please try again."
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
