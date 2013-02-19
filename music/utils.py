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

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File


def _set_image_via_wikipedia(instance):
    #print "PROCESSING %s" % instance.title

    # Prevent a circular import by importing here
    from music.models import TrackContributor, Track, Album

    # Help wikipedia out with the search string
    if isinstance(instance, TrackContributor):
        search = instance.title + ' artist'
    elif isinstance(instance, Track):
        search = ''
        contributors = instance.get_primary_contributors()
        if contributors:
            search = contributors[0].title + ' '
        search = search + instance.title + ' song'
    elif isinstance(instance, Album):
        search = instance.title + ' album'
    else:
        return

    #print "SEARCH FOR %s" % search

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


def set_image_via_wikipedia(instance):
    # Many things can go wrong. Catch and log.
    try:
        _set_image_via_wikipedia(instance)
    except Exception, e:
        logging.warn("set_image_via_wikipedia - title %s exception %s" \
            % (instance.title, e))


def _set_image_via_lastfm(instance):
    """xxx: lastfm may currently be broken"""    
    INVALID_IMAGE_MD5 = ['28fa757eff47ecfb498512f71dd64f5f']

    # Only artist lookup currently supported
    if not isinstance(instance, TrackContributor):
        return

    try:
        network = pylast.LastFMNetwork(
            api_key=settings.LASTFM_API_KEY,
            api_secret=settings.LASTFM_API_SECRET
        )
        artist = network.get_artist(instance.title)
        image_url = artist.get_cover_image()
        url = artist.get_cover_image()
        if url:
            file_name = '.'.join([instance.title, url.split('.')[-1]]).\
                    replace('/', '-')
            data = urlopen(url).read()
            if hashlib.md5(data).hexdigest() not in INVALID_IMAGE_MD5:
                relative_path = instance.image.upload_to('', file_name)
                f = open(os.path.join(settings.MEDIA_ROOT, relative_path), 'w')
                f.write(data)
                f.close()
    except Exception, e:
        logging.warn("Unable to set image for %s: %s" % (instance.title, e))


def set_image_via_lastfm(instance):
    # Many things can go wrong. Catch and log.
    try:
        _set_image_via_lastfm(instance)
    except Exception, e:
        logging.warn("set_image_via_lastfm - title %s exception %s" \
            % (instance.title, e))

