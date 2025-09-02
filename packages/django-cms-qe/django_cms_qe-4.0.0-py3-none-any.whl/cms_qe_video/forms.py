from django import forms

from .models import HostingVideoPlayer


class HostingVideoPlayerForm(forms.ModelForm):
    """
    Adding ids (HTML attributes) to control(checkbox) and video_hosting_service(selection) to process with JS.
    Script with processing: templates/cms_qe/defaul/video_widget.html
    """

    class Meta:
        model = HostingVideoPlayer
        fields = '__all__'
        widgets = {
            'controls': forms.CheckboxInput(attrs={'id': 'django-cms-qe-vimeo-disabled'}),
            'video_hosting_service': forms.Select(attrs={'id': 'django-cms-qe-hosting-choices'})
        }
