from django.contrib import admin
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import Product, Category, Order, Cart, OrderItem


# =========================
# ORDER ITEMS INLINE
# =========================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


# =========================
# ORDER ADMIN + DASHBOARD
# =========================

class OrderAdmin(admin.ModelAdmin):

    change_list_template = "admin/dashboard.html"

    list_display = (
        "id",
        "user",
        "total",
        "status",
        "created_at",
    )

    list_editable = ("status",)

    inlines = [OrderItemInline]

    def changelist_view(self, request, extra_context=None):

        total_orders = Order.objects.count()
        total_users = User.objects.count()
        total_revenue = Order.objects.aggregate(
            Sum("total")
        )["total__sum"] or 0

        extra_context = extra_context or {}

        extra_context.update({
            "total_orders": total_orders,
            "total_users": total_users,
            "total_revenue": total_revenue,
        })

        return super().changelist_view(
            request,
            extra_context=extra_context
        )


admin.site.register(Order, OrderAdmin)


# =========================
# CATEGORY ADMIN
# =========================

class CategoryAdmin(admin.ModelAdmin):

    list_display = ("name",)
    list_display_links = ("name",)

    search_fields = ("name",)


admin.site.register(Category, CategoryAdmin)


# =========================
# PRODUCT ADMIN (FIXED)
# =========================

class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",          # clickable
        "category",
        "price",
        "discount",
        "is_veg",
        "is_available",
    )

    # ✅ NAME clickable instead of ID
    list_display_links = ("name",)

    list_filter = (
        "category",
        "is_veg",
        "is_available",
    )

    list_editable = (
        "price",
        "discount",
        "is_available",
    )

    search_fields = ("name",)

    ordering = ("-id",)


admin.site.register(Product, ProductAdmin)


# =========================
# CART ADMIN
# =========================

class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "quantity",
    )

    list_display_links = ("product",)


admin.site.register(Cart, CartAdmin)