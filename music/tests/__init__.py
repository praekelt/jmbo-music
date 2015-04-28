from django.test import TestCase
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet

from preferences import preferences

from music.models import TrackContributor, Credit, Track, Album, CreditOption
from music.utils import wikipedia, lastfm


class ScraperTestCase(TestCase):

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
        album = Album.objects.create(title="What's the story morning glory")
        track = Track.objects.create(title="Don't look back in anger")
        track.create_credit("Oasis", "artist")
        track.album.add(album.id)
        track.save()
        cls.wikipedia_artist = artist
        cls.wikipedia_album = album
        cls.wikipedia_track = track

        artist = TrackContributor.objects.create(title="Foo Fighters")
        album = Album.objects.create(title="One By One")
        track = Track.objects.create(title="All My Life")
        track.create_credit("Foo Fighters", "artist")
        track.album.add(album.id)
        track.save()
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
        # Abort test if no API key was set
        try:
            dc = settings.JMBO_MUSIC['lastfm_api_key']
            dc = settings.JMBO_MUSIC['lastfm_api_secret']
        except KeyError:
            return
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
