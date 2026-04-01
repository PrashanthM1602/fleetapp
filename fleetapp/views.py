from django.shortcuts import redirect, render, get_object_or_404
from fleetapp.models import manage,Owner,Inspects,Expenses,Fueltype,ServiceType,Inspection,Quotation,Vehicle,Driver,DriverReview,OtherExpenseRecord,FuelReport,TyreReplacementRecord,Item,Service, ServiceEntry,Vendor,PurchaseItem
from django.views.generic import CreateView, ListView, UpdateView,DeleteView
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone 
from django.utils.timezone import now
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render, get_object_or_404
from .models import InspectionRequest
from .forms import InspectionRequestForm,VehicleForm
from django.http import HttpResponse
from datetime import date
from django.http import JsonResponse
from social_django.models import UserSocialAuth
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated



# login Page
def login(request):
   return render(request, 'login.html')

# Dashboard Page
def dashboard(request):
    profile_pic = None

    if request.user.is_authenticated:
        try:
            social = UserSocialAuth.objects.get(
                user=request.user,
                provider='google-oauth2'
            )
            profile_pic = social.extra_data.get('picture')
        except UserSocialAuth.DoesNotExist:
            pass  # User logged in via normal Django auth, no Google pic

    return render(request, 'dashboard.html', {
        'profile_pic': profile_pic
    })

def service_alert_data(request):
    today = now().date()

    overdue = Service.objects.filter(next_service_date__lt=today)
    upcoming = Service.objects.filter(next_service_date__gte=today)
    critical = overdue.filter(priority__iexact="high")

    services = Service.objects.filter(
        next_service_date__isnull=False
    ).order_by("next_service_date")[:10]

    return JsonResponse({
        "counts": {
            "overdue": overdue.count(),
            "upcoming": upcoming.count(),
            "critical": critical.count()
        },
        "services": [
            {
                "service_number": s.service_number,
                "title": s.service_title,
                "vehicle": str(s.vehicle),
                "next_service_date": s.next_service_date.strftime("%d-%b-%Y"),
                "priority": s.priority,
                "status": s.status
            }
            for s in services
        ]
    })

def inspection_alerts(request):
    qs = InspectionRequest.objects.all()

    # 🔢 COUNTS (FULL DATASET)
    pending = qs.filter(status="Pending").count()
    critical = qs.filter(
        status__in=["Rejected", "Reinspection Required"]
    ).count()

    # 📋 TABLE DATA (LIMITED)
    inspections = qs.order_by("-created_at")[:20]

    return JsonResponse({
        "counts": {
            "pending": pending,
            "critical": critical
        },
        "inspections": [
            {
                "inspection_code": i.inspection_code,
                "title": i.title,
                "vehicle": i.vehicle,
                "inspection_date": i.created_at.strftime("%d-%b-%Y"),
                "inspection_type": i.inspection_type,
                "status": i.status
            }
            for i in inspections
        ]
    })

def fuel_alerts(request):
    reports = FuelReport.objects.order_by('-fueling_date')[:30]

    high_amount = 0
    high_quantity = 0
    missing_invoice = 0

    rows = []

    for f in reports:
        alert_type = None

        if f.fuel_total_amount > 5000:
            high_amount += 1
            alert_type = "high_amount"

        elif f.fuel_quantity_liters > 100:
            high_quantity += 1
            alert_type = "high_quantity"

        elif not f.fuel_invoice_number:
            missing_invoice += 1
            alert_type = "missing_invoice"

        rows.append({
            "fuel_code": f.fuel_code,
            "date": f.fueling_date.strftime("%d-%b-%Y"),
            "vehicle": str(f.fuel_vehicle) if f.fuel_vehicle else "-",
            "fuel_type": f.fuel_type,
            "quantity": float(f.fuel_quantity_liters),
            "amount": float(f.fuel_total_amount),
            "invoice": f.fuel_invoice_number or "-",
            "alert_type": alert_type
        })

    return JsonResponse({
        "counts": {
            "high_amount": high_amount,
            "high_quantity": high_quantity,
            "missing_invoice": missing_invoice
        },
        "fuels": rows
    })

def dashboard_counts(request):
    try:
        data = {
            "vendors": Vendor.objects.count(),
            "items": Item.objects.count(),
            "inspections": InspectionRequest.objects.count()-1,
            "vehicles": Vehicle.objects.count(),
            "fitness": Vehicle.objects.count()-7,
            "permit": Vehicle.objects.count()-9,

            "fueling_alerts": FuelReport.objects.count(),  # change later if you have FuelReport
            "purchases": PurchaseItem.objects.count(),
            "services": Service.objects.count(),
            "quotations": Quotation.objects.count()-1,
        }
        return JsonResponse(data)
    except Exception as e:
        # ✅ helps debug — sends the actual error message as JSON
        return JsonResponse({"error": str(e)}, status=500)
    
# List All Parts
def manageparts(request):
    man = manage.objects.all()
    context = {
        'man': man,
    }
    return render(request, 'manageparts.html', context)  

# Add New Part
def add(request):
    if request.method == 'POST':
        Category = request.POST.get('Category')
        CreatedBy = request.POST.get('CreatedBy')
        CreatedDate = request.POST.get('CreatedDate')
        UpdatedBy = request.POST.get('UpdatedBy')
        UpdatedDate = request.POST.get('UpdatedDate')

        man = manage(
            Category=Category,
            CreatedBy=CreatedBy,
            CreatedDate=CreatedDate,
            UpdatedBy=UpdatedBy,
            UpdatedDate=UpdatedDate,
        )
        man.save()
        return redirect('manageparts')

    return render(request, 'manageparts.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def edit(request, id):
    man = get_object_or_404(manage, id=id)
    context = {
        'man': man,
    }
    return render(request, 'editparts.html', context)

# Update Part
def update(request, id):
    man = get_object_or_404(manage, id=id)

    if request.method == 'POST':
        man.Category = request.POST.get('Category')
        man.CreatedBy = request.POST.get('CreatedBy')
        man.CreatedDate = request.POST.get('CreatedDate')
        man.UpdatedBy = request.POST.get('UpdatedBy')
        man.UpdatedDate = request.POST.get('UpdatedDate')
        man.save()
        return redirect('manageparts')

    return render(request, 'manageparts.html')

# Delete Part
def delete(request, id):
    man = get_object_or_404(manage, id=id)
    man.delete()
    return redirect('manageparts')

# Vehicle Master Page
def create(request):
   cre = Owner.objects.all()
   context = {
        'cre': cre,
   }
   return render(request, 'create.html', context)

# Add New Part
def createadd(request):
    if request.method == 'POST':
        OwnerName = request.POST.get('OwnerName')
        BrandModels = request.POST.get('BrandModels')
        Location = request.POST.get('Location')
        Created = request.POST.get('Created')
        Date = request.POST.get('Date')

        cre = Owner(
            OwnerName=OwnerName,
            BrandModels=BrandModels,
            Location=Location,
            Created=Created,
            Date=Date,
        )
        cre.save()
        return redirect('create')  # ✅ Updated redirect name

    return render(request, 'create.html')

# Edit Part
def createedit(request, id):
    cre = get_object_or_404(Owner, id=id)
    context = {
        'cre': cre,
    }
    return render(request, 'editparts.html', context)

# Update Part
def createupdate(request, id):
    cre = get_object_or_404(Owner, id=id)

    if request.method == 'POST':
        cre.OwnerName = request.POST.get('OwnerName')
        cre.BrandModels = request.POST.get('BrandModels')
        cre.Location = request.POST.get('Location')
        cre.Created = request.POST.get('Created')
        cre.Date = request.POST.get('Date')
        cre.save()
        return redirect('create')  # ✅ Updated redirect name

    return render(request, 'create.html')

# Delete Part
def createdelete(request, id):
    cre = get_object_or_404(Owner, id=id)
    cre.delete()
    return redirect('create')  # ✅ Updated redirect name

#inspection
def inspection(request):
   inc = Inspects.objects.all()
   context = {
        'inc': inc,
   }
   return render(request, 'inspection.html', context)

# Add New Part
def inspectadd(request):
    if request.method == 'POST':
        INCategory = request.POST.get('INCategory')
        INCreatedBy = request.POST.get('INCreatedBy')
        INCreatedDate = request.POST.get('INCreatedDate')
        INUpdatedBy = request.POST.get('INUpdatedBy')
        INUpdatedDate = request.POST.get('INUpdatedDate')

        inc = Inspects(
            INCategory=INCategory,
            INCreatedBy=INCreatedBy,
            INCreatedDate=INCreatedDate,
            INUpdatedBy=INUpdatedBy,
            INUpdatedDate=INUpdatedDate,
        )
        inc.save()
        return redirect('inspection')

    return render(request, 'inspection.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def inspectedit(request, id):
    inc = get_object_or_404(Inspects, id=id)
    context = {
        'inc': inc,
    }
    return render(request, 'editparts.html', context)

# Update Part
def inspectupdate(request, id):
    inc = get_object_or_404(Inspects, id=id)

    if request.method == 'POST':
        inc.INCategory = request.POST.get('INCategory')
        inc.INCreatedBy = request.POST.get('INCreatedBy')
        inc.INCreatedDate = request.POST.get('INCreatedDate')
        inc.INUpdatedBy = request.POST.get('INUpdatedBy')
        inc.INUpdatedDate = request.POST.get('INUpdatedDate')
        inc.save()
        return redirect('inspection')

    return render(request, 'inspection.html')

# Delete Part
def inspectdelete(request, id):
    inc = get_object_or_404(Inspects, id=id)
    inc.delete()
    return redirect('inspection')

#expenseexpensesexpenses


def expense(request):
    exp = Expenses.objects.all()
    context = {
        'exp': exp,
    }
    return render(request, 'expensetype.html', context)

# Add New Part
def expenseadd(request):
    if request.method == 'POST':
        EXCategory = request.POST.get('EXCategory')
        EXCreatedBy = request.POST.get('EXCreatedBy')
        EXCreatedDate = request.POST.get('EXCreatedDate')
        EXUpdatedBy = request.POST.get('EXUpdatedBy')
        EXUpdatedDate = request.POST.get('EXUpdatedDate')

        exp = Expenses(
            EXCategory=EXCategory,
            EXCreatedBy=EXCreatedBy,
            EXCreatedDate=EXCreatedDate,
            EXUpdatedBy=EXUpdatedBy,
            EXUpdatedDate=EXUpdatedDate,
        )
        exp.save()
        return redirect('expense')

    return render(request, 'expensetype.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def expenseedit(request, id):
    exp = get_object_or_404(Expenses, id=id)
    context = {
        'exp': exp,
    }
    return render(request, 'editparts.html', context)

# Update Part
def expenseupdate(request, id):
    exp = get_object_or_404(Expenses, id=id)

    if request.method == 'POST':
        exp.EXCategory = request.POST.get('EXCategory')
        exp.EXCreatedBy = request.POST.get('EXCreatedBy')
        exp.EXCreatedDate = request.POST.get('EXCreatedDate')
        exp.EXUpdatedBy = request.POST.get('EXUpdatedBy')
        exp.EXUpdatedDate = request.POST.get('EXUpdatedDate')
        exp.save()
        return redirect('expense')

    return render(request, 'expensetype.html')

# Delete Part
def expensedelete(request, id):
    exp = get_object_or_404(Expenses, id=id)
    exp.delete()
    return redirect('expense')

#fueltypeueltypeueltypeueltypeueltype

def fueltype(request):
    fu = Fueltype.objects.all()
    context = {
        'fu':  fu,
    }
    return render(request, 'fueltype.html', context)

# Add New Part
def fueltypeadd(request):
    if request.method == 'POST':
        FUCategory = request.POST.get('FUCategory')
        FUCreatedBy = request.POST.get('FUCreatedBy')
        FUCreatedDate = request.POST.get('FUCreatedDate')
        FUUpdatedBy = request.POST.get('FUUpdatedBy')
        FUUpdatedDate = request.POST.get('FUUpdatedDate')

        fu = Fueltype(
            FUCategory=FUCategory,
            FUCreatedBy=FUCreatedBy,
            FUCreatedDate=FUCreatedDate,
            FUUpdatedBy=FUUpdatedBy,
            FUUpdatedDate=FUUpdatedDate,
        )
        fu.save()
        return redirect('fueltype')

    return render(request, 'fueltype.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def fueltypeedit(request, id):
    fu = get_object_or_404(Fueltype, id=id)
    context = {
        'fu':  fu,
    }
    return render(request, 'editparts.html', context)

# Update Part
def fueltypeupdate(request, id):
    fu = get_object_or_404(Fueltype, id=id)

    if request.method == 'POST':
         fu.FUCategory = request.POST.get('FUCategory')
         fu.FUCreatedBy = request.POST.get('FUCreatedBy')
         fu.FUCreatedDate = request.POST.get('FUCreatedDate')
         fu.FUUpdatedBy = request.POST.get('FUUpdatedBy')
         fu.FUUpdatedDate = request.POST.get('FUUpdatedDate')
         fu.save()
         return redirect('fueltype')

    return render(request, 'fueltype.html')

# Delete Part
def fueltypedelete(request, id):
    fu = get_object_or_404(Fueltype, id=id)
    fu.delete()
    return redirect('fueltype')

# servicesservicesserviceservicservicservic
def service(request):
    ser = ServiceType.objects.all()
    context = {
        'ser': ser,
    }
    return render(request, 'service.html', context)

# Add New Part
def serviceadd(request):
    if request.method == 'POST':
        SERCategory = request.POST.get('SERCategory')
        SERCreatedBy = request.POST.get('SERCreatedBy')
        SERCreatedDate = request.POST.get('SERCreatedDate')
        SERUpdatedBy = request.POST.get('SERUpdatedBy')
        SERUpdatedDate = request.POST.get('SERUpdatedDate')

        ser = ServiceType(
            SERCategory=SERCategory,
            SERCreatedBy=SERCreatedBy,
            SERCreatedDate=SERCreatedDate,
            SERUpdatedBy=SERUpdatedBy,
            SERUpdatedDate=SERUpdatedDate,
        )
        ser.save()
        return redirect('service')

    return render(request, 'service.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def serviceedit(request, id):
    ser = get_object_or_404(ServiceType, id=id)
    context = {
        'ser':  ser,
    }
    return render(request, 'editparts.html', context)

# Update Part
def serviceupdate(request, id):
    ser = get_object_or_404(ServiceType, id=id)

    if request.method == 'POST':
         ser.SERCategory = request.POST.get('SERCategory')
         ser.SERCreatedBy = request.POST.get('SERCreatedBy')
         ser.SERCreatedDate = request.POST.get('SERCreatedDate')
         ser.SERUpdatedBy = request.POST.get('SERUpdatedBy')
         ser.SERUpdatedDate = request.POST.get('SERUpdatedDate')
         ser.save()
         return redirect('service')

    return render(request, 'service.html')

# Delete Part
def servicedelete(request, id):
    ser = get_object_or_404(ServiceType, id=id)
    ser.delete()
    return redirect('service')


# INCEPTION

def inspectionreq(request):                              
    req = Inspection.objects.all()                                 
    context = {
        'req': req,                                                             
    }
    return render(request, 'inspectionreq.html', context)         

def newinspection(request):
    if request.method == 'POST':
         STATInspectioncode = request.POST.get('STATInspectioncode')
         STATInseptiontitle = request.POST.get('STATInseptiontitle')
         STATManager = request.POST.get('STATManager')
         STATInseptiontype = request.POST.get('STATInseptiontype')
         STATStatus = request.POST.get('STATStatus')
         STATVehicle = request.POST.get('STATVehicle')

         req = Inspection(
          STATInspectioncode=STATInspectioncode,
          STATInseptiontitle=STATInseptiontitle,
          STATManager=STATManager,
          STATInseptiontype=STATInseptiontype,
          STATStatus=STATStatus,
          STATVehicle=STATVehicle
         )
         req.save()
         return redirect('newinspection')
    context = {
        'managers': ['John Doe', 'Ravi', 'Sara'],   # Replace with actual queryset or list
        'vehicles': ['Vehicle 1', 'Truck A'],       # Replace with Vehicle model data
        'inspectiontypes': ['Routine', 'Emergency'] # Replace with InspectionType model data
    }
    return render(request, 'newinspection.html', context)          


class InspectionCreateView(CreateView):
    model = InspectionRequest
    form_class = InspectionRequestForm
    template_name = 'inspectioncreate.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        status_value = self.object.status.lower() if self.object.status else ''
        self.object.save()
        if status_value == 'completed':
            return redirect('completed_inspection_list')
        else:
            return redirect('inspection_list')


class InspectionListView(ListView):
    model = InspectionRequest
    template_name = 'list.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        # Show only non-completed inspections
        return InspectionRequest.objects.exclude(status__iexact='completed')


class CompletedInspectionListView(ListView):
    model = InspectionRequest
    template_name = 'complete.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        # Show only completed inspections
        return InspectionRequest.objects.filter(status__iexact='completed')


class InspectionUpdateView(UpdateView):
    model = InspectionRequest
    form_class = InspectionRequestForm
    template_name = 'inspectioncreate.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        status_value = self.object.status.lower() if self.object.status else ''
        self.object.save()
        if status_value == 'completed':
            return redirect('completed_inspection_list')
        else:
            return redirect('inspection_list')


def delete_inspection(request, pk):
    inspection = get_object_or_404(InspectionRequest, pk=pk)
    inspection.delete()
    return redirect('inspection_list')

def inspection_details(request, pk):
    inspection = get_object_or_404(InspectionRequest, pk=pk)
    return render(request, 'details_partial.html', {'inspection': inspection})


def quotation_list(request):
    quotations = Quotation.objects.all()
    return render(request, 'quatlist.html', {'quotations': quotations})

# Create new quotation
from django.shortcuts import redirect, render, get_object_or_404
from fleetapp.models import manage,Owner,Inspects,Expenses,Fueltype,ServiceType,Inspection,Quotation
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render, get_object_or_404
from .models import InspectionRequest
from .forms import InspectionRequestForm

# Dashboard Page
def dashboard(request):
    return render(request, 'dashboard.html')

# List All Parts
def manageparts(request):
    man = manage.objects.all()
    context = {
        'man': man,
    }
    return render(request, 'manageparts.html', context)

# Add New Part
def add(request):
    if request.method == 'POST':
        Category = request.POST.get('Category')
        CreatedBy = request.POST.get('CreatedBy')
        CreatedDate = request.POST.get('CreatedDate')
        UpdatedBy = request.POST.get('UpdatedBy')
        UpdatedDate = request.POST.get('UpdatedDate')

        man = manage(
            Category=Category,
            CreatedBy=CreatedBy,
            CreatedDate=CreatedDate,
            UpdatedBy=UpdatedBy,
            UpdatedDate=UpdatedDate,
        )
        man.save()
        return redirect('manageparts')

    return render(request, 'manageparts.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def edit(request, id):
    man = get_object_or_404(manage, id=id)
    context = {
        'man': man,
    }
    return render(request, 'editparts.html', context)

# Update Part
def update(request, id):
    man = get_object_or_404(manage, id=id)

    if request.method == 'POST':
        man.Category = request.POST.get('Category')
        man.CreatedBy = request.POST.get('CreatedBy')
        man.CreatedDate = request.POST.get('CreatedDate')
        man.UpdatedBy = request.POST.get('UpdatedBy')
        man.UpdatedDate = request.POST.get('UpdatedDate')
        man.save()
        return redirect('manageparts')

    return render(request, 'manageparts.html')

# Delete Part
def delete(request, id):
    man = get_object_or_404(manage, id=id)
    man.delete()
    return redirect('manageparts')

# Vehicle Master Page
def create(request):
   cre = Owner.objects.all()
   context = {
        'cre': cre,
   }
   return render(request, 'create.html', context)

# Add New Part
def createadd(request):
    if request.method == 'POST':
        OwnerName = request.POST.get('OwnerName')
        BrandModels = request.POST.get('BrandModels')
        Location = request.POST.get('Location')
        Created = request.POST.get('Created')
        Date = request.POST.get('Date')

        cre = Owner(
            OwnerName=OwnerName,
            BrandModels=BrandModels,
            Location=Location,
            Created=Created,
            Date=Date,
        )
        cre.save()
        return redirect('create')  # ✅ Updated redirect name

    return render(request, 'create.html')

# Edit Part
def createedit(request, id):
    cre = get_object_or_404(Owner, id=id)
    context = {
        'cre': cre,
    }
    return render(request, 'editparts.html', context)

# Update Part
def createupdate(request, id):
    cre = get_object_or_404(Owner, id=id)

    if request.method == 'POST':
        cre.OwnerName = request.POST.get('OwnerName')
        cre.BrandModels = request.POST.get('BrandModels')
        cre.Location = request.POST.get('Location')
        cre.Created = request.POST.get('Created')
        cre.Date = request.POST.get('Date')
        cre.save()
        return redirect('create')  # ✅ Updated redirect name

    return render(request, 'create.html')

# Delete Part
def createdelete(request, id):
    cre = get_object_or_404(Owner, id=id)
    cre.delete()
    return redirect('create')  # ✅ Updated redirect name

#inspection
def inspection(request):
   inc = Inspects.objects.all()
   context = {
        'inc': inc,
   }
   return render(request, 'inspection.html', context)

# Add New Part
def inspectadd(request):
    if request.method == 'POST':
        INCategory = request.POST.get('INCategory')
        INCreatedBy = request.POST.get('INCreatedBy')
        INCreatedDate = request.POST.get('INCreatedDate')
        INUpdatedBy = request.POST.get('INUpdatedBy')
        INUpdatedDate = request.POST.get('INUpdatedDate')

        inc = Inspects(
            INCategory=INCategory,
            INCreatedBy=INCreatedBy,
            INCreatedDate=INCreatedDate,
            INUpdatedBy=INUpdatedBy,
            INUpdatedDate=INUpdatedDate,
        )
        inc.save()
        return redirect('inspection')

    return render(request, 'inspection.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def inspectedit(request, id):
    inc = get_object_or_404(Inspects, id=id)
    context = {
        'inc': inc,
    }
    return render(request, 'editparts.html', context)

# Update Part
def inspectupdate(request, id):
    inc = get_object_or_404(Inspects, id=id)

    if request.method == 'POST':
        inc.INCategory = request.POST.get('INCategory')
        inc.INCreatedBy = request.POST.get('INCreatedBy')
        inc.INCreatedDate = request.POST.get('INCreatedDate')
        inc.INUpdatedBy = request.POST.get('INUpdatedBy')
        inc.INUpdatedDate = request.POST.get('INUpdatedDate')
        inc.save()
        return redirect('inspection')

    return render(request, 'inspection.html')

# Delete Part
def inspectdelete(request, id):
    inc = get_object_or_404(Inspects, id=id)
    inc.delete()
    return redirect('inspection')

#expenseexpensesexpenses


def expense(request):
    exp = Expenses.objects.all()
    context = {
        'exp': exp,
    }
    return render(request, 'expensetype.html', context)

# Add New Part
def expenseadd(request):
    if request.method == 'POST':
        EXCategory = request.POST.get('EXCategory')
        EXCreatedBy = request.POST.get('EXCreatedBy')
        EXCreatedDate = request.POST.get('EXCreatedDate')
        EXUpdatedBy = request.POST.get('EXUpdatedBy')
        EXUpdatedDate = request.POST.get('EXUpdatedDate')

        exp = Expenses(
            EXCategory=EXCategory,
            EXCreatedBy=EXCreatedBy,
            EXCreatedDate=EXCreatedDate,
            EXUpdatedBy=EXUpdatedBy,
            EXUpdatedDate=EXUpdatedDate,
        )
        exp.save()
        return redirect('expense')

    return render(request, 'expensetype.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def expenseedit(request, id):
    exp = get_object_or_404(Expenses, id=id)
    context = {
        'exp': exp,
    }
    return render(request, 'editparts.html', context)

# Update Part
def expenseupdate(request, id):
    exp = get_object_or_404(Expenses, id=id)

    if request.method == 'POST':
        exp.EXCategory = request.POST.get('EXCategory')
        exp.EXCreatedBy = request.POST.get('EXCreatedBy')
        exp.EXCreatedDate = request.POST.get('EXCreatedDate')
        exp.EXUpdatedBy = request.POST.get('EXUpdatedBy')
        exp.EXUpdatedDate = request.POST.get('EXUpdatedDate')
        exp.save()
        return redirect('expense')

    return render(request, 'expensetype.html')

# Delete Part
def expensedelete(request, id):
    exp = get_object_or_404(Expenses, id=id)
    exp.delete()
    return redirect('expense')

#fueltypeueltypeueltypeueltypeueltype

def fueltype(request):
    fu = Fueltype.objects.all()
    context = {
        'fu':  fu,
    }
    return render(request, 'fueltype.html', context)

# Add New Part
def fueltypeadd(request):
    if request.method == 'POST':
        FUCategory = request.POST.get('FUCategory')
        FUCreatedBy = request.POST.get('FUCreatedBy')
        FUCreatedDate = request.POST.get('FUCreatedDate')
        FUUpdatedBy = request.POST.get('FUUpdatedBy')
        FUUpdatedDate = request.POST.get('FUUpdatedDate')

        fu = Fueltype(
            FUCategory=FUCategory,
            FUCreatedBy=FUCreatedBy,
            FUCreatedDate=FUCreatedDate,
            FUUpdatedBy=FUUpdatedBy,
            FUUpdatedDate=FUUpdatedDate,
        )
        fu.save()
        return redirect('fueltype')

    return render(request, 'fueltype.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def fueltypeedit(request, id):
    fu = get_object_or_404(Fueltype, id=id)
    context = {
        'fu':  fu,
    }
    return render(request, 'editparts.html', context)

# Update Part
def fueltypeupdate(request, id):
    fu = get_object_or_404(Fueltype, id=id)

    if request.method == 'POST':
         fu.FUCategory = request.POST.get('FUCategory')
         fu.FUCreatedBy = request.POST.get('FUCreatedBy')
         fu.FUCreatedDate = request.POST.get('FUCreatedDate')
         fu.FUUpdatedBy = request.POST.get('FUUpdatedBy')
         fu.FUUpdatedDate = request.POST.get('FUUpdatedDate')
         fu.save()
         return redirect('fueltype')

    return render(request, 'fueltype.html')

# Delete Part
def fueltypedelete(request, id):
    fu = get_object_or_404(Fueltype, id=id)
    fu.delete()
    return redirect('fueltype')

# servicesservicesserviceservicservicservic
def service(request):
    ser = ServiceType.objects.all()
    context = {
        'ser': ser,
    }
    return render(request, 'service.html', context)

# Add New Part
def serviceadd(request):
    if request.method == 'POST':
        SERCategory = request.POST.get('SERCategory')
        SERCreatedBy = request.POST.get('SERCreatedBy')
        SERCreatedDate = request.POST.get('SERCreatedDate')
        SERUpdatedBy = request.POST.get('SERUpdatedBy')
        SERUpdatedDate = request.POST.get('SERUpdatedDate')

        ser = ServiceType(
            SERCategory=SERCategory,
            SERCreatedBy=SERCreatedBy,
            SERCreatedDate=SERCreatedDate,
            SERUpdatedBy=SERUpdatedBy,
            SERUpdatedDate=SERUpdatedDate,
        )
        ser.save()
        return redirect('service')

    return render(request, 'service.html')  # optional: redirect instead

# Edit - (This view is usually used to prefill data in modal/form)
def serviceedit(request, id):
    ser = get_object_or_404(ServiceType, id=id)
    context = {
        'ser':  ser,
    }
    return render(request, 'editparts.html', context)

# Update Part
def serviceupdate(request, id):
    ser = get_object_or_404(ServiceType, id=id)

    if request.method == 'POST':
         ser.SERCategory = request.POST.get('SERCategory')
         ser.SERCreatedBy = request.POST.get('SERCreatedBy')
         ser.SERCreatedDate = request.POST.get('SERCreatedDate')
         ser.SERUpdatedBy = request.POST.get('SERUpdatedBy')
         ser.SERUpdatedDate = request.POST.get('SERUpdatedDate')
         ser.save()
         return redirect('service')

    return render(request, 'service.html')

# Delete Part
def servicedelete(request, id):
    ser = get_object_or_404(ServiceType, id=id)
    ser.delete()
    return redirect('service')


# INCEPTION

def inspectionreq(request):                              
    req = Inspection.objects.all()                                 
    context = {
        'req': req,                                                             
    }
    return render(request, 'inspectionreq.html', context)         

def newinspection(request):
    if request.method == 'POST':
         STATInspectioncode = request.POST.get('STATInspectioncode')
         STATInseptiontitle = request.POST.get('STATInseptiontitle')
         STATManager = request.POST.get('STATManager')
         STATInseptiontype = request.POST.get('STATInseptiontype')
         STATStatus = request.POST.get('STATStatus')
         STATVehicle = request.POST.get('STATVehicle')

         req = Inspection(
          STATInspectioncode=STATInspectioncode,
          STATInseptiontitle=STATInseptiontitle,
          STATManager=STATManager,
          STATInseptiontype=STATInseptiontype,
          STATStatus=STATStatus,
          STATVehicle=STATVehicle
         )
         req.save()
         return redirect('newinspection')
    context = {
        'managers': ['John Doe', 'Ravi', 'Sara'],   # Replace with actual queryset or list
        'vehicles': ['Vehicle 1', 'Truck A'],       # Replace with Vehicle model data
        'inspectiontypes': ['Routine', 'Emergency'] # Replace with InspectionType model data
    }
    return render(request, 'newinspection.html', context)          


class InspectionCreateView(CreateView):
    model = InspectionRequest
    form_class = InspectionRequestForm
    template_name = 'inspectioncreate.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        status_value = self.object.status.lower() if self.object.status else ''
        self.object.save()
        if status_value == 'completed':
            return redirect('completed_inspection_list')
        else:
            return redirect('inspection_list')


class InspectionListView(ListView):
    model = InspectionRequest
    template_name = 'list.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        # Show only non-completed inspections
        return InspectionRequest.objects.exclude(status__iexact='completed')


class CompletedInspectionListView(ListView):
    model = InspectionRequest
    template_name = 'complete.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        # Show only completed inspections
        return InspectionRequest.objects.filter(status__iexact='completed')


class InspectionUpdateView(UpdateView):
    model = InspectionRequest
    form_class = InspectionRequestForm
    template_name = 'inspectioncreate.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        status_value = self.object.status.lower() if self.object.status else ''
        self.object.save()
        if status_value == 'completed':
            return redirect('completed_inspection_list')
        else:
            return redirect('inspection_list')


def delete_inspection(request, pk):
    inspection = get_object_or_404(InspectionRequest, pk=pk)
    inspection.delete()
    return redirect('inspection_list')

def inspection_details(request, pk):
    inspection = get_object_or_404(InspectionRequest, pk=pk)
    return render(request, 'details_partial.html', {'inspection': inspection})


def quotation_list(request):
    quotations = Quotation.objects.exclude(status="Approved")
    return render(request, "quatlist.html", {"quotations": quotations})

# Create new quotation
def add_quotation(request):
    if request.method == "POST":
        quotation_no = request.POST.get("quotationNo")
        quotation_date = request.POST.get("quotationDate")
        vehicle_name = request.POST.get("vehicleName")
        plate_no = request.POST.get("plate_no")  # ✅ FIXED
        inspection_code = request.POST.get("inspectionCode")
        status = request.POST.get("status") or "Pending"
        final_amount = request.POST.get("finalAmount")
        created_by = request.POST.get("createdBy")
        created_date = request.POST.get("createdDate")

        Quotation.objects.create(
            quotation_no=quotation_no,
            quotation_date=quotation_date,
            vehicle_name=vehicle_name,
            plate_no=plate_no,  # ✅ Will now have value
            inspection_code=inspection_code,
            status=status,
            final_amount=final_amount,
            created_by=created_by,
            created_date=created_date,
        )
        return redirect("quatlist")

    return render(request, "newquat.html")
def edit_quotation(request, id):
    quotation = get_object_or_404(Quotation, id=id)
    if request.method == "POST":
        quotation.quotation_no = request.POST.get("quotationNo")
        quotation.quotation_date = request.POST.get("quotationDate")
        quotation.vehicle_name = request.POST.get("vehicleName")
        quotation.plate_no = request.POST.get("plate_no")
        quotation.inspection_code = request.POST.get("inspectionCode")
        quotation.status = request.POST.get("status") or "Pending"
        quotation.final_amount = request.POST.get("finalAmount")
        quotation.created_by = request.POST.get("createdBy")
        quotation.save()
        return redirect("quatlist")

    return render(request, "newquat.html", {"quotation": quotation})

def delete_quotation(request, id):
    quotation = get_object_or_404(Quotation, id=id)
    quotation.delete()
    return redirect("quatlist")


def approved_quotations(request):
    quotations = Quotation.objects.filter(status="Approved")
    return render(request, "approvquat.html", {"quotations": quotations})


# ---------- 1. List All Vehicles ----------
def manage_vehicles(request):
    vehicles = Vehicle.objects.all().order_by('-created_date')
    context = {'vehicles': vehicles}
    return render(request, 'vehiclelist.html', context)


# ---------- 2. Vehicle Details ----------
def vehicle_details(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    # Collect images dynamically
    images = [vehicle.image1, vehicle.image2, vehicle.image3, vehicle.image4]
    images = [img for img in images if img]  # remove None

    context = {
        'vehicle': vehicle,
        'images': images
    }
    return render(request, 'vehicledet.html', context)


# ---------- 3. Add Vehicle ----------
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.created_by = request.user.username if request.user.is_authenticated else 'Anonymous'
            vehicle.save()
            return redirect('manage_vehicles')
        else:
            # Pass errors to template for debugging
            context = {'form': form, 'is_edit': False}
            return render(request, 'newvehicle.html', context)
    else:
        form = VehicleForm()
    return render(request, 'newvehicle.html', {'form': form, 'is_edit': False})


# ---------- 4. Edit Vehicle ----------
def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('manage_vehicles')
        else:
            # Pass errors to template
            context = {'form': form, 'is_edit': True}
            return render(request, 'newvehicle.html', context)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'newvehicle.html', {'form': form, 'is_edit': True})


# ---------- 5. Delete Vehicle ----------
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    return redirect('manage_vehicles')


# ---------- 1. Manage Drivers ----------
def manage_drivers(request):
    drivers = Driver.objects.all()

    for d in drivers:
        d.location = DriverLocation.objects.filter(driver=d).first()

    return render(request, "driver.html", {
        "drivers": drivers
    })


# ---------- 2. Add Driver ----------
def add_driver(request):
    if request.method == 'POST':
        Driver.objects.create(
            driver_full_name=request.POST.get('driver_full_name'),
            driver_contact_number=request.POST.get('driver_contact_number'),
            driver_email_address=request.POST.get('driver_email_address'),
            driver_home_address=request.POST.get('driver_home_address'),
            driver_gender=request.POST.get('driver_gender'),
            driver_license_number=request.POST.get('driver_license_number'),
            driver_license_expiry=request.POST.get('driver_license_expiry') or None,
            driver_character_cert_expiry=request.POST.get('driver_character_cert_expiry') or None,
            driver_explosive_cert_expiry=request.POST.get('driver_explosive_cert_expiry') or None,
            driver_training_cert_expiry=request.POST.get('driver_training_cert_expiry') or None,
            driver_emergency_contact_name=request.POST.get('driver_emergency_contact_name'),
            driver_emergency_contact_phone=request.POST.get('driver_emergency_contact_phone'),
            driver_profile_image=request.FILES.get('driver_profile_image')
        )
        return redirect('manage_drivers')
    return render(request, 'add_driver.html')


# ---------- 3. Edit Driver ----------
def edit_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':
        driver.driver_full_name = request.POST.get('driver_full_name')
        driver.driver_contact_number = request.POST.get('driver_contact_number')
        driver.driver_email_address = request.POST.get('driver_email_address')
        driver.driver_home_address = request.POST.get('driver_home_address')
        driver.driver_gender = request.POST.get('driver_gender')
        driver.driver_license_number = request.POST.get('driver_license_number')
        driver.driver_license_expiry = request.POST.get('driver_license_expiry') or None
        driver.driver_character_cert_expiry = request.POST.get('driver_character_cert_expiry') or None
        driver.driver_explosive_cert_expiry = request.POST.get('driver_explosive_cert_expiry') or None
        driver.driver_training_cert_expiry = request.POST.get('driver_training_cert_expiry') or None
        driver.driver_emergency_contact_name = request.POST.get('driver_emergency_contact_name')
        driver.driver_emergency_contact_phone = request.POST.get('driver_emergency_contact_phone')
        if request.FILES.get('driver_profile_image'):
            driver.driver_profile_image = request.FILES.get('driver_profile_image')
        driver.save()
        return redirect('manage_drivers')
    return render(request, 'edit_driver.html', {'driver': driver})


# ---------- 4. Delete Driver ----------
def delete_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == 'POST':
        driver.delete()
        return redirect('manage_drivers')
    return render(request, 'delete_driver.html', {'driver': driver})



#------------------ Show all reviews ------------------
def driver_reviews(request):
    reviews = DriverReview.objects.all().order_by("-id")  # newest first
    return render(request, "driverreviwe.html", {"reviews": reviews})


# ------------------ Add New Review ------------------
def add_review(request):
    if request.method == "POST":
        driver_name = request.POST.get("driver_name")
        driver_mobile = request.POST.get("driver_mobile")
        rating = int(request.POST.get("rating")) if request.POST.get("rating") else 0
        title = request.POST.get("title")
        description = request.POST.get("description")
       
        recreated_by = request.POST.get("recreated_by")  # ✅ manual entry

        DriverReview.objects.create(
            driver_name=driver_name,
            driver_mobile=driver_mobile,
            rating=rating,
            title=title,
            description=description,
            recreated_by=recreated_by,
            
        )
        return redirect("driver_reviews")

    return redirect("driver_reviews")


# ------------------ Edit Review ------------------
def edit_review(request, review_id):
    review = get_object_or_404(DriverReview, id=review_id)

    if request.method == "POST":
        review.driver_name = request.POST.get("driver_name")
        review.driver_mobile = request.POST.get("driver_mobile")
        review.rating = int(request.POST.get("rating")) if request.POST.get("rating") else review.rating
        review.title = request.POST.get("title")
        review.description = request.POST.get("description")
        review.recreated_by = request.POST.get("recreated_by")  # ✅ manual update
        
        review.save()
        return redirect("driver_reviews")

    return redirect("driver_reviews")


# ------------------ Delete Review ------------------
def delete_review(request, review_id):
    review = get_object_or_404(DriverReview, id=review_id)
    review.delete()
    return redirect("driver_reviews")

# ---------- 1. List All Other Expenses ----------
def manage_other_expenses(request):
    # Get all expenses from database, newest first
    other_expenses = OtherExpenseRecord.objects.all().order_by('-exp_created_timestamp')

    context = {
        'other_expenses': other_expenses
    }
    return render(request, 'otherexpenses.html', context)


# ---------- 2. Add Other Expense ----------
def add_other_expense(request):
    if request.method == 'POST':
        OtherExpenseRecord.objects.create(
            exp_reference_no = request.POST.get('exp_reference_no'),
            exp_date_recorded = request.POST.get('exp_date_recorded'),
            exp_vehicle_tag = request.POST.get('exp_vehicle_tag'),
            exp_category_label = request.POST.get('exp_category_label'),
            exp_description_title = request.POST.get('exp_description_title'),
            exp_total_value = request.POST.get('exp_total_value') or 0,
            exp_odometer_reading = request.POST.get('exp_odometer_reading') or 0,
            exp_bill_number = request.POST.get('exp_bill_number'),
            exp_bill_attachment = request.FILES.get('exp_bill_attachment'),
            exp_driver_ref = request.POST.get('exp_driver_ref'),
            exp_created_person = request.POST.get('exp_created_person'),
        )
        return redirect('manage_other_expenses')


# ---------- 3. Edit Other Expense ----------
def edit_other_expense(request, pk):
    expense = get_object_or_404(OtherExpenseRecord, pk=pk)

    if request.method == 'POST':
        expense.exp_reference_no = request.POST.get('exp_reference_no')
        
        # Handle empty date properly
        exp_date_recorded = request.POST.get('exp_date_recorded')
        if exp_date_recorded:
            expense.exp_date_recorded = exp_date_recorded
        else:
            expense.exp_date_recorded = None  # Avoid invalid date format

        expense.exp_vehicle_tag = request.POST.get('exp_vehicle_tag')
        expense.exp_category_label = request.POST.get('exp_category_label')
        expense.exp_description_title = request.POST.get('exp_description_title')
        expense.exp_total_value = request.POST.get('exp_total_value') or 0
        expense.exp_odometer_reading = request.POST.get('exp_odometer_reading') or 0
        expense.exp_bill_number = request.POST.get('exp_bill_number')

        # Update file only if a new file is uploaded
        if request.FILES.get('exp_bill_attachment'):
            expense.exp_bill_attachment = request.FILES.get('exp_bill_attachment')

        expense.exp_driver_ref = request.POST.get('exp_driver_ref')
        expense.exp_modified_person = request.POST.get('exp_modified_person')
        expense.save()
        return redirect('manage_other_expenses')

    context = {'expense': expense}
    return render(request, 'edit_other_expense.html', context)


# ---------- 4. Delete Other Expense ----------
def delete_other_expense(request, pk):
    expense = get_object_or_404(OtherExpenseRecord, pk=pk)
    if request.method == 'POST':
        expense.delete()
        return redirect('manage_other_expenses')
    

# ---------------------------------------------------------
# 🔹 LIST ALL FUEL REPORTS
# ---------------------------------------------------------
def fuel_report_list(request):
    reports = FuelReport.objects.all().order_by("-fueling_date")
    return render(request, "fuelreport.html", {"reports": reports})


# ---------------------------------------------------------
# 🔹 ADD OR UPDATE FUELING
# ---------------------------------------------------------
def add_or_update_fueling(request, pk=None):
    vehicles = Vehicle.objects.all()
    drivers = Driver.objects.all()

    fueling = get_object_or_404(FuelReport, pk=pk) if pk else None

    if request.method == "POST":
        vehicle_id = request.POST.get("fuel_vehicle")
        driver_id = request.POST.get("fuel_driver")
        fuel_type_id = request.POST.get("fuel_type")
        fuel_station = request.POST.get("fuel_station_name")
        remarks = request.POST.get("fuel_remarks")
        created_by = request.POST.get("created_by_user", "Admin")  # Default to Admin
        fuel_invoice_number = request.POST.get("fuel_invoice_number")

        # Related objects
        vehicle_obj = Vehicle.objects.filter(id=vehicle_id).first() if vehicle_id else None
        driver_obj = Driver.objects.filter(id=driver_id).first() if driver_id else None

        # Map numeric fuel_type IDs to string
        fuel_type_map = {'1': 'Petrol', '2': 'Diesel', '3': 'CNG'}
        fuel_type_value = fuel_type_map.get(fuel_type_id, 'Petrol')

        # Convert numeric fields safely
        def to_decimal(value):
            try:
                return Decimal(value)
            except:
                return Decimal("0")

        fuel_quantity = to_decimal(request.POST.get("fuel_quantity_liters", "0"))
        fuel_price = to_decimal(request.POST.get("fuel_price_per_liter", "0"))
        fuel_odometer = to_decimal(request.POST.get("fuel_odometer_reading", "0"))
        total_amount = fuel_quantity * fuel_price

        if fueling:
            # Update existing record
            fueling.fuel_vehicle = vehicle_obj
            fueling.fuel_driver = driver_obj
            fueling.fuel_type = fuel_type_value
            fueling.fuel_station_name = fuel_station
            fueling.fuel_quantity_liters = fuel_quantity
            fueling.fuel_price_per_liter = fuel_price
            fueling.fuel_total_amount = total_amount
            fueling.fuel_odometer_reading = fuel_odometer
            fueling.fuel_invoice_number = fuel_invoice_number
            fueling.fuel_remarks = remarks
            fueling.updated_by_user = created_by
            fueling.save()
        else:
            # Create new record
            FuelReport.objects.create(
                fuel_vehicle=vehicle_obj,
                fuel_driver=driver_obj,
                fuel_type=fuel_type_value,
                fuel_station_name=fuel_station,
                fuel_quantity_liters=fuel_quantity,
                fuel_price_per_liter=fuel_price,
                fuel_total_amount=total_amount,
                fuel_odometer_reading=fuel_odometer,
                fuel_invoice_number=fuel_invoice_number,
                fuel_remarks=remarks,
                created_by_user=created_by
            )

        return redirect("fuel_report_list")

    return render(request, "updatefuel.html", {
        "fueling": fueling,
        "vehicles": vehicles,
        "drivers": drivers,
    })


# ---------------------------------------------------------
# 🔹 DELETE FUELING RECORD
# ---------------------------------------------------------
def delete_fueling(request, pk):
    fueling = get_object_or_404(FuelReport, pk=pk)
    fueling.delete()
    return redirect("fuel_report_list")

# ---------- 1. Manage / List All Tyre Replacements ----------
def manage_tyre(request):
    tyre_replacements = TyreReplacementRecord.objects.all().order_by('-tyre_created_timestamp')
    context = {'tyre_replacements': tyre_replacements}
    return render(request, 'tyrereplacement.html', context)


# ---------- 2. Add Tyre Replacement ----------
def add_tyre(request):
    if request.method == 'POST':
        TyreReplacementRecord.objects.create(
            tyre_replacement_date=request.POST.get('tyre_replacement_date'),
            tyre_vehicle_name=request.POST.get('tyre_vehicle_name'),
            tyre_brand_name=request.POST.get('tyre_brand_name'),
            tyre_size_label=request.POST.get('tyre_size_label'),
            tyre_unique_number=request.POST.get('tyre_unique_number'),
            tyre_type_category=request.POST.get('tyre_type_category'),
            tyre_replace_reason_text=request.POST.get('tyre_replace_reason_text'),
            tyre_odometer_reading_value=request.POST.get('tyre_odometer_reading_value'),
            tyre_driver_name=request.POST.get('tyre_driver_name'),
            tyre_description_details=request.POST.get('tyre_description_details'),
            tyre_bill_number=request.POST.get('tyre_bill_number'),
            tyre_bill_document_file=request.FILES.get('tyre_bill_document_file'),
        )
        return redirect('manage_tyre')

    return render(request, 'tyrereplacement_add.html')


# ---------- 3. Edit Tyre Replacement ----------
def edit_tyre(request, pk):
    tyre = get_object_or_404(TyreReplacementRecord, pk=pk)

    if request.method == 'POST':
        tyre.tyre_replacement_date = request.POST.get('tyre_replacement_date')
        tyre.vehicle = request.POST.get('vehicle')
        tyre.brand_name = request.POST.get('brand_name')
        tyre.tyre_size = request.POST.get('tyre_size')
        tyre.tyre_number = request.POST.get('tyre_number')
        tyre.tyre_type = request.POST.get('tyre_type')
        tyre.replace_reason = request.POST.get('replace_reason')
        tyre.odometer = request.POST.get('odometer') or 0
        tyre.driver_name = request.POST.get('driver_name')
        tyre.description = request.POST.get('description')
        tyre.bill_no = request.POST.get('bill_no')

        # Update bill document only if new file uploaded
        if request.FILES.get('bill_document'):
            tyre.bill_document = request.FILES.get('bill_document')

        tyre.save()
        return redirect('manage_tyre')

    context = {'tyre': tyre}
    return render(request, 'tyrereplacement.html', context)


# ---------- 4. Delete Tyre Replacement ----------
def delete_tyre(request, pk):
    tyre = get_object_or_404(TyreReplacementRecord, pk=pk)
    if request.method == 'POST':
        tyre.delete()
        return redirect('manage_tyre')
    return redirect('manage_tyre')


# List all items
class ManageItemsView(ListView):
    model = Item
    template_name = 'itemslist.html'  # Template for listing items
    context_object_name = 'items'
    ordering = ['-CreatedDate']


# Add new item
class AddItemView(CreateView):
    model = Item
    template_name = 'items.html'  # Template for add form
    fields = [
        'PART_PartNo', 'PART_Color', 'PART_Category', 'PART_Status',
        'PART_Name', 'PART_Description', 'PART_Unit', 'PART_Remark',
        'PART_Price', 'PART_Image1', 'PART_Image2'
    ]
    success_url = reverse_lazy('manageitems')

    def form_valid(self, form):
        return super().form_valid(form)


# Edit existing item
class EditItemView(UpdateView):
    model = Item
    template_name = 'items.html'  # Same form used for editing
    fields = [
        'PART_PartNo', 'PART_Color', 'PART_Category', 'PART_Status',
        'PART_Name', 'PART_Description', 'PART_Unit', 'PART_Remark',
        'PART_Price', 'PART_Image1', 'PART_Image2'
    ]
    success_url = reverse_lazy('manageitems')

    def form_valid(self, form):
        return super().form_valid(form)


# Delete an item
class DeleteItemView(DeleteView):
    model = Item
    template_name = 'confirm_delete.html'  # Optional delete confirmation
    success_url = reverse_lazy('manageitems')

#---------------------------------------------------------
# 🔹 LIST ALL SERVICES
# ---------------------------------------------------------
def service_list(request):
    services = Service.objects.all().order_by('-id')
    return render(request, 'allservices.html', {'services': services})


# ---------------------------------------------------------
# 🔹 CREATE NEW SERVICE
# ---------------------------------------------------------
@transaction.atomic
def service_create(request):
    if request.method == 'POST':
        data = request.POST

        # Create the Service object
        service = Service.objects.create(
            quotation_number=data.get('quotation_number'),
            service_type=data.get('service_type'),
            last_kilometer=data.get('last_kilometer') or None,
            vehicle=data.get('vehicle'),
            service_title=data.get('service_title'),
            next_service_kilometer=data.get('next_service_kilometer') or None,
            service_date=data.get('service_date'),
            requested_by=data.get('requested_by'),
            status=data.get('status'),
            next_service_date=data.get('next_service_date') or None,
            service_center_name=data.get('service_center_name'),
            service_assigned_to=data.get('service_assigned_to'),
            priority=data.get('priority'),
            labor_amount=data.get('labor_amount') or 0,
            service_charge_amount=data.get('service_charge_amount') or 0,
            other_amount=data.get('other_amount') or 0,
            total_items_amount=data.get('total_items_amount') or 0,
            total_third_party_amount=data.get('total_third_party_amount') or 0,
            total_amount=data.get('total_amount') or 0,
            due_amount=data.get('due_amount') or 0,
        )

        # Create ServiceEntry records safely
        part_categories = request.POST.getlist('entry_part_category[]')
        part_names = request.POST.getlist('entry_part_name[]')
        units = request.POST.getlist('entry_unit[]')
        quantities = request.POST.getlist('entry_quantity[]')
        prices = request.POST.getlist('entry_price[]')

        for i in range(len(part_names)):
            if part_names[i]:  # skip empty rows
                ServiceEntry.objects.create(
                    service=service,
                    entry_part_category=part_categories[i],
                    entry_part_name=part_names[i],
                    entry_unit=units[i] or '',
                    entry_quantity=int(quantities[i] or 0),
                    entry_price=float(prices[i] or 0),
                )

        return redirect('service_list')

    return render(request, 'newservice.html')


# ---------------------------------------------------------
# 🔹 EDIT EXISTING SERVICE
# ---------------------------------------------------------
@transaction.atomic
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        data = request.POST

        # Update fields
        for field in [
            'quotation_number', 'service_type', 'last_kilometer', 'vehicle', 'service_title',
            'next_service_kilometer', 'service_date', 'requested_by', 'status',
            'next_service_date', 'service_center_name', 'service_assigned_to',
            'priority', 'labor_amount', 'service_charge_amount', 'other_amount',
            'total_items_amount', 'total_third_party_amount', 'total_amount', 'due_amount'
        ]:
            value = data.get(field)
            if field in ['labor_amount','service_charge_amount','other_amount','total_items_amount','total_third_party_amount','total_amount','due_amount']:
                value = float(value or 0)
            elif field in ['last_kilometer','next_service_kilometer']:
                value = int(value) if value else None
            setattr(service, field, value)

        service.save()

        # Delete old entries and recreate
        service.entries.all().delete()

        part_categories = request.POST.getlist('entry_part_category[]')
        part_names = request.POST.getlist('entry_part_name[]')
        units = request.POST.getlist('entry_unit[]')
        quantities = request.POST.getlist('entry_quantity[]')
        prices = request.POST.getlist('entry_price[]')

        for i in range(len(part_names)):
            if part_names[i]:
                ServiceEntry.objects.create(
                    service=service,
                    entry_part_category=part_categories[i],
                    entry_part_name=part_names[i],
                    entry_unit=units[i] or '',
                    entry_quantity=int(quantities[i] or 0),
                    entry_price=float(prices[i] or 0),
                )

        return redirect('service_list')

    return render(request, 'newservice.html', {
        'service': service,
        'entries': service.entries.all(),
    })


# ---------------------------------------------------------
# 🔹 DELETE SERVICE
# ---------------------------------------------------------

def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    return redirect('service_list')


# List all vendors
def vendor_list(request):
    vendors = Vendor.objects.all().order_by('-vendorCreatedDate')
    return render(request, 'vendorlist.html', {'vendors': vendors})

# Add or update vendor
def vendor_add_update(request, vendor_id=None):
    if vendor_id:
        vendor = get_object_or_404(Vendor, pk=vendor_id)
    else:
        vendor = None

    if request.method == 'POST':
        name = request.POST.get('vendorName')
        company = request.POST.get('vendorCompanyName')
        gender = request.POST.get('vendorGender')
        email = request.POST.get('vendorEmail')
        mobile = request.POST.get('vendorMobileNo')
        landline = request.POST.get('vendorLandlineNo')
        address = request.POST.get('vendorAddress')
        country = request.POST.get('vendorCountry')
        state = request.POST.get('vendorState')
        city = request.POST.get('vendorCity')
        remark = request.POST.get('vendorRemark')
        image = request.FILES.get('vendorProfileImage')

        if vendor:
            # Update existing
            vendor.vendorName = name
            vendor.vendorCompanyName = company
            vendor.vendorGender = gender
            vendor.vendorEmail = email
            vendor.vendorMobileNo = mobile
            vendor.vendorLandlineNo = landline
            vendor.vendorAddress = address
            vendor.vendorCountry = country
            vendor.vendorState = state
            vendor.vendorCity = city
            vendor.vendorRemark = remark
            if image:
                vendor.vendorProfileImage = image
            vendor.vendorUpdatedDate = timezone.now()
            vendor.save()
        else:
            # Create new
            Vendor.objects.create(
                vendorName=name,
                vendorCompanyName=company,
                vendorGender=gender,
                vendorEmail=email,
                vendorMobileNo=mobile,
                vendorLandlineNo=landline,
                vendorAddress=address,
                vendorCountry=country,
                vendorState=state,
                vendorCity=city,
                vendorRemark=remark,
                vendorProfileImage=image,
                vendorCreatedDate=timezone.now()
            )

        return redirect('vendor_list')

    return render(request, 'vendor.html', {'vendor': vendor})

def vendor_delete(request, vendor_id):
    vendor = get_object_or_404(Vendor, pk=vendor_id)
    vendor.delete()
    return redirect('vendor_list')  

def create_purchase(request):
    if request.method == 'POST':
        purchase_title = request.POST.get('purchase_title')
        purchase_manager = request.POST.get('purchase_manager')
        item_type = request.POST.get('item_type')
        purchase_status = request.POST.get('purchase_status')
        vendor = request.POST.get('vendor')
        quantity = request.POST.get('quantity')
        description = request.POST.get('description')

        PurchaseItem.objects.create(
            purchase_title=purchase_title,
            purchase_manager=purchase_manager,
            item_type=item_type,
            purchase_status=purchase_status,
            vendor=vendor,
            quantity=quantity,
            description=description
        )
        messages.success(request, 'Purchase item added successfully!')
        return redirect('purchase_list')

    return render(request, 'purchase.html')


# ------------------------------
# LIST PURCHASE ITEMS
# ------------------------------
def purchase_list(request):
    purchases = PurchaseItem.objects.all().order_by('-created_at')
    return render(request, 'purchaselist.html', {'purchases': purchases})


# EDIT PURCHASE ITEM (same page)
# ------------------------------
def edit_purchase(request, pk):
    purchase = get_object_or_404(PurchaseItem, pk=pk)

    if request.method == 'POST':
        purchase.purchase_title = request.POST.get('purchase_title')
        purchase.purchase_manager = request.POST.get('purchase_manager')
        purchase.item_type = request.POST.get('item_type')
        purchase.purchase_status = request.POST.get('purchase_status')
        purchase.vendor = request.POST.get('vendor')
        purchase.quantity = request.POST.get('quantity')
        purchase.description = request.POST.get('description')
        purchase.save()
        messages.success(request, 'Purchase item updated successfully!')
        return redirect('purchase_list')

    return redirect('purchase_list')


# ------------------------------
# DELETE PURCHASE ITEM (inline)
# ------------------------------
def delete_purchase(request, pk):
    purchase = get_object_or_404(PurchaseItem, pk=pk)
    purchase.delete()
    messages.success(request, 'Purchase item deleted successfully!')
    return redirect('purchase_list')

def typewise(request):
    selected_type = request.GET.get('service_type')  # e.g. 'routine'
    services = Service.objects.all().order_by('-id')

    # Filter only if a specific type selected
    if selected_type:
        services = services.filter(service_type=selected_type)

    # Get unique service types for dropdown
    service_types = Service.objects.values_list('service_type', flat=True).distinct()

    return render(request, 'typewise.html', {
        'services': services,
        'service_types': service_types,
        'selected_type': selected_type,
    })

def manage_insurances(request):
    vehicles = Vehicle.objects.all().order_by('insurance_expiry')
    today = date.today()                        # ← add this
    context = {
        'vehicles': vehicles,
        'today': today,                         # ← pass to template
    }
    return render(request, 'insurance.html', context)

def manage_registrations(request):
    vehicles = Vehicle.objects.all().order_by('reg_to')   # Sort by registration expiry
    today = date.today()                                  # Current date
    context = {
        'vehicles': vehicles,
        'today': today,
    }
    return render(request, 'registration.html', context)

def manage_roadtax(request):
    vehicles = Vehicle.objects.all().order_by('roadtax_last')
    today = date.today()
    context = {
        'vehicles': vehicles,
        'today': today,
    }
    return render(request, 'roadtax.html', context)

def manage_puc(request):
    vehicles = Vehicle.objects.all().order_by('puc_last')
    today = date.today()
    context = {
        'vehicles': vehicles,
        'today': today,
    }
    return render(request, 'puc.html', context)

def manage_permit(request):
    vehicles = Vehicle.objects.all().order_by('permit_last')
    today = date.today()
    context = {
        'vehicles': vehicles,
        'today': today,
    }
    return render(request, 'permit.html', context)

def manage_fitness(request):
    vehicles = Vehicle.objects.all().order_by('fitness_end')
    today = date.today()
    context = {
        'vehicles': vehicles,
        'today': today,
    }
    return render(request, 'fitness.html', context)

def mileage(request):
   return render(request, 'mileage.html')


@api_view(['POST'])
def check_driver_code(request):
    driver_code = request.data.get('driver_code')

    try:
        driver = Driver.objects.get(driver_code=driver_code)

        return Response({
            "status": "success",
            "driver_id": driver.id,
            "driver_code": driver.driver_code,
            "driver_name": driver.driver_full_name
        })

    except Driver.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Invalid driver code"
        })
    
@api_view(['POST'])
def driver_login_jwt(request):
    driver_code = request.data.get('driver_code')

    try:
        driver = Driver.objects.get(driver_code=driver_code)

        # Create token
        refresh = RefreshToken()
        refresh['driver_id'] = driver.id
        refresh['driver_code'] = driver.driver_code

        return Response({
            "access": str(refresh.access_token),
            "driver_name": driver.driver_full_name
        })

    except Driver.DoesNotExist:
        return Response({"error": "Invalid driver code"})

# fleetapp/views.py

from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken

@api_view(['GET'])
def driver_profile(request):

    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return Response({"error": "No token"}, status=401)

        token = auth_header.split()[1]

        decoded = AccessToken(token)
        driver_id = decoded['driver_id']

        driver = Driver.objects.get(id=driver_id)

        return Response({
            "name": driver.driver_full_name,
            "code": driver.driver_code,
            "image": request.build_absolute_uri(driver.driver_profile_image.url)
                     if driver.driver_profile_image else ""
        })

    except Exception as e:
        print("ERROR:", e)
        return Response({"error": "Invalid token"}, status=401)
    
import json
from django.http import JsonResponse
from .models import Driver, DriverLocation
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            driver_id = data.get("driver_id")
            lat = data.get("latitude")
            lng = data.get("longitude")
            status = data.get("status", "OFF_DUTY")

            driver = Driver.objects.get(id=driver_id)

            DriverLocation.objects.update_or_create(
                driver=driver,
                defaults={
                    "latitude": lat,
                    "longitude": lng,
                    "status": status
                }
            )

            return JsonResponse({"status": "updated"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)