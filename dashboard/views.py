from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from products.models import Product, Category
from orders.models import OrderItem
from core.permissions import OwnerRequiredMixin


class OwnerProductListView(OwnerRequiredMixin, ListView):
    model = Product
    template_name = "dashboard/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)


class OwnerProductCreateView(OwnerRequiredMixin, CreateView):
    model = Product
    fields = ["category", "name", "description", "price", "stock"]
    template_name = "dashboard/product_form.html"
    success_url = reverse_lazy("dashboard:product_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerProductUpdateView(OwnerRequiredMixin, UpdateView):
    model = Product
    fields = ["category", "name", "description", "price", "stock"]
    template_name = "dashboard/product_form.html"
    success_url = reverse_lazy("dashboard:product_list")

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)


class OwnerProductDeleteView(OwnerRequiredMixin, DeleteView):
    model = Product
    template_name = "dashboard/product_confirm_delete.html"
    success_url = reverse_lazy("dashboard:product_list")

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)


class OwnerOrdersView(OwnerRequiredMixin, ListView):
    template_name = "dashboard/owner_orders.html"
    context_object_name = "order_items"

    def get_queryset(self):
        return OrderItem.objects.filter(owner=self.request.user).select_related("order", "product")