# utils.py
import bleach
from flask import Markup


allowed_tags = ['div', 'span', 'p', 'b', 'i', 'u', 'strong', 'em']
allowed_attributes = {'*': ['style']}
allowed_css_properties = ['color', 'font-weight', 'font-style', 'text-decoration']

style_cleaner = bleach.sanitizer.Cleaner(
    tags=allowed_tags,
    attributes=allowed_attributes,
    css_sanitizer=bleach.sanitizer.CSSSanitizer(allowed_css_properties=allowed_css_properties)
)

def sanitize_style(value):
    return style_cleaner.clean(value)
