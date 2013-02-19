from django import forms
from django.contrib import admin

from jmbo.admin import ModelBaseAdmin
from preferences import preferences
from music.models import AudioEmbed, Album, Credit, CreditOption, Track, \
        TrackContributor, MusicPreferences


class CreditOptionInline(admin.TabularInline):
    model = CreditOption


class MusicPreferencesAdmin(admin.ModelAdmin):
    inlines = [
        CreditOptionInline,
    ]


class TrackCreditInlineAdminForm(forms.ModelForm):

    class Meta:
        model = Credit


class TrackCreditInline(admin.TabularInline):
    form = TrackCreditInlineAdminForm
    model = Credit


class TrackAdmin(ModelBaseAdmin):
    inlines = (
        TrackCreditInline,
    )

admin.site.register(Album, ModelBaseAdmin)
admin.site.register(AudioEmbed, ModelBaseAdmin)
admin.site.register(MusicPreferences, MusicPreferencesAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(TrackContributor, ModelBaseAdmin)
