import datetime
from app_admin.models import dimDate
from django.shortcuts import render, redirect

def populate_dim_date(request):
    """Populate the dimDate table with dates from 1950-01-01 to 2099-12-31."""
    
    # Clear existing data to avoid duplicates
    dimDate.objects.all().delete()
    start_date = datetime.date(1950, 1, 1)
    end_date = datetime.date(2099, 12, 31)
    delta = datetime.timedelta(days=1)
    current_date = start_date

    dates_to_create = []

    while current_date <= end_date:
        dates_to_create.append(
            dimDate(
                date=current_date,
                year=current_date.year,
                month=current_date.month,
                day=current_date.day,
                month_name=current_date.strftime("%B"),
                day_name=current_date.strftime("%A"),
                quarter=(current_date.month - 1) // 3 + 1,
                is_weekend=current_date.weekday() >= 5
            )
        )
        current_date += delta

    # insert in chunks to avoid memory issues
    dimDate.objects.bulk_create(dates_to_create, batch_size=5000)

    print("✅ dimDate table populated successfully from 1950 to 2099.")
