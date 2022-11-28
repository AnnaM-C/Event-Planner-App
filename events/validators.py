from django.core.exceptions import ValidationError
from datetime import datetime

def present_or_future_date(value):
   if value < datetime.date.today():
      raise ValidationError("The date cannot be in the past!")
   return value