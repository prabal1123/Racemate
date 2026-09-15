import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_tournaments', '0014_populate_tournamentcategory_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentcategory',
            name='uuid',
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
                help_text="Public identifier used in this category's shareable registration link.",
            ),
        ),
    ]
