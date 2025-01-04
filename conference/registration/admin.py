from django.db.models import Q
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import FeatureSpeaker, Participant, AbstractSubmission, Department, HallRoom, TimeSlot, ProgramDay, ProgramSchedule, Invitation, AboutTheConference, Sponsor, Event, Chairperson, Panelist, Moderator, PaymentStatus, UserProfile
from .forms import AbstractSubmissionForm, RegistrationForm, ProgramScheduleForm
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.core.mail import send_mail
from .resources import ParticipantResource, AbstractSubmissionResource, TimeSlotResource, PaymentStatusResource, RegistrationKitResource
# SchedulingResource
from .pdf_utils import generate_abstract_pdf
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from .views import send_approval_email


User = get_user_model()  # Getting the user model.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'country')
admin.site.register(UserProfile, UserProfileAdmin)
# Register your models here.
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('name', 'event')
    list_filter = ('event',)

admin.site.register(Invitation, InvitationAdmin)

class AboutTheConferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'event')
    list_filter = ('event',)

admin.site.register(AboutTheConference, AboutTheConferenceAdmin)

class ChairpersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'country', 'event')
    list_filter = ('event',)
admin.site.register(Chairperson, ChairpersonAdmin)

class PanelistAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'country', 'event')
    list_filter = ('event',)
admin.site.register(Panelist, PanelistAdmin)

class ModeratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'event')
    list_filter = ('event',)
admin.site.register(Moderator, ModeratorAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'id','year', 'location', 'start_date', 'event_status', 'registration')
    list_filter = ('year', 'event_status')
admin.site.register(Event, EventAdmin)

class FeatureSpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality', 'institution', 'event')
    list_filter = ('event',)
admin.site.register(FeatureSpeaker, FeatureSpeakerAdmin)

# Event Specific Participants admin view START------------------------------------------------------------------------------#
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def approve_participants(modeladmin, request, queryset):
    for participant in queryset:
        if not User.objects.filter(email=participant.email).exists():
            password = get_random_string(length=12)
            user = User.objects.create_user(username=participant.email, email=participant.email, password=password)
            include_password = True
        else:
            user = User.objects.get(email=participant.email)
            password = None
            include_password = False

        if not participant.approved:
            participant.approved = True
        if participant.denied:
            participant.denied = False
        participant.save()
        send_consolidated_email(participant, password, include_password)

def send_consolidated_email(participant, password, include_password):
    event = participant.event
    subject = f'Your Registration for {event.name} {event.year} is Approved!'
    payment_url = f'http://http://127.0.0.1:8000/payment?event_id={event.id}&participant_id={participant.id}'
    try:
        context = {
            'participant': participant,
            'event': event,
            'payment_url': payment_url
        }
        if include_password:
            context['password'] = password

        html_content = render_to_string('consolidated_email.html', context)
        text_content = strip_tags(html_content)
        from_email = 'no-reply@example.com'
        recipient_list = [participant.email]

        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Error sending consolidated email: {e}")


def deny_participants(modeladmin, request, queryset):
    queryset.update(denied=True, approved=False)

approve_participants.short_description = "Approve selected participants"
deny_participants.short_description = "Deny selected participants"

class ParticipantAdmin(ImportExportModelAdmin):
    resource_class = ParticipantResource
    list_display = ('name', 'email', 'phone', 'department', 'organization', 'BMDC_registration_number', 'country', 'created_at', 'approved', 'denied', 'event')
    search_fields = ('name', 'phone', 'organization', 'BMDC_registration_number')
    list_filter = ('approved', 'denied', 'country', 'event')  # Add filters
    actions = [approve_participants, deny_participants]

admin.site.register(Participant, ParticipantAdmin)


from import_export.admin import ImportExportModelAdmin
from .models import PaymentStatus
from .resources import PaymentStatusResource  # Import the custom resource

class PaymentStatusAdmin(ImportExportModelAdmin):
    resource_class = PaymentStatusResource  # Use the custom resource
    list_display = ('participant', 'event', 'status', 'amount', 'merchant_invoice_number', 'transaction_id', 'trxID', 'invoice', 'email_sent', 'updated_at')
    search_fields = ('participant__name', 'participant__email', 'event__name', 'merchant_invoice_number', 'transaction_id', 'trxID', 'email_sent')
    list_filter = ('status', 'event')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(participant__approved=True)

admin.site.register(PaymentStatus, PaymentStatusAdmin)

# Departments admin view START------------------------------------------------------------------------------#
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'event')
    search_fields = ('name',)
    list_filter = ('event',)
# Departments admin view END-----------------------------------------------------------------------------#



class HallRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'event')
    list_filter = ('event',)
admin.site.register(HallRoom, HallRoomAdmin)
class TimeSlotAdmin(ImportExportModelAdmin):
    resource_class = TimeSlotResource
    list_display = ('start_time', 'end_time', 'program_day', 'hall_room', 'event')
    search_fields = ('hall_room', 'program_day')
    list_filter = ('program_day', 'hall_room', 'event')
admin.site.register(TimeSlot, TimeSlotAdmin)

# Program Day admin view START------------------------------------------------------------------------------#
class ProgramDayAdmin(admin.ModelAdmin):
    list_display = ('event', 'date', 'name')
    list_filter = ('event', 'date', 'name')
admin.site.register(ProgramDay, ProgramDayAdmin)

# Abstracts admin view START------------------------------------------------------------------------------#
def approve_for_presentation(modeladmin, request, queryset):
    queryset.update(approved_for_presentation=True, approved_for_poster=False)

    # send an approval email
    for abstract in queryset:
        send_approval_email(abstract, "Presentation")

def approve_for_poster(modeladmin, request, queryset):
    queryset.update(approved_for_poster=True, approved_for_presentation=False)

    # send an approval email
    for abstract in queryset:
        send_approval_email(abstract, "Poster")
def export_as_pdf(modeladmin, request, queryset):
    if queryset.exists():
        event = queryset.first().event
        buffer = generate_abstract_pdf(event, queryset)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="abstracts.pdf"'
        return response
    else:
        messages.error(request, "No abstracts selected for export.")
        return HttpResponseRedirect(request.get_full_path())

export_as_pdf.short_description = "Export selected abstracts as PDF"

class AbstractSubmissionAdmin(ImportExportModelAdmin):
    list_display = ('title', 'authors', 'institution', 'user', 'approved_for_presentation', 'approved_for_poster', 'event')
    search_fields = ('title', 'authors')
    list_filter = ('approved_for_presentation', 'approved_for_poster', 'event')
    actions = [approve_for_presentation, approve_for_poster, export_as_pdf]
    fields = ['user', 'title', 'authors', 'institution', 'introduction', 'methods', 'results', 'conclusion', 'image', 'approved_for_presentation', 'approved_for_poster', 'event']

admin.site.register(AbstractSubmission, AbstractSubmissionAdmin)
# Abstracts admin view END-----------------------------------------------------------------------------#
# Abstracts approval email START------------------------------------------------------------------------------#
def send_approval_email(abstract, approval_type):
    # Determine the subject and email content based on approval type
    subject = f"Abstract Approved for {approval_type.capitalize()}"
    context = {
        'user': abstract.user,
        'abstract': abstract,
        'approval_type': approval_type
    }
    html_content = render_to_string('abstract_approval_email.html', context)
    text_content = strip_tags(html_content)
    from_email = 'info.bsbcs@gmail.com'  # Replace with your sender email
    recipient_list = [abstract.user.email]

    # Create and send the email
    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()
# Abstracts approval email END-----------------------------------------------------------------------------#
# Program Schedule admin view START------------------------------------------------------------------------------#
from .pdf_utils import generate_schedule_pdf
class ProgramScheduleAdmin(admin.ModelAdmin):
    form = ProgramScheduleForm
    list_display = ('title', 'presenter', 'get_hall_rooms', 'get_program_days', 'get_start_times', 'get_end_times', 'chairperson', 'moderator', 'event', 'email_sent')
    filter_horizontal = ('time_slots', 'panelist')
    list_filter = ('time_slots__program_day', 'time_slots__hall_room', 'time_slots__start_time', 'event', 'email_sent')
    actions = ['send_schedule_email', 'export_schedule_pdf']
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['abstract_submission'].queryset = AbstractSubmission.objects.filter(pk=obj.abstract_submission.pk)
        else:
            form.base_fields['abstract_submission'].queryset = AbstractSubmission.objects.filter(
                Q(approved_for_presentation=True) | Q(approved_for_poster=True)
            ).exclude(programschedule__isnull=False)
        return form
    def send_schedule_email(self, request, queryset):
        for schedule in queryset:
            participants = [schedule.abstract_submission.user.email]
            subject = f"Program Schedule: {schedule.event.name} {schedule.event.year}"
            context = {
                'schedule': schedule,
                'event': schedule.event,
                'hall_rooms': ", ".join([slot.hall_room.name for slot in schedule.time_slots.all()]),
                'program_days': ", ".join([slot.program_day.name for slot in schedule.time_slots.all()]),
                'start_times': ", ".join([slot.start_time.strftime('%I:%M %p') for slot in schedule.time_slots.all()]),
                'end_times': ", ".join([slot.end_time.strftime('%I:%M %p') for slot in schedule.time_slots.all()]),
            }
            html_content = render_to_string('schedule_mail.html', context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email='info.bsbcs@gmail.com',
                to=participants
            )
            email.attach_alternative(html_content, "text/html")
            try:
                email.send()
                schedule.email_sent = True
                schedule.save()
                self.message_user(request, f"Email sent to participant for schedule: {schedule.title}")
            except Exception as e:
                messages.error(request, f"Failed to send email for schedule: {schedule.title}. Error: {e}")
    send_schedule_email.short_description = "Send Schedule Email to Participants"
    def export_schedule_pdf(self, request, queryset):
        if queryset.count() == 0:
            self.message_user(request, "No schedules selected for PDF export.", level=messages.WARNING)
            return

        event = queryset.first().event  # Assuming schedules belong to the same event
        pdf_buffer = generate_schedule_pdf(event, queryset)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Program_Schedule_{event.name}_{event.year}.pdf"'
        return response

    export_schedule_pdf.short_description = "Export Program Schedule as PDF"
    def get_hall_rooms(self, obj):
        return ", ".join([slot.hall_room.name for slot in obj.time_slots.all()])
    get_hall_rooms.short_description = 'Hall Room'

    def get_program_days(self, obj):
        return ", ".join([slot.program_day.name for slot in obj.time_slots.all()])
    get_program_days.short_description = 'Program Day'

    def get_start_times(self, obj):
        return ", ".join([slot.start_time.strftime('%I:%M %p') for slot in obj.time_slots.all()])
    get_start_times.short_description = 'Start Time'

    def get_end_times(self, obj):
        return ", ".join([slot.end_time.strftime('%I:%M %p') for slot in obj.time_slots.all()])
    get_end_times.short_description = 'End Time'

admin.site.register(ProgramSchedule, ProgramScheduleAdmin)
# Program Schedule admin view END-----------------------------------------------------------------------------#

class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'event')
    list_filter = ('category', 'event')
admin.site.register(Sponsor, SponsorAdmin)

# Event Gallery admin view START-------------------------------------------------------------------#

from .models import EventImage, EventVideo

class EventImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'caption', 'event')
    list_filter = ('event',)

class EventVideoAdmin(admin.ModelAdmin):
    list_display = ('youtube_url', 'caption', 'event')
    list_filter = ('event',)

admin.site.register(EventImage, EventImageAdmin)
admin.site.register(EventVideo, EventVideoAdmin)

# Event Gallery admin view END-------------------------------------------------------------------#
# Registration Kit admin view START-------------------------------------------------------------------#
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import RegistrationKit, PaymentStatus, Event
from .resources import RegistrationKitResource
from django.utils.timezone import now

class RegistrationKitAdmin(ImportExportModelAdmin):
    resource_class = RegistrationKitResource
    list_display = ('participant_name', 'amount', 'payment_status_display', 'event', 'kit_status', 'issued_at')
    list_filter = ('status', 'event')
    actions = ['populate_registration_kits', 'issue_registration_kits']

    def participant_name(self, obj):
        return obj.payment_status.participant.name
    participant_name.short_description = 'Participant Name'

    def amount(self, obj):
        return obj.payment_status.amount
    amount.short_description = 'Amount'

    def payment_status_display(self, obj):
        return obj.payment_status.status
    payment_status_display.short_description = 'Payment Status'

    def event_year(self, obj):
        return obj.event.year
    event_year.short_description = 'Event Year'

    def kit_status(self, obj):
        return obj.status
    kit_status.short_description = 'Registration Kit Status'

    def populate_registration_kits(self, request, queryset):
        paid_payment_statuses = PaymentStatus.objects.filter(status='completed')
        for payment_status in paid_payment_statuses:
            RegistrationKit.objects.get_or_create(
                event=payment_status.event,
                payment_status=payment_status,
                defaults={'status': 'not_issued'}
            )
        self.message_user(request, "Registration Kits populated for participants with completed payments.")

    populate_registration_kits.short_description = "Populate Registration Kits for paid participants"

    def issue_registration_kits(self, request, queryset):
        updated_count = queryset.update(status='issued', issued_at=now())
        self.message_user(request, f"{updated_count} Registration Kits have been issued.")

    issue_registration_kits.short_description = "Issue selected Registration Kits"

admin.site.register(RegistrationKit, RegistrationKitAdmin)


from .models import BkashData
class BkashDataAdmin(ImportExportModelAdmin):
    list_display = ('payment_id', 'trx_id', 'mode', 'payment_create_time', 'payment_execute_time', 'amount', 'currency', 'intent', 'merchant_invoice', 'transaction_status', 'service_fee', 'verification_status', 'payer_reference', 'payer_type', 'status_code', 'status_message')
    list_filter = ('verification_status', 'status_message')
admin.site.register(BkashData, BkashDataAdmin)









