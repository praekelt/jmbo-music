from django.conf.urls import url

from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie import fields
from jmbo.api import ModelBaseResource

from music.models import Track, TrackContributor


class TrackContributorResource(ModelBaseResource):

    class Meta:
        queryset = TrackContributor.permitted.all()
        resource_name = 'trackcontributor'

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]


class TrackResource(ModelBaseResource):
    contributor = fields.ToManyField(TrackContributorResource, 'contributor', full=True)

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
