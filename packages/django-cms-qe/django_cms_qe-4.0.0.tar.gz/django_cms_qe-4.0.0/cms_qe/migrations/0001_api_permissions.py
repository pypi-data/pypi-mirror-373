from django.db import migrations

from cms_qe.api.constants import CMS_QE_USER_ACCES_API_PERMISSION


def create_permission(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    app_label, model = CMS_QE_USER_ACCES_API_PERMISSION.split(".")
    cms_qe_user, _ = ContentType.objects.get_or_create(app_label=app_label)
    Permission.objects.get_or_create(defaults={ "content_type": cms_qe_user, "codename": model}, name="Can access to the API")


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(create_permission),
    ]
