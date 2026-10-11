from django.db import models
from django.db.models import F, DecimalField, ExpressionWrapper
from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy

from django.views.generic import ListView, FormView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from apps.forms import *
from apps.models import Category, Product, Order, Oqim, Region, District

User = get_user_model()


# def user_login(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         password = request.POST["password"]
#
#         user = authenticate(request, username=username, password=password)
#
#         if user is not None:
#             login(request, user=user)
#             return redirect('home')
#
#     return redirect('login')

# ======================== MAIN ========================

class HomeListView(ListView):
    queryset = Category.objects.all()
    template_name = "home.html"
    context_object_name = "categories"
    slug_url_kwarg = "slug"

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data["products"] = Product.objects.all()
        return data


# ======================== OPERATOR ========================

class OperatorListView(ListView):
    queryset = Order.objects.all()
    template_name = 'operator_orders.html'
    context_object_name = "orders"

    def get_queryset(self):
        queryset = Order.objects.select_related("user", "product", "oqim").annotate(total_price=ExpressionWrapper(
            F("unit_price") * F("quantity"),output_field=DecimalField(max_digits=12, decimal_places=0)))

        region_id = self.request.GET.get("region")

        if region_id and region_id != "all":
            queryset = queryset.filter(user__region_id=region_id)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = self.get_queryset()
        statuses = []

        context["statuses"] = statuses
        context["orders_count"] = Order.objects.all().count()
        context["form"] = OperatorOrderMiniUpdate_FormView()
        context["regions"] = Region.objects.all()

        for value, label in Order.StatusType.choices:
            statuses.append({
                "value": value,
                "label": label,
                "count": orders.filter(status=value).count()
            })

        return context

# -----------------------------------------------------

class OperatorOrderListMiniUpdateView(UpdateView): # в странице оператора рядом с звонком стоит карандащ
    model = Order
    form_class = OperatorOrderMiniUpdate_FormView
    success_url = reverse_lazy("operator-list")

    def form_valid(self, form):
        return super().form_valid(form)



# class OperatorOrderDetailView(DetailView):
#     model = Order
#     template_name = "operator_order_detail.html"
#     context_object_name = "order"
#
#     def get_queryset(self):
#         queryset = Order.objects.select_related("user", "product")
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["regions"] = Region.objects.all()
#         if self.object.region:
#             context["districts"] = District.objects.filter(region=self.object.region)
#         else:
#             context["districts"] = District.objects.none()


class OperatorOrderUpdateView(UpdateView):
    model = Order
    form_class = OperatorOrderUpdateForm
    template_name = "operator_order_detail.html"
    context_object_name = "order"
    success_url = reverse_lazy("operator-list")

    def get_queryset(self):
        return Order.objects.select_related("user", "product", "region", "district")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["regions"] = Region.objects.all()
        if self.object.region_id:
            context["districts"] = District.objects.filter(region=self.object.region)
        else:
            context["districts"] = District.objects.none()

        return context


# ======================== LOGINS ========================

class LoginFormView(FormView):
    form_class = LoginForm
    template_name = "home.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        login(self.request, form.session_user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect("home")

# -----------------------------------------------------

class RegisterCreateView(CreateView):
    form_class = RegisterModelForm
    template_name = "home.html"
    success_url = reverse_lazy("home")
    queryset = User.objects.all()

    def form_valid(self, form):
        user = form.save(commit=False)

        user.set_password(form.cleaned_data["password"])
        user.save()

        login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect("home")


    # def form_invalid(self, form):
    #     for error in form.errors.values():
    #         messages.error(self.request, str(error))
    #     return super().form_invalid(form)

# -----------------------------------------------------

class MyLogoutView(LogoutView):
    next_page = 'home'


# ======================== Admin_Cabinet ========================

class AdminCabinetTemplateView(TemplateView):
    template_name = "admin_cabinet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = Category.objects.all()
        context["api_key"] = self.request.user.api_key
        context["active_column"] = 'cabinet'

        return context

# -----------------------------------------------------

class AdminMarketListView(ListView):
    queryset = Category.objects.all()
    template_name = "admin_market.html"
    context_object_name = "categories"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["products"] = Product.objects.all()
        context["active_column"] = 'market'
        context["active_category"] = None

        for product in context["products"]:
            product.payment = product.price / 2

        return context

# -----------------------------------------------------

class AdminMarketDetailView(DetailView):
    model = Category
    template_name = "admin_market.html"
    slug_url_kwarg = "slug"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["products"] = Product.objects.filter(category=self.object)
        context["categories"] = Category.objects.all()
        context["active_category"] = self.object

        return context

# -----------------------------------------------------

class AdminSozlamalarUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "admin_sozlamalar.html"
    success_url = reverse_lazy("admin-sozlamalar")

    def get_object(self, queryset=None):
        # «Не бери пользователя из URL. Редактируй именно того пользователя, который сейчас вошёл в аккаунт».
        # То есть пользователь не сможет просто поменять URL и попытаться редактировать чужой профиль.
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["regions"] = Region.objects.all()
        if self.object.region:
            context["districts"] = District.objects.filter(region=self.object.region)
        else:
            context["districts"] = District.objects.none()
        context["categories"] = Category.objects.all()
        context["active_column"] = 'settings'

        return context


# -----------------------------------------------------

def district_list(request):

    region_id = request.GET.get("region")
    districts = District.objects.filter(region_id=region_id)

    data = []
    for district in districts:
        data.append(
            {
                "id": district.id,
                "title": district.title,
            }
        )

    return JsonResponse(data, safe=False)

# -----------------------------------------------------

class AdminChangePasswordUpdateView(FormView):
    form_class = UserChangePasswordForm
    template_name = "admin_sozlamalar.html"
    success_url = reverse_lazy("admin-sozlamalar")

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data["new_password"])

        user.save()
        update_session_auth_hash(self.request, user)

        return super().form_valid(form)

# -----------------------------------------------------

class AdminSorovnomalarTemplateView(TemplateView):
    template_name = "admin_so'rovnomalar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        context["active_column"] = 'sorovnomalar'

        return context

# -----------------------------------------------------

class AdminStatistikaTemplateView(TemplateView):
    template_name = "admin_statistika.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_column"] = 'statistika'

        return context


class AdminTolovTemplateView(TemplateView):
    template_name = "admin_to'lov.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_column"] = "tolov"

        return context


class AdminReferalTemplateView(TemplateView):
    template_name = "admin_referal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_column"] = "referal"

        return context


class AdminKonkursTemplateView(TemplateView):
    template_name = "admin_konkurs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_column"] = "konkurs"

        return context

# ======================== Admin_Oqimlar ========================

class AdminOqimCreateView(CreateView):
    model = Oqim
    form_class = OqimFormView
    template_name = "admin_market.html"
    success_url = reverse_lazy("admin-oqim-list")

    def form_valid(self, form):
        oqim = form.save(commit=False)

        oqim.user = self.request.user

        product_id = self.request.POST.get("product_id")

        if not product_id:
            form.add_error(None, "Mahsulot tanlanmagan")
            return self.form_invalid(form)


        oqim.product = Product.objects.get(pk=product_id)


        oqim.save()


        return super().form_valid(form)

# -----------------------------------------------------

class AdminOqimDeleteView(DeleteView):
    model = Oqim
    success_url = reverse_lazy("admin-oqim-list")

    def get_queryset(self):
        return Oqim.objects.filter(user=self.request.user)

# -----------------------------------------------------

class AdminOqimListView(ListView):
    template_name = "admin_oqim.html"
    context_object_name = "oqims"

    def get_queryset(self):
        return Oqim.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = Category.objects.all()
        context["active_column"] = 'oqim'

        return context


# ======================== PRODUCTS ========================

class CategoryDetailView(DetailView):
    model = Category
    template_name = "product-list.html"
    slug_url_kwarg = "slug"
    context_object_name = "category"


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["products"] = Product.objects.filter(category=self.object)
        data["categories"] = Category.objects.all()
        return data

# -----------------------------------------------------

class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = "product-list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["categories"] = Category.objects.all()
        return data

# -----------------------------------------------------

class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = "product-detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        oqim_id = self.request.GET.get("oqim")
        oqim = None

        if oqim_id:
            oqim = Oqim.objects.filter(id=oqim_id,product=self.object).first()

        if oqim:
            context["final_price"] = self.object.price - oqim.discount
        else:
            context["final_price"] = self.object.price

        context["oqim"] = oqim




        initial = {}

        if self.request.user.is_authenticated:
            first_name = self.request.user.first_name or ""
            last_name = self.request.user.last_name or ""

            initial["username"] = f"{first_name} {last_name}".strip()
            initial["phone_number"] = self.request.user.phone_number

        context["form"] = OrderFormView(initial=initial)

        return context


# ======================== Orders ========================

class SuccessOrderDetailView(DetailView):
    model = Order
    template_name = "succes.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_price"] = self.object.unit_price * self.object.quantity
        return context

# -----------------------------------------------------

class OrderCreateView(CreateView):
    form_class = OrderFormView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = Product.objects.get(slug=self.kwargs["slug"])
        return context


    def form_valid(self, form):
        order = form.save(commit=False)

        if self.request.user.is_authenticated:
            order.user = self.request.user
        else:
            order.user = None

        product = get_object_or_404(Product,slug=self.kwargs["slug"])
        order.product = product
        order.unit_price = product.price

        oqim_id = self.request.POST.get("oqim_id")

        if oqim_id:
            oqim = Oqim.objects.filter(id=oqim_id,product=product).first()

            if oqim:
                order.oqim = oqim
                order.discount = oqim.discount
                order.unit_price = product.price - oqim.discount

        order.save()
        return redirect("success", pk=order.pk)

    def form_invalid(self, form):
        return redirect("home")

# -----------------------------------------------------






