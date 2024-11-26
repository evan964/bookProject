import re

def extract_text(element, strip: bool = True) -> str:
    """Safely extract text from BS4 element"""
    if element:
        return element.get_text(strip=strip)
    return 'N/A'

def extract_number(text: str) -> int:
    """Extract number from string"""
    try:
        return int(re.sub(r'[^0-9]', '', text))
    except ValueError:
        return 0