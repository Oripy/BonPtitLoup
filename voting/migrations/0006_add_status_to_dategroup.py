# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0005_auto_20251222_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='dategroup',
            name='status',
            field=models.CharField(choices=[('active', 'Actif'), ('closed', 'Fermé')], default='active', max_length=10, verbose_name='Statut'),
        ),
    ]

