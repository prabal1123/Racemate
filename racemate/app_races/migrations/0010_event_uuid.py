import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_races', '0009_delete_doublesentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='uuid',
            field=models.UUIDField(null=True, editable=False, blank=True),
        ),
    ]
