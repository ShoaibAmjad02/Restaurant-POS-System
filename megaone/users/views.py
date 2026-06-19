from click import Group
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.views.generic import DetailView, UpdateView, RedirectView
from urllib3 import request

from megaone.conftest import user

from megaone.conftest import user

from .models import User


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    pk_url_kwarg = "pk"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Updated successfully")

    def get_success_url(self) -> str:
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User


def register_view(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("food-delivery:food_delivery_registration")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("food-delivery:food_delivery_registration")

        User.objects.create_user(
            email=email,
            password=password1,
            name=name
        )

        messages.success(request, "Registration successful.")
        return redirect("food-delivery:food_delivery_login")

    return redirect("food-delivery:food_delivery_registration")


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect


def food_delivery_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect("users:admin_dashboard")

            elif getattr(user, "is_operator", False):
                return redirect("users:operator_dashboard")

            elif getattr(user, "is_kitchen", False):
                return redirect("users:kitchen_dashboard")

            return redirect("/")

        else:
            messages.error(request, "Invalid credentials")
            return redirect("food-delivery:food_delivery_login")

    return render(request, "food-delivery/login.html")
from django.contrib.auth import logout
def logout_view(request):

    logout(request)

    return redirect("/")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='food-delivery:food_delivery_login')
def food_delivery_restaurant_detail(request):
    return render(
        request,
        'food-delivery/restaurant-detail.html'
    )

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from menu.models import Food
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()

from django.utils import timezone
from django.db.models import Sum

from .models import KitchenOrder

@staff_member_required
def admin_dashboard(request):

    foods_count = Food.objects.count()
    invoices_count = Invoice.objects.count()
    users_count = User.objects.count()

    # 👇 ORDER COUNTS
    pending_count = KitchenOrder.objects.filter(status="pending").count()
    preparing_count = KitchenOrder.objects.filter(status="preparing").count()

    # ✅ SERVED / COMPLETED (tumhare case me "served")
    completed_count = KitchenOrder.objects.filter(status__in=["served", "completed"]).count()

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    invoices = Invoice.objects.all()

    if start_date and end_date:
        invoices = invoices.filter(created_at__date__range=[start_date, end_date])

    revenue = invoices.aggregate(total=Sum("total_amount"))["total"] or 0

    return render(request, "admin/dashboard.html", {
        "foods_count": foods_count,
        "invoices_count": invoices_count,
        "users_count": users_count,
        "revenue": revenue,

        # ✅ ADD THESE
        "pending_count": pending_count,
        "preparing_count": preparing_count,
        "completed_count": completed_count,

        "start_date": start_date,
        "end_date": end_date,
    })

from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def revenue_filter(request):

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    invoices = Invoice.objects.all()

    if start_date and end_date:
        invoices = invoices.filter(
            created_at__date__range=[start_date, end_date]
        )

    revenue = invoices.aggregate(
    total=Sum("total_amount")
)["total"] or 0

    return JsonResponse({
        "revenue": float(revenue)
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from menu.models import Food

@staff_member_required
def product_list(request):

    products = Food.objects.all()

    return render(
        request,
        "admin/products.html",
        {
            "products": products
        }
    )

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages

from menu.models import Food, Category


@staff_member_required
def add_product(request):

    categories = Category.objects.all()

    if request.method == "POST":

        category_id = request.POST.get("category")
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        available = request.POST.get("available") == "on"

        category = Category.objects.get(id=category_id)

        Food.objects.create(
            category=category,
            name=name,
            description=description,
            price=price,
            image=image,
            available=available
        )

        messages.success(
            request,
            "Product added successfully."
        )

        return redirect("users:product_list")

    return render(
        request,
        "admin/add_product.html",
        {
            "categories": categories
        }
    )

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from menu.models import Food, Category

@staff_member_required
def edit_product(request, pk):

    product = get_object_or_404(Food, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":

        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")

        category_id = request.POST.get("category_id")
        product.category = get_object_or_404(Category, id=category_id)

        product.available = request.POST.get("available") == "on"

        # image optional update
        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        messages.success(request, "Product updated successfully")
        return redirect("users:product_list")

    return render(request, "admin/edit_product.html", {
    "product": product,
    "categories": categories
})

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from menu.models import Food

@staff_member_required
def delete_product(request, pk):

    product = get_object_or_404(Food, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully")
        return redirect("users:products")

    return redirect("users:products")


from menu.models import Food

def food_delivery_restaurant_detail(request):

    products = Food.objects.filter(available=1)

    print(products.count())  # Debug

    return render(
        request,
        "food-delivery/restaurant-detail.html",
        {
            "products": products
        }
    )


from .models import Invoice, InvoiceItem
import io
import json
import uuid

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

@login_required
@require_POST
def checkout_invoice(request):

    try:
        data = json.loads(request.body)
        cart = data.get("cart", [])

        if not cart:
            return JsonResponse(
                {"success": False, "message": "Cart is empty"},
                status=400
            )

        total_amount = 0

        invoice = Invoice.objects.create(
            user=request.user,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            total_amount=0
        )

        for item in cart:

            qty = int(item["qty"])
            price = float(item["price"])

            subtotal = qty * price
            total_amount += subtotal

            InvoiceItem.objects.create(
                invoice=invoice,
                product_name=item["name"],
                price=price,
                quantity=qty,
                subtotal=subtotal
            )

        invoice.total_amount = total_amount
        invoice.save()

        # Kitchen Order
        order = KitchenOrder.objects.create(
            invoice=invoice,
            order_number=""
        )

        order.order_number = f"ORD-{order.id}"
        order.save()

        for item in cart:

            KitchenOrderItem.objects.create(
                order=order,
                product_name=item["name"],
                quantity=int(item["qty"])
            )

        return JsonResponse({
            "success": True,
            "invoice_id": invoice.id
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)
    
@login_required
def invoice_pdf(request, invoice_id):

    invoice = Invoice.objects.filter(
        id=invoice_id
    ).first()
    
    if not invoice:
        return HttpResponse("Invoice not found")

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    pdf.setTitle(invoice.invoice_number)

    # Header
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, height - 50, "Restaurant Invoice")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        50,
        height - 90,
        f"Invoice No: {invoice.invoice_number}"
    )

    customer_name = invoice.customer_name or invoice.user.name
    customer_email = invoice.customer_email or invoice.user.email

    pdf.drawString(
        50,
        height - 110,
        f"Customer: {customer_name}"
    )

    pdf.drawString(
        50,
        height - 130,
        f"Email: {customer_email}"
    )

    pdf.drawString(
       50,
       height - 170,
       f"Order No: {invoice.kitchen_order.order_number}"
    )

    pdf.drawString(
        50,
        height - 150,
        f"Date: {invoice.created_at.strftime('%d-%m-%Y %H:%M')}"
    )

    y = height - 200

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawString(50, y, "Product")
    pdf.drawString(250, y, "Qty")
    pdf.drawString(330, y, "Price")
    pdf.drawString(430, y, "Subtotal")

    y -= 20

    pdf.line(50, y, 550, y)

    y -= 20

    pdf.setFont("Helvetica", 11)

    for item in invoice.items.all():

        pdf.drawString(50, y, item.product_name)

        pdf.drawString(
            250,
            y,
            str(item.quantity)
        )

        pdf.drawString(
            330,
            y,
            f"Rs {item.price}"
        )

        pdf.drawString(
            430,
            y,
            f"Rs {item.subtotal}"
        )

        y -= 25

        if y < 80:
            pdf.showPage()
            y = height - 80

    pdf.line(300, y, 550, y)

    y -= 30

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        330,
        y,
        f"Total: Rs {invoice.total_amount}"
    )

    pdf.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="{invoice.invoice_number}.pdf"'
    )

    return response


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
@csrf_exempt
def search_invoice(request):
    if request.method == "POST":
        data = json.loads(request.body)

        email = data.get("email")

        invoices = Invoice.objects.filter(
            user__email__icontains=email
        )

        return JsonResponse({
            "invoices": [
                {
                    "id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "email": invoice.user.email,
                    "total": float(invoice.total_amount),
                }
                for invoice in invoices
            ]
        })

    return JsonResponse({"invoices": []})

from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model

User = get_user_model()

@staff_member_required
def search_users(request):

    users = User.objects.all()

    return JsonResponse({
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name
            }
            for u in users
        ]
    })



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import make_password

from .models import User


# =========================
# CREATE OPERATOR
# =========================
@staff_member_required
@csrf_exempt
def create_operator(request):
    if request.method == "POST":

        data = json.loads(request.body)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if User.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists"}, status=400)

        user = User.objects.create_user(
            name=name,
            email=email,
            password=password
        )

        # ✅ mark operator
        user.is_operator = True
        user.is_staff = False
        user.is_superuser = False
        user.save()

        return JsonResponse({"message": "Operator created"})

    return JsonResponse({"message": "Invalid request"}, status=400)
# =========================
# LIST OPERATORS
# =========================
@staff_member_required
def list_operators(request):

    ops = User.objects.filter(is_operator=True)

    return JsonResponse({
        "operators": [
            {
                "id": o.id,
                "name": o.name,
                "email": o.email
            }
            for o in ops
        ]
    })
# =========================
# EDIT OPERATOR
# =========================
@staff_member_required
@csrf_exempt
def edit_operator(request, pk):

    if request.method == "POST":

        data = json.loads(request.body)

        try:
            op = User.objects.get(pk=pk, is_operator=True)
        except User.DoesNotExist:
            return JsonResponse({"message": "Operator not found"}, status=404)

        if data.get("name"):
            op.name = data.get("name")

        if data.get("email"):
            op.email = data.get("email")

        if data.get("password"):
            op.set_password(data.get("password"))

        op.save()

        return JsonResponse({"message": "Operator updated"})

    return JsonResponse({"message": "Invalid request"}, status=400)

# =========================
# DELETE OPERATOR
# =========================
@staff_member_required
@csrf_exempt
def delete_operator(request, pk):

    try:
        user = User.objects.get(pk=pk, is_operator=True)
        user.delete()
        return JsonResponse({"message": "Deleted"})
    except User.DoesNotExist:
        return JsonResponse({"message": "Not found"}, status=404)

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt

from .models import Invoice


# =========================
# CHECK OPERATOR
# =========================
def is_operator(user):
    return user.is_authenticated and user.is_operator


# =========================
# OPERATOR DASHBOARD
# =========================
@login_required
def operator_dashboard(request):

    if not request.user.is_operator:
        return JsonResponse({"message": "Access denied"}, status=403)

    return render(request, "operator/dashboard.html")
# =========================
# SEARCH INVOICES (Operator)
# =========================
from django.db.models import Q

@login_required
@csrf_exempt
def operator_search_invoice(request):

    if not is_operator(request.user):
        return JsonResponse({"message": "Access Denied"}, status=403)

    if request.method == "POST":

        data = json.loads(request.body)
        keyword = data.get("email", "")  # you can rename to "q"

        invoices = Invoice.objects.filter(
    Q(invoice_number__icontains=keyword) |
    Q(kitchen_order__order_number__icontains=keyword) |
    Q(user__email__icontains=keyword) |
    Q(user__name__icontains=keyword) |
    Q(customer_email__icontains=keyword) |
    Q(customer_name__icontains=keyword)
).distinct()[:20]
        return JsonResponse({
    "invoices": [
        {
            "id": i.id,
            "invoice_number": i.invoice_number,
            "email": i.user.email,
            "customer_name": i.customer_name,
            "customer_email": i.customer_email,
            "total": float(i.total_amount),

            "order_number": (
                i.kitchen_order.order_number
                if hasattr(i, "kitchen_order")
                else ""
            ),

            "status": (
                i.kitchen_order.status
                if hasattr(i, "kitchen_order")
                else ""
            ),
        }
        for i in invoices
    ]
})

    return JsonResponse({"invoices": []})

@login_required
def operator_product_search(request):

    keyword = request.GET.get("q")

    products = Product.objects.filter(
        name__icontains=keyword
    )[:20]

    return JsonResponse({
        "products":[
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price)
            }
            for p in products
        ]
    })


from .models import KitchenOrder, KitchenOrderItem
@login_required
@csrf_exempt
def operator_create_invoice(request):

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST required"}, status=400)

    if not request.user.is_operator:
        return JsonResponse({"success": False, "message": "Access denied"}, status=403)

    try:
        data = json.loads(request.body or "{}")

        cart = data.get("cart", [])
        if not cart:
            return JsonResponse({"success": False, "message": "Cart is empty"}, status=400)

        customer_name = (data.get("customer_name") or "").strip()
        customer_email = (data.get("customer_email") or "").strip()

        # ✅ WALK-IN LOGIC
        if not customer_name:
            customer_name = "Walk-in Customer"

        if not customer_email:
            customer_email = "........"

        invoice = Invoice.objects.create(
            user=request.user,
            customer_name=customer_name,
            customer_email=customer_email,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            total_amount=0
        )
        order = KitchenOrder.objects.create(
           invoice=invoice,
           order_number=""
        )

        order.order_number = f"ORD-{order.id}"
        order.save()

        total = 0

        for item in cart:
            qty = int(item.get("qty", 0))
            price = float(item.get("price", 0))

            subtotal = qty * price
            total += subtotal

            InvoiceItem.objects.create(
                invoice=invoice,
                product_name=item.get("name", ""),
                price=price,
                quantity=qty,
                subtotal=subtotal
            )

            
            KitchenOrderItem.objects.create(
             order=order,
             product_name=item["name"],
             quantity=qty
           )

        invoice.total_amount = total
        invoice.save()

        return JsonResponse({
            "success": True,
            "invoice_id": invoice.id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)
  
@login_required
def operator_product_search(request):

    keyword = request.GET.get("q")

    products = Food.objects.filter(
        name__icontains=keyword
    )[:20]

    return JsonResponse({
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price)
            }
            for p in products
        ]
    })



# =========================
# Kitchen DASHBOARD
# =========================
from .models import KitchenOrder
from .models import InventoryRequest, InventoryIssue

@login_required
def kitchen_dashboard(request):

    if not request.user.is_kitchen:
        return JsonResponse(
            {"message":"Access denied"},
            status=403
        )


    orders = KitchenOrder.objects.exclude(
        status="served"
    ).order_by("-created_at")


    latest_order_id = orders.first().id if orders.exists() else 0


    inventory_requests = InventoryRequest.objects.filter(
        kitchen_user=request.user
    ).order_by("-created_at")


    inventory_issues = InventoryIssue.objects.filter(
        kitchen_user=request.user
    ).order_by("-created_at")


    return render(
        request,
        "kitchen/dashboard.html",
        {
            "orders": orders,
            "latest_order_id": latest_order_id,
            "inventory_requests": inventory_requests,
            "inventory_issues": inventory_issues,
        }
    )

@login_required
def update_order_status(request, order_id):

    if not request.user.is_kitchen:
        return redirect("users:kitchen_dashboard")

    order = KitchenOrder.objects.get(id=order_id)

    order.status = request.POST.get("status")
    order.save()

    return redirect("users:kitchen_dashboard")

@staff_member_required
@csrf_exempt
def create_kitchen(request):
    if request.method == "POST":

        data = json.loads(request.body)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if User.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists"}, status=400)

        user = User.objects.create_user(
            name=name,
            email=email,
            password=password
        )

        # ✅ mark kitchen
        user.is_kitchen = True
        user.is_staff = False
        user.is_superuser = False
        user.save()

        return JsonResponse({"message": "Kitchen user created"})

    return JsonResponse({"message": "Invalid request"}, status=400)


@staff_member_required
def kitchen_list(request):

    kitchens = User.objects.filter(is_kitchen=True)

    return JsonResponse({
        "kitchens": [
            {
                "id": k.id,
                "name": k.name,
                "email": k.email
            }
            for k in kitchens
        ]
    })

@csrf_exempt
def edit_kitchen(request, id):

    if request.method != "POST":
        return JsonResponse(
            {"message": "Invalid request"},
            status=400
        )

    try:
        user = User.objects.get(id=id, is_kitchen=True)

        data = json.loads(request.body)

        user.name = data.get("name")
        user.save()

        return JsonResponse({
            "message": "Kitchen user updated"
        })

    except User.DoesNotExist:
        return JsonResponse({
            "message": "Kitchen user not found"
        }, status=404)


@csrf_exempt
def delete_kitchen(request, id):
    user = User.objects.get(id=id)

    user.delete()

    return JsonResponse({
        "message": "Kitchen user deleted"
    })

from django.http import JsonResponse
from .models import KitchenOrder

def search_order(request):

    order_no = request.GET.get("order_no")

    try:
        order = KitchenOrder.objects.get(
            order_number__iexact=order_no
        )

        return JsonResponse({
            "found": True,
            "order_number": order.order_number,
            "status": order.status,
            "created_at": order.created_at.strftime("%d-%m-%Y %H:%M")
        })

    except KitchenOrder.DoesNotExist:

        return JsonResponse({
            "found": False
        })
    

from .models import KitchenOrder


@staff_member_required
def orders_by_date(request):

    date = request.GET.get("date")
    order_dir = request.GET.get("order", "desc")

    orders = KitchenOrder.objects.all()

    if date:
        orders = orders.filter(created_at__date=date)

    # Counts for selected date
    pending_count = orders.filter(status="pending").count()
    preparing_count = orders.filter(status="preparing").count()
    completed_count = orders.filter(
        status__in=["served", "completed"]
    ).count()

    if order_dir == "asc":
        orders = orders.order_by("created_at")
    else:
        orders = orders.order_by("-created_at")

    return JsonResponse({
        "pending_count": pending_count,
        "preparing_count": preparing_count,
        "completed_count": completed_count,

        "orders": [
            {
                "id": order.id,
                "order_number": order.order_number,
                "status": order.status,
                "created_at": order.created_at.strftime("%d-%m-%Y %H:%M"),
                "invoice_id": order.invoice.id
            }
            for order in orders
        ]
    })




import subprocess
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings


@staff_member_required
def mysql_backup(request):

    db = settings.DATABASES["default"]

    MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

    command = [
        MYSQLDUMP_PATH,
        f"--user={db['USER']}",
        f"--password={db['PASSWORD']}",
        db["NAME"],
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return HttpResponse(
            result.stderr,
            status=500
        )

    response = HttpResponse(
        result.stdout,
        content_type="application/sql"
    )

    response["Content-Disposition"] = (
        'attachment; filename="database_backup.sql"'
    )

    return response


@login_required
def my_orders(request):

    invoices = Invoice.objects.filter(
        user=request.user
    ).select_related(
        "kitchen_order"
    ).order_by("-id")[:10]

    return JsonResponse({
        "orders": [
            {
                "invoice": i.invoice_number,
                "order_no": i.kitchen_order.order_number,
                "status": i.kitchen_order.status,

                # Order Date Time
                "created_at": i.created_at.strftime(
                    "%d-%m-%Y %I:%M %p"
                ) if hasattr(i, "created_at") else ""
            }
            for i in invoices
        ]
    })


@staff_member_required
def orders_by_status(request):

    status = request.GET.get("status")

    orders = KitchenOrder.objects.filter(
        status=status
    ).order_by("-created_at")

    return JsonResponse({
    "orders": [
        {
            "id": o.id,
            "order_number": o.order_number,
            "status": o.status,
            "created_at": o.created_at.strftime("%d-%m-%Y %H:%M"),
            "invoice_id": o.invoice.id
        }
        for o in orders
    ],
    "count": orders.count()
})
    

@login_required
@csrf_exempt
def request_inventory(request):

    if request.method=="POST":

        data=json.loads(request.body)


        InventoryRequest.objects.create(
            kitchen_user=request.user,
            item_name=data.get("item"),
            quantity=data.get("quantity"),
            description=data.get("description")
        )


        return JsonResponse({
            "message":"Inventory request sent"
        })

@staff_member_required
def inventory_requests(request):

    requests = InventoryRequest.objects.filter(
        status="Pending"
    )


    return JsonResponse({

        "requests":[

        {
        "id":r.id,
        "item":r.item_name,
        "qty":r.quantity,
        "description":r.description,
        "kitchen":r.kitchen_user.name
        }

        for r in requests

        ]

    })
@staff_member_required
def give_inventory(request):

    if request.method == "POST":

        request_id = request.POST.get("request_id")
        quantity = request.POST.get("quantity")
        description = request.POST.get("description")


        req = InventoryRequest.objects.get(
            id=request_id
        )


        InventoryIssue.objects.create(

            kitchen_user=req.kitchen_user,

            item_name=req.item_name,

            quantity=quantity,

            description=description,

            issued_by=request.user
        )


        req.status="Completed"
        req.save()


        messages.success(
            request,
            "Inventory sent successfully"
        )


    return redirect(
        "users:admin_dashboard"
    )

@staff_member_required
def inventory_issues(request):

    issues = InventoryIssue.objects.all().order_by("-created_at")

    return JsonResponse({
        "issues": [
            {
                "id": i.id,
                "item": i.item_name,
                "qty": i.quantity,
                "description": i.description,
                "kitchen": i.kitchen_user.name,
                "issued_by": i.issued_by.name,
                "date": i.created_at.strftime("%d-%m-%Y %H:%M")
            }
            for i in issues
        ]
    })