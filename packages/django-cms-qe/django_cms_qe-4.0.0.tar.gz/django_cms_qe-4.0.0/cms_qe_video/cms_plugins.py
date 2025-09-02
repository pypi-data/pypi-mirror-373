from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from cms_qe_video.forms import HostingVideoPlayerForm

from . import models


@plugin_pool.register_plugin
class SourceFileVideoPlayerPlugin(CMSPluginBase):
    model = models.SourceFileVideoPlayer
    module = _('Video player')
    name = _('Video player - source file')
    render_template = 'cms_qe/video/video_source_file.html'
    text_enabled = True
    allow_children = True
    child_classes = ['VideoTrackPlugin']
    fieldsets = [
        (None, {
            'fields': (
                'label',
            )
        }),
        (_('Source file settings'), {
            'fields': (
                'source_file',
                'text_title',
            )
        }),

        (_('Player settings'), {
            'classes': ('collapse',),
            'fields': (
                'width',
                'height',
                'controls',
                'autoplay',
                'loop',
                'muted',
                'other_attributes',
            )
        }),
        (_('Advanced settings'), {
            'classes': ('collapse',),
            'fields': (
                'poster',
                'other_attributes',
                'text_description',
            )
        })
    ]


@plugin_pool.register_plugin
class HostingVideoPlayerPlugin(CMSPluginBase):
    model = models.HostingVideoPlayer
    module = _('Video player')
    name = _('Video player - hosting services')
    text_enabled = True
    render_template = 'cms_qe/video/iframe_with_embed_link.html'
    change_form_template = 'cms_qe/video/video_widget.html'
    form = HostingVideoPlayerForm

    fieldsets = [
        (None, {
            'fields': (
                'label',
                'video_hosting_service',
                'video_url',
            )
        }),
        (_('Player settings'), {
            'classes': ('collapse',),
            'fields': (
                'width',
                'height',
                'controls',
                'autoplay',
                'loop',
                'other_attributes',
            )
        }),
        (_('Advanced settings'), {
            'classes': ('collapse',),
            'fields': (
                'poster',
                'other_attributes',
            )
        })
    ]


@plugin_pool.register_plugin
class VideoTrackPlugin(CMSPluginBase):
    model = models.VideoTrack
    module = _('Video player')
    name = _('Track')
    render_template = 'cms_qe/video/track.html'
    require_parent = True
    parent_classes = ['SourceFileVideoPlayerPlugin']

    fieldsets = [
        (None, {
            'fields': (
                'kind',
                'src',
                'srclang',
            )
        }),
        (_('Advanced settings'), {
            'classes': ('collapse',),
            'fields': (
                'label',
                'attributes',
            )
        })
    ]
