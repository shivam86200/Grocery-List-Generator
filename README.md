# Smart Grocery List Generator

A Flask-based web application that helps users generate smart grocery lists based on their requirements. The application uses the Spoonacular API for recipe recommendations and includes various grocery categories.

## Features
- Multiple grocery categories (veg, non-veg, vegan, breakfast, lunch, dinner, etc.)
- Spoonacular API integration for recipe recommendations
- Smart food-related text detection
- Customized grocery list generation

## Setup
1. Clone the repository
```bash
git clone <your-repository-url>
cd AICA3
```

2. Create a virtual environment and activate it
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your Spoonacular API key
```
SPOONACULAR_API_KEY=your_api_key_here
```

5. Run the application
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## Environment Variables
- `SPOONACULAR_API_KEY`: Your Spoonacular API key (required)

## Technologies Used
- Flask
- Python
- HTML/CSS
- Spoonacular API
