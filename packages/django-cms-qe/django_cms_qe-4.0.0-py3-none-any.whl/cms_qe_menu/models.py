from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils.translation import gettext as _


class MenuPluginModel(CMSPlugin):
    HORIZONTAL = 1
    VERTICAL = 2
    ORIENTATION_CHOICES = (
        (HORIZONTAL, _('Horizontal')),
        (VERTICAL, _('Vertical'))
    )
    orientation = models.IntegerField(choices=ORIENTATION_CHOICES, default=HORIZONTAL)

    # reverse_id in page model
    start_page = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('ID of page in advanced settings.'),
    )
    end_level = models.IntegerField(
        default=2,
        verbose_name=_('End level'),
        help_text=_('''
            Specify at which level the navigation should stop.\n
            Keep in mind that Bootstrap by default does not support dropdown submenu.
            Any deep dropdown menu is not very well accessible from mobile devices.
        '''),
    )

    submenu_in_inactive_item = models.BooleanField(
        default=True,
        verbose_name=_('Submenu for inactive items'),
    )

    def __str__(self):
        return _('Menu')

    @property
    def is_horizontal(self) -> bool:
        return self.orientation == self.HORIZONTAL

    @property
    def is_vertical(self) -> bool:
        return self.orientation == self.VERTICAL

    @property
    def extra_inactive(self) -> int:
        """
        Third parameter of tag `show_menu` of Django CMS. Specifies
        how many sub items should be displayed when item is not active.

        Admin can choose if he wants to show everything or nothing.
        """
        if not self.submenu_in_inactive_item:
            return 0
        return self.end_level

    @property
    def extra_active(self) -> int:
        """
        Fourth parameter of tag `show_menu` of Django CMS. Specifies
        how many sub items should be displayed when item is active.

        For vertical menu is good for users to show only one more
        level, for horizontal with dropdown is possible to show all
        to same deep level admin want to users to be able to go.
        """
        if self.is_horizontal:
            return self.end_level
        return 1
