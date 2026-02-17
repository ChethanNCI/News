from django.urls import path
from . import views
from .views import register, login
from .views import login_view, register_view
from .views import subscription_page
from .views import subscription_page, process_payment, subscription_success, unsubscribe
from .views import advertisement_list
from .views import home


urlpatterns = [ 
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('subscribe/', subscription_page, name='subscription_page'),
    path('unsubscribe/', unsubscribe, name='unsubscribe'),
    path('process_payment/', process_payment, name='process_payment'),  # ✅ Ensure this exists
    path('subscription-success/', subscription_success, name='subscription_success'),
    path('api/advertisements/', advertisement_list, name='advertisement-list'),
    path('',views.home,name="home"),
    path('<str:category>/',views.category,name="category"),   
]