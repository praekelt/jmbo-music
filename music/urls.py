from django.conf import settings
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    '',
    url(r'^track/(?P<slug>[\w-]+)/$', 'jmbo.views.object_detail', name='track_object_detail'),
    url(r'^album/(?P<slug>[\w-]+)/$', 'jmbo.views.object_detail', name='album_object_detail'),
    url(r'^audioembed/(?P<slug>[\w-]+)/$', 'jmbo.views.object_detail', name='audioembed_object_detail'),
    url(r'^trackcontributor/(?P<slug>[\w-]+)/$', 'jmbo.views.object_detail', name='trackcontributor_object_detail'),
)
