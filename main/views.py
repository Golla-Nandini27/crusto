import uuid   # ✅ IMPORTANT (fixes transaction_id error)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Cart, Order, Payment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Profile


# =========================
# HOME PAGE
# =========================
def home(request):

    category_id = request.GET.get("category")

    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = sum(
            i.quantity for i in Cart.objects.filter(user=request.user)
        )

    return render(request, "main/home.html", {
        "products": products,
        "categories": categories,
        "cart_count": cart_count
    })


# =========================
# REGISTER
# =========================
def register(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return render(request, "main/register.html", {
                "error": "Username already exists"
            })

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(request, "main/register.html")


# =========================
# LOGIN
# =========================
def login_user(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("home")

        return render(request, "main/login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "main/login.html")


# =========================
# LOGOUT
# =========================
def logout_user(request):

    logout(request)
    return redirect("home")


# =========================
# ADD TO CART (AJAX)
# =========================
@login_required
def add_to_cart(request, id):

    product = get_object_or_404(Product, id=id)

    if not product.is_available:
        return JsonResponse({
            "cart_count": 0,
            "error": "Out of stock"
        })

    cart, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 1}
    )

    if not created:
        cart.quantity += 1
        cart.save()

    cart_count = sum(
        i.quantity for i in Cart.objects.filter(user=request.user)
    )

    return JsonResponse({
        "cart_count": cart_count
    })


# =========================
# CART PAGE
# =========================
@login_required
def cart(request):

    items = Cart.objects.filter(user=request.user)

    total = sum(
        i.total_price()
        for i in items
        if i.product.is_available
    )

    return render(request, "main/cart.html", {
        "items": items,
        "total": total
    })


# =========================
# INCREASE QTY
# =========================
@login_required
def increase_qty(request, id):

    try:
        item = Cart.objects.get(
            id=id,
            user=request.user
        )

        if item.product.is_available:
            item.quantity += 1
            item.save()

    except Cart.DoesNotExist:
        pass

    return redirect("cart")


# =========================
# DECREASE QTY
# =========================
@login_required
def decrease_qty(request, id):

    try:
        item = Cart.objects.get(
            id=id,
            user=request.user
        )

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    except Cart.DoesNotExist:
        pass

    return redirect("cart")


# =========================
# CHECKOUT
# =========================
@login_required
def checkout(request):
    return redirect("payment")


# =========================
# PAYMENT PAGE
# =========================
@login_required
def payment(request):

    items = Cart.objects.filter(user=request.user)

    total = sum(i.total_price() for i in items)

    return render(request, "main/payment.html", {
        "total": total
    })


# =========================
# PLACE ORDER (MAIN FIX)
# =========================
@login_required
def place_order(request):

    if request.method == "POST":

        method = request.POST.get("method")

        items = Cart.objects.filter(user=request.user)

        total = sum(i.total_price() for i in items)

        if total == 0:
            return redirect("home")

        # create order
        order = Order.objects.create(
            user=request.user,
            total=total,
            status="Paid"
        )

        # create payment
        Payment.objects.create(
            user=request.user,
            order=order,
            method=method,
            amount=total,
            transaction_id=str(uuid.uuid4())[:12]
        )

        # clear cart
        items.delete()

        return render(request, "main/success.html", {
            "order": order
        })

    return redirect("payment")


# =========================
# AJAX PAYMENT (optional)
# =========================
@login_required
@require_POST
def process_payment(request):

    items = Cart.objects.filter(user=request.user)

    total = sum(i.total_price() for i in items)

    if total == 0:
        return JsonResponse({"success": False})

    order = Order.objects.create(
        user=request.user,
        total=total,
        status="Paid"
    )

    items.delete()

    return JsonResponse({"success": True})


# =========================
# ORDER HISTORY
# =========================
@login_required
def orders(request):

    user_orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "main/orders.html", {
        "orders": user_orders
    })


# =========================
# ADMIN DASHBOARD
# =========================
@staff_member_required
def dashboard(request):

    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_products = Product.objects.count()

    total_revenue = sum(
        o.total for o in Order.objects.all()
    )

    return render(request, "main/dashboard.html", {
        "orders": total_orders,
        "users": total_users,
        "products": total_products,
        "revenue": total_revenue
    })




@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")

        request.user.username = username
        request.user.email = email
        request.user.save()

        # upload image
        if request.FILES.get("image"):
            profile.image = request.FILES.get("image")
            profile.save()

        # delete image
        if request.POST.get("delete_image"):
            profile.image = "profiles/default.png"
            profile.save()

    return render(request,"main/profile.html",{
        "profile": profile
    })

def remove_cart(request,id):
    Cart.objects.filter(id=id).delete()
    return redirect("cart")