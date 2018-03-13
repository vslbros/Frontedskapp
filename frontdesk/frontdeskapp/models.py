# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests
from django.core.mail import send_mail

SERVICETYPE = (
	('DOCTOR', "DOCTOR"),
	('LAUNDRY', "LAUNDRY"),
	('TRANSPORT', "TRANSPORT"),
)
ROOMSTATUS = (
	('AVAILABLE', "AVAILABLE"),
	('NOT AVAILABLE', "NOT AVAILABLE"),
	('CLEANING', "CLEANING"),
        ('UNDER REPAIR', "UNDER REPAIR"),
)


# Create your models here.
from django.db import models
class Customerdetails(models.Model):
        customer_name = models.CharField(max_length=50, null=False, blank=False)
        no_of_adults = models.IntegerField(verbose_name="No of Adults", default=1, blank=True)
        no_of_children = models.IntegerField(verbose_name="Children", default=0, blank=True)
        purpose = models.CharField(max_length=20)
        nationality = models.CharField(max_length=20)
        aadhar_ID = models.BigIntegerField(verbose_name="Adhaar")
        phone_no = models.BigIntegerField(verbose_name="Phone", max_length=10)
        occupation = models.CharField(max_length=20, null=True, blank=True)
        email_ID = models.CharField(max_length=20, null=True, blank=True)

        def __str__(self):
                return self.customer_name

        class Meta:
                db_table = 'customer_details'
                verbose_name = 'Customer Detail'
                verbose_name_plural = "Customer Details"

class Roomdetails(models.Model):
        room_type = models.CharField(max_length=50, null=False, blank=False)
        no_of_adults = models.IntegerField(verbose_name="No of Adults", default=1, blank=False)
        no_of_children = models.IntegerField(verbose_name="Children", default=0, blank=False)
        room_number = models.IntegerField(verbose_name="Room No.", null=False)
        rent = models.IntegerField(verbose_name="Rent", null=False)
        status = models.CharField(max_length=20, choices= ROOMSTATUS)

        def __str__(self):
                return self.room_type

        class Meta:
                db_table = 'room_details'
                verbose_name = 'Room Detail'
                verbose_name_plural = "Room Details"

class Servicedetails(models.Model):
        service_type = models.CharField(max_length=10, choices = SERVICETYPE)
        service_price = models.IntegerField(verbose_name="Service Price", null=True)

        def __str__(self):
                return self.service_type

        class Meta:
                db_table = 'service_details'
                verbose_name = 'Service Detail'
                verbose_name_plural = "Service Details"

class Resources(models.Model):
        resource_name = models.CharField(max_length=30)
        resource_availability = models.IntegerField(verbose_name="Resource Availability", null=True)
        price = models.IntegerField(verbose_name="Price")

        def __str__(self):
                return self.resource_name

        class Meta:
                db_table = 'resources'
                verbose_name = 'Resource'
                verbose_name_plural = "Resources"

class Bookedrooms(models.Model):
        customer_ID =  models.ForeignKey(Customerdetails, on_delete=models.DO_NOTHING)
        booking_unique_no =  models.CharField(max_length=30, null= False, blank=True)
        room_ID = models.ForeignKey(Roomdetails, on_delete=models.DO_NOTHING)
        booking_date = models.DateTimeField(default=datetime.now)
        arrival_time = models.DateTimeField(default=datetime.now)
        departure_time = models.DateTimeField(default=datetime.now()+timedelta(days=1))
        relationship = models.CharField(max_length=20, null=True, blank=True)
        advance_receipt_no = models.IntegerField(verbose_name="Advance Reciept", null=True, blank=True)
        service_ID = models.ForeignKey(Servicedetails, verbose_name="Service Required", on_delete=models.DO_NOTHING, null=True, blank=True)
        service_qty = models.IntegerField(verbose_name="Service Quantity", default=0)
        resource_ID = models.ForeignKey(Resources,verbose_name="Extra Resource Required", on_delete=models.DO_NOTHING, null=True, blank=True)
        resource_qty = models.IntegerField(verbose_name="Resource Quantity", default=0)
        
        def __str__(self):
                return self.booking_unique_no

        class Meta:
                db_table = 'booked_rooms'
                verbose_name = 'Booked Room'
                verbose_name_plural = "Booked Rooms"

class Billing(models.Model):
        booked_room_ID = models.ForeignKey(Bookedrooms, on_delete=models.DO_NOTHING)
        biling_date = models.DateTimeField(default=datetime.now)
        room_ID = models.ForeignKey(Roomdetails, on_delete=models.DO_NOTHING, default=1)
        customer_ID =  models.ForeignKey(Customerdetails, on_delete=models.DO_NOTHING, default=1)
        amount = models.IntegerField(verbose_name="Amount", blank=True)
        paid = models.BooleanField()

        class Meta:
                db_table = 'billing'
                verbose_name = 'Billing'
                verbose_name_plural = "Billings"


class Reservation(models.Model):
        customer_name = models.CharField(max_length=50)
        room_ID = models.ForeignKey(Roomdetails, on_delete=models.DO_NOTHING)
        reservation_created_date = models.DateTimeField(default=datetime.now)
        reserved_date = models.DateTimeField(default=datetime.now)

        def __str__(self):
                return self.customer_name

        class Meta:
                db_table = 'reservation'
                verbose_name = 'Reservation'
                verbose_name_plural = "Reservations"


class Employee_details(models.Model):
        employee_name = models.CharField(max_length=30)
        nationality = models.CharField(max_length=20)
        DOB = models.DateTimeField(default=datetime.now)
        address = models.CharField(max_length=50)
        contact_no = models.BigIntegerField(verbose_name="Contact")
        email_ID = models.CharField(max_length=30, verbose_name="Email")
        aadhar_ID = models.BigIntegerField(verbose_name="Aadhaar")
        leaves_available = models.IntegerField(verbose_name="Leaves Available", default=0)
        gross_salary = models.IntegerField(verbose_name="Gross Salary",  default=0)
        
        def __str__(self):
                return self.employee_name

        class Meta:
                db_table = 'employee_details'
                verbose_name = 'Employee Detail'
                verbose_name_plural = "Employee Details"

class Eattendance_details(models.Model):
        emp_ID = models.ForeignKey(Employee_details, on_delete=models.DO_NOTHING)
        leave_date = models.DateTimeField(default=datetime.now)
        reason = models.CharField(max_length=50,  verbose_name="Leave Reason", null=True, blank=True,  default='Fever')

        class Meta:
                db_table = 'eattendance_details'
                verbose_name = 'Eattendance Detail'
                verbose_name_plural = "Eattendance Details"

class Esalary_details(models.Model):
        emp_ID = models.ForeignKey(Employee_details, on_delete=models.DO_NOTHING, blank=True)
        salary_date = models.DateTimeField(default=datetime.now, blank=True)
        salary = models.IntegerField(verbose_name="Salary", default=0, blank=True)

        class Meta:
                db_table = 'esalary_details'
                verbose_name = 'Esalary Detail'
                verbose_name_plural = "Esalary Details"

@receiver(post_save, sender=Bookedrooms)
def update_extra_purchase(sender, instance, **kwargs):
        if instance.resource_ID:
                instance.resource_ID.resource_availability -= instance.resource_qty
                instance.resource_ID.save()
        instance.room_ID.status = 'NOT AVAILABLE'
        instance.room_ID.save()

        message = 'Hi %s, Your Booking ID is %s, please save the Booking ID. Thank you and have a wonderfull stay.' % (instance.customer_ID.customer_name, instance.booking_unique_no)
        to_email = instance.customer_ID.email_ID
        mobile_no = instance.customer_ID.phone_no
        send_sms(mobile_no, message)
        send_email(message, to_email)

@receiver(post_save, sender=Billing)
def update_room_status(sender, instance, **kwargs):
        if instance.paid == True:
                instance.room_ID.status = 'CLEANING'
                instance.room_ID.save()

        to_email = instance.customer_ID.email_ID
        mobile_no = instance.customer_ID.phone_no
        message = 'Hi %s, Your payment is Successful of Rs.%s for booking id %s. Thank you and Please visit again' % (instance.customer_ID.customer_name, instance.amount, instance.booked_room_ID.booking_unique_no)
        send_sms(mobile_no, message)
        send_email(message, to_email)

def send_sms(mobile_no, message):
        way_2_sms_url = 'http://site24.way2sms.com/Login1.action?'
        way_2_sms_cred = {'username': '9740729688', 'password': 'T8922H'}
        session_obj = requests.Session()
        session_obj.headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0"
        url_response = session_obj.post(way_2_sms_url,data=way_2_sms_cred)
        jsid = session_obj.cookies.get_dict()['JSESSIONID'][4:]
        # Send SMS
        payload = {'ssaction':'ss','Token':jsid, 'mobile':mobile_no, 'message':message, 'msgLen':'129'}
        msg_url = 'http://site24.way2sms.com/smstoss.action'
	url_response = session_obj.post(msg_url,data=payload)
        # logout
        session_obj.get('http://site24.way2sms.com/entry?ec=0080&id=dwks')
        session_obj.close()

def send_email(message, to_email):
        subject = 'Payment Successful'
        from_email = 'booking@vslbros.com'
        send_mail(subject, message, from_email, [to_email], fail_silently=False,)

            

