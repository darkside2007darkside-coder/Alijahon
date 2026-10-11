
from django.urls import path
from apps.views import *

urlpatterns = [
    # -------------------------------- MAIN --------------------------------
    path('', HomeListView.as_view(), name='home'),

    # -------------------------------- MAIN --------------------------------

    path('operator/orders/', OperatorListView.as_view(), name='operator-list'),
    path("operator/order/update/<int:pk>/", OperatorOrderUpdateView.as_view(), name="operator-order-update", ),
    path('operator/order/<int:pk>/mini/update/', OperatorOrderListMiniUpdateView.as_view(), name='operator-list-mini-update'),
    # path("operator/order/<int:pk>/", OperatorOrderDetailView.as_view(),name="operator-order-detail",),

    # -------------------------------- LOGINS --------------------------------
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('register/', RegisterCreateView.as_view(), name='register'),



    # -------------------------------- PRODUCTS --------------------------------
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('category/', ProductListView.as_view(), name='product-list'),
    path('product/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('product/<str:slug>/order/', OrderCreateView.as_view(), name='order-create'),

    path('success/<int:pk>/', SuccessOrderDetailView.as_view(), name='success'),



    # -------------------------------- ADMIN --------------------------------
    path('admin_page/', AdminCabinetTemplateView.as_view(), name='admin-page'),
    path('admin_page/market/', AdminMarketListView.as_view(), name='admin-market'),
    path('admin_page/market/<str:slug>/', AdminMarketDetailView.as_view(), name='admin-market-category'),
    path("admin_page/so'rovnomalar/", AdminSorovnomalarTemplateView.as_view(), name='admin-sorovnomalar'),
    path("admin_page/statistika/", AdminStatistikaTemplateView.as_view(), name='admin-statistika'),
    path("admin_page/konkers/", AdminKonkursTemplateView.as_view(), name='admin-konkurs'),
    path("admin_page/tolov/", AdminTolovTemplateView.as_view(), name='admin-tolov'),
    path("admin_page/referal/", AdminReferalTemplateView.as_view(), name='admin-referal'),
    path("admin_page/sozlamalar/", AdminSozlamalarUpdateView.as_view(), name='admin-sozlamalar'),
    path("districts/", district_list, name="district-list"),
    path("admin_page/sozlamalar/change_password/", AdminChangePasswordUpdateView.as_view(), name='admin-change-password'),

    path("admin_page/oqim/", AdminOqimCreateView.as_view(), name='admin-oqim-create'),
    path("admin_page/oqimlar/", AdminOqimListView.as_view(), name='admin-oqim-list'),
    path("admin_page/oqim/delete/<int:pk>/", AdminOqimDeleteView.as_view(), name='admin-delete'),


]

