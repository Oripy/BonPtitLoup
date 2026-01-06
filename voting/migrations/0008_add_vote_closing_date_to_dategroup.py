# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0007_merge_status_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='dategroup',
            name='vote_closing_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date de fermeture des votes'),
        ),
    ]

