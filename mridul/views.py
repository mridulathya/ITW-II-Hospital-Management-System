from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from . import forms
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib import messages
from . import models
from django.shortcuts import get_object_or_404, HttpResponseRedirect, render
from PIL import Image, ImageDraw, ImageFont
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.hashers import check_password
from datetime import datetime, time


def home(request):
    return render(request,'mridul/main_desktop.html')
def admin(request):
    return redirect('/admin/login/?next=/admin/')
def aboutus(request):
    return render(request,'mridul/aboutus.html')


def login(request):
    form = forms.LoginForm()
    
    if request.method == 'POST':
        email_id = request.POST.get('email_id')
        password = request.POST.get('password')
        
        try:
            user = models.Users.objects.get(email_id=email_id) 
            auth_user = authenticate(request, username=user.phone_no, password=password)
            
            if auth_user is not None:
                auth_login(request, auth_user)
                if user.role_as_a == 'patient':
                    return HttpResponseRedirect(f'/patient_dashboard/{user.user_sr_no}/')
                elif user.role_as_a == 'doctor':
                    return HttpResponseRedirect(f'/doctor_dashboard/{user.user_sr_no}/')
                elif user.role_as_a == 'receptionist': 
                    return HttpResponseRedirect(f'/receptionist_dashboard/{user.user_sr_no}/')
                    # return HttpResponseRedirect(f'/admin_dash/{user.user_sr_no}/')
            else:
                messages.error(request, "Incorrect password. Please try again.")
                print("Authentication failed.\n")
        
        except models.Users.DoesNotExist:
            messages.error(request, "No account found with that email ID. Please register.")
            print("User doesn't exist.\n")
    
    return render(request, 'mridul/login.html', {'form': form})
def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/')
def register(request):
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email_id = request.POST.get('email_id')
        phone_no = request.POST.get('phone_no')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password validation
        if password != confirm_password:
            return render(request, 'mridul/register.html', {'error': "Passwords do not match."})

        # Create and save the user
        user = models.Users(
            first_name=first_name,
            last_name=last_name,
            email_id=email_id,
            phone_no=phone_no,
            gender=gender,
            password=make_password(password),
            role_as_a="Patient",
            created_at=timezone.now()
        )
        user.save()

        # Create associated Django auth user
        auth_user = User.objects.create_user(
            username=phone_no,
            email=email_id,
            password=password
        )
        auth_user.first_name = first_name
        auth_user.last_name = last_name
        auth_user.save()

        return HttpResponseRedirect('/')
    
    return render(request, 'mridul/register.html')




@login_required
def patient_dashboard(request, user_id):
    search = forms.DoctorSearch(request.POST or None)
    all_appointments = models.Appointment.objects.filter(user_id=user_id,appointment_date__gte=timezone.now().date()).order_by('appointment_date')
    user = get_object_or_404(models.Users, user_sr_no=user_id)

    specialisation = request.POST.get('specialisation') or request.GET.get('specialisation')
    doctors = models.Doctor.objects.all().only('first_name', 'last_name').order_by('first_name', 'last_name')

    if specialisation:
        doctors = doctors.filter(specialization__icontains=specialisation).order_by('first_name', 'last_name')
        if not doctors.exists():
            messages.error(request, "No doctors found for this specialization. Please try again.")

    paginator = Paginator(doctors, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'mridul/patient_dash.html', {
        'form': search,
        'user': user,
        'all_appointments': all_appointments,
        'page_obj': page_obj,
        'user_id': user_id,
        'specialisation': specialisation, 
    })

@login_required
def all_bookings(request,user_id):
    all_appointments = models.Appointment.objects.filter(user_id = user_id).order_by('created_at')
    
    user_instance = get_object_or_404(models.Users, user_sr_no=user_id)
    return  render(request,'mridul/all_bookings.html',
                   {'user_id':user_id , 
                    'all_appointments':all_appointments, 
                    'user':user_instance
                    }
                )

@login_required
def doctor_dashboard(request, user_id):
    user = get_object_or_404(models.Users, user_sr_no=user_id)
    doctor_data = get_object_or_404(models.Doctor, email=user.email_id)
    appointments = models.Appointment.objects.filter(doctor_id=doctor_data.doctor_id)
    total_appointments = appointments.count()

    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    total_pending_today = appointments.filter(status='Waiting to be Scheduled',  appointment_date=today).count()
    total_pending_tomorrow = appointments.filter(status='Waiting to be Scheduled',  appointment_date=tomorrow).count()
    total_pending_all = appointments.filter(status='Waiting to be Scheduled').count()
    total_scheduled = appointments.filter(status='Scheduled').count()
    total_canceled = appointments.filter(status='cancelled').count()
    total_completed = appointments.filter(status='completed').count()
    rating = doctor_data.rating

    context = {
        'doctor_data': doctor_data,
        'user': user,
        'total_appointments': total_appointments,
        'total_pending_today': total_pending_today,
        'total_pending_tomorrow': total_pending_tomorrow,
        'total_pending_all': total_pending_all,
        'total_scheduled': total_scheduled,
        'total_canceled': total_canceled,
        'total_completed': total_completed,
        'rating': rating,
    }
    return render(request, 'mridul/doctor_dash.html', context)


@login_required
def receptionist_dashboard(request,user_id):
    user = get_object_or_404(models.Users, user_sr_no=user_id)  
    appointments = models.Appointment.objects.all()
    total_appointments = appointments.count()

    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)
    total_pending_today = appointments.filter(status='Waiting to be Scheduled',  appointment_date=today).count()
    total_pending_tomorrow = appointments.filter(status='Waiting to be Scheduled',  appointment_date=tomorrow).count()
    total_pending_all = appointments.filter(status='Waiting to be Scheduled').count()
    total_scheduled = appointments.filter(status='Scheduled').count()
    total_canceled = appointments.filter(status='Cancelled').count()
    total_completed = appointments.filter(status='Completed').count()

    context = {
        'user_id':user_id,
        'all_appointments':appointments,
        'user': user,
        'total_appointments': total_appointments,
        'total_pending_today': total_pending_today,
        'total_pending_tomorrow': total_pending_tomorrow,
        'total_pending_all': total_pending_all,
        'total_scheduled': total_scheduled,
        'total_canceled': total_canceled,
        'total_completed': total_completed
    }
    return render(request,'mridul/recept_dash.html',context)

@login_required
def add_patient(request,user_id):
    user = get_object_or_404(models.Users, user_sr_no=user_id) 
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        phone_no = request.POST.get('phone_no')
        email = request.POST.get('email')
        address = request.POST.get('address')
        blood_group = request.POST.get('blood_group')
        emergency_contact_name = request.POST.get('emergency_contact_name')
        emergency_contact_number = request.POST.get('emergency_contact_number')
        
        add_patient = models.Patient(
            first_name = first_name,
            last_name = last_name,
            gender= gender,
            date_of_birth = date_of_birth,
            phone_no=phone_no,
            email=email,
            address=address,
            blood_group = blood_group,
            emergency_contact_name = emergency_contact_name,
            emergency_contact_number = emergency_contact_number
        )
        add_patient.save()
        print('Done sucessfully @@@@@@@')
        return HttpResponseRedirect(f'/receptionist_dashboard/{user_id}')
    return render(request,'mridul/add_patient.html',{'user':user})


@login_required
def alldoctor(request, user_id):
    alldoctors = models.Doctor.objects.all()
    user = get_object_or_404(models.Users, user_sr_no=user_id) 
    if not alldoctors.exists():
        messages.error(request, "No doctors available at the moment.")
    
    paginator = Paginator(alldoctors, 12)
    page_number = request.GET.get('page', 1) 
    page_obj = paginator.get_page(page_number)
    return render(request, 'mridul/alldoctor.html', {
        'page_obj': page_obj,
        'user_id': user_id,
        'user':user
    })

import re
def convert_to_24_hour_format(time_str):
    if(time_str == 'noon'):
        return '12:00:00'
    time_str = time_str.strip().lower() 
    time_str = time_str.replace(" ", "") 

    time_str = time_str.replace("p.m.", "PM").replace("a.m.", "AM")
    time_str = time_str.replace("pm", "PM").replace("am", "AM")
    
    pattern = r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)'

    match = re.match(pattern, time_str)
    if match:
        hour = int(match.group(1))
        minute = match.group(2) 
        period = match.group(3)

        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0

        if minute is None:
            minute = "00" 
        
        return f"{hour:02}:{minute}:00"
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    
@login_required
def book_appointment(request, user_id,doctor_id):
    doctor = models.Doctor.objects.filter(doctor_id=doctor_id).first() 
    print(doctor.first_name,doctor.last_name)
    user_instance = get_object_or_404(models.Users, user_sr_no=user_id)
    all_time_slots = {
            time(9, 0): 'yes',
            time(9, 30): 'yes',
            time(10, 0): 'yes',
            time(10, 30): 'yes',
            time(11, 0): 'yes',
            time(11, 30): 'yes',
            time(12, 0): 'yes',
            time(12, 30): 'yes',
            time(13, 0): 'yes',
            time(13, 30): 'yes',
            time(14, 0): 'yes',
            time(14, 30): 'yes',
            time(15, 0): 'yes',
            time(15, 30): 'yes',
            time(16, 0): 'yes',
            time(16, 30): 'yes',
            time(17, 0): 'yes',
            time(17, 30): 'yes',
            time(18, 0): 'yes',
            time(18, 30): 'yes',
            time(19, 0): 'yes',
            time(19, 30): 'yes',
            time(20, 0): 'yes',
            time(20, 30): 'yes',
            time(21, 0): 'yes',
            time(21, 30): 'yes'
        }

    if request.method == 'POST' :
        appointment_date=request.POST.get('appointment_date')
        print(type(appointment_date))
        all_booked_appointments_on_this_date = models.Appointment.objects.filter(
            appointment_date=appointment_date,
            doctor_id=doctor_id).exclude(status='Cancelled')

        print(all_booked_appointments_on_this_date)
        for i in all_booked_appointments_on_this_date:
            all_time_slots[i.appointment_time]='no'
        print(all_time_slots)  
        if request.POST.get('appointment_time'):
            appointment_time =request.POST.get('appointment_time')
            appointment_time = convert_to_24_hour_format(appointment_time)
            appointment = models.Appointment(
            doctor_id=doctor,
            user_id=user_instance,    
            appointment_date=request.POST.get('appointment_date'),
            appointment_time=appointment_time,
            reason=request.POST.get('reason'),
            status='Waiting to be Scheduled', 
            created_at=timezone.now(),  
            updated_at=timezone.now()
            )
            print(appointment_time)
            appointment.save()
            print("Appointment done successfully")
            if (appointment.status == 'Waiting to be Scheduled'):
                return HttpResponseRedirect(f'/update_payment_table/{appointment.appointment_id}')
        return render(request, 'mridul/appointment_form.html', {'doctor': doctor, 'user': user_instance,'user_id':user_id,'dict':all_time_slots})
    return render(request, 'mridul/appointment_form.html', {'doctor': doctor, 'user': user_instance,'user_id':user_id,'dict':all_time_slots})

@login_required
def update_payment_table(request, app_id):

    appointment = models.Appointment.objects.filter(appointment_id=app_id).first()

    doctor_instance = get_object_or_404(models.Doctor, doctor_id=appointment.doctor_id.doctor_id)
    payment = models.Payment.objects.create(
        appointment_id=appointment.appointment_id,
        description=f"Appointment fee with Dr. {doctor_instance.first_name} {doctor_instance.first_name} : {doctor_instance.doctor_id}",
        amount=doctor_instance.consultation_fee,
        billing_date=timezone.now().date(),
        payment_status='Pending'
    )
    return HttpResponseRedirect(f'/patient_dashboard/{appointment.user_id.user_sr_no}')

@login_required
def update_appointment_status(request, app_id,user_id):
    appointment = get_object_or_404(models.Appointment, appointment_id=app_id)
    status = appointment.status
    if request.method == 'POST':
        new_status=None
        if 'confirm' in request.POST:
            new_status = 'Scheduled'
        elif 'cancel' in request.POST:
            new_status = 'Cancelled' 
        appointment.status = new_status
        appointment.updated_at = timezone.now()
        appointment.save()
        print("updated succesfully")
    return HttpResponseRedirect(f'/show_appointments/{user_id}/{status}/') 


@login_required
def show_appointments(request,user_id,status):
    all_appointments = models.Appointment.objects.filter(status=status).order_by('appointment_date','created_at')
    user = get_object_or_404(models.Users, user_sr_no=user_id)
    if user.role_as_a == 'doctor':
        doctor = get_object_or_404(models.Doctor, email=user.email_id)
        all_appointments = models.Appointment.objects.filter(status=status, doctor_id = doctor.doctor_id)
    dict = {
        'user': user,
        'all_appointments':all_appointments,
        'status':status,
    }
    return render(request,'mridul/show_appointments.html',dict)

@login_required
def patient_prescriptions(request, app_id, user_id):
    appointment = get_object_or_404(models.Appointment, appointment_id=app_id)
    user = get_object_or_404(models.Users, user_sr_no=user_id)
    patient_id = request.POST.get('patient_id')

    if request.method == 'POST':
        if 'phone_no' in request.POST:
            phone_no = request.POST.get('phone_no')
            patient = models.Patient.objects.filter(phone_no=phone_no).first()
            if patient:
                return render(request, 'mridul/patient_prescriptions.html', {
                    'appointment': appointment,
                    'patient': patient,
                    'user': user,
                })
            else:
                messages.error(request, "Patient not found! Please add the patient first.")
        
        elif 'patient_id' in request.POST:
            prescription = models.Prescriptions.objects.filter(appointment_id=appointment.appointment_id).first()
            if user.role_as_a == 'receptionist':
                appointment_id = appointment.appointment_id          
                doctor_id = appointment.doctor_id.doctor_id
                prescription_date = timezone.now().date()
                
                prescription = models.Prescriptions(
                    appointment_id=appointment_id,
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    prescription_date=prescription_date
                )
                prescription.save()
                return HttpResponseRedirect(f'/receptionist_dashboard/{user_id}')
            
            elif user.role_as_a == "doctor":
                prescription = models.Prescriptions.objects.filter(appointment_id=appointment.appointment_id).first()
                print(prescription)
                if prescription is None:
                    messages.error(request, "No existing prescription found for this appointment.")
                    return render(request, 'mridul/patient_prescriptions.html', {
                        'appointment': appointment,
                        'patient': models.Patient.objects.filter(patient_id=patient_id).first(),
                        'user': user,
                    })

                prescription_date = timezone.now().date()
                symptoms = request.POST.get('symptoms')
                cause = request.POST.get('cause')
                #####
                name=""
                dosage=""
                remark=""
                data=[]
                i=1
                while True:
                    medicine_name = request.POST.get(f'medicine_name_{i}')
                    dosage_value = request.POST.get(f'dosage_{i}')
                    remark_value = request.POST.get(f'remark_{i}')
                    if not medicine_name:
                        break
                    data.append({
                        "medicine_name": medicine_name,
                        "dosage": dosage_value or "",  
                        "remark": remark_value or ""   
                    })
                    name += medicine_name + ';'
                    dosage += dosage_value + ';'
                    remark +=remark_value + ';'
                    i += 1  
                medicine_obj = models.MedicinalPrescription(
                    prescription_id = prescription.prescription_id,
                    medicine_name = name,
                    dosage = dosage,
                    remark = remark,
                    date_of_prescription = prescription.prescription_date
                )
                medicine_obj.save()
                # Image settings
                image_width = 800
                row_height = 40
                header_height = 50
                padding = 10
                font_size = 20
                table_start_y = header_height

                image_height = header_height + (len(data)) * row_height

                image = Image.new("RGB", (image_width, image_height), "white")
                draw = ImageDraw.Draw(image)

                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()

                
                draw.rectangle([0, 0, image_width, header_height], fill="lightgrey")
                draw.text((padding, padding), "Medicine Name", font=font, fill="black")
                draw.text((image_width // 3, padding), "Dosage", font=font, fill="black")
                draw.text((2 * image_width // 3, padding), "Remark", font=font, fill="black")

                
                for i, row in enumerate(data, start=1):
                    y = table_start_y + (i - 1) * row_height
                    draw.rectangle([0, y, image_width, y + row_height], outline="black")

                    
                    draw.text((padding, y + padding), row["medicine_name"], font=font, fill="black")
                    draw.text((image_width // 3, y + padding), row["dosage"], font=font, fill="black")
                    draw.text((2 * image_width // 3, y + padding), row["remark"], font=font, fill="black")

                image.save(f"static/images/medicinal_prescriptions/patient_id_{patient_id}_appoint_id_{app_id}.png")
                #####
                lab_tests = request.POST.get('lab_tests')
                hospitalization_needed = request.POST.get('hospitalization_needed')

                type_of_hospitalisation = request.POST.get('type_of_hospitalization') if hospitalization_needed == 'YES' else "None"
                surgery_needed = request.POST.get('surgery_needed')

                if surgery_needed == "YES":
                    surgery_obj = models.PreSurgeryInfo(
                        prescription_id=prescription.prescription_id,
                        surgery_type=request.POST.get('surgery_type'),
                        suggested_date=request.POST.get('suggested_date'),
                        suggested_time=request.POST.get('suggested_time'),
                        advice=request.POST.get('advice'),
                    )
                    surgery_obj.save()
                prescription.medicine_image_path = f"static/images/medicinal_prescriptions/patient_id_{patient_id}_appoint_id_{app_id}.png"
                prescription.symptoms = symptoms
                prescription.cause = cause
                prescription.lab_tests = lab_tests
                prescription.hospitalization_needed = hospitalization_needed
                prescription.type_of_hospitalization = type_of_hospitalisation
                prescription.surgery_needed = surgery_needed
                prescription.dietary_precautions = request.POST.get('dietary_precautions')
                prescription.remark_on_lab_test = request.POST.get('remark_on_lab_test')
                prescription.save()  

                #UPDATE Appointment status#
                appoint_stat = models.Appointment.objects.filter(appointment_id=app_id).first()
                appoint_stat.status = 'Completed'
                appoint_stat.save()
                
            return HttpResponseRedirect(f'/doctor_dashboard/{user_id}')

    # Handle GET requests
    patient_id = request.GET.get('patient_id')
    patient = models.Patient.objects.filter(patient_id=patient_id).first() if patient_id else None

    return render(request, 'mridul/patient_prescriptions.html', {
        'appointment': appointment,
        'patient': patient,
        'user': user,
    })

@login_required
def my_prescriptions(request, user_id):
    user = get_object_or_404(models.Users, user_sr_no=user_id)
    all_appointments = models.Appointment.objects.filter(user_id=user_id)
    all_prescriptions = [] 

    for appointment in all_appointments:
        app_id = appointment.appointment_id
        prescriptions = models.Prescriptions.objects.filter(appointment_id=app_id)
        
        if prescriptions.exists():
            all_prescriptions.extend(prescriptions)

    return render(request, 'mridul/my_prescriptions.html', {
        "user": user,
        "all_prescriptions": all_prescriptions 
    })

def pres_page(request, p_id):
    now = timezone.now()
    prescription = get_object_or_404(models.Prescriptions, prescription_id=p_id)
    surgery = models.PreSurgeryInfo.objects.filter(prescription_id=p_id).first()
    return render(request, 'mridul/pres_page.html', {'prescription': prescription, 'surgery': surgery,'now':now})


import pdfkit
config = pdfkit.configuration(wkhtmltopdf = r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
@login_required
def pdf_prescription_create(request,p_id):
    prescription = get_object_or_404(models.Prescriptions, prescription_id=p_id)
    options = {
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        'encoding': 'UTF-8',
        'no-stop-slow-scripts': None,
        'enable-local-file-access': None,
        'zoom': 1.0, 
    }
    pdf = pdfkit.from_url(request.build_absolute_uri(reverse('pres_page',args=[p_id])),False,configuration=config,options=options)
    # pdf = pdfkit.from_string('<h1>Hello World</h1>', False, configuration=config, options=options)
    response = HttpResponse(pdf,content_type='application/pdf')
    file_name = f"pres_id_{p_id}_appoint_id_{prescription.appointment_id}"
    response['Content-Disposition']=f'attachment;filename="{file_name}.pdf"'
    return response

@login_required
def final_bill(request, p_id, user_id):

    prescription = models.Prescriptions.objects.filter(prescription_id=p_id).first()
    user = models.Users.objects.filter(user_sr_no=user_id).first()
    if not prescription or not user:
        return render(request, 'mridul/final_bill.html', {'error': 'Prescription or User not found'})

    all_payments = models.Payment.objects.filter(appointment_id=prescription.appointment_id)

    total_paid = sum(payment.amount for payment in all_payments if payment.payment_status == "Paid")
    total_pending = sum(payment.amount for payment in all_payments if payment.payment_status == "Pending")
    total_refund = total_paid-total_pending
    if(total_refund < 0):
        total_refund=0
    context = {
        'prescription': prescription,
        'all_payments': all_payments,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'total_refund':total_refund,
        'user': user,
    }

    return render(request, 'mridul/final_bill.html', context)

def final_bill_page(request,p_id):
    prescription = models.Prescriptions.objects.filter(prescription_id=p_id).first()
    all_payments = models.Payment.objects.filter(appointment_id=prescription.appointment_id)
    total_paid = sum(payment.amount for payment in all_payments if payment.payment_status == "Paid")
    total_pending = sum(payment.amount for payment in all_payments if payment.payment_status == "Pending")
    total_refund = total_paid-total_pending
    if(total_refund < 0):
        total_refund=0
    now = timezone.now()
    context = {
        'prescription': prescription,
        'all_payments': all_payments,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'total_refund':total_refund,
        'now':now,
    }
    return render(request, 'mridul/final_bill_page.html',context)

@login_required
def pdf_final_bill(request,p_id):
    prescription = get_object_or_404(models.Prescriptions, prescription_id=p_id)
    options = {
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        'encoding': 'UTF-8',
        'no-stop-slow-scripts': None,
        'enable-local-file-access': None,
        'zoom': 1.0, 
    }
    pdf = pdfkit.from_url(request.build_absolute_uri(reverse('final_bill_page',args=[p_id])),False,configuration=config,options=options)
    response = HttpResponse(pdf,content_type='application/pdf')
    file_name = f"final_bill_pres_id_{p_id}_appoint_id_{prescription.appointment_id}"
    response['Content-Disposition']=f'attachment;filename="{file_name}.pdf"'
    return response

def rate_app(request, user_id):
    all_appointments = models.Appointment.objects.filter(user_id=user_id, status='Completed').order_by('created_at')
    all_prescriptions = []
    for appointment in all_appointments:
        prescriptions = models.Prescriptions.objects.filter(appointment_id=appointment.appointment_id).first()
        rating = models.Ratings.objects.filter(appointment_id = appointment).first()
        all_prescriptions.append((appointment, prescriptions, rating))

    user_instance = get_object_or_404(models.Users, user_sr_no=user_id)
    
    return render(request, 'mridul/rate_app.html', {
        'user_id': user_id,
        'all_appointments': all_appointments,
        'user': user_instance,
        'all_prescriptions': all_prescriptions
    })
def update_rating(request, app_id):
    appointment = get_object_or_404(models.Appointment, appointment_id=app_id)
    rating_value = Decimal(request.POST.get('rating_value'))
    if request.method == 'POST':
        rating = models.Ratings(
            appointment_id=app_id,  
            doctor_id=appointment.doctor_id.doctor_id,
            rating_value=rating_value,
            comment=request.POST.get('comment'),
            created_at=timezone.now()
        )
        rating.save()
        doctor = models.Doctor.objects.filter(doctor_id = appointment.doctor_id.doctor_id).first()
        doctor.rating = (rating_value + doctor.rating)/2
        doctor.save()
        
        messages.success(request, "Thank you for your rating!")

        return HttpResponseRedirect(f"/rate_app/{appointment.user_id.user_sr_no}/")


def add_doctor(request, user_id):
    user = models.Users.objects.filter(user_sr_no=user_id).first()

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        education = request.POST.get('education')
        specialization = request.POST.get('specialization')
        phone_no = request.POST.get('phone_no')
        email = request.POST.get('email')
        consultation_fee = request.POST.get('consultation_fee')
        time_slot_begin = request.POST.get('time_slot_begin')
        time_slot_end = request.POST.get('time_slot_end')
        experience = request.POST.get('experience')
        raw_password = request.POST.get('password') 
        confirm_password =request.POST.get('confirm_password')
        # Hash password
        hashed_password = make_password(raw_password)

        # Check if a doctor or user with the same email or phone number already exists
        if models.Doctor.objects.filter(email=email).exists() or models.Doctor.objects.filter(phone_no=phone_no).exists() or User.objects.filter(username=email).exists():
            messages.error(request, "Doctor with this email or phone number already exists.")
            return HttpResponseRedirect(f'/add_doctor/{user_id}')
        if raw_password!=confirm_password:
            messages.error(request, "Both Passwords doesn'match.")
            return HttpResponseRedirect(f'/add_doctor/{user_id}')
        # Save to `Doctor` table
        new_doctor = models.Doctor(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            education=education,
            specialization=specialization,
            phone_no=phone_no,
            email=email,
            joining_date=timezone.now().date(),
            consultation_fee=consultation_fee,
            time_slot_begin=time_slot_begin,
            time_slot_end=time_slot_end,
            experience=experience,
            rating=0.00
        )
        new_doctor.save()

        user_entry = models.Users(
            first_name=first_name,
            last_name=last_name,
            email_id=email,
            phone_no=phone_no,
            password=hashed_password,  
            gender=gender,
            created_at=timezone.now(),
            role_as_a='doctor'  
        )
        user_entry.save()

        auth_user_entry = User(
            username=phone_no,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_staff=True,  
            is_active=True,
            date_joined=timezone.now(),
        )
        auth_user_entry.save()

        messages.success(request, "Doctor added successfully.")
        return HttpResponseRedirect(f'/receptionist_dashboard/{user_id}')

    return render(request, 'mridul/add_doctor.html', {'user': user})

def add_receptionist(request, user_id):
    user = models.Users.objects.filter(user_sr_no=user_id).first()

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        phone_no = request.POST.get('phone_no')
        email = request.POST.get('email')
        shift = request.POST.get('shift')
        salary = request.POST.get('salary')
        hire_date = timezone.now().date()
        created_at = timezone.now()
        updated_at = timezone.now()
        raw_password = request.POST.get('password') 
        confirm_password =request.POST.get('confirm_password')
        # Hash password
        hashed_password = make_password(raw_password)

        # Check if a doctor or user with the same email or phone number already exists
        if models.Receptionist.objects.filter(email=email).exists() or models.Receptionist.objects.filter(phone_no=phone_no).exists() or User.objects.filter(username=email).exists():
            messages.error(request, "Receptionist with this email or phone number already exists.")
            return HttpResponseRedirect(f'/add_receptionist/{user_id}')
        if raw_password!=confirm_password:
            messages.error(request, "Both Passwords doesn't match. Re-enter !!!")
            return HttpResponseRedirect(f'/add_receptionist/{user_id}')
        
        new_receptionist = models.Receptionist(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            phone_no=phone_no,
            email=email,
            hire_date = hire_date,
            shift = shift,
            salary=salary,
            created_at=created_at,
            updated_at=updated_at
        )
        new_receptionist.save()

        user_entry = models.Users(
            first_name=first_name,
            last_name=last_name,
            email_id=email,
            phone_no=phone_no,
            password=hashed_password,  
            gender=gender,
            created_at=timezone.now(),
            role_as_a='receptionist'  
        )
        user_entry.save()

        auth_user_entry = User(
            username=phone_no,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_staff=True,  
            is_active=True,
            date_joined=timezone.now(),
        )
        auth_user_entry.save()

        messages.success(request, "Receptionist added successfully.")
        return HttpResponseRedirect(f'/receptionist_dashboard/{user_id}')

    return render(request, 'mridul/add_receptionist.html', {'user': user})
def settings(request, user_id):
    user = get_object_or_404(models.Users, user_sr_no=user_id)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if check_password(old_password, user.password) and new_password == confirm_password:
                user.password = make_password(new_password)
                user.save()
                
                auth_user = get_object_or_404(User, username=user.phone_no)
                auth_user.set_password(new_password)
                auth_user.save()
                messages.success(request, 'Password changed successfully.')
                return HttpResponseRedirect(f"/login")
            else:
                messages.error(request, 'Old password is incorrect or new passwords do not match.')

        elif form_type == 'change_phone':
            old_phone = request.POST.get('old_phone')
            new_phone = request.POST.get('new_phone')

            if user.phone_no == old_phone:
                user.phone_no = new_phone
                user.save()

                auth_user = get_object_or_404(User, username=old_phone)
                auth_user.username = new_phone
                auth_user.save()

                messages.success(request, 'Phone number changed successfully.')
                
            else:
                messages.error(request, 'Old phone number entered is incorrect.')
            return HttpResponseRedirect(f"/settings/{user_id}")
    return render(request,'mridul/settings.html',{'user':user})