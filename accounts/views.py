import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm
from .models import UserProfile, Address
from orders.models import Order
from wishlist.models import Wishlist


def send_welcome_email(user, request):
    """Sends a warm aesthetic thank-you welcome email to the newly registered customer."""
    if not user.email:
        return

    subject = "Welcome to Aesthetic Store ✦ Thank you for joining us!"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Aesthetic Store <hello@aestheticstore.com>')
    to_email = [user.email]

    site_url = request.build_absolute_uri('/')[:-1] if request else 'https://aestheticstore.com'
    context = {
        'user': user,
        'site_url': site_url,
    }

    try:
        text_content = render_to_string('emails/welcome_email.txt', context)
        html_content = render_to_string('emails/welcome_email.html', context)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
    except Exception:
        pass


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    redirect_to = request.POST.get('next') or request.GET.get('next') or 'accounts:profile'

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Profile newsletter
            if hasattr(user, 'profile'):
                user.profile.newsletter_subscribed = form.cleaned_data.get('newsletter', True)
                user.profile.save()

            # Send Thank-You Welcome Email
            send_welcome_email(user, request)

            # Auto login
            login(request, user)
            messages.success(request, f"Welcome to Aesthetic Store, {user.first_name}! Your account has been created.")
            return redirect(redirect_to)
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form, 'next': redirect_to})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    redirect_to = request.POST.get('next') or request.GET.get('next') or 'accounts:profile'

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(redirect_to)
        else:
            # Check if user passed email instead of username
            login_id = request.POST.get('username')
            password = request.POST.get('password')
            user_obj = User.objects.filter(email__iexact=login_id).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    return redirect(redirect_to)
            messages.error(request, "Invalid username/email or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': redirect_to})


def google_login_view(request):
    """Initiates Google OAuth2 login or simulated sandbox sign-in."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    state = uuid.uuid4().hex[:16]
    request.session['google_oauth_state'] = state

    if client_id:
        redirect_uri = request.build_absolute_uri('/account/google/callback/')
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"state={state}&"
            f"prompt=select_account"
        )
        return redirect(google_auth_url)

    # Sandbox / Local Testing Mode
    return render(request, 'accounts/google_simulate.html', {
        'state': state,
    })


def google_callback_view(request):
    """Handles Google OAuth2 callback and creates/authenticates user."""
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')
    code = request.GET.get('code')

    user_email = ''
    first_name = 'Conscious'
    last_name = 'Member'

    if client_id and client_secret and code:
        import requests
        redirect_uri = request.build_absolute_uri('/account/google/callback/')
        try:
            # Exchange code for tokens
            token_res = requests.post('https://oauth2.googleapis.com/token', data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }, timeout=10)
            token_data = token_res.json()
            access_token = token_data.get('access_token')

            if access_token:
                userinfo_res = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
                    'Authorization': f'Bearer {access_token}'
                }, timeout=10)
                user_info = userinfo_res.json()
                user_email = user_info.get('email', '')
                first_name = user_info.get('given_name', 'Member')
                last_name = user_info.get('family_name', '')
        except Exception:
            pass

    # Fallback to simulated POST / GET parameters if in sandbox mode
    if not user_email:
        user_email = request.POST.get('email', '').strip() or request.GET.get('email', '').strip()
        first_name = request.POST.get('first_name', 'Google User').strip() or request.GET.get('first_name', 'Google User').strip()

    if not user_email or '@' not in user_email:
        messages.error(request, "Google sign-in cancelled or no email provided.")
        return redirect('accounts:login')

    # Find existing or create new account
    user = User.objects.filter(email__iexact=user_email).first()
    is_new = False
    if not user:
        # Create unique username from email
        base_username = user_email.split('@')[0].replace('.', '_')
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=user_email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_unusable_password()
        user.save()
        is_new = True

        # Send Thank-You Welcome Email
        send_welcome_email(user, request)

    # Log user in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    if is_new:
        messages.success(request, f"Welcome to Aesthetic Store, {user.first_name}! Your Google account is ready & a welcome gift was emailed to you.")
    else:
        messages.success(request, f"Welcome back, {user.first_name or user.username}!")

    return redirect('accounts:profile')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon!")
    return redirect('core:home')


@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    orders = Order.objects.filter(user=user).prefetch_related('items').order_by('-created_at')
    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    wishlist = Wishlist.objects.filter(user=user).first()
    wishlist_items = wishlist.items.select_related('product') if wishlist else []

    tab = request.GET.get('tab', 'orders')

    if request.method == 'POST' and tab == 'profile':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            profile.phone_number = request.POST.get('phone_number', '')
            profile.bio = request.POST.get('bio', '')
            profile.save()
            messages.success(request, "Your profile details have been updated.")
            return redirect('/account/?tab=profile')
    else:
        form = UserProfileForm(instance=user, initial={
            'phone_number': profile.phone_number,
            'bio': profile.bio
        })

    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'addresses': addresses,
        'wishlist_items': wishlist_items,
        'form': form,
        'active_tab': tab,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "New address added successfully.")
            return redirect('/account/?tab=addresses')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Add'})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('/account/?tab=addresses')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Edit', 'address': address})


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.info(request, "Address removed.")
    return redirect('/account/?tab=addresses')


@login_required
def address_set_default(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"Default delivery address updated to {address.full_name}.")
    return redirect('/account/?tab=addresses')
