from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Sum
from datetime import datetime

class User(AbstractUser):
    account_number = models.CharField(max_length=20, unique=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.account_number}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            super().save(*args, **kwargs)
            self.account_number = f"ACC{self.id:08d}"
        super().save(*args, **kwargs)

    def deposit(self, amount):
        """Deposit money to account"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += Decimal(str(amount))
        self.save()
        Transaction.objects.create(
            from_user=self,
            to_user=self,
            amount=amount,
            transaction_type='DEPOSIT',
            description=f"Deposit of ${amount}"
        )
        return self.balance

    def withdraw(self, amount):
        """Withdraw money from account"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= Decimal(str(amount))
        self.save()
        Transaction.objects.create(
            from_user=self,
            to_user=self,
            amount=amount,
            transaction_type='WITHDRAWAL',
            description=f"Withdrawal of ${amount}"
        )
        return self.balance

    def transfer(self, to_user, amount):
        """Transfer money to another user"""
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        
        # Deduct from sender
        self.balance -= Decimal(str(amount))
        self.save()
        
        # Add to receiver
        to_user.balance += Decimal(str(amount))
        to_user.save()
        
        # Create transaction record
        Transaction.objects.create(
            from_user=self,
            to_user=to_user,
            amount=amount,
            transaction_type='TRANSFER',
            description=f"Transfer to {to_user.username}"
        )
        
        return self.balance

    @classmethod
    def get_user_by_account(cls, account_number):
        """Get user by account number"""
        try:
            return cls.objects.get(account_number=account_number)
        except cls.DoesNotExist:
            return None


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']