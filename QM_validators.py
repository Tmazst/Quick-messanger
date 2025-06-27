import re
# This function validates and normalizes Eswatini phone numbers.
class PhoneNumberError(Exception):
    """Custom exception for phone number validation errors."""
    pass

class PhoneValidator:
    """Validator for Eswatini phone numbers."""
    
    def __init__(self, phone_number):
        self.phone_number = phone_number
    
    def validate(self):
        """Validate and normalize the phone number."""
        valid_number = phone_number_validator(self.phone_number)
        if not valid_number:
            raise PhoneNumberError("Invalid Eswatini phone number.")
        return valid_number
    
def phone_number_validator(phone_number):
    # Split on /, \, ;, ,, or whitespace
    numbers = re.split(r"[\/\\,; ]+", phone_number)
    valid_number = None
    for num in numbers:
        num = num.strip()
        # Remove any non-digit except leading '+'
        num = re.sub(r"(?!^\+)\D", "", num)
        # Remove leading zeros
        num = re.sub(r"^0+", "", num)
        # Normalize to +268 format
        if num.startswith("+268"):
            num_core = num[4:]
        elif num.startswith("268"):
            num_core = num[3:]
        else:
            num_core = num
        # Check for valid Eswatini mobile prefixes
        if num_core.startswith("76") or num_core.startswith("79"):
            # Must be 8 digits after country code
            if len(num_core) == 8:
                valid_number = "+268" + num_core
                break
    if valid_number:
        phone = valid_number
        return phone
    else:
        print("No valid Eswatini number found.")
        return None