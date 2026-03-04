from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver


# ===============================
# CATEGORY
# ===============================
class Category(models.Model):
    name = models.CharField(max_length=100)

    # Static image filename (example: pizza.png)
    image = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    def __str__(self):
        return self.name


# ===============================
# PRODUCT
# ===============================
class Product(models.Model):
    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    # Static image filename only (example: burger.webp)
    image = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    discount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    is_veg = models.BooleanField(
        default=True
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def final_price(self):
        return self.price - self.discount

    def __str__(self):
        return self.name


# ===============================
# CART
# ===============================
class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(
        default=1
    )

    def total_price(self):
        return self.product.final_price() * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ===============================
# ORDER
# ===============================
class Order(models.Model):
    STATUS_CHOICES = (
        ("Preparing", "Preparing"),
        ("Out for delivery", "Out for delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total = models.FloatField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Preparing"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


# ===============================
# ORDER ITEMS
# ===============================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.product.name


# ===============================
# TRANSACTION ID GENERATOR
# ===============================
def generate_transaction_id():
    return str(uuid.uuid4())[:12]


# ===============================
# PAYMENT
# ===============================
class Payment(models.Model):
    PAYMENT_METHODS = (
        ("UPI", "UPI"),
        ("CARD", "Card"),
        ("NETBANKING", "Net Banking"),
        ("COD", "Cash on Delivery"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        default=generate_transaction_id
    )

    amount = models.FloatField()

    status = models.CharField(
        max_length=20,
        default="Success"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.method} - {self.transaction_id}"


# ===============================
# USER PROFILE
# ===============================
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    # Static image filename only
    image = models.CharField(
        max_length=200,
        default="default-user.png"
    )

    def __str__(self):
        return self.user.username


# ===============================
# AUTO CREATE PROFILE
# ===============================
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email