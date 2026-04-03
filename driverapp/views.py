from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from fleetapp.models import Driver
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from fleetapp.models import Driver
from rest_framework_simplejwt.tokens import RefreshToken

# ---------------- LOGIN ----------------
@ensure_csrf_cookie
def login_view(request):
    if request.method == "POST":
        request.session.flush()
        driver_code = request.POST.get('driver_code')

        try:
            # ✅ Check driver
            driver = Driver.objects.get(driver_code=driver_code)

            # ✅ Create/get Django user
            user, created = User.objects.get_or_create(username=driver.driver_code)

            # ✅ Generate JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # ✅ Store in session
            request.session['jwt_token'] = access_token
            request.session['driver_id'] = driver.id
            request.session['driver_name'] = driver.driver_name

            return redirect('driver_home')

        except Driver.DoesNotExist:
            return render(request, 'driver/login.html', {
                'error': 'Invalid driver code'
            })

    return render(request, 'driver/login.html')




# ---------------- HOME ----------------
def home(request):
    driver_id = request.session.get('driver_id')

    if not driver_id:
        return redirect('driver_login')

    driver = Driver.objects.get(id=driver_id)

    return render(request, 'driver/home.html', {
        'driver': driver
    })
# ---------------- PROFILE (CALL API) ----------------
def driver_profile_view(request):
    token = request.session.get('jwt_token')

    if not token:
        return redirect('driver_login')

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        "http://127.0.0.1:8000/api/driver-profile/",
        headers=headers
    )

    data = response.json()

    return render(request, 'driver/profile.html', {'data': data})


# ---------------- LOGOUT ----------------
def driver_logout(request):
    request.session.flush()
    return redirect('driver_login')

# Trip Accepted Page
def accepted_view(request):
    return render(request, 'driver/accepted.html')


# My Bookings Page
def bookings(request):
    return render(request, 'driver/bookings.html')


# Travel Packages Page
def packages(request):
    return render(request, 'driver/packages.html')


# Emergency Contacts Page
def emergency(request):
    return render(request, 'driver/emergency.html')


# Settings Page
def settings(request):
    return render(request, 'driver/settings.html')


# Help Page
def help(request):
    return render(request, 'driver/help.html')


def tracking_view(request):
    return render(request, 'driver/tracking.html')