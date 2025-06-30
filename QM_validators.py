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
        print("Phone Number PhoneValidator: ", valid_number)
        if not valid_number:
            raise PhoneNumberError("Invalid Eswatini phone number.")
        return valid_number
    
def phone_number_validator(phone_number):
    # Split on /, \, ;, or , to handle multiple numbers
    possible_numbers = re.split(r"[\/\\,;]+", phone_number)
    for num in possible_numbers:
        # Remove all spaces from each number
        cleaned = re.sub(r"\s+", "", num)
        # Remove any non-digit except leading '+'
        cleaned = re.sub(r"(?!^\+)\D", "", cleaned)
        # Remove leading zeros
        cleaned = re.sub(r"^0+", "", cleaned)
        # Normalize to +268 format
        if cleaned.startswith("+268"):
            num_core = cleaned[4:]
        elif cleaned.startswith("268"):
            num_core = cleaned[3:]
        else:
            num_core = cleaned
        # Check for valid Eswatini mobile prefixes
        if (num_core.startswith("76") or num_core.startswith("79") or num_core.startswith("78")) and len(num_core) == 8:
            valid_number = "+268" + num_core
            print("Eswatini number found: ", valid_number)
            return valid_number
    print("No valid Eswatini number found.")
    return None