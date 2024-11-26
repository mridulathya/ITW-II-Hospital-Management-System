
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Appointment,Prescriptions
from django.db.models import F
from django.db import transaction
from datetime import date,datetime
from django.utils import timezone

@receiver(user_logged_in)
def run_on_login(sender, request, user, **kwargs):
    print(f"User {user.email} has logged in.")
    appointments = Appointment.objects.filter(
        appointment_date__lt=timezone.now().date()
    ).exclude(
        appointment_id__in=Prescriptions.objects.values_list('appointment_id', flat=True)
    )
    for appointment in appointments:
        appointment.status = "Cancelled"
        appointment.remark = "Patient not Visited"
        appointment.updated_at = timezone.now() 
        appointment.save()  
@receiver(post_save, sender=Appointment)
def check_and_cancel_duplicates(sender, instance, created, **kwargs):
    if created: 
        cancel_duplicate_appointments()

def cancel_duplicate_appointments():
   
    with transaction.atomic():
        duplicates = (Appointment.objects
                      .values('appointment_date', 'appointment_time')
                      .annotate(count=F('appointment_id'))
                      .filter(count__gt=1))

        for duplicate in duplicates:
            appointments = (Appointment.objects
                            .filter(appointment_date=duplicate['appointment_date'], appointment_time=duplicate['appointment_time'])
                            .order_by('appointment_id'))

            first_appointment = appointments.first()
            remaining_appointments = appointments.exclude(appointment_id=first_appointment.appointment_id)
            remaining_appointments.update(status='cancelled',remark = '''Appointment could not be made!
                                   Some user already booked the slot before you.
                                   Sorry for the inconvenience caused.''')


