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


class TrackResource(ModelBaseResource):
    contributor = fields.ToManyField(TrackContributorResource, 'contributor', full=True)

    class Meta:
        queryset = Track.permitted.all()
        resource_name = 'track'
        filtering = {
            'last_played': ALL
        }
        ordering = ['last_played']
