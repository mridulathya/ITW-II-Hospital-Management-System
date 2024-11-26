# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone



class Receptionist(models.Model):
    receptionist_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=6)
    phone_no = models.CharField(unique=True, max_length=10)
    email = models.CharField(unique=True, max_length=100)
    hire_date = models.DateField(blank=True, null=True)
    shift = models.CharField(max_length=7, blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'receptionist'
    def __str__(self):
        return f"Room Number: {self.room_number} - Type: {self.room_type} - Status: {self.status}"


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=6)
    education = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone_no = models.CharField(unique=True, max_length=10)
    email = models.CharField(unique=True, max_length=100)
    joining_date = models.DateField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    time_slot_begin = models.TimeField()
    time_slot_end = models.TimeField()
    experience = models.IntegerField(blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doctor'
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - Specialization: {self.specialization}"

class Users(models.Model):
    user_sr_no = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=15, blank=True, null=True)
    email_id = models.CharField(unique=True, max_length=50)
    phone_no = models.CharField(unique=True, max_length=10)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=6,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    role_as_a = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
    def __str__(self):
        return f"User: {self.first_name} {self.last_name} - Role: {self.role_as_a}"

class Admission(models.Model):
    admission_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', models.DO_NOTHING)
    room = models.ForeignKey('Room', models.DO_NOTHING)
    admission_date = models.DateField()
    discharge_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admission'
    def __str__(self):
        return f"Admission ID: {self.admission_id} - Patient ID: {self.patient_id} - Room ID: {self.room_id}"


class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    doctor_id = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        db_column='doctor_id'  # Custom database column name
    )
    user_id = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        db_column='user_id'  # Custom database column name
    ) 
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=25, choices=[
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Waiting to be Scheduled','Waiting to be Scheduled')
    ], default='Scheduled', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)
    remark = models.CharField(max_length=255)

    def __str__(self):
        return f"Appointment with {self.doctor_id} on {self.appointment_date}"

    class Meta:
        managed = True
        db_table = 'appointment' 
    def __str__(self):
        return f"Appointment ID: {self.appointment_id} - Doctor: {self.doctor_id} - User: {self.user_id} - Date: {self.appointment_date}"
        
class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=6)
    date_of_birth = models.DateField()
    phone_no = models.CharField(unique=True, max_length=10)
    email = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    blood_group = models.CharField(max_length=3, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    registration_date = models.DateField(default=timezone.now, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'patient'
    def __str__(self):
        return f"{self.first_name} {self.last_name} - ID: {self.patient_id}"


class ContactSupport(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    user_sr_no = models.ForeignKey('Users', models.DO_NOTHING, db_column='user_sr_no')
    email = models.OneToOneField('Users', models.DO_NOTHING, related_name='contactsupport_email_set')
    phone_no = models.OneToOneField('Users', models.DO_NOTHING, db_column='phone_no', related_name='contactsupport_phone_no_set')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=11, blank=True, null=True)
    support_agent = models.ForeignKey('Receptionist', models.DO_NOTHING, blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contact_support'
    def __str__(self):
        return f"Ticket ID: {self.ticket_id} - User ID: {self.user_sr_no} - Status: {self.status}"

class Documents(models.Model):
    patient = models.OneToOneField('Patient', models.DO_NOTHING, primary_key=True)  # The composite primary key (patient_id, appointment_id) found, that is not supported. The first column is selected.
    appointment = models.ForeignKey(Appointment, models.DO_NOTHING)
    prescription = models.TextField()
    lab_test_reports = models.TextField(blank=True, null=True)
    lab_bills = models.TextField(blank=True, null=True)
    final_bill = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documents'
        unique_together = (('patient', 'appointment'),)
    def __str__(self):
        return f"Document for Patient ID: {self.patient_id} - Appointment ID: {self.appointment_id}"



class FinalBills(models.Model):
    bill_id = models.IntegerField(primary_key=True)
    appointment = models.ForeignKey(Appointment, models.DO_NOTHING)
    patient = models.ForeignKey('Patient', models.DO_NOTHING)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'final_bills'
    def __str__(self):
        return f"Bill ID: {self.bill_id} - Patient ID: {self.patient_id} - Appointment ID: {self.appointment_id}"


class MedicinalPrescription(models.Model):
    prescription = models.OneToOneField('Prescriptions', models.DO_NOTHING, primary_key=True)
    medicine_name = models.TextField()
    dosage = models.TextField()
    remark = models.TextField(blank=True, null=True)
    date_of_prescription = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'medicinal_prescription'
    def __str__(self):
        return f"Prescription for Prescription ID: {self.prescription_id} - Medicine: {self.medicine_name}"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, models.DO_NOTHING, related_name="payments")
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_date = models.DateField(blank=True, null=True)
    payment_status = models.CharField(max_length=7, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment'
    def __str__(self):
        return f"Payment ID: {self.payment_id} - Appointment ID: {self.appointment_id} - Status: {self.payment_status}"

class PreSurgeryInfo(models.Model):
    prescription = models.OneToOneField('Prescriptions', models.DO_NOTHING, primary_key=True)
    surgery_type = models.TextField()
    suggested_date = models.DateField()
    suggested_time = models.CharField(max_length=50, blank=True, null=True)
    advice = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pre_surgery_info'
    def __str__(self):
        return f"Pre-Surgery Info for Prescription ID: {self.prescription_id} - Surgery Type: {self.surgery_type}"



class Prescriptions(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, models.DO_NOTHING, blank=True, null=True)
    doctor = models.ForeignKey(Doctor, models.DO_NOTHING, blank=True, null=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, blank=True, null=True)
    prescription_date = models.DateField()
    symptoms = models.TextField()
    cause = models.TextField(blank=True, null=True)
    medicine_image_path = models.ImageField(upload_to="F:\django learn\hms\assets\images\medicinal_prescriptions", blank=True, null=True)
    lab_tests = models.TextField(blank=True, null=True)
    hospitalization_needed = models.CharField(max_length=3, blank=True, null=True)
    type_of_hospitalization = models.CharField(max_length=12, blank=True, null=True)
    surgery_needed = models.CharField(max_length=3, blank=True, null=True)
    dietary_precautions = models.TextField(blank=True, null=True)
    remark_on_lab_test = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prescriptions'
    def __str__(self):
        return f"Prescription for Appointment ID: {self.appointment_id} - Prescription ID: {self.prescription_id}"


class Ratings(models.Model):
    appointment = models.ForeignKey(Appointment, models.DO_NOTHING)
    doctor = models.ForeignKey(Doctor, models.DO_NOTHING)
    rating_value = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True) 
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rating'
    def __str__(self):
        return f"Rating for Appointment ID: {self.appointment_id} - Doctor ID: {self.doctor_id} - Rating: {self.rating_value}"



class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=12, blank=True, null=True)
    status = models.CharField(max_length=9, blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'room'

