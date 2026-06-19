from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager
from django.conf import settings
import uuid


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)
    is_kitchen = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Invoice(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    customer_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    customer_email = models.EmailField(
        blank=True,
        null=True
    )

    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        default=uuid.uuid4
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        related_name="items",
        on_delete=models.CASCADE
    )

    product_name = models.CharField(max_length=255)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField()

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product_name

class KitchenOrder(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("served", "Served"),
    )

    invoice = models.OneToOneField(
        Invoice,
        on_delete=models.CASCADE,
        related_name="kitchen_order"
    )

    order_number = models.CharField(
        max_length=30,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.order_number


class KitchenOrderItem(models.Model):

    order = models.ForeignKey(
        KitchenOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_name = models.CharField(max_length=255)

    quantity = models.IntegerField()


class InventoryRequest(models.Model):

    kitchen_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inventory_requests"
    )

    item_name = models.CharField(
        max_length=100
    )

    quantity = models.CharField(
        max_length=50
    )

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.item_name

class InventoryIssue(models.Model):

    kitchen_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_inventory"
    )


    item_name=models.CharField(
        max_length=100
    )


    quantity=models.CharField(
        max_length=50
    )


    description=models.TextField(
        blank=True
    )


    issued_by=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="issued_inventory"
    )


    created_at=models.DateTimeField(
        auto_now_add=True
    )

