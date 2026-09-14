import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0005_dimdistrict_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='dimeventcategory',
            name='uuid',
            field=models.UUIDField(null=True, editable=False, blank=True),
        ),
    ]
