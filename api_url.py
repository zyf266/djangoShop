from django.urls import path, include

urlpatterns = [
    # 用户 API
    path('users/', include('users.api_urls')),

    # 商品 API
    path('products/', include('products.api_urls')),

    # 购物车 API
    path('cart/', include('carts.api_urls')),

    # 订单 API
    path('orders/', include('orders.api_urls')),

    # 促销 API
    path('promotions/', include('promotions.api_urls')),
]
