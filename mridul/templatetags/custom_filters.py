from django import template
from datetime import date,datetime,timedelta

register = template.Library()
@register.filter
def calculate_age(birth_date):
    if not birth_date:
        return "N/A"
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return f"{age} years"

@register.filter
def format_image_path(prescription):
    path = f"images/medicinal_prescriptions/patient_id_{prescription.patient_id}_appoint_id_{prescription.appointment_id}.png"
    print(path)
    return path


