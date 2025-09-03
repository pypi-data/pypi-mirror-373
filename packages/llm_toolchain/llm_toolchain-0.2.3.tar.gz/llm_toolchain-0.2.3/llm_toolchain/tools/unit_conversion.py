from ..core import tool

# Conversion factors relative to a base unit (e.g., meters for length)
CONVERSION_FACTORS = {
    "length": {
        "meters": 1.0, "kilometers": 1000.0, "miles": 1609.34, "feet": 0.3048, "inches": 0.0254
    },
    "mass": {
        "kilograms": 1.0, "grams": 0.001, "pounds": 0.453592, "ounces": 0.0283495
    },
    "temperature": { # Temperature is a special case, handled by functions
        "celsius": lambda c: c,
        "fahrenheit": lambda f: (f - 32) * 5/9,
        "kelvin": lambda k: k - 273.15
    }
}

@tool
def convert_units(value: float, from_unit: str, to_unit: str):
    """
    Converts a value from one unit of measurement to another.
    Supports length, mass, and temperature.

    Args:
        value: The numerical value to convert.
        from_unit: The starting unit (e.g., 'miles', 'pounds', 'fahrenheit').
        to_unit: The target unit (e.g., 'kilometers', 'kilograms', 'celsius').
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    found_category = None
    for category, units in CONVERSION_FACTORS.items():
        if from_unit in units and to_unit in units:
            found_category = category
            break

    if not found_category:
        return {"error": f"Cannot convert between '{from_unit}' and '{to_unit}'. Units must be in the same category (length, mass, or temperature)."}

    # Handle temperature separately due to its non-linear conversion
    if found_category == "temperature":
        to_celsius_func = CONVERSION_FACTORS["temperature"][from_unit]
        value_in_celsius = to_celsius_func(value)
        
        # Invert the conversion for the target unit
        if to_unit == "celsius":
            result = value_in_celsius
        elif to_unit == "fahrenheit":
            result = (value_in_celsius * 9/5) + 32
        elif to_unit == "kelvin":
            result = value_in_celsius + 273.15
        else: # Should be unreachable
            return {"error": "Unknown temperature conversion."}
            
        return {"original_value": value, "from_unit": from_unit, "result": round(result, 2), "to_unit": to_unit}

    # Handle linear conversions for length and mass
    else:
        base_value = value * CONVERSION_FACTORS[found_category][from_unit]
        result = base_value / CONVERSION_FACTORS[found_category][to_unit]
        return {"original_value": value, "from_unit": from_unit, "result": round(result, 4), "to_unit": to_unit}
