# Postman Testing Guide

## Quick Start

1. Import the collection JSON (see below) into Postman
2. Set up environment variables (optional)
3. Start your FastAPI server: `python main.py`
4. Test the endpoints!

## Postman Collection JSON

Copy this JSON and import it into Postman:

```json
{
  "info": {
    "name": "Meal Planner API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Generate Meal Plan",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"input_text\": \"I am a 25-year-old male, 70kg, 175cm, moderately active, want to lose weight. Prefer Kerala cuisine with non-veg options.\"\n}"
        },
        "url": {
          "raw": "http://localhost:8080/mealplan",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8080",
          "path": ["mealplan"]
        }
      }
    },
    {
      "name": "Get Food Alternative",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"input_text\": \"emergency: 200g Rice\"\n}"
        },
        "url": {
          "raw": "http://localhost:8080/alternative",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8080",
          "path": ["alternative"]
        }
      }
    },
    {
      "name": "Meal Plan - Weight Loss (Vegetarian)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"input_text\": \"I am a 30-year-old female, 65kg, 160cm, sedentary lifestyle, want to lose weight. Prefer Tamil Nadu cuisine, vegetarian only.\"\n}"
        },
        "url": {
          "raw": "http://localhost:8080/mealplan",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8080",
          "path": ["mealplan"]
        }
      }
    },
    {
      "name": "Meal Plan - Weight Gain",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"input_text\": \"I am a 22-year-old male, 60kg, 170cm, active lifestyle, want to gain weight. Prefer Punjabi cuisine.\"\n}"
        },
        "url": {
          "raw": "http://localhost:8080/mealplan",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8080",
          "path": ["mealplan"]
        }
      }
    }
  ]
}
```

## Manual Testing Steps

### Test 1: Generate Meal Plan

1. Open Postman
2. Create a new POST request
3. Set URL to: `http://localhost:8080/mealplan`
4. Go to **Headers** tab and add:
   - Key: `Content-Type`
   - Value: `application/json`
5. Go to **Body** tab, select **raw** and **JSON**
6. Paste this JSON:
```json
{
  "input_text": "I am a 25-year-old male, 70kg, 175cm, moderately active, want to lose weight. Prefer Kerala cuisine with non-veg options."
}
```
7. Click **Send**
8. You should receive a 200 OK response with a complete 7-day meal plan

### Test 2: Get Food Alternative

1. Create a new POST request
2. Set URL to: `http://localhost:8080/alternative`
3. Set Headers: `Content-Type: application/json`
4. Set Body (raw JSON):
```json
{
  "input_text": "emergency: 200g Rice"
}
```
5. Click **Send**
6. You should receive a 200 OK response with an alternative food suggestion

## Expected Responses

### Successful Meal Plan Response
- Status: `200 OK`
- Response time: 10-30 seconds (depends on Groq API)
- Body: JSON with `target_weight`, `macros`, and `meal_plan` array

### Successful Alternative Response
- Status: `200 OK`
- Response time: 2-5 seconds
- Body: JSON with `alternative` and `calories` fields

### Error Response
- Status: `500 Internal Server Error`
- Body: JSON with `detail` field containing error message

## Troubleshooting

1. **Connection Refused**: Make sure the FastAPI server is running on port 8080
2. **500 Error**: Check that your `.env` file has a valid `GROQ_API_KEY`
3. **Timeout**: The meal plan generation can take 10-30 seconds, be patient
4. **Invalid JSON**: Make sure your request body is valid JSON

