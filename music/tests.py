import unittest

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet

from preferences import preferences

from music.models import TrackContributor, Credit, Track, Album, CreditOption

from music.utils import wikipedia, lastfm

'''
class TrackTestCase(unittest.TestCase):

    def test_get_primary_contributors(self):
        # Create website site item and set as current site.
        web_site = Site(domain="web.address.com")
        web_site.save()
        settings.SITE_ID = web_site.id

        # Create a track with some credits.
        track = Track(title="title")
        track.save()
        contributor1 = TrackContributor(title="title", state="published")
        contributor1.save()
        contributor1.sites.add(web_site)
        contributor2 = TrackContributor(title="title", state="published")
        contributor2.save()
        contributor2.sites.add(web_site)
        contributor3 = TrackContributor(title="title", state="published")
        contributor3.save()
        contributor3.sites.add(web_site)
        contributor4 = TrackContributor(title="title", state="published")
        contributor4.save()
        contributor4.sites.add(web_site)
        unpublished_contributor = TrackContributor(title="title")
        unpublished_contributor.save()
        Credit(track=track, contributor=contributor1, role=2).save()
        Credit(track=track, contributor=contributor2, role=10).save()
        Credit(track=track, contributor=contributor3, role=2).save()
        Credit(track=track, contributor=unpublished_contributor, role=2).save()
        Credit(track=track, contributor=contributor4).save()

        # result should only contain contributors with highest role.
        # can contain multiples.
        # highest role not neccessarily 1.
        # result should not include non permitted contributors.
        # result should not include contributors with None credit role
        primary_contributors = track.get_primary_contributors()
        self.failUnless(contributor1 in primary_contributors)
        self.failUnless(contributor3 in primary_contributors)
        self.failIf(contributor2 in primary_contributors)
        self.failIf(unpublished_contributor in primary_contributors)
        self.failIf(contributor4 in primary_contributors)
'''


class ScraperTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Disable scraping
        settings.JMBO_MUSIC['scrapers'] = []

        # Bootstrap music preferences
        prefs = preferences.MusicPreferences
        prefs.save()
        creditoption = CreditOption.objects.create(
            music_preferences=prefs, role_type='artist', role_name='Artist',
            role_priority=1
        )

        # Legitimate entries
        artist = TrackContributor.objects.create(title="Oasis")
        album = Album.objects.create(title="What's the story morning glory?")
        track = Track.objects.create(title="Don't look back in anger")
        track.create_credit("Oasis", "artist")
        track.album.add(album.id)
        #track.save()
        cls.wikipedia_artist = artist
        cls.wikipedia_album = album
        cls.wikipedia_track = track

        artist = TrackContributor.objects.create(title="Foo Fighters")
        album = Album.objects.create(title="One By One")
        track = Track.objects.create(title="All My Life")
        track.create_credit("Foo Fighters", "artist")
        track.album.add(album.id)
        #track.save()
        cls.lastfm_artist = artist
        cls.lastfm_album = album
        cls.lastfm_track = track

        # Illegitimate entries
        artist = TrackContributor.objects.create(title="vgnfdnvnvfnsncfd")
        album = Album.objects.create(title="tggbfbvfvf")
        track = Track.objects.create(title="grfgrgeagteg")
        track.create_credit("vgnfdnvnvfnsncfd", "artist")
        track.album = [album]
        track.save()
        cls.iartist = artist
        cls.ialbum = album
        cls.itrack = track

    def test_wikipedia(self):
        settings.JMBO_MUSIC['scrapers'] = ['wikipedia']
        wikipedia(self.wikipedia_artist)
        wikipedia(self.wikipedia_album)
        wikipedia(self.wikipedia_track)
        wikipedia(self.iartist)
        wikipedia(self.ialbum)
        wikipedia(self.itrack)
        self.failUnless(self.wikipedia_artist.image)
        self.failUnless(self.wikipedia_album.image)
        self.failUnless(self.wikipedia_track.image)
        self.failIf(self.iartist.image)
        self.failIf(self.ialbum.image)
        # Track is exempt because it always gets a default image

    def test_lastfm(self):
        settings.JMBO_MUSIC['scrapers'] = ['lastfm']
        lastfm(self.lastfm_artist)
        lastfm(self.lastfm_album)
        lastfm(self.lastfm_track)
        lastfm(self.iartist)
        lastfm(self.ialbum)
        lastfm(self.itrack)
        self.failUnless(self.lastfm_artist.image)
        self.failUnless(self.lastfm_album.image)
        self.failUnless(self.lastfm_track.image)
        self.failIf(self.iartist.image)
        self.failIf(self.ialbum.image)
        # Track is exempt because it always gets a default image
