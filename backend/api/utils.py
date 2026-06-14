from django.core.management.base import BaseCommand
from decimal import Decimal

def validate_amount(amount):
    """Validate transaction amount"""
    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > 1000000:  # Max transaction limit
            raise ValueError("Amount exceeds maximum limit of $1,000,000")
        return amount
    except:
        raise ValueError("Invalid amount format")

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"