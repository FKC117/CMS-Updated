from django.conf import settings
from django.urls import path, reverse_lazy
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from .views import *

app_name = 'registration'  # Define app_name

# Update URL pattern
urlpatterns = [
    # URL patterns for the app.
    # path('', views.index, name='index'),  # Path for index view
    path('<int:event_id>/home/', views.home, name='home'),  # Ensure this path is correct

    # urls for events
    path('<int:event_id>/participants/', views.participant_list, name='participant_list'),
    path('<int:event_id>/participants/partial/', views.participant_list_partial, name='participant_list_partial'),

    path('<int:event_id>/participant_list/', views.participant_list, name='participant_list'),
    path('<int:event_id>/about/', views.about, name='about'),
    path('<int:event_id>/speakers/', views.speakers, name='speakers'),
    path('<int:event_id>/registration/', views.registration, name='registration'),
    path('<int:event_id>/registration_submitted/', views.registration_submitted, name='registration_submitted'),
    path('<int:event_id>/abstract_submission/', views.abstract_submission, name='abstract_submission'),
    # path('<int:event_id>/registration_message/', views.registration_message, name='registration_message'),
    path('<int:event_id>/submission_success/', views.submission_success, name='submission_success'),
    path('<int:event_id>/invitation/', views.invitation, name='invitation'),
    path('<int:event_id>/schedule/', views.schedule, name='schedule'),
    path('<int:event_id>/session_detail/<int:pk>/', views.session_detail, name='session_detail'),
    path('<int:event_id>/download_schedule_pdf/', views.download_schedule_pdf, name='download_schedule_pdf'),
    # path('<int:event_id>/modal_image/', views.modal_image, name='modal_image'),
    path('<int:event_id>/sponsors/', views.sponsor_list, name='sponsor_list'),
    path('<int:event_id>/publication_list/', views.publication_list, name='publication_list'),
    path('<int:event_id>/publication/<int:pub_id>/', views.publication_detail, name='publication_detail'),
    # Event Gallery url
    path('<int:event_id>/gallery/', views.event_gallery, name='event_gallery'),
    # Event Payment url
    # path('<int:event_id>/payment/<int:participant_id>/', views.payment, name='payment'),
    # Bkash Payment url
    path('<int:event_id>/payment/<int:participant_id>/', views.payment, name='payment'), 
    path('<int:event_id>/finalize-payment/<int:participant_id>/', finalize_payment, name='finalize_payment'),
    path('<int:event_id>/payment-success/<int:participant_id>/', payment_success, name='payment_success'), 
    path('<int:event_id>/payment-failure/<int:participant_id>/', payment_failure, name='payment_failure'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

