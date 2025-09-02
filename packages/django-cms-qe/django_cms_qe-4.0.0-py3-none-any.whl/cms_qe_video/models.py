import re
from collections.abc import Iterable

from cms.models import CMSPlugin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from djangocms_attributes_field.fields import AttributesField
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField

# mp4, are required for full browser support
ALLOWED_EXTENSIONS = getattr(
    settings,
    'DJANGOCMS_VIDEO_ALLOWED_EXTENSIONS',
    ['mp4', 'webm', 'ogv'],
)


class AbstractVideoPlayer(CMSPlugin):
    """
    Abstract configuration model for video player.
    """
    label = models.CharField(
        verbose_name=_('Label'),
        blank=True,
        max_length=255,
    )
    poster = FilerImageField(
        verbose_name=_('Poster'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    width = models.IntegerField(
        verbose_name=_('Width'),
        blank=True,
        null=True,
        help_text='Leave it blank to make a video player of the default width of video source'
    )
    height = models.IntegerField(
        verbose_name=_('Height'),
        blank=True,
        null=True,
        help_text='Leave it blank to make a video player of the default width of video source'
    )
    controls = models.BooleanField(
        verbose_name=_('Show controls'),
        default=True,
    )
    autoplay = models.BooleanField(
        verbose_name=_('Autoplay'),
        default=False)
    loop = models.BooleanField(
        verbose_name=_('Loop'),
        default=False)
    other_attributes = AttributesField(
        verbose_name=_('Other attributes'),
        blank=True,
    )

    class Meta:
        abstract = True

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin,
        related_name='%(app_label)s_%(class)s',
        parent_link=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.label or str(self.pk)

    def copy_relations(self, old_instance):
        # Because we have a ForeignKey, it's required to copy over
        # the reference from the instance to the new plugin.
        self.poster = old_instance.poster

    def _get_attributes_str_to_html(self, attributes: Iterable[str]) -> str:
        """
        Return string with attributes to add to HTML tag e.g.:
        width="500" autoplay mute
        """
        return ' '.join(
            [f"{attribute}" if isinstance(value, bool) else f"{attribute}={value}"
             for attribute, value in self.__dict__.items() if attribute in attributes and value]
        )

    def _get_attributes_str_to_url(self, attributes: Iterable[str]) -> str:
        """
        Return string with attributes to add to URL e.g.:
        width=500&autoplay=0&mute=0
        """
        return '&'.join(
            [f"{attribute}={int(value)}" for attribute, value in self.__dict__.items()
             if attribute in attributes and value]
        )

    @property
    def attributes_str_to_html(self) -> str:
        """
        Return height and width attributes to put them to html tag. Looks like:
        height="{value}" width="{value}" etc
        """
        attributes_to_print = ('width', 'height', 'controls', 'autoplay', 'loop')
        return self._get_attributes_str_to_html(attributes_to_print)

    @property
    def attributes_str_to_url(self) -> str:
        """
        Return height and width attributes to put them to url. Looks like:
        controls={value}&width={value} etc.
        """
        attributes_to_print = ('controls', 'autoplay', 'loop')
        return self._get_attributes_str_to_url(attributes_to_print)


class SourceFileVideoPlayer(AbstractVideoPlayer):
    """
    Configuration model for video player to play video from file on local disk.
    """
    source_file = FilerFileField(
        verbose_name=_('Source'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    text_title = models.CharField(
        verbose_name=_('Title'),
        blank=True,
        max_length=255,
    )
    text_description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )
    muted = models.BooleanField(
        verbose_name=_('Mute'),
        default=False)

    def __str__(self):
        res = self.label or str(self.pk)
        if not self.source_file:
            res += gettext(' <file is missing>')
        return res

    def clean(self):
        if self.source_file and self.source_file.extension not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                gettext('Incorrect file type: {extension}.').format(extension=self.source_file.extension)
            )

    def get_short_description(self):
        return str(self)

    def copy_relations(self, old_instance):
        # Because we have a ForeignKey, it's required to copy over
        # the reference from the instance to the new plugin.
        self.source_file = old_instance.source_file

    @property
    def attributes_str_to_html(self) -> str:
        """
        Overloaded.
        Add mute attribute to base-class function.
        """
        attributes_to_print = ('muted',)
        return super().attributes_str_to_html + ' ' + self._get_attributes_str_to_html(attributes_to_print)


# Video hosts services constants
YOUTUBE = 1
VIMEO = 2
OTHERS = 3


class HostingVideoPlayer(AbstractVideoPlayer):
    """
    Configuration model for video player to play video from video hosting services.
    """
    VIDEO_HOSTING_SERVICES = (
        (YOUTUBE, 'YouTube'),
        (VIMEO, 'Vimeo'),
        (OTHERS, _('Others'))
    )
    video_hosting_service = models.IntegerField(
        verbose_name=_('Video hosting service'),
        choices=VIDEO_HOSTING_SERVICES,
        default=OTHERS,
    )

    video_url = models.URLField(
        verbose_name=_('Embed link'),
        max_length=255,
        help_text=_('Use this field to embed videos from external services '
                    'such as YouTube, Vimeo or others.'),
    )

    @property
    def size_attributes_str_to_html(self) -> str:
        """
        Return height and width attributes to put them to html tag. Looks like:
        height="{value}" width="{value}"
        """
        attributes_to_print = ('height', 'width')
        return self._get_attributes_str_to_html(attributes_to_print)

    def clean(self):
        """
        Validation URLs. Function checks if URL belongs to selected video host service.
        """
        if self.video_hosting_service == VIMEO:
            if not re.search(r'(^|[/.])vimeo.com/', self.video_url):
                raise ValidationError(_('URL does not belong to Vimeo'))
            if not self.controls:
                raise ValidationError(_('Vimeo does not support hiding controls.'))

        elif self.video_hosting_service == YOUTUBE:
            if not re.search(r'(^|[/.])youtu.be/', self.video_url) and not re.search(r'(^|[/.])youtube.com/',
                                                                                     self.video_url):
                raise ValidationError(_('URL does not belong to YouTube'))


class VideoTrack(CMSPlugin):
    """
    Renders the HTML <track> element inside <video>.
    """
    KIND_CHOICES = [
        ('subtitles', _('Subtitles')),
        ('captions', _('Captions')),
        ('descriptions', _('Descriptions')),
        ('chapters', _('Chapters')),
    ]

    kind = models.CharField(
        verbose_name=_('Kind'),
        choices=KIND_CHOICES,
        max_length=255,
    )
    src = FilerFileField(
        verbose_name=_('Source file'),
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    srclang = models.CharField(
        verbose_name=_('Source language'),
        blank=True,
        max_length=255,
        help_text=_('Examples: "en" or "de" etc.'),
    )
    label = models.CharField(
        verbose_name=_('Label'),
        blank=True,
        max_length=255,
    )
    attributes = AttributesField(
        verbose_name=_('Attributes'),
        blank=True,
    )

    def __str__(self):
        label = self.kind
        if self.srclang:
            label += f' {self.srclang}'
        return label
