import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0007_populate_dimeventcategory_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dimeventcategory',
            name='uuid',
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text='Public identifier used in the shareable registration link for this event.',
            ),
        ),
    ]
