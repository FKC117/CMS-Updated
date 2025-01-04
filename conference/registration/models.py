from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth.models import User

# Create your models here.
# Create User Profile Model START------------------------------------------------------------------------------------#
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email


# Create Event Models START------------------------------------------------------------------------------------#

from django.urls import reverse

class Event(models.Model):
    EVENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('upcoming', 'Upcoming'),
    ]
    REGISTRATION_STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Starting Soon', 'Starting Soon'),
    ]
    name = models.CharField(max_length=200)
    slogan = models.CharField(max_length=200, default="Empowering Survivors, Education & Support")
    year = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200, blank=True, null=True)
    event_status = models.CharField(max_length=10, choices=EVENT_STATUS_CHOICES, default='upcoming')
    event_logo = models.ImageField(upload_to='media/event_logos/', blank=True, null=True)
    modal_image = models.ImageField(upload_to='media/modal_images/', blank=True, null=True)
    event_hero_image = models.ImageField(upload_to='media/hero_images/', blank=True, null=True, help_text='Upload an image for the hero section of the event page. Recomended size: 1920x1080')
    registration = models.CharField(max_length=50, choices=REGISTRATION_STATUS_CHOICES, default='Open')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    keywords = models.CharField(max_length=1000, blank=True, null=True, help_text='Enter Keywords seperated by comma')
    author = models.CharField(max_length=100, blank=True, null=True)
    og_image = models.ImageField(upload_to='static/images/og_images/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name} {self.year}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.year}"
    def get_absolute_url(self):
        return reverse('registration:home', args=[self.id])



#Feature Speaker Models START------------------------------------------------------------------------------------#
class FeatureSpeaker(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    speciality = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    biography = models.TextField(default='No biography available')
    image = models.ImageField(upload_to='images/', default='images/default.jpg')

    class Meta:
        verbose_name_plural = 'Feature Speakers'

    def __str__(self):
        return self.name

#Feature Speaker Models END------------------------------------------------------------------------------------#

#Department Models START------------------------------------------------------------------------------------#
class Department(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

#Department Models END------------------------------------------------------------------------------------#

#Participant Models START------------------------------------------------------------------------------------#
class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    degree = models.CharField(max_length=50)
    year_of_graduation = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    organization = models.CharField(max_length=100)
    email = models.EmailField(blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, default='Bangladesh')
    BMDC_registration_number = models.CharField(max_length=20, blank=True, null=True)
    approved = models.BooleanField(default=False)
    denied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'event')
        unique_together = ('phone', 'event')

    def __str__(self):
        return self.name

#Participant Models END------------------------------------------------------------------------------------#

# Creating Payment Status Models START------------------------------------------------------------------------------------#
class PaymentStatus(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('completed', 'Completed'),
        ('unpaid', 'Unpaid'),
        ('initiated', 'Initiated'),
        ('failed', 'Failed')
    ]
    
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE, related_name='payment_statuses')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)  # bKash Payment ID
    merchant_invoice_number = models.CharField(max_length=255, unique=True)  # Merchant Invoice Number
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    trxID = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice = models.FileField(upload_to='media/invoices/', blank=True, null=True)
    email_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.event:
            self.amount = self.event.amount  # Automatically set amount from the event
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.participant.name} - {self.event.name} - {self.amount} - {self.status}"
    
    class Meta:
        verbose_name_plural = 'Payment Status'

# Creating Payment Status Models End --------------------------------------------------------------------#


# Hall room Model START---------------------------------------------------------------------------------#
class HallRoom(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Hall Room'

    def __str__(self):
        return self.name
    
### Hall room Model END---------------------------------------------------------------------------------#


### Program day-----------------------------------------------------------------------------------------#
class ProgramDay(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default='Day 1')
    date = models.DateField()
    class Meta:
        verbose_name_plural = 'Program Day'
    def __str__(self):
        return self.name

### Timeslot Model START---------------------------------------------------------------------------------#
class TimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    program_day = models.ForeignKey(ProgramDay, on_delete=models.CASCADE, related_name='ProgramDay')
    start_time = models.TimeField()
    end_time = models.TimeField()
    hall_room = models.ForeignKey(HallRoom, on_delete=models.CASCADE, related_name='timeslots')

    class Meta:
        verbose_name_plural = 'Time Slot'

    def __str__(self):
        start_time_formatted = self.start_time.strftime('%I:%M %p')
        end_time_formatted = self.end_time.strftime('%I:%M %p')
        return f"{self.hall_room} - {start_time_formatted} - {end_time_formatted}"
    
    def clean(self):
        super().clean()
        overlapping_time_slots = TimeSlot.objects.filter(
            program_day=self.program_day,
            hall_room=self.hall_room,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)

        if overlapping_time_slots.exists():
            raise ValidationError(_("This time slot overlaps with another time slot in the same program day and hall room."))
 
### Timeslot Model END---------------------------------------------------------------------------------#

#Abstract Submission Models START------------------------------------------------------------------------------------#
from django.contrib.auth.models import User
class AbstractSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=400)
    authors = models.CharField(max_length=500)
    institution = models.CharField(max_length=200)
    introduction = models.TextField()
    methods = models.TextField()
    results = models.TextField()
    conclusion = models.TextField()
    image = models.ImageField(upload_to='media/abstract_images/', null=True, blank=True)
    approved_for_presentation = models.BooleanField(default=False)
    approved_for_poster = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Abstract Submission'

    def __str__(self):
        return self.title
#Abstract Submission Models END------------------------------------------------------------------------------------#

# Chairperson Model START------------------------------------------------------------------------------------#

class Chairperson(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(unique=True, max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, default='Bangladesh')

    class Meta:
        verbose_name_plural = 'Chairperson'
    def __str__(self):
        return self.name

# Chairperson Model END------------------------------------------------------------------------------------#
# Panelist Model START------------------------------------------------------------------------------------#
class Panelist(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(unique=True, max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, default='Bangladesh')

    def __str__(self):
        return self.name

# Panelist Model END------------------------------------------------------------------------------------#

# Moderator Model START------------------------------------------------------------------------------------#
class Moderator(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(unique=True, max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, default='Bangladesh')

    def __str__(self):
        return self.name

# Moderator Model END------------------------------------------------------------------------------------#

#ProgramSchedule Model START------------------------------------------------------------------------------------#

class ProgramSchedule(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    abstract_submission = models.OneToOneField(AbstractSubmission, on_delete=models.CASCADE)
    presenter = models.TextField(null=True, blank=True)
    time_slots = models.ManyToManyField(TimeSlot, related_name='schedules')
    chairperson = models.ForeignKey(Chairperson, on_delete=models.SET_NULL, null=True, blank=True)
    panelist = models.ManyToManyField(Panelist, blank=True)
    moderator = models.ForeignKey(Moderator, on_delete=models.SET_NULL, null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    # is_parallel = models.BooleanField(default=False)


    class Meta:
        verbose_name_plural = 'Program Schedule'

    @property
    def title(self):
        return self.abstract_submission.title

    @property
    def authors(self):
        return self.abstract_submission.authors

    def clean(self):
        super().clean()
        
        # Check if the abstract is approved for presentation or poster
        if not self.abstract_submission.approved_for_presentation and not self.abstract_submission.approved_for_poster:
            raise ValidationError(_("Abstract must be approved for either presentation or poster to be included in the schedule."))

        # Check for duplicate schedules
        duplicates = ProgramSchedule.objects.filter(abstract_submission__title=self.abstract_submission.title, abstract_submission__authors=self.abstract_submission.authors)
        if self.pk:
            duplicates = duplicates.exclude(pk=self.pk)
        if duplicates.exists():
            raise ValidationError(_("A program schedule with this title and author already exists."))

        # Check for overlapping schedules
        if self.pk:
            overlapping_schedules = ProgramSchedule.objects.filter(time_slots__in=self.time_slots.all()).distinct().exclude(pk=self.pk)  
            if overlapping_schedules.exists():
                overlapping_titles = ', '.join(overlapping_schedules.values_list('abstract_submission__title', flat=True))
                raise ValidationError(_(f"Warning: The schedule overlaps with existing schedules: {overlapping_titles}"))

    def __str__(self):
        return f"{self.title} by {self.authors}"
# ProgramSchedule Model END------------------------------------------------------------------------------------#

# Invitation Model START------------------------------------------------------------------------------------#
class Invitation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    message = models.TextField()
    image = models.ImageField(upload_to='media/invitation_images/', null=True, blank=True)
    
    def __str__(self):
        return self.name
   
# Invitation Model END------------------------------------------------------------------------------------#
# About the Conference Model START------------------------------------------------------------------------------------#
class AboutTheConference(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='media/about_images/', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'About the Conference'
    def __str__(self):
        return self.title
# About the Conference Model END------------------------------------------------------------------------------------#

# Sponsorship Models START------------------------------------------------------------------------------------#
from django.db import models

class Sponsor(models.Model):
    TITLE = 'Title'
    PLATINUM = 'Platinum'
    GOLDEN = 'Golden'
    SILVER = 'Silver'
    LOGISTICS = 'Logistics'
    MEDIA = 'Media'
    IT = 'IT'
    EVENT = 'Event'

    CATEGORY_CHOICES = [
        (TITLE, 'Title'),
        (PLATINUM, 'Platinum'),
        (GOLDEN, 'Golden'),
        (SILVER, 'Silver'),
        (LOGISTICS, 'Logistics'),
        (MEDIA, 'Media'),
        (IT, 'IT'),
        (EVENT, 'Event')
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='media/sponsor_images/', null=True, blank=True)
    category = models.CharField(max_length=200, choices=CATEGORY_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Sponsors'

    def __str__(self):
        return self.name
# Sponsorship Models END------------------------------------------------------------------------------------#


# EventImage and EventVideo Models START------------------------------------------------------------------------------------#

from django.db import models

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/event_images/')
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.caption or "Event Image"

class EventVideo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    youtube_url = models.URLField()
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.caption or "Event Video"
# EventImage and EventVideo Models END------------------------------------------------------------------------------------#

# Registration kit model START------------------------------------------------------------------------------------#
from django.db import models
from .models import PaymentStatus, Event

class RegistrationKit(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('not_issued', 'Not Issued'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registration_kits")
    payment_status = models.OneToOneField(PaymentStatus, on_delete=models.CASCADE, related_name="registration_kit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_issued')
    issued_at = models.DateTimeField(blank=True, null=True)  # To track when the kit was issued

    def __str__(self):
        return f"Kit for {self.payment_status.participant.name} - {self.event.name} ({self.status})"

    class Meta:
        verbose_name_plural = "Registration Kits"
        unique_together = ('event', 'payment_status')  # Ensure one kit per event and payment


# Registration kit model END------------------------------------------------------------------------------------#

# Bkash Payment Model START------------------------------------------------------------------------------------#
from django.db import models

class BkashData(models.Model):
    payment_id = models.CharField(max_length=255, unique=True)
    trx_id = models.CharField(max_length=255)
    mode = models.CharField(max_length=50)
    payment_create_time = models.CharField(max_length=150)
    payment_execute_time = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    intent = models.CharField(max_length=20)
    merchant_invoice = models.CharField(max_length=255)
    transaction_status = models.CharField(max_length=50)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    verification_status = models.CharField(max_length=50)
    payer_reference = models.CharField(max_length=255)
    payer_type = models.CharField(max_length=50)
    status_code = models.CharField(max_length=10)
    status_message = models.CharField(max_length=255)

    def __str__(self):
        return f"Payment {self.payment_id} - Status: {self.transaction_status}"
