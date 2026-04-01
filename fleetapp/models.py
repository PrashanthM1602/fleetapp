from django.db import models
from django.utils import timezone
import uuid

class manage(models.Model):
    Category=models.CharField(max_length=100)
    CreatedBy=models.CharField(max_length=50)
    CreatedDate=models.DateTimeField(auto_now_add=True)
    UpdatedBy=models.CharField(max_length=50, null=True, blank=True)
    UpdatedDate=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Category

class Owner(models.Model):
    OwnerName = models.CharField(max_length=100)
    BrandModels = models.CharField(max_length=100)
    Location = models.CharField(max_length=100)
    Created = models.CharField(max_length=50)
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.OwnerName
    
class Inspects(models.Model):
    INCategory=models.CharField(max_length=100)
    INCreatedBy=models.CharField(max_length=50)
    INCreatedDate=models.DateTimeField(auto_now_add=True)
    INUpdatedBy=models.CharField(max_length=50, null=True, blank=True)
    INUpdatedDate=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Inspects
    

class Expenses(models.Model):
    EXCategory=models.CharField(max_length=100)
    EXCreatedBy=models.CharField(max_length=50)
    EXCreatedDate=models.DateTimeField(auto_now_add=True)
    EXUpdatedBy=models.CharField(max_length=50, null=True, blank=True)
    EXUpdatedDate=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Expenses
    
class Fueltype(models.Model):
    FUCategory=models.CharField(max_length=100)
    FUCreatedBy=models.CharField(max_length=50)
    FUCreatedDate=models.DateTimeField(auto_now_add=True)
    FUUpdatedBy=models.CharField(max_length=50, null=True, blank=True)
    FUUpdatedDate=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.FUCategory
    
class ServiceType(models.Model):
    SERCategory=models.CharField(max_length=100)
    SERCreatedBy=models.CharField(max_length=50)
    SERCreatedDate=models.DateTimeField(auto_now_add=True)
    SERUpdatedBy=models.CharField(max_length=50, null=True, blank=True)
    SERUpdatedDate=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.SERCategory
    
class Inspection(models.Model):
    STATCreatedDate=models.DateTimeField(auto_now=True)
    STATInspectionCode=models.IntegerField()
    STATInseptiontitle =models.CharField(max_length=50)
    STATManager = models.CharField(max_length=50)
    STATInseptiontype= models.CharField(max_length=50)
    STATStatus= models.CharField(max_length=50)
    STATVehicle = models.CharField(max_length=20)  
    def __str__(self):
        return self.STATNo

class InspectionType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20)

    def __str__(self):
        return self.plate_number

class InspectionRequest(models.Model):
    inspection_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    title = models.CharField(max_length=200)
    manager = models.CharField(max_length=100, choices=[
        ("Select Manager","Select Manager"),
        ("John Smith","John Smith"),
        ("Aisha Khan","Aisha Khan"),
        ("Carlos Ramirez","Carlos Ramirez"),
        ("Emily Zhang","Emily Zhang"),
        ("David Osei","David Osei"),
    ])
    inspection_type = models.CharField(max_length=100,choices=[
            ("Pre-Purchase Inspection", "Pre-Purchase Inspection"),
            ("Annual Inspection", "Annual Inspection"),
            ("Fleet Inspection","Fleet Inspection"),
            ("Accident Inspection","Accident Inspection"),
            ("Tire Inspection","Tire Inspection"),
            ("Brake Inspection","Brake Inspection"),
            ("Vehicle Exterior Inspection","Vehicle Exterior Inspection"),
        ]
    )
    status = models.CharField(max_length=50, choices=[
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Rejected", "Rejected"),
        ("Reinspection Required", "Reinspection Required"),
    ], default="Completed")
    vehicle = models.CharField(max_length=100,choices=[
            ("Xylo", "Xylo"),
            ("Scorpio", "Scorpio"),
            ("Bolero","Bolero"),
        ]
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
     if not self.inspection_code:
        self.inspection_code = f"INSP-{uuid.uuid4().hex[:6].upper()}"
     super().save(*args, **kwargs)

# quatation
 
class Quotation(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    quotation_no = models.CharField(max_length=20, unique=True, blank=True, null=True)
    quotation_date = models.DateField()
    vehicle_name = models.CharField(max_length=100)
    plate_no = models.CharField(
        max_length=100,
        choices=[
            ("Engine and Mechanical", "Engine and Mechanical"),
            ("Electrical and Lighting", "Electrical and Lighting"),
            ("Suspension and steering", "Suspension and steering"),
            ("Braking System", "Braking System"),
        ]
    )
    inspection_code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.quotation_no:
            self.quotation_no = f"QT-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.quotation_no or "Quotation"

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ("Sedans", "Sedans"),
        ("SUV", "SUV"),
        ("Truck", "Truck"),
    ]

    FUEL_TYPES = [
        ("Diesel", "Diesel"),
        ("Petrol", "Petrol"),
        ("Electric", "Electric"),
    ]

    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPES, null=True, blank=True)
    vehicle_name = models.CharField(max_length=100, null=True, blank=True)
    fuel_type = models.CharField(max_length=50, choices=FUEL_TYPES, null=True, blank=True)
    make = models.CharField(max_length=100, null=True, blank=True)
    make_year = models.PositiveIntegerField(null=True, blank=True)
    manufacture_year = models.PositiveIntegerField(null=True, blank=True)
    engine_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    chassis_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True)
    # --- Step 2: Advance Details ---
    OWNERSHIP_CHOICES = [
        ("Greenline Logistics", "Greenline Logistics"),
        ("Company Fleet", "Company Fleet"),
    ]

    LOCATION_CHOICES = [
        ("Canada", "Canada"),
        ("USA", "USA"),
    ]

    ownership = models.CharField(max_length=100, choices=OWNERSHIP_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    model_adv = models.CharField("Model", max_length=100, null=True, blank=True)
    tyre_size = models.CharField(max_length=50, null=True, blank=True)
    tons = models.CharField(max_length=20, null=True, blank=True)
    odometer = models.PositiveIntegerField(null=True, blank=True)

    # --- Step 3: Reminder Dates ---
    insurance_no = models.CharField(max_length=50, null=True, blank=True)
    insurance_start = models.DateField(null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    roadtax_last = models.DateField(null=True, blank=True)
    permit_last = models.DateField(null=True, blank=True)
    puc_last = models.DateField(null=True, blank=True)
    reg_from = models.DateField("Registration From", null=True, blank=True)
    reg_to = models.DateField("Registration To", null=True, blank=True)
    fitness_end = models.DateField("Fitness Certificate End", null=True, blank=True)

     # --- Step 4: Images ---
    image1 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    image4 = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)



    def __str__(self):
        return f"{self.vehicle_name or 'Unnamed'} ({self.plate_number})"

    
class Driver(models.Model):
    # --- Basic Details ---
    driver_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    driver_full_name = models.CharField(max_length=100)
    driver_contact_number = models.CharField(max_length=15)
    driver_email_address = models.EmailField(max_length=100, blank=True, null=True)
    driver_home_address = models.TextField(blank=True, null=True)
    driver_gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        blank=True,
        null=True
    )

    # --- License & Certificate Info ---
    driver_license_number = models.CharField(max_length=50)
    driver_license_expiry = models.DateField(blank=True, null=True)
    driver_character_cert_expiry = models.DateField(blank=True, null=True)
    driver_explosive_cert_expiry = models.DateField(blank=True, null=True)
    driver_training_cert_expiry = models.DateField(blank=True, null=True)

    # --- Emergency Contact ---
    driver_emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    driver_emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)

    # --- Meta Information ---
    driver_created_by = models.CharField(max_length=50, default='system')
    driver_created_on = models.DateTimeField(default=timezone.now)
    driver_updated_by = models.CharField(max_length=50, blank=True, null=True)
    driver_updated_on = models.DateTimeField(auto_now=True)

    # --- Driver Image ---
    driver_profile_image = models.ImageField(upload_to='driver_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.driver_full_name} - {self.driver_license_number}"
    
    def save(self, *args, **kwargs):
     if not self.driver_code:
        last_driver = Driver.objects.order_by('-id').first()
        if last_driver and last_driver.driver_code:
            last_number = int(last_driver.driver_code.split('_')[1])
            new_number = last_number + 1
        else:
            new_number = 1

        self.driver_code = f"fleet_{str(new_number).zfill(4)}"

     super().save(*args, **kwargs)

class DriverLocation(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20,choices=[ ('ON_DUTY', 'On Duty'), ('OFF_DUTY', 'Off Duty') ], default='OFF_DUTY')

    def __str__(self):
        return f"{self.driver.driver_full_name} - {self.latitude},{self.longitude}"
    
    
class DriverReview(models.Model):
    driver_name = models.CharField(max_length=100)
    driver_mobile = models.CharField(max_length=15)
    rating = models.IntegerField()
    title = models.CharField(max_length=150)
    description = models.TextField()
    recreated_by = models.CharField(max_length=100)   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.driver_name} - {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Driver Review"
        verbose_name_plural = "Driver Reviews"

class OtherExpenseRecord(models.Model):
    exp_reference_no = models.CharField(max_length=50)  # Unique identifier
    exp_date_recorded = models.DateField(default=timezone.now,null=True)
    exp_vehicle_label = models.CharField(max_length=100)
    exp_vehicle_tag = models.CharField(max_length=100, null=True, blank=True)
    exp_category_label = models.CharField(max_length=100)
    exp_description_title = models.CharField(max_length=200)
    exp_total_value = models.DecimalField(max_digits=10, decimal_places=2)
    exp_odometer_reading = models.PositiveIntegerField(null=True, blank=True)
    exp_bill_number = models.CharField(max_length=100, unique=False)
    exp_bill_attachment = models.FileField(upload_to='expense_docs/', null=True, blank=True)
    exp_driver_ref = models.CharField(max_length=100)
    exp_created_person = models.CharField(max_length=100)
    exp_created_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    exp_modified_person = models.CharField(max_length=100, null=True, blank=True)
    exp_modified_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.exp_description_title} - {self.exp_reference_no}"
    
class FuelReport(models.Model):
    # Fuel Type Choices
    FUEL_TYPE_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('CNG', 'CNG'),
    ]

    fuel_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    fueling_date = models.DateField(default=timezone.now)

    fuel_vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    fuel_driver = models.ForeignKey(
        'Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fuel_reports'
    )
    fuel_type = models.CharField(
        max_length=10,
        choices=FUEL_TYPE_CHOICES,
        default='Petrol',  # default for new rows and migrations
        null=False,
        blank=False
    )

    fuel_station_name = models.CharField(max_length=150, blank=True, null=True)
    fuel_price_per_liter = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fuel_quantity_liters = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fuel_total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fuel_odometer_reading = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fuel_invoice_number = models.CharField(max_length=100, blank=True, null=True)
    fuel_remarks = models.TextField(blank=True, null=True)

    created_by_user = models.CharField(max_length=100, blank=True, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_by_user = models.CharField(max_length=100, blank=True, null=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate fuel code if not set
        if not self.fuel_code:
            self.fuel_code = f"FUEL-{uuid.uuid4().hex[:6].upper()}"
        # Auto-calculate total amount
        if self.fuel_price_per_liter and self.fuel_quantity_liters:
            self.fuel_total_amount = self.fuel_price_per_liter * self.fuel_quantity_liters
        super().save(*args, **kwargs)

    def __str__(self):
        vehicle_name = self.fuel_vehicle if self.fuel_vehicle else "Unknown Vehicle"
        return f"{vehicle_name} | {self.fuel_code}"
    
class TyreReplacementRecord(models.Model):
    tyre_replacement_id = models.AutoField(primary_key=True)
    tyre_replacement_date = models.DateField(default=timezone.now, verbose_name="Tyre Replacement Date")

    tyre_vehicle_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Vehicle Name")
    tyre_brand_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Brand Name")
    tyre_size_label = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tyre Size")
    tyre_unique_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tyre Number")
    tyre_type_category = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tyre Type")

    tyre_replace_reason_text = models.TextField(null=True, blank=True, verbose_name="Replace Reason")
    tyre_odometer_reading_value = models.PositiveIntegerField(null=True, blank=True, verbose_name="Odometer Reading")

    tyre_driver_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Driver Name")
    tyre_description_details = models.TextField(null=True, blank=True, verbose_name="Description")

    tyre_bill_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="Bill Number")
    tyre_bill_document_file = models.FileField(upload_to='tyre_bills/', null=True, blank=True, verbose_name="Bill Document")

    tyre_created_timestamp = models.DateTimeField(auto_now_add=True)
    tyre_updated_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tyre Replacement Record"
        verbose_name_plural = "Tyre Replacement Records"
        ordering = ['-tyre_replacement_date']

    def __str__(self):
        return f"{self.tyre_vehicle_name or 'Unknown Vehicle'} - {self.tyre_unique_number or 'No Tyre Number'}"
    

class Item(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    CATEGORY_CHOICES = [
        ('Engine', 'Engine'),
        ('Brake', 'Brake'),
        ('Electrical', 'Electrical'),
    ]

    UNIT_CHOICES = [
        ('Piece', 'Piece'),
        ('Box', 'Box'),
        ('Kg', 'Kg'),
    ]

    PART_PartNo = models.CharField(max_length=50, unique=True)
    PART_Color = models.CharField(max_length=50, blank=True, null=True)
    PART_Category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    PART_Status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    PART_Name = models.CharField(max_length=100)
    PART_Description = models.TextField(blank=True, null=True)
    PART_Unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    PART_Remark = models.TextField(blank=True, null=True)
    PART_Price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    PART_Image1 = models.ImageField(upload_to='part_images/', blank=True, null=True)
    PART_Image2 = models.ImageField(upload_to='part_images/', blank=True, null=True)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    UpdatedDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.PART_Name

class Service(models.Model):
    # --- Dropdown Choices ---
    SERVICE_TYPE_CHOICES = [
        ('routine', 'Routine Maintenance'),
        ('engine', 'Engine Repair'),
        ('oil_change', 'Oil Change'),
        ('brake', 'Brake Service'),
        ('transmission', 'Transmission Repair'),
        ('electrical', 'Electrical System'),
        ('tyre', 'Tyre Replacement'),
        ('ac', 'AC/Heating Service'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('scheduled', 'Scheduled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    VEHICLE_CHOICES = [
        ('TN01', 'TN 01 AB 1234 - Toyota Innova'),
        ('TN02', 'TN 02 CD 5678 - Mahindra Bolero'),
        ('TN03', 'TN 03 EF 9101 - Maruti Swift'),
        ('TN04', 'TN 04 GH 1122 - Tata Nexon'),
        ('TN05', 'TN 05 JK 3344 - Hyundai Creta'),
    ]

    # --- Core Fields ---
    quotation_number = models.CharField(max_length=100, blank=True, null=True)
    service_number = models.CharField(max_length=20, unique=True, editable=False)
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPE_CHOICES)
    last_kilometer = models.PositiveIntegerField(blank=True, null=True)
    vehicle = models.CharField(max_length=50, choices=VEHICLE_CHOICES)
    service_title = models.CharField(max_length=100)
    next_service_kilometer = models.PositiveIntegerField(blank=True, null=True)
    service_date = models.DateField()
    requested_by = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    next_service_date = models.DateField(blank=True, null=True)
    service_center_name = models.CharField(max_length=100, blank=True, null=True)
    service_assigned_to = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    created_date = models.DateTimeField(default=timezone.now)

    # --- Amount Fields ---
    labor_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_third_party_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # --- Auto-generate Service Number ---
    def save(self, *args, **kwargs):
        if not self.service_number:
            last_service = Service.objects.order_by('-id').first()
            next_number = 1 if not last_service else last_service.id + 1
            self.service_number = f"SR-{next_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_number} - {self.service_title}"


# ----------------------------------------------------------
# 🧾 Service Entry Model (for Service Entry Tab)
# ----------------------------------------------------------
class ServiceEntry(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('engine', 'Engine'),
        ('brake', 'Brake'),
        ('electrical', 'Electrical'),
        ('tyre', 'Tyre'),
        ('fluid', 'Fluid'),
        ('filter', 'Filter'),
        ('battery', 'Battery'),
        ('other', 'Other'),
    ]

    PART_NAME_CHOICES = [
        ('engine_oil', 'Engine Oil'),
        ('brake_pad', 'Brake Pad'),
        ('air_filter', 'Air Filter'),
        ('fuel_filter', 'Fuel Filter'),
        ('spark_plug', 'Spark Plug'),
        ('car_battery', 'Car Battery'),
        ('ac_filter', 'AC Filter'),
        ('coolant', 'Coolant'),
        ('transmission_fluid', 'Transmission Fluid'),
        ('tyre', 'Tyre'),
        ('headlight_bulb', 'Headlight Bulb'),
        ('wiper_blade', 'Wiper Blade'),
        ('fan_belt', 'Fan Belt'),
        ('radiator', 'Radiator'),
        ('alternator', 'Alternator'),
    ]

    # --- Foreign Key to Service ---
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='entries')

    # --- Entry Details ---
    entry_part_category = models.CharField(max_length=50, choices=PRODUCT_TYPE_CHOICES)
    entry_part_name = models.CharField(max_length=100, choices=PART_NAME_CHOICES)
    entry_unit = models.CharField(max_length=50, blank=True, null=True)
    entry_quantity = models.PositiveIntegerField(default=1)
    entry_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    entry_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # --- Auto-calculate subtotal before saving ---
    def save(self, *args, **kwargs):
        self.entry_subtotal = self.entry_quantity * self.entry_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.entry_part_name} ({self.entry_part_category}) - {self.service.service_number}"

class Vendor(models.Model):
    # Basic Information
    vendorName = models.CharField(max_length=100)
    vendorCompanyName = models.CharField(max_length=150, blank=True, null=True)
    vendorGender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        blank=True,
        null=True
    )
    vendorEmail = models.CharField(blank=True, null=True)
    vendorMobileNo = models.CharField(max_length=15, blank=True, null=True)
    vendorLandlineNo = models.CharField(max_length=15, blank=True, null=True)

    # Location Information
    vendorAddress = models.TextField(blank=True, null=True)
    vendorCountry = models.CharField(max_length=100, blank=True, null=True)
    vendorState = models.CharField(max_length=100, blank=True, null=True)
    vendorCity = models.CharField(max_length=100, blank=True, null=True)

    # Additional Details
    vendorRemark = models.TextField(blank=True, null=True)
    vendorProfileImage = models.ImageField(upload_to='vendors/', blank=True, null=True)

    # Audit Fields
    vendorCreatedBy = models.CharField(max_length=100, blank=True, null=True, default='admin')
    vendorCreatedDate = models.DateTimeField(default=timezone.now)
    vendorUpdatedBy = models.CharField(max_length=100, blank=True, null=True)
    vendorUpdatedDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendorName} ({self.vendorCompanyName})" if self.vendorCompanyName else self.vendorName
    


# Optional choices for dropdowns
class PurchaseItem(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    ITEM_TYPE_CHOICES = [
        ('Engine Part', 'Engine Part'),
        ('Electrical Component', 'Electrical Component'),
        ('Body Material', 'Body Material'),
        ('Lubricant', 'Lubricant'),
        ('Tyre/Brake', 'Tyre/Brake'),
    ]

    VENDOR_CHOICES = [
        ('Bosch Ltd.', 'Bosch Ltd.'),
        ('Mahindra Spares', 'Mahindra Spares'),
        ('TVS Auto Parts', 'TVS Auto Parts'),
        ('Tata Genuine Parts', 'Tata Genuine Parts'),
        ('Hero MotoCorp Supplies', 'Hero MotoCorp Supplies'),
        ('SKF Bearings India', 'SKF Bearings India'),
        ('Castrol Lubricants', 'Castrol Lubricants'),
    ]

    MANAGER_CHOICES = [
        ('John Smith', 'John Smith'),
        ('Mary Johnson', 'Mary Johnson'),
        ('David Wilson', 'David Wilson'),
        ('Priya Nair', 'Priya Nair'),
        ('Arun Sharma', 'Arun Sharma'),
    ]

    purchase_title = models.CharField(max_length=150)
    purchase_manager = models.CharField(max_length=100, choices=MANAGER_CHOICES)
    item_type = models.CharField(max_length=100, choices=ITEM_TYPE_CHOICES)
    purchase_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    vendor = models.CharField(max_length=150, choices=VENDOR_CHOICES)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.purchase_title} ({self.purchase_status})"
