"""
Main food data module.
Imports all food datasets from the food_data package.
"""

# Import everything from the food_data package
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

# Re-export for backward compatibility
__all__ = [
    'kerala_food',
    'tamil_nadu_food',
    'delhi_food',
    'haryana_food',
    'himachal_pradesh_food',
    'jammu_kashmir_food',
    'jharkhand_food',
    'uttarakhand_food',
    'punjab_food',
    'rajasthan_food',
    'uttar_pradesh_food',
    'bihar_food',
    'karnataka_food',
    'andhra_pradesh_food',
    'telangana_food',
    'western_food',
    'snacks',
    'STATE_FOOD_MAPPING',
]
