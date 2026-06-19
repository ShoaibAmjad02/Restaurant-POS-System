from django.urls import path
from .views import (
    food_delivery_restaurant_detail,
    logout_view,
    add_product,
    product_list,
    edit_product,
    delete_product,
    admin_dashboard,
    food_delivery_login,
    register_view,
    search_users,
    user_detail_view,
    user_redirect_view,
    user_update_view,
)
from megaone.users import views

app_name = "users"

urlpatterns = [
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path(
    "checkout/",
    views.checkout_invoice,
    name="checkout_invoice"
),
# Inventory

path(
    "inventory/request/",
    views.request_inventory,
    name="request_inventory"
),

path(
    "inventory/requests/",
    views.inventory_requests,
    name="inventory_requests"
),

path(
    "inventory/issue/",
    views.give_inventory,
    name="inventory_issue"
),
path("kitchen/dashboard/", views.kitchen_dashboard, name="kitchen_dashboard"),

path(
    "request-inventory/",
    views.request_inventory,
    name="request_inventory"
),

path(
    "inventory/request/",
    views.inventory_requests,
    name="inventory_request"
),
path(
    "inventory/issues/",
    views.inventory_issues,
    name="inventory_issues"
),
    path("operator/dashboard/", views.operator_dashboard, name="operator_dashboard"),
    path("operator/search-invoice/", views.operator_search_invoice, name="operator_search_invoice"),
    path(
    "operator/search-products/",
    views.operator_product_search,
    name="operator_product_search"
),
   path(
        "operator/create-invoice/",
        views.operator_create_invoice,
        name="operator_create_invoice"
    ),
path(
    "mysql-backup/",
    views.mysql_backup,
    name="mysql_backup"
),
path(
    "my-orders/",
    views.my_orders,
    name="my_orders"
),
    path("kitchen/dashboard/", views.kitchen_dashboard, name="kitchen_dashboard"),
    path(
    "kitchen/order/<int:order_id>/status/",
    views.update_order_status,
    name="update_order_status",
),
path(
    "search-order/",
    views.search_order,
    name="search_order"
),
path(
    "orders-by-status/",
    views.orders_by_status,
    name="orders_by_status"
),
path(
    "orders-by-date/",
    views.orders_by_date,
    name="orders_by_date"
),
    path("create-operator/", views.create_operator, name="create_operator"),
    path("operators/", views.list_operators, name="list_operators"),
    path("edit-operator/<int:pk>/", views.edit_operator, name="edit_operator"),
    path("delete-operator/<int:pk>/", views.delete_operator, name="delete_operator"),
    path("create-kitchen/", views.create_kitchen, name="create_kitchen"),
    path("kitchen/", views.kitchen_list, name="kitchen_list"),
    path('edit-kitchen/<int:id>/', views.edit_kitchen, name='edit_kitchen'),
    path('delete-kitchen/<int:id>/', views.delete_kitchen, name='delete_kitchen'),

    # ✅ ADD THIS
    path('search-invoice/', views.search_invoice, name='search_invoice'),
    path(
    "invoice/<int:invoice_id>/",
    views.invoice_pdf,
    name="invoice_pdf"
),
path("search-users/", search_users, name="search_users"),
path(
    "invoice/<int:invoice_id>/",
    views.invoice_pdf,
    name="invoice_pdf"
),
    path("dashboard/", admin_dashboard, name="admin_dashboard"),
    path(
        "restaurant-detail/",
        food_delivery_restaurant_detail,
        name="food_delivery_restaurant_detail"
    ),
    path(
    "revenue-filter/",
    views.revenue_filter,
    name="revenue_filter"
),
    # ✅ ONLY ONE product list
    path("products/", product_list, name="product_list"),

    path("products/add/", add_product, name="add_product"),
    path("products/<int:pk>/edit/", edit_product, name="edit_product"),
    path("products/<int:pk>/delete/", delete_product, name="delete_product"),
    path("login/", food_delivery_login, name="login"),

    path("<int:pk>/", user_detail_view, name="detail"),
    path("~redirect/", user_redirect_view, name="redirect"),
    path("update/", user_update_view, name="update"),
]