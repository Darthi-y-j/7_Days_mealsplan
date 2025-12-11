from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, List, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import re
from groq import Groq
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
import random
import json
from food_data import (
    kerala_food,
    tamil_nadu_food,
    delhi_food,
    haryana_food,
    himachal_pradesh_food,
    jammu_kashmir_food,
    jharkhand_food,
    uttarakhand_food,
    punjab_food,
    rajasthan_food,
    uttar_pradesh_food,
    bihar_food,
    karnataka_food,
    andhra_pradesh_food,
    telangana_food,
    western_food,
    snacks,
    STATE_FOOD_MAPPING,
)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Optimized Meal Planner API")

# Initialize Groq client with API key
try:
    # Get API key from environment variable
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please create a .env file with your API key.")
    
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq client: {str(e)}")
    raise

def detect_regional_preferences(input_text: str) -> tuple:
    """
    Enhanced function to detect multiple regional preferences from input text
    Returns: (states_list, include_non_veg, detected)
    """
    input_lower = input_text.lower()
    
    # Detect multiple states
    detected_states = []
    
    # State detection mapping
    state_keywords = {
        'kerala': ['kerala', 'ker'],
        'tamil nadu': ['tamil nadu', 'tamilnadu', 'tamil', 'tn'],
        'delhi': ['delhi', 'dilli'],
        'haryana': ['haryana', 'hr'],
        'himachal pradesh': ['himachal pradesh', 'himachal', 'hp'],
        'jammu & kashmir': ['jammu & kashmir', 'jammu and kashmir', 'j&k'],
        'jharkhand': ['jharkhand', 'jh'],
        'uttarakhand': ['uttarakhand', 'uk'],
        'punjab': ['punjab', 'pb'],
        'rajasthan': ['rajasthan', 'rj'],
        'uttar pradesh': ['uttar pradesh', 'up'],
        'bihar': ['bihar', 'br'],
        'karnataka': ['karnataka', 'kar', 'ka'],
        'andhra pradesh': ['andhra pradesh', 'andhra', 'ap'],
        'telangana': ['telangana', 'tel', 'ts']
    }
    
    # Check for all states
    for state, keywords in state_keywords.items():
        if any(keyword in input_lower for keyword in keywords):
            detected_states.append(state)
    
    # Detect non-veg preference
    include_non_veg = True  # Default to including non-veg
    if any(keyword in input_lower for keyword in ['veg only', 'vegetarian only', 'no non-veg', 'veg:']):
        include_non_veg = False
    
    # Also check for structured cuisine info (from original parsing)
    cuisine_match = re.search(r'cuisine:\s*{([^}]+)}', input_text, re.IGNORECASE)
    if cuisine_match:
        cuisine_content = cuisine_match.group(1)
        include_non_veg = 'Non-Veg' in cuisine_content
        
        # NEW: Check if it's a general cuisine without specific regional info
        general_cuisines = ['asian', 'continental', 'mediterranean', 'mexican', 'italian', 'chinese', 'thai', 'japanese', 'korean']
        has_general_cuisine = any(general in cuisine_content.lower() for general in general_cuisines)
        
        region_match = re.search(r'RegionAndState:\s*\[([^\]]+)\]', cuisine_content, re.IGNORECASE)
        if region_match:
            region_content = region_match.group(1)
            
            # Reset detected_states for structured parsing
            detected_states = []
            
            # Check for multiple states in the structured format
            for state in state_keywords:
                if state in region_content or any(kw in region_content.lower() for kw in state_keywords[state]):
                    detected_states.append(state)
        elif has_general_cuisine and not region_match:
            # If it's a general cuisine without RegionAndState, don't load regional foods
            print(f"🌍 GENERAL CUISINE DETECTED: {cuisine_content} - Skipping regional food loading")
            detected_states = []  # Clear any previously detected states
    
    # Remove duplicates while preserving order
    detected_states = list(dict.fromkeys(detected_states))
    
    detected = len(detected_states) > 0
    return detected_states, include_non_veg, detected

def generate_multi_regional_foods_direct(states: List[str], include_non_veg: bool = True) -> dict:
    """
    Generate regional foods with 10 items max per meal type + log selections.
    Returns: Dictionary with 10 foods per meal type, and logs the selections.
    """
    state_food_map = {
        'kerala': kerala_food,
        'tamil nadu': tamil_nadu_food,
        'tamilnadu': tamil_nadu_food,
        'delhi': delhi_food,
        'haryana': haryana_food,
        'himachal pradesh': himachal_pradesh_food,
        'jammu & kashmir': jammu_kashmir_food,
        'jharkhand': jharkhand_food,
        'uttarakhand': uttarakhand_food,
        'punjab': punjab_food,
        'rajasthan': rajasthan_food,
        'uttar pradesh': uttar_pradesh_food,
        'bihar': bihar_food,
        'karnataka': karnataka_food,
        'andhra pradesh': andhra_pradesh_food,
        'telangana': telangana_food
    }
    
    combined_foods = {"breakfast": [], "lunch": [], "dinner": []}
    
    # Logging setup
    print(f"\n🔍 FOOD SELECTION PROCESS (Max 10/meal)")
    print(f"📍 Regions: {', '.join([state.upper() for state in states])}")
    print(f"🍗 Non-Veg Included: {include_non_veg}")
    print("=" * 60)
    
    # Step 1: Combine all foods from specified regions
    for state in states:
        state_lower = state.lower()
        if state_lower in state_food_map:
            state_food = state_food_map[state_lower]
            
            for meal_type in ["breakfast", "lunch", "dinner"]:
                combined_foods[meal_type].extend(state_food[meal_type]["veg"])
                if include_non_veg:
                    combined_foods[meal_type].extend(state_food[meal_type]["non_veg"])
    
    # Step 2: Deduplicate and sample
    for meal_type in combined_foods:
        seen = set()
        unique_foods = [x for x in combined_foods[meal_type] if not (x in seen or seen.add(x))]
        
        # Log pre-sampling stats
        print(f"\n📊 {meal_type.upper()} POOL:")
        print(f" - Total options: {len(combined_foods[meal_type])}")
        print(f" - Unique options: {len(unique_foods)}")
        
        # Apply 10-item limit
        if len(unique_foods) > 10:
            selected = random.sample(unique_foods, 10)
            combined_foods[meal_type] = selected
            print("⚠️ Randomly sampled 10 items (from available pool)")
        else:
            combined_foods[meal_type] = unique_foods
            print(f"✅ Using all {len(unique_foods)} unique items (≤10 limit)")
        
        # Log final selections
        print(f"\n🍽️ SELECTED {meal_type.upper()} ITEMS (10 max):")
        print("-" * 50)
        for i, item in enumerate(combined_foods[meal_type], 1):
            print(f"{i:2d}. {item}")
    
    print("\n" + "=" * 60)
    print(f"🚀 FINAL COUNTS: Breakfast={len(combined_foods['breakfast'])}, "
          f"Lunch={len(combined_foods['lunch'])}, "
          f"Dinner={len(combined_foods['dinner'])}")
    print("=" * 60)
    
    return combined_foods

def create_enhanced_prompt(original_input: str, regional_foods: dict = None, states: List[str] = None) -> str:
    """
    Create an enhanced prompt with regional foods pre-loaded from multiple states
    """
    base_prompt = """You are a meal recommendation expert who MUST generate a complete 7-day meal plan in the EXACT format specified.

CRITICAL: Your final answer must ONLY contain the meal plan in the exact bracketed format. Do NOT include any explanations, thoughts, or additional text before or after the meal plan.

CALORIE GUIDELINES (MANDATORY - Use these to calculate daily calorie needs):

The average daily calorie intake varies based on factors like age, sex, weight, height, and activity level:

FOR WOMEN:
- Sedentary (little or no exercise): 1,600-2,000 calories/day
- Moderately Active (moderate exercise/sports 3-5 days/week): 1,800-2,200 calories/day
- Active (hard exercise/sports 6-7 days/week): 2,000-2,400 calories/day
- Average intake: 1,800-2,400 calories/day

FOR MEN:
- Sedentary: 2,000-2,400 calories/day
- Moderately Active: 2,200-2,800 calories/day
- Active: 2,400-3,000 calories/day
- Average intake: 2,400-3,000 calories/day

WEIGHT LOSS:
- Women: 1,200-1,600 calories/day (0.5-1 kg/week loss)
- Men: 1,500-2,000 calories/day (0.5-1 kg/week loss)
- Aim for a deficit of 500-750 calories/day for sustainable weight loss

WEIGHT GAIN:
- Women: 2,200-2,800 calories/day (0.5-1 kg/week gain)
- Men: 2,800-3,500 calories/day (0.5-1 kg/week gain)
- Aim for a surplus of 250-500 calories/day for gradual weight gain

NUTRITION RATIOS:
- For weight loss: 25 kcal per kg of body weight, with around 1.6g protein/kg, 3g carbs/kg, 0.8g fat/kg, and 14g fiber per 1000 kcal
- For weight maintenance: 30 kcal/kg, 1.8g protein/kg, 4g carbs/kg, 1g fat/kg, and 14g fiber per 1000 kcal
- For weight gain: 35 kcal/kg, 2.2g protein/kg, 6g carbs/kg, 1.2g fat/kg, and 14g fiber per 1000 kcal

EXACT QUANTITY REQUIREMENTS:
- EVERY food item must include exact quantity: weight in grams/ml, pieces, cups, etc.
- Examples: "200g Puttu with 2 bananas and 10g sugar" NOT "Puttu with Banana and Sugar"
- Examples: "150g Rice with 100ml Sambar and 80g Fish Fry" NOT "Rice with Sambar and Fish Fry"
- Examples: "3 pieces Idli with 150ml Coconut Chutney" NOT "Idli with Coconut Chutney"
- BE VERY SPECIFIC with quantities for every single ingredient
- NEVER EVER mention the quantity as 150ml Tomato Upma, or 150 gm Parathas, it's supposed to be 150gm Tomato Upma and 2 or 3pcs Paratha
BE VERY careful in quantifying the foods, understand where you should mention gm, pcs and ml and don't mix them up.
EXAMPLE: Banana, paratha and food like these should be quantified in pcs, whereas rice, noodles, etc should be quantified in grams, and if it's a liquid, then mention it in ml.

EXACT FORMAT REQUIREMENTS (FOLLOW PRECISELY):
- Every value must be enclosed in square brackets: [value]
- Short Name format: [Short Name]:[food1, food2, food3]
- Calories format: [Calories]:[number]
- NO missing brackets anywhere

EXACT OUTPUT FORMAT:
[Target weight]:[value], [Total Calories]:[value], [Total Carbs]:[value], [Total Fat]:[value], [Total Fiber]:[value], [Total Protein]:[value], [day 1]:[Breakfast]:[detailed meal with specific quantities for each ingredient][Short Name]:[food names][Calories]:[number], [Snack 1]:[detailed snack with specific quantities][Short Name]:[food names][Calories]:[number], [Lunch]:[detailed meal with specific quantities for each ingredient][Short Name]:[food names][Calories]:[number], [Snack 2]:[detailed snack with specific quantities][Short Name]:[food names][Calories]:[number], [Dinner]:[detailed meal with specific quantities for each ingredient][Short Name]:[food names][Calories]:[number], [day 2]:[continue with detailed quantities for all 7 days]
- The same meal plan should be repeated for weight gain but with ONLY Snack 1 and NO Snack 2

QUANTITY EXAMPLES (COPY THIS LEVEL OF DETAIL):
- [Breakfast]:[200g Puttu with 2 medium bananas and 10g sugar][Short Name]:[Puttu, Banana, Sugar][Calories]:[350]
- [Lunch]:[150g Rice with 100ml Sambar and 80g Fish Fry][Short Name]:[Rice, Sambar, Fish Fry][Calories]:[520]  
- [Snack 1]:[30g Banana Chips][Short Name]:[Banana Chips][Calories]:[150]
- [Dinner]:[2 pieces Appam with 150ml Vegetable Stew][Short Name]:[Appam, Vegetable Stew][Calories]:[380]

MANDATORY RULES:
- [Short Name]:[food1, food2] - NOT [Short Name]:food1, food2
- [Calories]:[300] - NOT [Calories]:300
- Every single value must have brackets: [value]
- Weight loss: 3 meals + 2 snacks per day
- NEVER repeat foods across 7 days
- ALWAYS include specific quantities: grams, ml, pieces, cups for EVERY ingredient
- Think well when it comes to giving combinations of foods, don't just give random combinations, think about the food combinations and give the best ones for every meal!
- CALCULATE daily calories based on the user's gender, age, weight, height, activity level, and weight goal using the guidelines above
- ENSURE the total daily calories match the calculated target for their specific profile
- DISTRIBUTE calories appropriately across meals and snacks
- MOST IMPORTANT: Follow the calorie guidelines above for weight loss, maintenance, and weight gain, do not deviate from it, it'll lead to cardiac arrest of the individual
"""

    # Only add multi-regional foods section if we have valid regional data
    if regional_foods and states and len(states) > 0:
        regional_section = f"\n\nMULTI-REGIONAL FOODS TO USE (MANDATORY - Use ONLY these foods for main meals):\n"
        regional_section += f"REGIONS INCLUDED: {', '.join([state.upper() for state in states])}\n"
        regional_section += "="*80 + "\n"
        
        for meal_type, foods in regional_foods.items():
            if foods:  # Only add if foods exist for this meal type
                regional_section += f"\n{meal_type.upper()} OPTIONS ({len(foods)} items):\n"
                regional_section += "-" * 50 + "\n"
                for i, food in enumerate(foods, 1):
                    regional_section += f"{i:2d}. {food}\n"
        
        regional_section += "\n" + "="*80
        regional_section += f"\nIMPORTANT: Use ONLY the above multi-regional foods from {', '.join([state.upper() for state in states])} for Breakfast, Lunch, and Dinner. Mix and match different items across the 7 days to avoid repetition and never place a Non-Veg food in the Breakfast, if there is any push it to Snacks, Lunch or Dinner and be careful in giving the quantities of the foods and their combinations don't put random food combinations in the meal plan in a meal\n"
        
        base_prompt += regional_section
    else:
        # Add a note for general cuisine handling
        base_prompt += "\n\nNOTE: Generate meals based on the specified cuisine preferences in the input. Use appropriate foods from the requested cuisine type (Asian, Continental, etc.) without regional restrictions.\n"
    
    # Add 14 random snacks to the prompt
    random_snacks = random.sample(snacks["healthy_snacks"], 14)
    snacks_text = "\n\nAdd these relevant snacks to the meal plan:\n" + "\n".join(random_snacks)
    
    enhanced_prompt = base_prompt + snacks_text
    return enhanced_prompt

# System prompt for alternative endpoint (unchanged)
ALTERNATIVE_SYSTEM_PROMPT = """You are a food alternative assistant.
Given a food item, your task is to suggest a nutritionally similar alternative.
The response should be in the EXACT format: [alternative]:[alternative food name and quantity][Calories]:[calories in the alternative]
Example: [alternative]:[8 almonds (10g)][Calories]:[56]
Focus on providing a single, practical alternative with comparable caloric content. Do not provide any other text or explanation.
If the input consists of a key called previous alternative, then you have to give the alternative which is not the same as the previous alternative, but different.
MOST IMPORTANT: Follow the EXACT format AT ALL COSTS, never ever give me data in a different format, NEVER EVER forget the square brackets and the format I gave in the instructions, it'll lead to cardiac arrest of the individual
"""

class MealRequest(BaseModel):
    input_text: str

def parse_meal_plan_response(response: str) -> Dict:
    """Parse the full meal plan response into a structured dictionary."""
    result = {}
    
    print(f"\n🔍 PARSING: Starting to parse response...")
    print(f"📏 Response length: {len(response)} characters")
    
    # Extract target weight if present
    target_weight_match = re.search(r'\[Target weight\]:([^,]+)', response)
    if target_weight_match:
        target_weight = target_weight_match.group(1).strip()
        target_weight = re.sub(r'^\[|\]$', '', target_weight)
        result["target_weight"] = target_weight
        print(f"✅ Found target weight: {target_weight}")
    
    # Extract macros (including calories) with flexible patterns
    macro_patterns = {
        'Total Calories': r'\[Total Calories\]:\s*\[?(\d+)\]?\s*(?:kcal|calories)?',
        'Total Carbs':    r'\[Total Carbs\]:\s*\[?(\d+)g?\]?',
        'Total Protein':  r'\[Total Protein\]:\s*\[?(\d+)g?\]?',
        'Total Fat':      r'\[Total Fat\]:\s*\[?(\d+)g?\]?',
        'Total Fiber':    r'\[Total Fiber\]:\s*\[?(\d+)g?\]?'
    }
    
    result["macros"] = {}
    for macro, pattern in macro_patterns.items():
        match = re.search(pattern, response)
        if match:
            value = match.group(1).strip()
            if macro != 'Total Calories' and not value.endswith('g'):
                value += 'g'
            result["macros"][macro] = value
            print(f"✅ Found {macro}: {value}")
    
    # Extract daily meal plans
    days = []
    day_matches = list(re.finditer(r'\[day (\d+)\]:', response))
    print(f"🔍 Found {len(day_matches)} day markers")
    
    for i, day_match in enumerate(day_matches):
        day_num = int(day_match.group(1))
        start_pos = day_match.end()
        
        if i + 1 < len(day_matches):
            end_pos = day_matches[i + 1].start()
        else:
            end_pos = len(response)
        
        day_content = response[start_pos:end_pos].strip()
        print(f"📅 Processing Day {day_num}, content length: {len(day_content)}")
        
        day_dict = parse_single_day_improved(day_num, day_content)
        if day_dict["meals"]:
            days.append(day_dict)
            print(f"✅ Day {day_num}: Found {len(day_dict['meals'])} meals")
        else:
            print(f"❌ Day {day_num}: No meals found")
    
    if days:
        result["meal_plan"] = days
        print(f"✅ PARSING COMPLETE: {len(days)} days successfully parsed")
    else:
        print("❌ PARSING FAILED: No days found")
    
    return result

def parse_single_day_improved(day_num, day_content):
    """Improved parsing for a single day's meal plan content (supports 4 or 5 meals)"""
    day_dict = {
        "meals": {},
        "calories": {},
        "short_names": {},
        "day": day_num
    }
    
    # Updated regex pattern to:
    # 1. Strictly validate meal types (Breakfast/Snack 1/Lunch/Snack 2/Dinner)
    # 2. Handle both bracketed and unbracketed values
    # 3. Support optional Snack 2 (for weight gain/loss flexibility)
    meal_entry_pattern = re.compile(
        r"\[(?P<meal_type>Breakfast|Snack 1|Lunch|Snack 2|Dinner)\]:\[(?P<meal_content>[^]]+?)\]"
        r"(?:"
            r"\s*\[Short Name\]:"
            r"(?:"
                r"\[(?P<sn_bracketed>[^]]*?)\]"  # Bracketed short name
                r"|"
                r"(?P<sn_unbracketed>[^,\]]+)"    # Unbracketed short name
            r")"
        r")?"
        r"(?:"
            r"\s*\[Calories\]:"
            r"(?:"
                r"\[(?P<cal_bracketed>\d+)\]"     # Bracketed calories
                r"|"
                r"(?P<cal_unbracketed>\d+)"       # Unbracketed calories
            r")"
        r")?",
        re.IGNORECASE
    )
    
    matches = list(meal_entry_pattern.finditer(day_content))
    print(f"🔍 Day {day_num}: Found {len(matches)} meal entries")
    
    for entry in matches:
        match_dict = entry.groupdict()
        
        meal_type = match_dict['meal_type'].title()  # Normalize casing
        meal_content = match_dict['meal_content']
        
        # Store meal content (always required)
        day_dict["meals"][meal_type] = meal_content.strip()
        
        # Handle Short Name (optional)
        short_name_val = (
            match_dict['sn_bracketed'] 
            if match_dict['sn_bracketed'] is not None 
            else match_dict['sn_unbracketed']
        )
        if short_name_val:
            day_dict["short_names"][meal_type] = short_name_val.strip()
        
        # Handle Calories (optional)
        calories_str = (
            match_dict['cal_bracketed'] 
            if match_dict['cal_bracketed'] is not None 
            else match_dict['cal_unbracketed']
        )
        if calories_str:
            try:
                day_dict["calories"][meal_type] = int(calories_str)
            except ValueError:
                print(f"  ⚠️ Invalid calories value for {meal_type}: {calories_str}")
        
        # Log parsed entry
        calories_display = day_dict["calories"].get(meal_type, "N/A")
        print(f"  ✅ {meal_type}: {meal_content[:50]}... (Calories: {calories_display})")
    
    # Validate meal count (4 for gain, 5 for loss - but don't enforce here)
    return day_dict

def parse_emergency_response(response: str) -> Dict:
    """Parse the emergency food alternative response."""
    result = {}
    
    if isinstance(response, dict):
        return response
    
    alt_match = re.search(r'\[alternative\]:\[([^]]+)\]', response)
    cal_match = re.search(r'\[Calories\]:\[([^]]+)\]', response, re.IGNORECASE)
    
    if alt_match and cal_match:
        result["alternative"] = alt_match.group(1).strip()
        result["calories"] = cal_match.group(1).strip()
    else:
        return {"error": "Could not parse emergency response"}
    
    return result

def parse_meal_modification_response(response: str, input_text: str) -> Dict:
    """Parse the meal modification response."""
    result = {"modified_meal_plan": {}}

    meal_matches = re.findall(r'\[([^]]+)\]:\[([^]]+)\](?:\[Short Name\]:\[([^]]+)\])?(?:\[(\d+)\])?', response)

    for meal_info in meal_matches:
        if len(meal_info) >= 2:
            meal_type, meal_content = meal_info[0], meal_info[1]
            
            result["modified_meal_plan"][meal_type] = meal_content.strip()
            
            if len(meal_info) > 2 and meal_info[2]:
                if "short_names" not in result["modified_meal_plan"]:
                    result["modified_meal_plan"]["short_names"] = {}
                result["modified_meal_plan"]["short_names"][meal_type] = meal_info[2].strip()
            
            if len(meal_info) > 3 and meal_info[3]:
                if "calories" not in result["modified_meal_plan"]:
                    result["modified_meal_plan"]["calories"] = {}
                result["modified_meal_plan"]["calories"][meal_type] = meal_info[3]

    return result if result["modified_meal_plan"] else {"error": "No modifications found"}

def determine_input_type(input_text: str) -> str:
    if "emergency:" in input_text.lower():
        return "emergency"
    elif all(keyword in input_text for keyword in ["Total Carbs", "Total Protein", "Total Fat", "Total Fiber", "Breakfast"]):
        return "modification"
    else:
        return "meal_plan"

def validate_meal_plan_response(result: dict, input_text: str) -> bool:
    """
    Validate if the meal plan response has all necessary values and correct structure
    """
    print("\n🔍 VALIDATING MEAL PLAN RESPONSE...")
    
    # Check if result has basic structure
    if not result:
        print("❌ Validation failed: Empty result")
        return False
    
    # Check for target weight
    if 'target_weight' not in result or not result['target_weight']:
        print("❌ Validation failed: Missing target weight")
        return False
    
    # Check for macros
    if 'macros' not in result or not result['macros']:
        print("❌ Validation failed: Missing macros")
        return False
    
    required_macros = ['Total Calories', 'Total Carbs', 'Total Protein', 'Total Fat', 'Total Fiber']
    for macro in required_macros:
        if macro not in result['macros'] or not result['macros'][macro]:
            print(f"❌ Validation failed: Missing {macro}")
            return False
    
    # Check for meal plan
    if 'meal_plan' not in result or not result['meal_plan']:
        print("❌ Validation failed: Missing meal plan")
        return False
    
    # Check if we have 7 days
    if len(result['meal_plan']) != 7:
        print(f"❌ Validation failed: Expected 7 days, got {len(result['meal_plan'])}")
        return False
    
    # Check each day has required meals
    for day in result['meal_plan']:
        if 'meals' not in day or not day['meals']:
            print(f"❌ Validation failed: Day {day.get('day', 'unknown')} missing meals")
            return False
        
        # Check for required meal types
        required_meals = ['Breakfast', 'Lunch', 'Dinner']
        for meal in required_meals:
            if meal not in day['meals'] or not day['meals'][meal]:
                print(f"❌ Validation failed: Day {day.get('day', 'unknown')} missing {meal}")
                return False
    
    # Check for Snack2 in weight gain scenarios
    if "weight gain" in input_text.lower():
        for day in result['meal_plan']:
            if 'Snack 2' in day.get('meals', {}):
                print(f"❌ Validation failed: Snack 2 found in weight gain plan (Day {day.get('day', 'unknown')})")
                return False
    
    print("✅ Validation passed: All required fields present and correct structure")
    return True

def remove_snack2_from_weight_gain(result: dict) -> dict:
    """
    Remove Snack 2 from weight gain meal plans
    """
    if 'meal_plan' in result and result['meal_plan']:
        for day in result['meal_plan']:
            if 'meals' in day and 'Snack 2' in day['meals']:
                del day['meals']['Snack 2']
                print(f"🗑️ Removed Snack 2 from Day {day.get('day', 'unknown')}")
            if 'calories' in day and 'Snack 2' in day['calories']:
                del day['calories']['Snack 2']
            if 'short_names' in day and 'Snack 2' in day['short_names']:
                del day['short_names']['Snack 2']
    return result

@app.post("/mealplan")
async def get_meal_plan(request: MealRequest):
    try:
        print("\n" + "="*100)
        print("🚀 ENHANCED MULTI-REGIONAL MEALPLAN REQUEST - DIRECT PROCESSING")
        print("="*100)
        print("📥 INPUT TEXT:")
        print("-" * 50)
        print(request.input_text)
        print("-" * 50)
        
        # Step 1: Detect multiple regional preferences directly
        states, include_non_veg, is_regional = detect_regional_preferences(request.input_text)
        
        regional_foods = None
        if is_regional and states:
            print(f"\n🎯 MULTI-REGIONAL PREFERENCE DETECTED: {[state.upper() for state in states]}")
            print(f"🥗 Non-Veg Included: {include_non_veg}")
            
            # Step 2: Generate multi-regional foods directly (no tool calls)
            regional_foods = generate_multi_regional_foods_direct(states, include_non_veg)
            
            if not regional_foods:
                print(f"❌ Failed to generate regional foods for {states}")
        else:
            print("\n🌍 NO REGIONAL PREFERENCE DETECTED - Using general meal planning")
        
        # Step 3: Create enhanced prompt with pre-loaded multi-regional foods
        enhanced_prompt = create_enhanced_prompt(request.input_text, regional_foods, states)
        
        print(f"\n🔤 PROMPT LENGTH: {len(enhanced_prompt)} characters")
        print("🤖 CALLING GROQ API DIRECTLY...")
        print("\n📤 FINAL PROMPT BEING SENT TO GROQ:")
        print("=" * 80)
        print(enhanced_prompt)  # This contains the full prompt with regional foods
        print("=" * 80)
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": enhanced_prompt
                    },
                    {
                        "role": "user", 
                        "content": f"Generate a complete 7-day meal plan based on: {request.input_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            ai_response = response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Groq API Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
        
        print(f"\n📤 AI RESPONSE LENGTH: {len(ai_response)} characters")
        print("📤 ENTIRE AI RESPONSE:")
        print("=" * 80)
        print(ai_response)
        print("=" * 80)
        
        # Step 5: Parse and validate response with retry logic
        input_type = determine_input_type(request.input_text)
        print(f"\n🔍 DETECTED INPUT TYPE: {input_type}")
        
        max_retries = 3
        retry_count = 0
        result = None
        
        while retry_count < max_retries:
            try:
                if input_type == "emergency":
                    result = parse_emergency_response(ai_response)
                elif input_type == "modification":
                    result = parse_meal_modification_response(ai_response, request.input_text)
                else:
                    result = parse_meal_plan_response(ai_response)
                
                # Validate the response
                if input_type == "meal_plan":
                    if validate_meal_plan_response(result, request.input_text):
                        # Remove Snack2 from weight gain plans
                        if "weight gain" in request.input_text.lower():
                            result = remove_snack2_from_weight_gain(result)
                        break
                    else:
                        print(f"\n🔄 RETRY {retry_count + 1}/{max_retries}: Invalid response, retrying...")
                        retry_count += 1
                        
                        if retry_count < max_retries:
                            # Regenerate the response
                            response = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": enhanced_prompt
                                    },
                                    {
                                        "role": "user", 
                                        "content": f"Generate a complete 7-day meal plan based on: {request.input_text}"
                                    }
                                ],
                                temperature=0.3,
                                max_tokens=4000
                            )
                            ai_response = response.choices[0].message.content
                            print(f"\n📤 RETRY {retry_count} AI RESPONSE:")
                            print("=" * 80)
                            print(ai_response)
                            print("=" * 80)
                else:
                    # For emergency and modification, no validation needed
                    break
                    
            except Exception as e:
                print(f"\n❌ ERROR during parsing/validation: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"🔄 RETRY {retry_count}/{max_retries}...")
                else:
                    raise HTTPException(status_code=500, detail=f"Failed to generate valid response after {max_retries} attempts")
        
        if retry_count >= max_retries and input_type == "meal_plan":
            raise HTTPException(status_code=500, detail=f"Failed to generate valid meal plan after {max_retries} attempts")
        
        # Step 6: Log parsed results and JSON response
        print("\n📋 PARSED RESULT SUMMARY:")
        print("="*80)
        print(f"Target Weight: {result.get('target_weight', 'Not found')}")
        print(f"Macros: {result.get('macros', 'Not found')}")
        if 'meal_plan' in result and result['meal_plan']:
            print(f"Days in meal plan: {len(result['meal_plan'])}")
            for day in result['meal_plan']:
                print(f"  Day {day['day']}: {len(day['meals'])} meals")
        else:
            print("❌ WARNING: No meal plan found in parsed result!")
        print("="*80)
        
        # Log the JSON response
        print("\n📄 JSON RESPONSE:")
        print("="*80)
        print(json.dumps(result, indent=2))
        print("="*80)
        
        return JSONResponse(content=result)

    except Exception as e:
        print(f"❌ ERROR processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/alternative")
async def get_alternative(request: MealRequest):
    try:
        print("🔄 Alternative request:", request.input_text)
        
        # Combine system prompt with user input for Groq API
        combined_input = f"{ALTERNATIVE_SYSTEM_PROMPT}\n\nUser request: {request.input_text}"
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": ALTERNATIVE_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": request.input_text
                }
            ],
            temperature=1,
            max_tokens=500
        )
        
        # Extract response content from Groq API
        alternative_response_content = response.choices[0].message.content
        print("Raw alternative response:", alternative_response_content)
        
        result = parse_emergency_response(alternative_response_content)
        print("Parsed alternative result:", result)
        
        return JSONResponse(content=result)

    except Exception as e:
        print(f"❌ Error processing /alternative request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
