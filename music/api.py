from django.conf.urls.defaults import url

from tastypie.resources import ModelResource
from tastypie.constants import ALL
from jmbo.api import ModelBaseResource

from music.models import Track


class TrackResource(ModelBaseResource):

    class Meta:
        queryset = Track.permitted.all()
        resource_name = 'track'
        filtering = {
            'last_played': ALL
        }
        ordering = ['last_played']

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
