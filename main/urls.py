from django.urls import include, path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("add/<int:id>/", views.add_to_cart, name="add"),

    path("cart/", views.cart, name="cart"),

    path("increase/<int:id>/", views.increase_qty, name="increase"),
    path("decrease/<int:id>/", views.decrease_qty, name="decrease"),

    path("checkout/", views.checkout, name="checkout"),

    path("payment/", views.payment, name="payment"),

    path("place-order/", views.place_order, name="place_order"),  # ⭐ FIX

    path("orders/", views.orders, name="orders"),

    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),
    path('accounts/', include('allauth.urls')),
    path("process-payment/", views.process_payment, name="process_payment"),
    path("profile/", views.profile, name="profile"),
    path("remove/<int:id>/",views.remove_cart,name="remove_cart"),
    path("subscribe/", views.subscribe, name="subscribe"),

]