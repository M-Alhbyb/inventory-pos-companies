"""URL routing for accounts app."""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/', views.register_company, name='register'),
    path('register/pending/', views.registration_pending, name='registration_pending'),
    path('subscription/status/', views.subscription_status, name='subscription_status'),
    
    # Platform Manager
    path('platform/', views.platform_dashboard, name='platform_dashboard'),
    path('platform/companies/', views.platform_companies, name='platform_companies'),
    path('platform/companies/<int:company_id>/approve/', views.approve_company, name='approve_company'),
    path('platform/plans/', views.platform_plans, name='platform_plans'),
    path('platform/plans/add/', views.add_plan, name='add_plan'),
    path('platform/plans/<int:plan_id>/edit/', views.edit_plan, name='edit_plan'),
    path('platform/plans/<int:plan_id>/delete/', views.delete_plan, name='delete_plan'),
    
    # Company Manager
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('dashboard/users/', views.company_users, name='company_users'),
    path('dashboard/users/add/', views.add_user, name='add_user'),
    path('dashboard/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('dashboard/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('dashboard/settings/', views.company_settings, name='company_settings'),
]
