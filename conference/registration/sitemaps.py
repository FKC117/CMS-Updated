# registration/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Event, AbstractSubmission

class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Event.objects.order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('registration:home', args=[obj.id])
# registration/sitemaps.py

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        events = Event.objects.all()
        static_urls = [
            'about', 'invitation', 'speakers', 'schedule', 'participant_list',
            'registration', 'abstract_submission', 'sponsor_list', 'event_gallery',
            'publication_list'
        ]
        return [(url, event.id) for event in events for url in static_urls]

    def location(self, item):
        return reverse(f'registration:{item[0]}', args=[item[1]])
# registration/sitemaps.py

class PublicationSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return AbstractSubmission.objects.filter(approved_for_presentation=True) | AbstractSubmission.objects.filter(approved_for_poster=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('registration:publication_detail', args=[obj.event.id, obj.id])
