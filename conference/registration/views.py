from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import RegistrationForm, AbstractSubmissionForm, UserProfileForm
from .models import *
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

# User Profile View STARTS ---------------------------------------------------------------###
def create_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserProfileForm()
    return render(request, 'create_profile.html', {'form': form})

# User profile Views START-----------------------------------------------------###

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import UserProfile, AbstractSubmission, ProgramSchedule, Event

@login_required
def user_profile(request):
    # Fetch the user's profile
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Fetch related submissions and schedules
    abstract_submissions = AbstractSubmission.objects.filter(user=request.user)
    program_schedules = ProgramSchedule.objects.filter(abstract_submission__in=abstract_submissions)

    # Fetch active, upcoming, and closed events
    active_events = Event.objects.filter(event_status='active').order_by('-start_date')
    upcoming_events = Event.objects.filter(event_status='upcoming').order_by('start_date')
    closed_events = Event.objects.filter(event_status='closed').order_by('-end_date')

    # Fetch payment Status for the user's in registered events
    payment_statuses = PaymentStatus.objects.filter(participant__user=request.user).select_related('event', 'participant')
    payment_data = []
    for payment in payment_statuses:
        payment_data.append({
            'event': f"{payment.event.name} {payment.event.year}",  # Assuming the event name and year are stored in the Event modelpayment.event.name,
            'trxID': payment.trxID,
            'amount': payment.event.amount,  # Assuming the event amount is stored in the Event model
            'status': payment.status,
            'updated_at': payment.updated_at,  # Assuming there's an updated_at field in PaymentStatus
        })

    if request.method == 'POST':
        user_profile.name = request.POST.get('name')
        user_profile.email = request.POST.get('email')
        user_profile.phone = request.POST.get('phone')
        user_profile.save()
        message = "Profile updated successfully"
    else:
        message = ""

    return render(request, 'user_profile.html', {
        'user': request.user,
        'user_profile': user_profile,
        'abstract_submissions': abstract_submissions,
        'program_schedules': program_schedules,
        'message': message,
        'active_events': active_events,
        'upcoming_events': upcoming_events,
        'closed_events': closed_events,
        'payment_data': payment_data,
    })

# Custom Password Change View STARTS ---------------------------------------------------------------###
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'

    def get_success_url(self):
        return reverse_lazy('password_change_done')

# Custom Password Change View ENDS ---------------------------------------------------------------###

# Custom Password Reset View STARTS ---------------------------------------------------------------###
from django.contrib.auth.views import PasswordResetView
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'

    def get_success_url(self):
        return reverse_lazy('password_reset_done')

# Custom Password Reset View ENDS ---------------------------------------------------------------###

from django.shortcuts import render
from .models import Event, UserProfile

def index(request):
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass  # UserProfile does not exist; continue without redirecting

    active_events = Event.objects.filter(event_status='active').order_by('-start_date')
    upcoming_events = Event.objects.filter(event_status='upcoming').order_by('start_date')
    closed_events = Event.objects.filter(event_status='closed').order_by('-end_date')

    context = {
        'user_profile': user_profile,
        'active_events': active_events,
        'upcoming_events': upcoming_events,
        'closed_events': closed_events,
    }
    return render(request, 'index.html', context)


# Login and logout view STARTS -----------------------------------------------------------------------------------###

from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

def user_login(request):
    # Authentication logic here
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('index')

    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('index')

# Login and logout view ENDS -----------------------------------------------------------------------------------###

# Home View ---------------------------------------------------------------###
from django.shortcuts import get_object_or_404
from .models import FeatureSpeaker, AboutTheConference, Invitation, Event

def home(request, event_id):
    # print(event_id)
    user_profile = None
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
    event = get_object_or_404(Event, id=event_id)
    speakers = FeatureSpeaker.objects.filter(event=event)
    about_conference = AboutTheConference.objects.filter(event=event).first()  # Assuming you have one instance per event
    invitations = Invitation.objects.filter(event=event)
    modal_image_path = 'images/BBCC_2024_Poster_Final.jpg'

    context = {
        'user_profile': user_profile,
        'event': event,
        'speakers': speakers,
        'about_conference': about_conference,
        'invitations': invitations,
        'modal_image': modal_image_path,
    }

    return render(request, 'home.html', context)
# Home View Ends ---------------------------------------------------------------###

# Home Modal View ---------------------------------------------------------------###
from django.http import JsonResponse
# def modal_image_view(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     modal_html = render_to_string('partials/modal_image.html', {'event': event})
#     return JsonResponse({'html': modal_html})
# Home Modal View Ends ---------------------------------------------------------------###

# Participant List View ---------------------------------------------------------------###
from django.shortcuts import get_object_or_404
from .models import Participant, Event

def participant_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    approved_paid_participants = Participant.objects.filter(event=event, approved=True, payment_statuses__status='completed')
    
    if request.headers.get('HX-Request'):
        return render(request, 'partials/participant_list.html', {'participants': approved_paid_participants})
    
    return render(request, 'participant_list.html', {'participants': approved_paid_participants, 'event': event})
def participant_list_partial(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Filter participants with approved=True and payment status='completed'
    approved_paid_participants = Participant.objects.filter(
        event=event, approved=True, payment_statuses__status='completed'
    )

    return render(request, 'partials/participant_list.html', {'participants': approved_paid_participants})



# About The Conference View ---------------------------------------------------------------###
def about(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    about_conference = AboutTheConference.objects.filter(event=event).first()
    return render(request, 'about.html', {'about_conference': about_conference, 'event': event})
# About The Conference View Ends ---------------------------------------------------------------### 

# Speakers View ---------------------------------------------------------------###
def speakers(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    speakers = FeatureSpeaker.objects.filter(event=event)
    return render(request, 'speakers.html', {'speakers': speakers, 'event': event})
# Speakers View Ends ---------------------------------------------------------------###

# Registration view Starts --------------------------------------------------######
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, UserProfile, Participant, PaymentStatus
from .forms import RegistrationForm
from django.db import IntegrityError



# Registration View Ends -----------------------------------------------------------------#
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import IntegrityError

def registration(request, event_id):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return render(request, 'registration_login_prompt.html', {
            'message': 'You need to log in to be able to register for this event.',
            'login_url': '/login/',  # Replace with your login URL name or path
            'signup_url': '/create_profile/'  # Replace with your signup URL name or path
        })

    event = get_object_or_404(Event, id=event_id)

    # Check if registration for the event is open
    if event.registration != 'Open':  # Match case-sensitive values as per your model
        status_message = {
            'Closed': 'Registration for this event is closed.',
            'Starting Soon': 'Registration for this event will start soon. Please check back later.',
        }
        return render(request, 'registration_error.html', {
            'message': status_message.get(event.registration, 'Registration is not open for this event.'),
            'event': event
        })

    user_profile = UserProfile.objects.get(user=request.user)

    # Check if the user has already registered for the event
    try:
        participant = Participant.objects.get(user=request.user, event=event)
        return render(request, 'registration_error.html', {
            'message': 'You have already submitted your registration or already registered for this event. Please check your email for further details.',
            'event': event,
            'participant': participant
        })
    except Participant.DoesNotExist:
        pass  # User has not registered yet, proceed with registration 

    initial_data = {
        'name': user_profile.name,
        'email': request.user.email,
        'phone': user_profile.phone,
    }

    if request.method == 'POST':
        form = RegistrationForm(request.POST, event=event)  # Pass event instance
        if form.is_valid():
            try:
                participant = form.save(commit=False)
                participant.user = request.user  # Assign the logged-in user
                participant.event = event  # Assign the event explicitly
                participant.save()
                PaymentStatus.objects.create(participant=participant, event=event, status='unpaid')
                send_registration_form_submission_email(participant)
                messages.success(request, 'Registration form submitted successfully!')
                return redirect('registration:registration_submitted', event_id=event.id)
            except IntegrityError as e:
                print(f"IntegrityError: {e}")  # Debugging line
                messages.error(request, 'A participant with this email or phone number already exists for this event.')
        else:
            messages.error(request, 'There are errors in your form. Registration failed. Please check the form.')
    else:
        form = RegistrationForm(initial=initial_data, event=event)

    return render(request, 'registration.html', {'form': form, 'event': event})


from django.shortcuts import render, get_object_or_404

def registration_submitted(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    print(f"Event ID: {event.id}")  # Log to console to check
    return render(request, 'registration_submitted.html', {'event': event})

def registration_message(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'registration_message.html', {'event': event})
# Email sending function
def send_registration_form_submission_email(participant):
    subject = 'Registration Confirmation'
    # Render the email template with context
    html_content = render_to_string('registration_submitted.html', {'participant': participant})
    text_content = strip_tags(html_content)
    from_email = 'info.bsbcs@gmail.com'  # Replace with your sender email
    recipient_list = [participant.email]

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Participant, Event
from .forms import RegistrationForm

def send_approval_email(participant, event):
    subject = f'Registration Approval for {event.name} {event.year}'
    try:
        html_content = render_to_string('registration_badge_download.html', {'participant': participant, 'event': event})
        text_content = strip_tags(html_content)
        from_email = 'no-reply@example.com'
        recipient_list = [participant.email]

        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Error sending approval email: {e}")


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_payment_link_email(participant, event):
    subject = f'Complete Your Payment for {event.name} {event.year} Conference'
    base_url = 'http://127.0.0.1:8000'  # Ensure the correct protocol and base address
    payment_url = f'{base_url}/payment?event_id={event.id}&participant_id={participant.id}'  # Correctly formatted URL

    try:
        html_content = render_to_string('payment_link.html', {'participant': participant, 'event': event, 'payment_url': payment_url})
        text_content = strip_tags(html_content)
        from_email = 'no-reply@example.com'
        recipient_list = [participant.email]

        email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Error sending payment link email: {e}")

# #### Registration process, registration mail Ends ----------------------------------###

# Abstract Submission View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Participant, PaymentStatus, AbstractSubmission
from .forms import AbstractSubmissionForm

# Custom decorator for approved user
def approved_user_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        event_id = kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        try:
            participant = Participant.objects.get(email=request.user.email, event=event)
        except Participant.DoesNotExist:
            return render(request, 'error.html', {
                'message': 'You need to register for the event to submit an abstract. Please register first.',
                'event': event,
                'participant': None  # Pass None for participant
            })
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Participant, PaymentStatus, AbstractSubmission
from .forms import AbstractSubmissionForm
from django.db import IntegrityError


# New Abstract_Submission View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def abstract_submission(request, event_id):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return render(request, 'login_required_message.html', {
            'message': 'You need to log in to submit an abstract. Please log in or create a profile.',
            'login_url': '/login/',  # Replace with your login URL name or path
            'signup_url': '/signup/'  # Replace with your signup URL name or path
        })

    event = get_object_or_404(Event, id=event_id)

    # Fetch the participant associated with the logged-in user and the current event
    try:
        participant = Participant.objects.get(user=request.user, event=event)
    except Participant.DoesNotExist:
        return render(request, 'error.html', {
            'message': 'You are not registered as a participant for this event.',
            'event': event,
            'participant': None  # Pass None to indicate no participant
        })

    # Check if the participant is approved for the specific event
    if not participant.approved:
        return render(request, 'error.html', {
            'message': 'Your registration for this event has not been approved yet. Once approved and payment is done, you will be able to submit an abstract.',
            'event': event,
            'participant': None  # Pass None to indicate no participant
        })

    # Check if the participant has completed the payment for the specific event
    try:
        payment_status = PaymentStatus.objects.get(participant=participant, event=event)
        if payment_status.status != 'completed':
            return render(request, 'error.html', {
                'message': 'You must complete your payment to submit an abstract.',
                'event': event,
                'participant': participant  # Pass participant for payment button
            })
    except PaymentStatus.DoesNotExist:
        return render(request, 'error.html', {
            'message': 'You must complete your payment to submit an abstract.',
            'event': event,
            'participant': participant  # Pass participant for payment button
        })

    if request.method == 'POST':
        form = AbstractSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            abstract = form.save(commit=False)
            # Assign the required fields
            abstract.user = request.user  # Ensure user is assigned
            abstract.event = event  # Assign the current event
            try:
                abstract.save()
                # Send an email to the participant
                try:
                    send_abstract_submission_email(participant)
                    messages.success(request, 'Abstract submitted successfully!')
                except Exception as e:
                    messages.warning(request, f'ABstract SUbmitted but an error occured while sending the mail: {e}')
                return redirect('registration:submission_success', event_id=event.id)
            except IntegrityError as e:
                messages.error(request, f'An error occurred while saving your abstract: {e}')
        else:
            messages.error(request, 'There were errors in your form submission. Please check the form.')
    else:
        form = AbstractSubmissionForm()

    return render(request, 'abstract_submission.html', {
        'form': form,
        'event': event,
        'participant': participant
    })

# New Abstract_Submission View Ends

def submission_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'submission_success.html', {'event': event})



def send_abstract_submission_email(participant):
    subject = 'Abstract Submission Confirmation'
    # Render the email template with context
    html_content = render_to_string('submission_success.html', {'participant': participant})
    text_content = strip_tags(html_content)
    from_email = 'info.bsbcs@gmail.com'  # Replace with your sender email
    recipient_list = [participant.email]

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()

# ### Abstract Submission process, abstract submission mail Ends ----------------------------------###

# Invitation View
def invitation(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    invitations = Invitation.objects.filter(event=event)
    return render(request, 'invitation.html', {'invitations': invitations, 'event': event})
# Program Schedule View
def schedule(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    program_schedules = ProgramSchedule.objects.filter(event=event).select_related('abstract_submission').prefetch_related('time_slots').order_by('time_slots__program_day', 'time_slots__start_time')
    return render(request, 'schedule.html', {'program_schedules': program_schedules, 'event': event})

def session_detail(request, event_id, pk):
    event = get_object_or_404(Event, id=event_id)
    session = get_object_or_404(AbstractSubmission, event=event, pk=pk)
    return render(request, 'partials/session_detail.html', {'session': session, 'event': event})

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Event, ProgramSchedule
from .pdf_utils import generate_schedule_pdf

def download_schedule_pdf(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    program_schedules = ProgramSchedule.objects.filter(event=event)\
        .select_related('abstract_submission')\
        .prefetch_related('time_slots')\
        .order_by('time_slots__program_day', 'time_slots__start_time')
    
    # Pass both event and schedules to the PDF generator
    buffer = generate_schedule_pdf(event, program_schedules)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="program_schedule_{event.name}_{event.year}.pdf"'
    return response


# Sponsors View START------------------------------------------------------------------------------#
def sponsor_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    categories = ['Title', 'Platinum', 'Golden', 'Silver', 'Logistics', 'Media', 'IT', 'Event']
    sponsors_by_category = {category: Sponsor.objects.filter(event=event, category=category) for category in categories}
    return render(request, 'sponsor_list.html', {'sponsors_by_category': sponsors_by_category, 'event': event})

# Sponsors View END--------------------------------------------------------------------------------#

# Publication View START------------------------------------------------------------------------------#
def publication_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    publications = AbstractSubmission.objects.filter(event=event, approved_for_presentation=True) | AbstractSubmission.objects.filter(event=event, approved_for_poster=True)
    return render(request, 'publication_list.html', {'event': event, 'publications': publications})

def publication_detail(request, event_id, pub_id):
    event = get_object_or_404(Event, id=event_id)
    publication = get_object_or_404(AbstractSubmission, event=event, id=pub_id)
    return render(request, 'publication_detail.html', {'event': event, 'publication': publication})
# Publication View END--------------------------------------------------------------------------------#

# Event Gallery View START------------------------------------------------------------------------------#

from django.shortcuts import render, get_object_or_404
from .models import Event, EventImage, EventVideo

def event_gallery(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    images = EventImage.objects.filter(event=event)
    videos = EventVideo.objects.filter(event=event)
    return render(request, 'event_gallery.html', {'event': event, 'images': images, 'videos': videos})

# Event Gallery View END--------------------------------------------------------------------------------#

# Bkash Payment gatweay Integration
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Participant, Event, PaymentStatus
import os
from dotenv import load_dotenv
# lets load environment variables
load_dotenv()

# Access the credentials and production URL from the environment variables
BKASH_USERNAME = os.getenv("BKASH_USERNAME")
BKASH_APP_KEY = os.getenv("BKASH_APP_KEY")
BKASH_APP_SECRET = os.getenv("BKASH_APP_SECRET")
BKASH_PRODUCTION_URL = os.getenv("BKASH_PRODUCTION_URL")


def render_error_page(request, error_message):
    """Utility function to render the error page with a specific message."""
    context = {
        'title': "Payment Failure",
        'error_message': error_message,
    }
    return render(request, 'payment_message.html', context)

# Step 1: Grant Token

def get_bkash_token():
    url = f"{BKASH_PRODUCTION_URL}/tokenized/checkout/token/grant"
    headers = {
        "username": BKASH_USERNAME,
        "password": "8=*gF8h]ziM",
        "Content-Type": "application/json"
    }
    payload = {
        "app_key": BKASH_APP_KEY,
        "app_secret": BKASH_APP_SECRET
    }

    try:
        print("Requesting token...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        token = response.json().get("id_token")
        print("Token retrieved successfully:", token)
        return token
    except requests.exceptions.RequestException as e:
        print(f"Failed to get token: {e}")
        return None

# Step 2: Create Payment
def create_bkash_payment(token, amount, payer_reference, callback_url, merchant_invoice_number):
    url = f"{BKASH_PRODUCTION_URL}/tokenized/checkout/create"
    payload = {
        "mode": "0011",
        "amount": str(amount),
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": merchant_invoice_number,
        "callbackURL": callback_url,
        "payerReference": payer_reference
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-APP-Key": BKASH_APP_KEY
    }

    try:
        print("Creating payment...")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP errors (4xx, 5xx)
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error in creating payment: {e}")
        return None

# Step 3: Execute Payment
def execute_payment(token, payment_id):
    url = f"{BKASH_PRODUCTION_URL}/tokenized/checkout/execute"
    payload = {"paymentID": payment_id}
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "X-APP-Key": BKASH_APP_KEY # Add the required APP Key here
    }
    try:
        print(f"Executing payment for Payment ID: {payment_id}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error in payment execution: {e}")
        if e.response:
            print(f"Error in executing payment: {e}")
        return None
    

# Step 4: Payment View
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Participant, Event, PaymentStatus  # Replace with your actual models

@login_required
def payment(request, event_id, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        try:
            # Step 1: Get token
            token = get_bkash_token()
            if not token:
                messages.error(request, "Failed to get token.")
                return redirect('index')

            # Step 2: Create payment
            amount = event.amount
            payer_reference = str(getattr(request.user.userprofile, 'phone', None))
            if not payer_reference:
                messages.error(request, "Phone number not found.")
                return redirect('index')

            merchant_invoice_number = f"INV-{event.id}-{request.user.id}-{int(time.time())}"
            callback_url = request.build_absolute_uri(
                reverse_lazy('registration:payment_success', kwargs={'event_id': event_id, 'participant_id': participant_id})
            ) + f"?merchant_invoice_number={merchant_invoice_number}"
            payment_response = create_bkash_payment(token, amount, payer_reference, callback_url, merchant_invoice_number)
            
            print(f"Merchant Invoice Number sent to bkash: {merchant_invoice_number}")
            
            if payment_response and payment_response.get("statusCode") == "0000":
                # Redirect to bKash payment page
                return redirect(payment_response["bkashURL"])
            else:
                messages.error(request, f"Payment failed: {payment_response.get('statusMessage')}")
                return redirect('index')

        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, "An error occurred.")
            return redirect('index')

    return render(request, 'payment.html', {'participant': participant, 'event': event})


from django.urls import reverse
import time

@login_required
def payment_success(request, event_id, participant_id):
    payment_id = request.GET.get('paymentID')
    merchant_invoice_number = request.GET.get('merchant_invoice_number')
    if not payment_id:
        messages.error(request, "Payment ID not found.")
        return redirect('index')

    # Save payment ID to database for future reference
    participant = get_object_or_404(Participant, id=participant_id)
    event = get_object_or_404(Event, id=event_id)
    
    PaymentStatus.objects.update_or_create(
        participant=participant,
        event=event,
        defaults={
            'transaction_id': payment_id,
            'status': 'pending',
            'merchant_invoice_number': merchant_invoice_number  # Check if this is being set correctly
        }
    )
    print(f"Generated Merchant Invoice Number: {merchant_invoice_number}")

    # Redirect to finalize the payment
    messages.success(request, "Payment completed. Finalizing...")
    return redirect(reverse('registration:finalize_payment', kwargs={'event_id': event_id, 'participant_id': participant_id}))


import time
from registration.pdf_utils import generate_invoice
from datetime import datetime
from django.utils.timezone import make_aware
from dateutil import parser
# @login_required
# def finalize_payment(request, event_id, participant_id):
#     try:
#         # Retrieve PaymentStatus record
#         payment_status = get_object_or_404(PaymentStatus, participant_id=participant_id, event_id=event_id)
        
#         # Execute payment logic
#         token = get_bkash_token()
#         if not token:
#             messages.error(request, "Failed to retrieve token.")
#             return render(request, 'payment_message.html', {'title': "Payment Failure", 'error_message': "Failed to retrieve token."})

#         # Call bKash execute API
#         response = execute_payment(token, payment_status.transaction_id)
#         if response and response.get('statusCode') == '0000':
#             # Payment finalized successfully
#             payment_status.status = 'completed'
#             payment_status.amount = response.get('amount', payment_status.amount)  # Store amount if provided
#             payment_status.merchant_invoice_number = response.get('merchantInvoiceNumber', payment_status.merchant_invoice_number)
#             payment_status.transaction_id = response.get('paymentID')  # Store transaction ID
#             payment_status.save()

#             # Query payment status to get trxID
#             time.sleep(5) # Wait for the payment status to be updated
#             query_response = payment_query(token, response.get('paymentID'))
            
#             if query_response and query_response.get('trxID'):
#                 payment_status.trxID = query_response['trxID']
#                 payment_status.save()

#                 # Optionally update other models if necessary
#                 participant = get_object_or_404(Participant, id=participant_id)
#                 participant.payment_status = 'completed'  # Or whatever field you use to indicate paid status
#                 participant.save()
#                 # Let's Save Query Status as well
#                 # Save query response in BkashData model
#                 bkash_data, created = BkashData.objects.update_or_create(
#                     payment_id=query_response['paymentID'],
#                     defaults={
#                         'trx_id': query_response['trxID'],
#                         'mode': query_response['mode'],
#                         'payment_create_time': make_aware(parser.parse(query_response['paymentCreateTime'])),
#                         'payment_execute_time': make_aware(parser.parse(query_response['paymentExecuteTime'])),
#                         'amount': query_response['amount'],
#                         'currency': query_response['currency'],
#                         'intent': query_response['intent'],
#                         'merchant_invoice': query_response['merchantInvoice'],
#                         'transaction_status': query_response['transactionStatus'],
#                         'service_fee': query_response['serviceFee'],
#                         'verification_status': query_response['verificationStatus'],
#                         'payer_reference': query_response['payerReference'],
#                         'payer_type': query_response['payerType'],
#                         'status_code': query_response['statusCode'],
#                         'status_message': query_response['statusMessage'],
#                     }
#                 )

#                 # Attempt to generate the invoice and send the email
#                 invoice_error = None
#                 try:
#                     if not payment_status.email_sent:
#                         invoice_path = generate_invoice(participant, payment_status.event, payment_status)
#                         send_invoice_email(participant, payment_status.event, payment_status, invoice_path)
#                 except Exception as e:
#                     invoice_error = str(e)
#                     print(f"Invoice/Email Error: {e}")

#                 # Render the finalize payment page
#                 context = {
#                     'message': "Payment successfully finalized.",
#                     'payment_details': response,
#                 }
#                 if invoice_error:
#                     context['note'] = "Payment successful, but there was an issue generating the invoice or sending the email. Please contact support."
#                 return render(request, 'finalize_payment.html', context)

#             else:
#                 # If trxID is not available, show failure message
#                 payment_status.status = 'failed'
#                 payment_status.save()
#                 # messages.error(request, "Transaction ID not found. Payment could not be completed.")
#                 return render(request, 'payment_message.html', {'title': 'Payment Failure', 'error_message': 'Transaction ID not found. Payment could not be completed. Please attempt again or if payment has been deducted, contact with the organizers.'})

#         else:
#             # Payment finalization failed
#             payment_status.status = 'failed'
#             payment_status.save()
#             # messages.error(request, f"Payment finalization failed: {response.get('statusMessage')}")
#             error_message = response.get('statusMessage', 'Payment finalization failed. try again or if payment  deducted, contact with the organizers.')
#             return render(request, 'payment_message.html', {'title': 'Payment Failure', 'error_message': error_message})

#     except Exception as e:
#         print(f"Error in finalizing payment: {e}")
#         # messages.error(request, "An error occurred during finalization.")
#         return render(request, 'payment_message.html', {'title': 'Payment Failure', 'error_message': 'An unexpected error occurred during finalization.'})


from dateutil import parser
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import time

@login_required
def finalize_payment(request, event_id, participant_id):
    try:
        # Retrieve PaymentStatus record
        payment_status = get_object_or_404(PaymentStatus, participant_id=participant_id, event_id=event_id)
        
        # Execute payment logic
        token = get_bkash_token()
        if not token:
            messages.error(request, "Failed to retrieve token.")
            return render(request, 'payment_message.html', {
                'title': "Payment Failure", 
                'error_message': "Failed to retrieve token."
            })

        # Call bKash execute API
        response = execute_payment(token, payment_status.transaction_id)
        if response and response.get('statusCode') == '0000':
            # Payment finalized successfully
            payment_status.status = 'completed'
            payment_status.amount = response.get('amount', payment_status.amount)
            payment_status.merchant_invoice_number = response.get('merchantInvoiceNumber', payment_status.merchant_invoice_number)
            payment_status.transaction_id = response.get('paymentID')
            payment_status.save()

            # Query payment status to get trxID
            time.sleep(5)  # Wait for the payment status to be updated
            query_response = payment_query(token, response.get('paymentID'))

            if query_response and query_response.get('trxID'):
                payment_status.trxID = query_response['trxID']
                payment_status.save()

                # Update participant status
                participant = get_object_or_404(Participant, id=participant_id)
                participant.payment_status = 'completed'
                participant.save()

                # Generate Invoice and Send Email
                invoice_error = None
                try:
                    invoice_path = generate_invoice(participant, payment_status.event, payment_status)
                    send_invoice_email(participant, payment_status.event, payment_status, invoice_path)
                except Exception as e:
                    invoice_error = str(e)
                    print(f"Invoice/Email Error: {e}")
                    payment_status.status = 'error'
                    payment_status.save()
                    return render(request, 'payment_message.html', {
                        'title': 'Payment Successful with Issues',
                        'error_message': 'Payment was successful, but there was an issue generating the invoice or sending the email. Please contact support.'
                    })

                # Save bKash Data model as the final step
                try:
                    bkash_data = BkashData(
                        payment_id=query_response['paymentID'],
                        trx_id=query_response['trxID'],
                        mode=query_response['mode'],
                        payment_create_time=query_response.get('paymentCreateTime', ''),
                        payment_execute_time=query_response.get('paymentExecuteTime', ''),
                        amount=query_response['amount'],
                        currency=query_response['currency'],
                        intent=query_response['intent'],
                        merchant_invoice=query_response['merchantInvoice'],
                        transaction_status=query_response['transactionStatus'],
                        service_fee=query_response['serviceFee'],
                        verification_status=query_response['verificationStatus'],
                        payer_reference=query_response['payerReference'],
                        payer_type=query_response['payerType'],
                        status_code=query_response['statusCode'],
                        status_message=query_response['statusMessage']
                    )
                    bkash_data.save()
                except Exception as e:
                    print(f"Error saving bKash data: {e}")
                    return render(request, 'payment_message.html', {
                        'title': 'Payment Successful with Issues',
                        'error_message': 'Payment was successful, but there was an issue saving the transaction data. Please contact support.'
                    })

                # Render success message
                return render(request, 'finalize_payment.html', {
                    'message': "Payment successfully finalized.",
                    'payment_details': query_response,
                })

            else:
                # If trxID is not available, show failure message
                payment_status.status = 'failed'
                payment_status.save()
                return render(request, 'payment_message.html', {
                    'title': 'Payment Failure',
                    'error_message': 'Transaction ID not found. Payment could not be completed. Please attempt again or contact the organizers.'
                })

        else:
            # Payment finalization failed
            payment_status.status = 'failed'
            payment_status.save()
            error_message = response.get('statusMessage', 'Payment finalization failed. Try again or contact the organizers.')
            return render(request, 'payment_message.html', {
                'title': 'Payment Failure', 
                'error_message': error_message
            })

    except Exception as e:
        print(f"Error in finalizing payment: {e}")
        return render(request, 'payment_message.html', {
            'title': 'Payment Failure',
            'error_message': 'An unexpected error occurred during finalization.'
        })


import requests

def payment_query(token, payment_id):

    url = f"{BKASH_PRODUCTION_URL}/tokenized/checkout/payment/status"
    payload = {"paymentID": payment_id}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-APP-Key": BKASH_APP_KEY  # Ensure APP Key is properly set
    }

    try:
        print(f"Querying payment status for Payment ID: {payment_id}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP codes >= 400
        
        # Debugging response
        print(f"Payment query successful: {response.status_code}")
        print(f"Response content: {response.json()}")
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if http_err.response:
            print(f"HTTP response error: {http_err.response.json()}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None


# Step 6: Payment Failure
@login_required
def payment_failure(request, event_id, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    event = get_object_or_404(Event, id=event_id)

    # Update payment status to 'failed'
    PaymentStatus.objects.filter(participant=participant, event=event).update(status='failed')

    # Optional: Show a failure reason
    failure_reason = request.GET.get('reason', "Payment failed. Please try again.")
    messages.error(request, failure_reason)
    return render(request, 'payment_message.html', {'event_id': event_id, 'participant_id': participant_id})

# Invoice Generation Start ----------------------------------------------------------------#
from django.core.mail import EmailMessage

from django.core.mail import EmailMessage

def send_invoice_email(participant, event, payment_status, invoice_path):
    subject = f"Payment done and Invoice for {event.name}"
    message = (
        f"Dear {participant.name},\n\n"
        f"Thank you for registering for {event.name}.\n"
        f"Please find your invoice attached.\n\n"
        "Best regards,\nConference Team"
    )
    recipient = participant.email

    # Create Email
    email = EmailMessage(subject, message, to=[recipient])
    email.attach_file(invoice_path)
    
    try:
        email.send()
        payment_status.email_sent = True
        payment_status.invoice = invoice_path
        payment_status.save()
        print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email: {e}")












