# Meal Planner API

A FastAPI-based meal planning API that generates personalized 7-day meal plans using Groq's LLM. Supports regional Indian cuisines and provides food alternatives.

## Features

- 🍽️ Generate 7-day personalized meal plans
- 🌍 Support for multiple regional Indian cuisines (Kerala, Tamil Nadu, Delhi, Punjab, etc.)
- 🔄 Food alternative suggestions
- 📊 Detailed nutritional information (calories, carbs, protein, fat, fiber)
- 🎯 Weight loss, maintenance, and weight gain meal plans

## API Endpoints

### 1. Generate Meal Plan
**POST** `/mealplan`

Generates a personalized 7-day meal plan based on user preferences.

**Request Body:**
```json
{
  "input_text": "I am a 25-year-old male, 70kg, 175cm, moderately active, want to lose weight. Prefer Kerala cuisine with non-veg options."
}
```

**Response:**
```json
{
  "target_weight": "65kg",
  "macros": {
    "Total Calories": "2000",
    "Total Carbs": "250g",
    "Total Protein": "150g",
    "Total Fat": "65g",
    "Total Fiber": "28g"
  },
  "meal_plan": [
    {
      "day": 1,
      "meals": {
        "Breakfast": "200g Puttu with 2 bananas and 10g sugar",
        "Snack 1": "30g Banana Chips",
        "Lunch": "150g Rice with 100ml Sambar and 80g Fish Fry",
        "Snack 2": "1 Apple",
        "Dinner": "2 pieces Appam with 150ml Vegetable Stew"
      },
      "calories": {
        "Breakfast": 350,
        "Snack 1": 150,
        "Lunch": 520,
        "Snack 2": 80,
        "Dinner": 380
      },
      "short_names": {
        "Breakfast": "Puttu, Banana, Sugar",
        "Lunch": "Rice, Sambar, Fish Fry",
        "Dinner": "Appam, Vegetable Stew"
      }
    }
    // ... 6 more days
  ]
}
```

### 2. Get Food Alternative
**POST** `/alternative`

Suggests a nutritionally similar alternative for a given food item.

**Request Body:**
```json
{
  "input_text": "emergency: 200g Rice"
}
```

**Response:**
```json
{
  "alternative": "150g Quinoa",
  "calories": "220"
}
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd backend
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   GROQ_API_KEY=your_actual_api_key_here
   ```

5. **Run the server**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

The API will be available at `http://localhost:8080`

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs (Swagger UI):** http://localhost:8080/docs
- **Alternative API Docs (ReDoc):** http://localhost:8080/redoc

## Testing with Postman

### Setup Postman Collection

1. **Create a new Collection** in Postman named "Meal Planner API"

2. **Add Environment Variables** (optional but recommended):
   - `base_url`: `http://localhost:8080`

### Test Endpoints

#### 1. Generate Meal Plan

**Method:** POST  
**URL:** `http://localhost:8080/mealplan`  
**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "input_text": "I am a 30-year-old female, 65kg, 160cm, sedentary lifestyle, want to lose weight. Prefer Tamil Nadu cuisine, vegetarian only."
}
```

**Expected Response:** 200 OK with meal plan JSON

#### 2. Get Food Alternative

**Method:** POST  
**URL:** `http://localhost:8080/alternative`  
**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "input_text": "emergency: 2 pieces Idli"
}
```

**Expected Response:** 200 OK with alternative food suggestion

### Example Postman Requests

See the `POSTMAN_EXAMPLES.md` file for detailed Postman collection export.

## Project Structure

```
backend/
├── main.py                 # FastAPI application and endpoints
├── food_data.py           # Food data imports
├── food_data/             # Regional food data modules
│   ├── kerala_food.py
│   ├── tamil_nadu_food.py
│   └── ...
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Supported Regional Cuisines

- Kerala
- Tamil Nadu
- Delhi
- Haryana
- Himachal Pradesh
- Jammu & Kashmir
- Jharkhand
- Uttarakhand
- Punjab
- Rajasthan
- Uttar Pradesh
- Bihar
- Karnataka
- Andhra Pradesh
- Telangana

## Error Handling

The API returns appropriate HTTP status codes:
- `200 OK`: Successful request
- `500 Internal Server Error`: Server error or API failure

## Security Notes

- ⚠️ **Never commit your `.env` file to Git**
- The `.gitignore` file is configured to exclude `.env`
- Always use environment variables for sensitive data like API keys

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

