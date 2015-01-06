from django.conf import settings
from django.conf.urls import patterns, url

from jmbo.urls import v1_api
from jmbo.views import ObjectDetail

from music.api import TrackResource


v1_api.register(TrackResource())

urlpatterns = patterns(
    '',
    url(r'^track/(?P<slug>[\w-]+)/$', ObjectDetail.as_view(), name='track_object_detail'),
    url(r'^album/(?P<slug>[\w-]+)/$', ObjectDetail.as_view(), name='album_object_detail'),
    url(r'^audioembed/(?P<slug>[\w-]+)/$', ObjectDetail.as_view(), name='audioembed_object_detail'),
    url(r'^trackcontributor/(?P<slug>[\w-]+)/$', ObjectDetail.as_view(), name='trackcontributor_object_detail'),
)
