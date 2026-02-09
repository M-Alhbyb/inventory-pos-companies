"""Views for accounts app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from functools import wraps

from .models import User, Company, CompanySubscription, SubscriptionPlan
from .forms import CompanyRegistrationForm, CustomAuthenticationForm, UserForm, CompanySettingsForm, SubscriptionPlanForm


# =============================================================================
# DECORATORS
# =============================================================================

def platform_manager_required(view_func):
    """Restrict access to platform managers only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_platform_manager:
            messages.error(request, 'هذه الصفحة مخصصة لمدير المنصة فقط.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def company_manager_required(view_func):
    """Restrict access to company managers only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_company_manager:
            messages.error(request, 'هذه الصفحة مخصصة لمدير الشركة فقط.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def company_required(view_func):
    """Require user to belong to a company with valid subscription."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.company:
            messages.error(request, 'يجب أن تنتمي إلى شركة للوصول إلى هذه الصفحة.')
            return redirect('accounts:login')
        
        # Check subscription validity
        try:
            subscription = request.user.company.subscription
            if not subscription.is_valid:
                messages.warning(request, 'اشتراك شركتك منتهي أو في انتظار التفعيل.')
                return redirect('accounts:subscription_status')
        except CompanySubscription.DoesNotExist:
            messages.error(request, 'شركتك ليس لديها اشتراك فعال.')
            return redirect('accounts:subscription_status')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

def login_view(request):
    """Custom login with role-based redirect."""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'مرحباً {user.get_full_name() or user.username}!')
            return redirect_by_role(user)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle logout."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'تم تسجيل الخروج بنجاح.')
        return redirect('accounts:login')
    return render(request, 'accounts/logout.html')


def redirect_by_role(user):
    """Redirect user based on their role."""
    if user.is_platform_manager:
        return redirect('accounts:platform_dashboard')
    elif user.is_company_manager:
        return redirect('accounts:company_dashboard')
    elif user.is_accountant:
        return redirect('inventory:dashboard')
    elif user.is_representative:
        return redirect('inventory:rep_dashboard')
    elif user.is_cashier:
        return redirect('pos:interface')
    else:
        return redirect('accounts:login')


# =============================================================================
# REGISTRATION
# =============================================================================

def register_company(request):
    """Handle company registration with plan selection."""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    plans = SubscriptionPlan.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            # Create company
            company = form.save()
            
            # Create subscription (pending approval)
            plan = form.cleaned_data['plan']
            CompanySubscription.objects.create(
                company=company,
                plan=plan,
                status=CompanySubscription.Status.PENDING
            )
            
            # Create company manager user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=company.email,
                company=company,
                role=User.Role.COMPANY_MANAGER
            )
            
            messages.success(
                request, 
                'تم تسجيل شركتك بنجاح! سيتم مراجعة طلبك وتفعيل حسابك قريباً.'
            )
            return redirect('accounts:registration_pending')
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'plans': plans
    })


def registration_pending(request):
    """Show registration pending message."""
    return render(request, 'accounts/registration_pending.html')


@login_required
def subscription_status(request):
    """Show subscription status for company users."""
    if not request.user.company:
        return redirect('accounts:login')
    
    try:
        subscription = request.user.company.subscription
    except CompanySubscription.DoesNotExist:
        subscription = None
    
    return render(request, 'accounts/subscription_status.html', {
        'subscription': subscription
    })


# =============================================================================
# PLATFORM MANAGER VIEWS
# =============================================================================

@platform_manager_required
def platform_dashboard(request):
    """Platform manager dashboard showing all companies."""
    companies = Company.objects.all().select_related('subscription', 'subscription__plan')
    pending_count = CompanySubscription.objects.filter(
        status=CompanySubscription.Status.PENDING
    ).count()
    trial_count = CompanySubscription.objects.filter(
        status=CompanySubscription.Status.TRIAL
    ).count()
    active_count = CompanySubscription.objects.filter(
        status=CompanySubscription.Status.ACTIVE
    ).count()
    
    context = {
        'companies': companies,
        'total_companies': companies.count(),
        'pending_count': pending_count,
        'trial_count': trial_count,
        'active_count': active_count,
        'total_users': User.objects.exclude(role=User.Role.PLATFORM_MANAGER).count(),
    }
    return render(request, 'accounts/platform/dashboard.html', context)


@platform_manager_required
def platform_companies(request):
    """List all companies with filters."""
    status_filter = request.GET.get('status', '')
    
    companies = Company.objects.all().select_related('subscription', 'subscription__plan')
    
    if status_filter:
        companies = companies.filter(subscription__status=status_filter)
    
    return render(request, 'accounts/platform/companies.html', {
        'companies': companies,
        'current_status': status_filter
    })


@platform_manager_required
def approve_company(request, company_id):
    """Approve a pending company subscription."""
    if request.method == 'POST':
        company = get_object_or_404(Company, id=company_id)
        try:
            subscription = company.subscription
            subscription.approve()
            messages.success(request, f'تم تفعيل شركة {company.name} بنجاح!')
        except CompanySubscription.DoesNotExist:
            messages.error(request, 'الشركة ليس لديها اشتراك.')
    
    return redirect('accounts:platform_companies')


@platform_manager_required
def platform_plans(request):
    """Manage subscription plans."""
    plans = SubscriptionPlan.objects.all()
    return render(request, 'accounts/platform/plans.html', {'plans': plans})


@platform_manager_required
def add_plan(request):
    """Add a new subscription plan."""
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة خطة الاشتراك بنجاح!')
            return redirect('accounts:platform_plans')
    else:
        form = SubscriptionPlanForm()
    
    return render(request, 'accounts/platform/add_plan.html', {'form': form})


@platform_manager_required
def edit_plan(request, plan_id):
    """Edit an existing subscription plan."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث خطة الاشتراك بنجاح!')
            return redirect('accounts:platform_plans')
    else:
        form = SubscriptionPlanForm(instance=plan)
    
    return render(request, 'accounts/platform/edit_plan.html', {
        'form': form,
        'plan': plan
    })


@platform_manager_required
def delete_plan(request, plan_id):
    """Delete a subscription plan if unused."""
    if request.method == 'POST':
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        
        # Check for active subscriptions
        if plan.subscriptions.exists():
            messages.error(request, 'لا يمكن حذف هذه الخطة لأنها مرتبطة باشتراكات شركات.')
        else:
            plan.delete()
            messages.success(request, 'تم حذف الخطة بنجاح!')
            
    return redirect('accounts:platform_plans')


# =============================================================================
# COMPANY MANAGER VIEWS
# =============================================================================

@company_manager_required
@company_required
def company_dashboard(request):
    """Company manager dashboard."""
    company = request.user.company
    users = company.users.all()
    
    # Get subscription info
    try:
        subscription = company.subscription
    except CompanySubscription.DoesNotExist:
        subscription = None
    
    context = {
        'company': company,
        'subscription': subscription,
        'users': users,
        'user_count': users.count(),
        'user_limit': subscription.plan.max_users if subscription else 0,
        'product_count': company.products.count(),
        'product_limit': subscription.plan.max_products if subscription else 0,
    }
    return render(request, 'accounts/company/dashboard.html', context)


@company_manager_required
@company_required
def company_users(request):
    """Manage company users."""
    company = request.user.company
    users = company.users.exclude(id=request.user.id)
    subscription = company.subscription
    
    can_add_user = users.count() < subscription.plan.max_users - 1  # -1 for manager
    
    return render(request, 'accounts/company/users.html', {
        'users': users,
        'can_add_user': can_add_user,
        'user_limit': subscription.plan.max_users
    })


@company_manager_required
@company_required
def add_user(request):
    """Add a new user to the company."""
    company = request.user.company
    subscription = company.subscription
    
    # Check user limit
    if company.users.count() >= subscription.plan.max_users:
        messages.error(request, 'لقد وصلت إلى الحد الأقصى للمستخدمين في خطتك.')
        return redirect('accounts:company_users')
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.company = company
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            else:
                # Generate random password
                import secrets
                user.set_password(secrets.token_urlsafe(12))
            user.save()
            messages.success(request, f'تم إضافة المستخدم {user.username} بنجاح!')
            return redirect('accounts:company_users')
    else:
        form = UserForm()
    
    return render(request, 'accounts/company/add_user.html', {'form': form})


@company_manager_required
@company_required
def edit_user(request, user_id):
    """Edit a company user."""
    company = request.user.company
    user = get_object_or_404(User, id=user_id, company=company)
    
    # Prevent editing self
    if user.id == request.user.id:
        messages.error(request, 'لا يمكنك تعديل حسابك من هنا.')
        return redirect('accounts:company_users')
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'تم تحديث المستخدم {user.username} بنجاح!')
            return redirect('accounts:company_users')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'accounts/company/edit_user.html', {
        'form': form,
        'edit_user': user
    })

# PASHA: i stopped it permantly
@company_manager_required
@company_required
def delete_user(request, user_id):
    messages.error(request, 'عذرًا هذا الخيار غير متاح حاليًا')
    return redirect('accounts:company_users')
    """Delete a company user."""
    if request.method == 'POST':
        company = request.user.company
        user = get_object_or_404(User, id=user_id, company=company)
        
        # Prevent deleting self
        if user.id == request.user.id:
            messages.error(request, 'لا يمكنك حذف حسابك.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'تم حذف المستخدم {username} بنجاح!')
    
    return redirect('accounts:company_users')


@company_manager_required
@company_required
def company_settings(request):
    """Company settings including tax configuration."""
    company = request.user.company
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث إعدادات الشركة بنجاح!')
            return redirect('accounts:company_settings')
    else:
        form = CompanySettingsForm(instance=company)
    
    return render(request, 'accounts/company/settings.html', {'form': form})
