# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django.db import connection, transaction
from datetime import datetime, timedelta
import StringIO
import csv
from django.http import HttpResponse
from .models import (Customerdetails, Roomdetails, Servicedetails, Resources, Bookedrooms, Billing,Reservation, Employee_details, Eattendance_details, Esalary_details)

MONTH = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}

INDIAN_PHONE_INITIAL_NUMBERS = [9, 8, 7, 6]

class CustomerdetailsAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'no_of_adults', 'no_of_children', 'aadhar_ID', 'phone_no', 'occupation', 'email_ID', 'purpose', 'nationality']

    def save_model(self, request, obj, form, change):
        old_resource_qty = 0
        if obj.phone_no:
            phone_no = str(obj.phone_no)
            if len(phone_no) != 10:
                messages.set_level(request, messages.ERROR)
                msg = 'Enter valid Phone No. Entered Phone No. is %s and consists of %s digits. Phone No. should have 10 Digits' % (phone_no, len(phone_no))
                messages.error(request, msg)
                return
            phone_initial_digit = phone_no[:1]
            if int(phone_initial_digit) not in INDIAN_PHONE_INITIAL_NUMBERS:
                messages.set_level(request, messages.ERROR)
                msg = 'Please enter valid Indian Phone No. Entered Phone No. is %s. Phone No. should start with 9/8/7/6' % (phone_no)
                messages.error(request, msg)
                return
        if obj.aadhar_ID:
            addhard_id = str(obj.aadhar_ID)
            if len(addhard_id) != 12:
                messages.set_level(request, messages.ERROR)
                msg = 'Enter valid Adhaar No. Entered Adhaar No. is %s and consists of %s digits. Adhaar No. should have 12 Digits' % (addhard_id, len(addhard_id))
                messages.error(request, msg)
                return
        obj.save()

class RoomdetailsAdmin(admin.ModelAdmin):
    list_display = ['room_type', 'no_of_adults', 'no_of_children', 'room_number', 'rent', 'status']
    list_filter = ['status']

class ServicedetailsAdmin(admin.ModelAdmin):
    list_display = ['service_type', 'service_price']

class ResourcesAdmin(admin.ModelAdmin):
    list_display = ['resource_name', 'resource_availability', 'price']

class ReservationAdmin(admin.ModelAdmin):
    def room_type(self, object):
        return object.room_ID.room_type
    room_type.short_description = 'room_type'
    search_fields = ['customer_name', 'reservation_created_date', 'reserved_date']
    list_display = ['customer_name', 'room_type', 'reservation_created_date', 'reserved_date']

class Employee_detailsAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'nationality', 'DOB', 'address', 'contact_no', 'email_ID', 'aadhar_ID', 'leaves_available','gross_salary']
    actions = ['download_csv_present_month']

    def download_csv_present_month(self, request, queryset):
        to_date = datetime.now()
        from_date = datetime.now() - timedelta(days=30)
        if to_date.day < 30:
            messages.set_level(request, messages.ERROR)
            msg = 'Salary cannot be generated before %s/%s/%s' % ('30', to_date.month, to_date.year)
            messages.error(request, msg)
            return
        file_name = 'Report_%s_Month_%s' % (MONTH[to_date.month], to_date.year)
        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(['Employee ID', 'Employee Name','Salary Date', 'Salary',])

        cursor = connection.cursor()
        cursor.execute("SELECT id, employee_name, gross_salary from employee_details")
        case_id_queryset = cursor.fetchall()

        for (emp_id, emp_name, gross_salary,) in case_id_queryset:
            cursor.execute("SELECT count(*) from eattendance_details where emp_ID_id=%s and leave_date BETWEEN %s and %s", (emp_id, from_date, to_date,))
            queryset = cursor.fetchone()
            for leave_count in queryset:
                if leave_count:
                    salary = ((gross_salary/30) * (30 - leave_count))
                else:
                    salary = gross_salary
                writer.writerow([emp_id, emp_name, to_date, salary])
        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response_cd = 'attachment; filename=%s.csv' % file_name
        response['Content-Disposition'] = response_cd
        return response
    download_csv_present_month.short_description = "Download Present Month Salary"

class Eattendance_detailsAdmin(admin.ModelAdmin):
    list_display = ['emp_ID', 'leave_date', 'reason']

class Esalary_detailsAdmin(admin.ModelAdmin):
    list_display = ['emp_ID', 'employee_name', 'salary_date', 'salary']

    def employee_name(self, object):
        return object.emp_ID.employee_name
    employee_name.short_description = 'Employee Name'

    def save_model(self, request, obj, form, change):
        to_date = datetime.now()
        from_date = datetime.now() - timedelta(days=30)
        '''if to_date.day < 30:
            messages.set_level(request, messages.ERROR)
            msg = 'Salary cannot be generated before %s/%s/%s' % ('30', to_date.month, to_date.year)
            messages.error(request, msg)
            return'''

        cursor = connection.cursor()
        cursor.execute("SELECT id, employee_name, gross_salary from employee_details")
        case_id_queryset = cursor.fetchall()
        import pdb
        pdb.set_trace()

        insert_list = []
        for (emp_id, emp_name, gross_salary,) in case_id_queryset:
            cursor.execute("SELECT count(*) from eattendance_details where emp_ID_id=%s and leave_date BETWEEN %s and %s", (emp_id,from_date,to_date,))
            queryset = cursor.fetchone()
            for leave_count in queryset:
                if leave_count:
                    salary = ((gross_salary/30) * (30 - leave_count))
                else:
                    salary = gross_salary
                insert_list.append(Esalary_details(salary=salary))
                obj.bulk_create(insert_list)

class BillingAdmin(admin.ModelAdmin):
    list_display = ['booked_room_ID', 'room_amount', 'service_amount', 'resource_amount', 'total', 'paid']
    readonly_fields = ['amount', 'room_ID', 'customer_ID']

    def resource_amount(self, object):
        if object.booked_room_ID.service_ID:
            return object.booked_room_ID.resource_ID.price
    resource_amount.short_description = 'Resource Charges'

    def service_amount(self, object):
        if object.booked_room_ID.service_ID:
            return object.booked_room_ID.service_ID.service_price
    service_amount.short_description = 'Service Charges'

    def room_amount(self, object):
        return object.room_ID.rent
    room_amount.short_description = 'Room Charges'

    def total(self, object):
        return object.amount
    total.short_description = 'Total'

    def save_model(self, request, obj, form, change):
        resource_amount = 0
        service_amount = 0 
        if obj.booked_room_ID:
            days_count_obj = obj.booked_room_ID.departure_time - obj.booked_room_ID.arrival_time
            days_count = days_count_obj.days
            (days, seconds) = divmod(days_count * 86400, 60)
            (days, seconds) = divmod(days/60, 24)
            days = days + 1
            room_amount =  obj.booked_room_ID.room_ID.rent * days
            if obj.booked_room_ID.resource_ID:
                resource_amount = obj.booked_room_ID.resource_ID.price * obj.booked_room_ID.resource_qty
            if obj.booked_room_ID.service_ID:
                service_amount = obj.booked_room_ID.service_ID.service_price * obj.booked_room_ID.service_qty
            obj.amount = room_amount+resource_amount+service_amount
            obj.room_ID = obj.booked_room_ID.room_ID
            obj.customer_ID = obj.booked_room_ID.customer_ID
        obj.save()

class BookedroomsAdmin(admin.ModelAdmin):
    def room_type(self, object):
        return object.room_ID.room_type
    room_type.short_description = 'room_type'

    def customer_name(self, object):
        return object.customer_ID.customer_name
    customer_name.short_description = 'customer_name'

    def service_type(self, object):
        if object.service_ID:
            return object.service_ID.service_type
    service_type.short_description = 'service_type'

    def resource_name(self, object):
        if object.resource_ID:
            return object.resource_ID.resource_name
    resource_name.short_description = 'resource_name'

    list_display = ['customer_name', 'booking_unique_no', 'booking_date', 'room_type', 'arrival_time', 'departure_time', 'relationship', 'advance_receipt_no', 'service_type', 'service_qty', 'resource_name', 'resource_qty']
    readonly_fields = ['booking_unique_no', 'booking_date']
    actions = ['download_csv_one_week', 'download_csv_one_month', 'download_csv_one_day', 'download_csv_three_day']

    def csv_base(self, file_name, no_of_days, queryset):
        file_name = '%s%s' % (file_name, datetime.now().strftime('%Y%m%d%H%M%s')[:16])
        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(['booking_unique_no', 'booking_date','arrival_time', 'departure_time',])

        to_date = datetime.now()
        from_date = datetime.now() - timedelta(days=no_of_days)
        queryset = queryset.filter(booking_date__range=[from_date, to_date])
        for s in queryset:
            writer.writerow([s.booking_unique_no, s.booking_date, s.arrival_time, s.departure_time])
        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response_cd = 'attachment; filename=%s.csv' % file_name
        response['Content-Disposition'] = response_cd
        return response

    def download_csv_one_week(self, request, queryset):
        file_name = 'Report_1_Week_'
        response = self.csv_base(file_name, 7, queryset)
        return response
    download_csv_one_week.short_description = "Download 1 Week Report"

    def download_csv_one_month(self, request, queryset):
        file_name = 'Report_1_Month_'
        response = self.csv_base(file_name, 30, queryset)
        return response
    download_csv_one_month.short_description = "Download 1 Month Report "

    def download_csv_one_day(self, request, queryset):
        file_name = 'Report_1_day_'
        response = self.csv_base(file_name, 1, queryset)
        return response
    download_csv_one_day.short_description = "Download 1 Day Report "

    def download_csv_three_day(self, request, queryset):
        file_name = 'Report_3_days_'
        response = self.csv_base(file_name, 3, queryset)
        return response
    download_csv_three_day.short_description = "Download 3 Days Report "

    def get_resource_count(self, obj, old_resource_qty, request):
        if obj.resource_ID:
            if old_resource_qty and old_resource_qty > 0:
                resource_qty = obj.resource_qty - old_resource_qty
            else:
                resource_qty = obj.resource_qty
            if obj.resource_ID.resource_availability < resource_qty:
                messages.set_level(request, messages.ERROR)
                msg = 'Only %s resources are available. Please reduce the request of %s below %s' % (obj.resource_ID.resource_availability, obj.resource_qty, obj.resource_ID.resource_availability)
                messages.error(request, msg)
                return

    def save_model(self, request, obj, form, change):
        old_resource_qty = 0
        if obj.arrival_time:
            selected_date = obj.arrival_time
            today = datetime.now()
            if selected_date.date() < today.date():
                messages.set_level(request, messages.ERROR)
                msg = 'Past date cannot be set as Arrival Date. Selected date is %s, Todays Date is %s' % (selected_date.strftime('%d/%m/%Y'), today.strftime('%d/%m/%Y'))
                messages.error(request, msg)
                return
        if obj.booking_unique_no:
            cursor = connection.cursor()
            cursor.execute("SELECT arrival_time, departure_time, booking_date, resource_qty from booked_rooms where booking_unique_no=%s", (obj.booking_unique_no,))
            queryset = cursor.fetchone()
            (old_arrival_time, old_depature_time, old_booking_date, old_resource_qty) = queryset
            self.get_resource_count(obj, old_resource_qty, request)
            obj.arrival_time = old_arrival_time
            obj.departure_time = old_depature_time
            obj.booking_date = old_booking_date
        else:
            self.get_resource_count(obj, old_resource_qty, request)
            obj.booking_unique_no = '%s%s' % (obj.customer_ID.customer_name[:3], datetime.now().strftime('%Y%m%d%H%M%s')[:16])
        obj.save()


# Register your models here.
admin.site.register(Customerdetails, CustomerdetailsAdmin)
admin.site.register(Roomdetails, RoomdetailsAdmin)
admin.site.register(Servicedetails, ServicedetailsAdmin)
admin.site.register(Resources, ResourcesAdmin)
admin.site.register(Bookedrooms, BookedroomsAdmin)
admin.site.register(Billing, BillingAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Employee_details, Employee_detailsAdmin)
admin.site.register(Eattendance_details, Eattendance_detailsAdmin)
#admin.site.register(Esalary_details, Esalary_detailsAdmin)