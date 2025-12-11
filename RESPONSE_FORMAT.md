# API Response Format Documentation

## Overview
The `/mealplan` endpoint receives a raw text response from Groq API and parses it into a structured JSON format.

---

## 1. Raw Response from Groq (String Format)

The API receives a **plain text string** from Groq with bracket-delimited format:

```
[Target weight]:[70kg], [Total Calories]:[2000], [Total Carbs]:[250g], [Total Fat]:[65g], [Total Fiber]:[28g], [Total Protein]:[150g], [day 1]:[Breakfast]:[200g Puttu with 2 medium bananas and 10g sugar][Short Name]:[Puttu, Banana, Sugar][Calories]:[350], [Snack 1]:[30g Banana Chips][Short Name]:[Banana Chips][Calories]:[150], [Lunch]:[150g Rice with 100ml Sambar and 80g Fish Fry][Short Name]:[Rice, Sambar, Fish Fry][Calories]:[520], [Snack 2]:[50g Mixed Nuts][Short Name]:[Mixed Nuts][Calories]:[300], [Dinner]:[2 pieces Appam with 150ml Vegetable Stew][Short Name]:[Appam, Vegetable Stew][Calories]:[380], [day 2]:...
```

### Format Rules:
- All values must be enclosed in square brackets: `[value]`
- Pattern: `[Key]:[Value]`
- Meal format: `[Meal Type]:[Meal Content][Short Name]:[Food Names][Calories]:[Number]`
- Day format: `[day N]:[Meal entries...]`

---

## 2. Parsed JSON Response (Returned to Client)

The API parses the raw string and returns a **structured JSON object**:

```json
{
  "target_weight": "70kg",
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
        "Breakfast": "200g Puttu with 2 medium bananas and 10g sugar",
        "Snack 1": "30g Banana Chips",
        "Lunch": "150g Rice with 100ml Sambar and 80g Fish Fry",
        "Snack 2": "50g Mixed Nuts",
        "Dinner": "2 pieces Appam with 150ml Vegetable Stew"
      },
      "short_names": {
        "Breakfast": "Puttu, Banana, Sugar",
        "Snack 1": "Banana Chips",
        "Lunch": "Rice, Sambar, Fish Fry",
        "Snack 2": "Mixed Nuts",
        "Dinner": "Appam, Vegetable Stew"
      },
      "calories": {
        "Breakfast": 350,
        "Snack 1": 150,
        "Lunch": 520,
        "Snack 2": 300,
        "Dinner": 380
      }
    },
    // ... days 2-7
  ]
}
```

---

## 3. Response Structure Details

### Top-Level Fields:
- **`target_weight`** (string): Target weight goal (e.g., "70kg")
- **`macros`** (object): Daily macro targets
  - `Total Calories` (string): e.g., "2000"
  - `Total Carbs` (string): e.g., "250g"
  - `Total Protein` (string): e.g., "150g"
  - `Total Fat` (string): e.g., "65g"
  - `Total Fiber` (string): e.g., "28g"
- **`meal_plan`** (array): Array of 7 day objects

### Day Object Structure:
Each day object contains:
- **`day`** (integer): Day number (1-7)
- **`meals`** (object): Detailed meal descriptions with quantities
  - `Breakfast` (string): Full meal description with quantities
  - `Snack 1` (string): Morning snack
  - `Lunch` (string): Lunch meal
  - `Snack 2` (string): Evening snack (optional - excluded for weight gain)
  - `Dinner` (string): Dinner meal
- **`short_names`** (object): Comma-separated food names for each meal
- **`calories`** (object): Calorie count for each meal (integers)

---

## 4. Meal Quantity Format

Meals include specific quantities:
- **Grams**: `200g Puttu`, `150g Rice`, `80g Fish Fry`
- **Milliliters**: `100ml Sambar`, `150ml Vegetable Stew`
- **Pieces**: `2 pieces Appam`, `3 pieces Idli`
- **Cups**: `1 cup Orange segments`
- **Medium/Large**: `1 medium Apple`, `2 medium bananas`

---

## 5. Special Cases

### Weight Gain Plans:
- **No Snack 2**: Weight gain plans exclude `Snack 2` (only 4 meals per day)
- Example: Only `Breakfast`, `Snack 1`, `Lunch`, `Dinner`

### Weight Loss Plans:
- **Includes Snack 2**: Weight loss plans include all 5 meals
- Example: `Breakfast`, `Snack 1`, `Lunch`, `Snack 2`, `Dinner`

---

## 6. Alternative Endpoint (`/alternative`)

Returns a simpler format:
```json
{
  "alternative": "8 almonds (10g)",
  "calories": "56"
}
```

---

## 7. Error Responses

If parsing fails after 3 retries:
```json
{
  "detail": "Failed to generate valid meal plan after 3 attempts"
}
```

---

## Example Files

- **`example_raw_groq_response.txt`**: Raw string format from Groq
- **`example_full_response.json`**: Complete parsed JSON response

---

## Parsing Logic

The API uses regex patterns to extract:
1. Target weight: `\[Target weight\]:([^,]+)`
2. Macros: `\[Total (Calories|Carbs|Protein|Fat|Fiber)\]:\s*\[?(\d+)g?\]?`
3. Days: `\[day (\d+)\]:`
4. Meals: `\[(Breakfast|Snack 1|Lunch|Snack 2|Dinner)\]:\[([^]]+?)\]\[Short Name\]:\[([^]]*?)\]\[Calories\]:\[?(\d+)\]?`

