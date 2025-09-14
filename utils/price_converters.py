#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def convert_persian_to_english_digits(persian_text):
    """
    Convert Persian digits to English digits
    
    Args:
        persian_text (str): Text containing Persian digits
        
    Returns:
        str: Text with English digits
    """
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    
    english_text = persian_text
    for persian, english in persian_to_english.items():
        english_text = english_text.replace(persian, english)
    
    return english_text


def convert_milligram_price_to_gram_price(milligram_price):
    """
    Convert milligram price to gram price by adding ",000"
    
    Args:
        milligram_price (str): Price in milligrams (e.g., "12,345")
        
    Returns:
        str: Price in grams (e.g., "12,345,000")
    """
    return milligram_price + ",000"

def remove_comma(price):
    """
    Remove comma from price
    
    Args:
        price (str): Price with comma
        
    Returns:
        str: Price without comma
    """
    return price.replace(',', '')

def toman_to_rial(toman_price):
    """
    Convert toman price to rial price
    
    Args:
        toman_price (str): Price in toman
        
    Returns:
        str: Price in rial
    """
    return toman_price + "0"

def add_comma(price):
    """
    Add comma to price
    
    Args:
        price (str): Price without comma
        
    Returns:
        str: Price with comma
    """
    return price.replace(',', '')


def format_number_with_commas(number_str):
    """
    Format a number string with commas every 3 digits from the right
    
    Args:
        number_str (str): Number as string (e.g., "12123123123")
        
    Returns:
        str: Formatted number with commas (e.g., "12,123,123,123")
    """
    # Remove any existing commas first
    clean_number = number_str.replace(',', '')
    
    # Add commas every 3 digits from the right
    if len(clean_number) <= 3:
        return clean_number
    
    # Reverse the string, add commas every 3 characters, then reverse back
    reversed_number = clean_number[::-1]
    formatted_reversed = ','.join(reversed_number[i:i+3] for i in range(0, len(reversed_number), 3))
    return formatted_reversed[::-1]