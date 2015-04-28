import cStringIO
import hashlib
import logging
import mimetypes
import os
import re
import json
from urllib import urlopen, urlencode, urlretrieve
import urllib2
from lxml import etree
import pylast

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
from django.conf import settings


def _wikipedia(instance):

    # Prevent a circular import by importing here
    from music.models import TrackContributor, Track, Album

    # Help wikipedia out with the search string
    if isinstance(instance, TrackContributor):
        search = instance.title + ' artist band'
    elif isinstance(instance, Track):
        # Track pages usually don't exist on Wikipedia so preferably use artist
        contributors = instance.get_primary_contributors()
        if contributors:
            search = contributors[0].title + ' artist band'
        else:
            # Maybe we get lucky with just the song title
            search = instance.title + ' song'
    elif isinstance(instance, Album):
        search = instance.title + ' album'
    else:
        return

    # Common settings
    url = 'http://en.wikipedia.org/w/api.php'
    headers = {'User-Agent': 'Jmbo Show HTTP Request'}

    # Do a search
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': unicode(search).encode('utf-8'),
        'srlimit': 1,
        'format': 'json'
    }
    request = urllib2.Request(url, urlencode(params), headers)
    response = urllib2.urlopen(request)
    data = response.read()
    struct = json.loads(data)
    try:
        title = struct['query']['search'][0]['title']
    except (KeyError, IndexError):
        return

    # Get the infobox summary
    # Example: http://en.wikipedia.org/w/api.php?action=query&titles=Pink (singer)&prop=revisions&rvprop=content&rvsection=0&format=xml
    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': unicode(title).encode('utf-8'),
        'rvprop': 'content',
        'rvsection': 0,
        'format': 'xml'
    }
    request = urllib2.Request(url, urlencode(params), headers)
    response = urllib2.urlopen(request)
    data = response.read()

    # Does info box contain an image?
    m = re.search(r'(Cover|image)[\s=]*([^\|]*)', data, re.M|re.I|re.DOTALL)
    if m:
        filename = m.group(2).strip()

        # Retrieve imageinfo
        # Example: http://en.wikipedia.org/w/api.php?action=query&prop=imageinfo&titles=File:Pink 3.jpg&iiprop=url
        params = {
            'action': 'query',
            'prop': 'imageinfo',
            'titles': 'File:%s' % filename,
            'iiprop': 'url',
            'format': 'xml'
        }
        request = urllib2.Request(url, urlencode(params), headers)
        response = urllib2.urlopen(request)
        data = response.read()
        xml = etree.fromstring(data)

        # Extract image url. Fetch and save.
        el = xml.find('.//ii')
        if el is not None:
            url_attr = el.get('url')
            if url_attr:
                tempfile = urlretrieve(url_attr)
                instance.image.save(filename, File(open(tempfile[0])))


def wikipedia(instance):
    # Many things can go wrong. Catch and log.
    try:
        _wikipedia(instance)
    except Exception, e:
        logging.warn("_wikipedia - title %s exception %s" \
            % (instance.title, e))


def _lastfm(instance):

    di = getattr(settings, 'JMBO_MUSIC', {})
    try:
        api_key = settings.JMBO_MUSIC['lastfm_api_key']
        api_secret = settings.JMBO_MUSIC['lastfm_api_secret']
    except (AttributeError, KeyError):
        raise RuntimeError("Settings is not configured properly")

    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)

    # Prevent a circular import by importing here
    from music.models import TrackContributor, Track, Album

    if isinstance(instance, TrackContributor):
        try:
            obj = network.get_artist(instance.title)
        except pylast.WSError:
            return
    elif isinstance(instance, Track):
        # Tracks don't have images on Last.fm so use artist
        contributors = instance.get_primary_contributors()
        if contributors:
            try:
                obj = network.get_artist(contributors[0].title)
            except pylast.WSError:
                return
        else:
            return
    elif isinstance(instance, Album):
        # We need the primary contributor but can't jump with 100% certainty to
        # the track, so make a best effort.
        tracks = instance.track_set.all()
        contributors = None
        if tracks:
            contributors = tracks[0].get_primary_contributors()
        if contributors:
            artist = contributors[0].title
        else:
            artist = None
        try:
            obj = network.get_album(artist, instance.title)
        except pylast.WSError:
            return
    else:
        return

    try:
        url = obj.get_cover_image()
    except pylast.WSError:
        return

    if url:
        filename = url.split('/')[-1]
        tempfile = urlretrieve(url)
        instance.image.save(filename, File(open(tempfile[0])))


def lastfm(instance):
    # Many things can go wrong. Catch and log.
    try:
        _lastfm(instance)
    except Exception, e:
        logging.warn("_lastfm - title %s exception %s" \
            % (instance.title, e))


def scrape_image(instance):
    di = getattr(settings, 'JMBO_MUSIC', {})
    scrapers = di.get('scrapers', ('lastfm', 'wikipedia'))
    for scraper in scrapers:
        globals()[scraper](instance)
        if instance.image:
            break
