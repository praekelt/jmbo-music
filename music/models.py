import os
import re

from django.db import models
from django.core.files import File
from django.conf import settings

from ckeditor.fields import RichTextField
from preferences.models import Preferences
from jmbo.models import ModelBase


from music.utils import scrape_image


# Content models
class AudioEmbed(ModelBase):
    embed = models.TextField()

    class Meta():
        verbose_name = "Audio embed"
        verbose_name_plural = "Audio embeds"


class Album(ModelBase):

    def save(self, *args, **kwargs):
        set_image = kwargs.pop('set_image', True)
        super(Album, self).save(*args, **kwargs)
        if set_image:
            self.set_image()

    def set_image(self):
        """This code must be in its own method since the fetch functions need
        credits to be set. m2m fields are not yet set at the end of either the
        save method or post_save signal."""

        if not self.image:
            scrape_image(self)


class Credit(models.Model):
    contributor = models.ForeignKey(
        'music.TrackContributor',
        related_name='credits',
    )
    track = models.ForeignKey(
        'music.Track',
        related_name='credits',
    )
    credit_option = models.ForeignKey('music.CreditOption', null=True)

    def __unicode__(self):
        return self.contributor.title


class TrackContributor(ModelBase):
    profile = RichTextField(
        help_text='Full profile for this contributor.',
        blank=True,
        null=True,
    )
    track = models.ManyToManyField(
        'music.Track',
        through='music.Credit',
        related_name='contributors',
    )

    def save(self, *args, **kwargs):
        super(TrackContributor, self).save(*args, **kwargs)
        if not self.image:
            scrape_image(self)


class Track(ModelBase):
    contributor = models.ManyToManyField(
        'music.TrackContributor',
        through='music.Credit',
        related_name='tracks',
    )
    album = models.ManyToManyField(
        Album,
        blank=True,
        null=True,
    )
    audio_embed = models.TextField(
        blank=True,
        null=True,
        help_text="An audio embed script related to the track.",
    )
    video_embed = models.TextField(
        blank=True,
        null=True,
        help_text="Embedding markup as supplied by Youtube.",
    )
    last_played = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )
    length = models.IntegerField(
        blank=True,
        null=True,
        help_text="Length of track in seconds."
    )

    def __unicode__(self):
        contributors = self.get_primary_contributors()
        if contributors:
            return '%s - %s' % (self.title, contributors[0].title)
        else:
            return self.title

    def save(self, *args, **kwargs):
        set_image = kwargs.pop('set_image', True)
        super(Track, self).save(*args, **kwargs)
        if set_image:
            self.set_image()

    def set_image(self):
        """This code must be in its own method since the fetch functions need
        credits to be set. m2m fields are not yet set at the end of either the
        save method or post_save signal."""

        if not self.image:
            scrape_image(self)

        # If still no image then use first contributor image
        if not self.image:
            contributors = self.get_primary_contributors()
            if contributors:
                self.image = contributors[0].image
                self.save(set_image=False)

        # If still not image then default
        if not self.image:
            filename = settings.STATIC_ROOT + 'music/images/default.png'
            if os.path.exists(filename):
                image = File(
                    open(filename, 'rb')
                )
                image.name = 'default.png'
                self.image = image
                self.save(set_image=False)

    # todo: investigate speed with large datasets
    def get_primary_contributors(self, permitted=False):
        """Returns a list of primary contributors, with primary being
        defined as those contributors that have the highest role
        assigned(in terms of priority).
        """
        primary_credits = []
        credits = self.credits.exclude(
            credit_option=None, credit_option__role_priority=None
        ).order_by('credit_option__role_priority')
        if credits.exists():
            primary_priority = credits[0].credit_option.role_priority
            for credit in credits:
                if credit.credit_option.role_priority == primary_priority:
                    primary_credits.append(credit)

        contributors = []
        for credit in primary_credits:
            contributor = credit.contributor
            if (permitted == False) or \
                ((permitted == True) and contributor.is_permitted):
                contributors.append(contributor)

        return contributors

    @property
    def primary_contributors_permitted(self):
        return self.get_primary_contributors(permitted=True)

    def create_credit(self, contributor_title, role_type):
        contributor, created = TrackContributor.objects.get_or_create(
            title=contributor_title
        )
        if created:
            # Copy some fields to contributor
            contributor.sites = self.sites.all()
            contributor.state = self.state
            contributor.owner = self.owner
            contributor.save()

        # Use first matching credit option if it exists. If it does not exist
        # then create it with available data.
        credit_options = CreditOption.objects.filter(role_type=role_type)
        if credit_options:
            credit_option = credit_options[0]
        else:
            credit_option = CreditOption.objects.create(
                role_type=role_type, role_name=role_type
            )

        credit, created = Credit.objects.get_or_create(
            contributor=contributor,
            track=self,
            credit_option=credit_option
        )
        return credit, contributor

    @property
    def youtube_id(self):
        """Extract and return Youtube video id"""
        if not self.video_embed:
            return ''
        m = re.search(r'/embed/([A-Za-z0-9\-=_]*)', self.video_embed)
        if m:
            return m.group(1)
        return ''

    @property
    def embed(self):
        """Compatibility with jmbo-gallery template tag"""
        return self.video_embed


# Options models
class MusicPreferences(Preferences):
    __module__ = 'preferences.models'

    class Meta:
        verbose_name = "Music preferences"
        verbose_name_plural = "Music preferences"


class CreditOption(models.Model):
    music_preferences = models.ForeignKey('preferences.MusicPreferences')
    role_type = models.CharField(
        max_length=16,
        default='artist',
        choices=(('artist', 'artist'), ('composer', 'composer'), ('other', 'other')),
        help_text="""An identifier used to do internal queries. Pick one that \
closest resembles the credit option."""
    )
    role_name = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="""A friendly name for the credit option."""
    )
    role_priority = models.IntegerField(
        blank=True,
        null=True,
        help_text="""An artist is typically more important than the producer. \
Set role priorities accordingly."""
    )

    def __unicode__(self):
        return self.role_name
