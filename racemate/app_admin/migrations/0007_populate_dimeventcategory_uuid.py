import uuid
from django.db import migrations


def populate_uuids(apps, schema_editor):
    DimEventCategory = apps.get_model('app_admin', 'DimEventCategory')
    for category in DimEventCategory.objects.filter(uuid__isnull=True):
        category.uuid = uuid.uuid4()
        category.save(update_fields=['uuid'])


def noop_reverse(apps, schema_editor):
    # Nothing to reverse - leaving uuids populated is harmless.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0006_dimeventcategory_uuid'),
    ]

    operations = [
        migrations.RunPython(populate_uuids, noop_reverse),
    ]
