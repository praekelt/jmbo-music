import re
import pylast

from django.db import models

from ckeditor.fields import RichTextField
from music import utils
from jmbo.models import ModelBase
from preferences.models import Preferences


# Content models
class AudioEmbed(ModelBase):
    embed = models.TextField()

    class Meta():
        verbose_name = "Audio embed"
        verbose_name_plural = "Audio embeds"


class Album(ModelBase):
    pass


class Credit(models.Model):
    contributor = models.ForeignKey(
        'music.TrackContributor',
        related_name='credits',
    )
    track = models.ForeignKey(
        'music.Track',
        related_name='credits',
    )
    role = models.IntegerField(
        blank=True,
        null=True,
    )


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
        if not self.image:
            self.image = utils.set_image_via_lastfm(
                self.title,
                self._meta.get_field_by_name('image')
            )

        super(TrackContributor, self).save(*args, **kwargs)


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
    )
    length = models.IntegerField(
        blank=True,
        null=True,
        help_text="Length of track in seconds."
    )

    # todo: investigate speed with large datasets
    @property
    def primary_contributors_permitted(self, permitted=True):
        """Returns a list of primary contributors, with primary being
        defined as those contributors that have the highest role
        assigned(in terms of priority).
        """
        primary_credits = []
        credits = self.credits.exclude(role=None).order_by('role')
        if credits.count():
            primary_role = credits[0].role
            for credit in credits:
                if credit.role == primary_role:
                    primary_credits.append(credit)

        contributors = []
        for credit in primary_credits:
            contributor = credit.contributor
            if contributor.is_permitted:
                contributors.append(contributor)

        return contributors

    def create_credit(self, contributor_title, role):
        contributor, created = TrackContributor.objects.get_or_create(
            title=contributor_title
        )
        credit, created = Credit.objects.get_or_create(
            contributor=contributor,
            track=self,
            role=role
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


class MusicCreditOption(models.Model):
    music_preferences = models.ForeignKey('preferences.MusicPreferences')
    role_name = models.CharField(
        max_length=256,
        blank=True,
        null=True,
    )
    role_priority = models.IntegerField(
        blank=True,
        null=True,
    )
