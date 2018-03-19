# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages
from django.db import connection, transaction
from datetime import datetime, timedelta
import re
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

email_id_regex = re.compile('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')
name_regex = re.compile('^([a-zA-Z]+[\s-]?)*$')

class CustomerdetailsAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'no_of_adults', 'no_of_children', 'aadhar_ID', 'phone_no', 'occupation', 'email_ID', 'purpose', 'nationality']
    search_fields = ['customer_name', 'phone_no', 'aadhar_ID']

    def save_model(self, request, obj, form, change):
        if (obj.customer_name) and (not name_regex.match(obj.customer_name)):
            messages.set_level(request, messages.ERROR)
            msg = 'Please enter a valid customer name. Customer Name cannot contain numbers. (Entered Customer Name is %s)' % obj.customer_name
            messages.error(request, msg)
            return
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
        if (obj.email_ID) and (not email_id_regex.match(obj.email_ID)):
            messages.set_level(request, messages.ERROR)
            msg = 'Enter a valid Email ID. Example: abc@xyz.com or abc@xyz.co.in (Entered email ID %s)' % obj.email_ID
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

class BillingAdmin(admin.ModelAdmin):
    list_display = ['booked_room_ID', 'room_amount', 'service_amount', 'resource_amount', 'total', 'paid']
    readonly_fields = ['amount', 'room_ID', 'customer_ID']
    actions = ['billing']

    def billing(self, request, queryset):
        queryset_list = queryset.values()
        query_dict = queryset_list[0]
        customer_id_value = query_dict['customer_ID_id']
        booked_room_id_value = query_dict['booked_room_ID_id']
        cursor = connection.cursor()

        import pdb
        pdb.set_trace()
        cursor.execute("SELECT service_ID_id from booked_rooms where id=%s", (booked_room_id_value,))
        queryset = cursor.fetchone()
        (service_id_value,) = queryset
        #(service_id_value = service_id_value

        cursor.execute("SELECT resource_ID_id from booked_rooms where id=%s", (booked_room_id_value,))
        queryset = cursor.fetchone()
        (resource_id_value,) = queryset

        service_type = '-' 
        service_price = 0 
        service_qty = 0
        resource_name = '-'
        resource_price = 0 
        resource_qty = 0
        if (not service_id_value) and (not resource_id_value):
            cursor.execute("SELECT c.customer_name, rm.room_type, rm.rent, br.arrival_time, br.departure_time from booked_rooms br INNER JOIN customer_details c ON c.id=br.customer_ID_id INNER JOIN room_details rm ON rm.id=br.room_ID_id where br.customer_ID_id=%s", (customer_id_value,))
            queryset = cursor.fetchone()
            (customer_name, room_type, room_rent, arrival_time, departure_time) = queryset
        elif not service_id_value:
            cursor.execute("SELECT c.customer_name, r.resource_name, r.price, br.resource_qty, rm.room_type, rm.rent, br.arrival_time, br.departure_time from booked_rooms br  INNER JOIN resources r ON r.id=br.resource_ID_id INNER JOIN customer_details c ON c.id=br.customer_ID_id INNER JOIN room_details rm ON rm.id=br.room_ID_id where br.customer_ID_id=%s", (customer_id_value,))
            queryset = cursor.fetchone()
            (customer_name, resource_name, resource_price, resource_qty, room_type, room_rent, arrival_time, departure_time) = queryset
        elif not resource_id_value:
            cursor.execute("SELECT c.customer_name, s.service_type, s.service_price, br.service_qty, rm.room_type, rm.rent, br.arrival_time, br.departure_time from booked_rooms br  INNER JOIN service_details s ON s.id=br.service_ID_id INNER JOIN customer_details c ON c.id=br.customer_ID_id INNER JOIN room_details rm ON rm.id=br.room_ID_id where br.customer_ID_id=%s", (customer_id_value,))
            queryset = cursor.fetchone()
            (customer_name, service_type, service_price, service_qty, room_type, room_rent, arrival_time, departure_time) = queryset
        else:
            cursor.execute("SELECT c.customer_name, r.resource_name, r.price, s.service_type, s.service_price, br.service_qty, br.resource_qty, rm.room_type, rm.rent, br.arrival_time, br.departure_time from booked_rooms br INNER JOIN resources r ON r.id=br.resource_ID_id INNER JOIN service_details s ON s.id=br.service_ID_id INNER JOIN customer_details c ON c.id=br.customer_ID_id INNER JOIN room_details rm ON rm.id=br.room_ID_id where br.customer_ID_id=%s", (customer_id_value,))
            queryset = cursor.fetchone()
            (customer_name, resource_name, resource_price, service_type, service_price, service_qty, resource_qty, room_type, room_rent, arrival_time, departure_time) = queryset
        
        file_name = 'Biling_%s' % (customer_name)
        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(['Customer Name', 'Arrival Time', 'Departure Time', 'Room', 'Room Price', 'Resource', 'Resource Quantity', 'Resource Price', 'Service', 'Service Quantity', 'Service Price', 'CGST', 'CGST Price', 'SGST', 'SGST Price', 'Total Amount'])

        calculate_resource_price = int(resource_price) * int(resource_qty)
        calculate_service_price = int(service_price) * int(service_qty)
        arrival_time = arrival_time.strftime('%d/%m/%Y')
        departure_time = departure_time.strftime('%d/%m/%Y')

        total_amount = room_rent + calculate_resource_price + calculate_service_price
        gst = 0
        if total_amount > 1000:
            gst = (total_amount/100) * 6
            total_amount = total_amount + (gst * 2)
        writer.writerow([customer_name, arrival_time, departure_time, room_type, room_rent, resource_name, resource_qty, calculate_resource_price, service_type, service_qty, calculate_service_price, '6%', gst, '6%', gst, total_amount])
        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response_cd = 'attachment; filename=%s.csv' % file_name
        response['Content-Disposition'] = response_cd
        return response
    billing.short_description = "Print Bill"

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
        if obj.departure_time:
            arrival_date = obj.arrival_time
            departure_date = obj.departure_time
            if departure_date.date() <= arrival_date.date():
                messages.set_level(request, messages.ERROR)
                msg = 'Departure date cannot be less than or equal to Arrival Date. Departure date selected is %s, Arrival Date selected is %s' % (departure_date.strftime('%d/%m/%Y'), arrival_date.strftime('%d/%m/%Y'))
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