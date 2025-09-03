import time
import random
import string
from datetime import datetime


def get_csv_separator(csv_file_path):
    with open(csv_file_path, 'r') as file:
        first_line = file.readline().strip()  # Read the first line
    # Define a list of common separators to check
    common_separators = [',', ';', '\t', '|']
    # Find the separator used in the first line
    for separator in common_separators:
        if separator in first_line:
            return separator
    # If none of the common separators are found, return None
    return None

def generate_unique_id():
     timestamp = int(time.time() * 1000)  # Equivalent to Date.now()
     random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))  # Equivalent to Math.random().toString(36).substring(2)
     return f"{timestamp:x}{random_part}"
 
def generate_timestamp():
    iso_timestamp = datetime.utcnow().isoformat() + "Z"
    return iso_timestamp
