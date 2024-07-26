from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class PocketMoney(models.Model):
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSACTION_TYPES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
    ]

    child = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pocket_money')
    group = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.child.username} - {self.get_transaction_type_display()} of {self.amount} on {self.date}"
