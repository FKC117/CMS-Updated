from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from registration.sitemaps import EventSitemap, StaticViewSitemap, PublicationSitemap


from registration import views as custom_views
from registration import views
from registration.views import index, create_profile, user_profile

sitemaps = {
    'events': EventSitemap,
    'static': StaticViewSitemap,
    'publications': PublicationSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('create-profile/', create_profile,name='create_profile'),
    path('event/', include(('registration.urls', 'registration'), namespace='registration')),

    path('profile/', views.user_profile, name='user_profile'),

    #universal login system
    path('accounts/login/', custom_views.user_login, name='login'),  # Universal login
    path('accounts/logout/', custom_views.user_logout, name='logout'),  # Universal logout
    path('accounts/password_change/', custom_views.CustomPasswordChangeView.as_view(), name='password_change'),  # Universal password change
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),  # Universal password change done
    path('accounts/password_reset/', custom_views.CustomPasswordResetView.as_view(), name='password_reset'),  # Universal password reset
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),  # Universal password reset done
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),  # Universal password reset confirm
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),  # Universal password reset complete
    #Bkash Payment Urls
    # path('initiate-payment/<int:event_id>/', initiate_payment, name='initiate_payment'),
    # path('payment-success/', payment_success, name='payment_success'),
    # path('payment-failure/', payment_failure, name='payment_failure'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # New Lines
from django.contrib import admin
from django.urls import path, include, reverse_lazy, re_path #  re_path is new added
from django.views.static import serve # new line
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from registration.sitemaps import EventSitemap, StaticViewSitemap, PublicationSitemap


from registration import views as custom_views
from registration import views
from registration.views import index, create_profile, user_profile

sitemaps = {
    'events': EventSitemap,
    'static': StaticViewSitemap,
    'publications': PublicationSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('create-profile/', create_profile,name='create_profile'),
    path('event/', include(('registration.urls', 'registration'), namespace='registration')),

    path('profile/', views.user_profile, name='user_profile'),

    #universal login system
    path('accounts/login/', custom_views.user_login, name='login'),  # Universal login
    path('accounts/logout/', custom_views.user_logout, name='logout'),  # Universal logout
    path('accounts/password_change/', custom_views.CustomPasswordChangeView.as_view(), name='password_change'),  # Universal password change
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),  # Universal password change done
    path('accounts/password_reset/', custom_views.CustomPasswordResetView.as_view(), name='password_reset'),  # Universal password reset
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),  # Universal password reset done
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),  # Universal password reset confirm
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),  # Universal password reset complete
    #Bkash Payment Urls
    # path('initiate-payment/<int:event_id>/', initiate_payment, name='initiate_payment'),
    # path('payment-success/', payment_success, name='payment_success'),
    # path('payment-failure/', payment_failure, name='payment_failure'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # for media and static files on server
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)




'''