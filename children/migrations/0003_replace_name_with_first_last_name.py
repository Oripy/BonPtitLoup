# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_name_to_first_last_name(apps, schema_editor):
    """Migrate existing name data to first_name and last_name"""
    Child = apps.get_model('children', 'Child')
    for child in Child.objects.all():
        # Split name into first_name and last_name
        # If name contains spaces, use first word as first_name, rest as last_name
        # Otherwise, use entire name as first_name
        name_parts = child.name.split(maxsplit=1)
        if len(name_parts) == 2:
            child.first_name = name_parts[0]
            child.last_name = name_parts[1]
        else:
            child.first_name = child.name
            child.last_name = ''  # Empty last name if only one word
        child.save()


def reverse_migrate(apps, schema_editor):
    """Reverse migration: combine first_name and last_name back to name"""
    Child = apps.get_model('children', 'Child')
    for child in Child.objects.all():
        if child.last_name:
            child.name = f"{child.first_name} {child.last_name}"
        else:
            child.name = child.first_name
        child.save()


class Migration(migrations.Migration):

    dependencies = [
        ('children', '0002_merge_status_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: Add new fields as nullable
        migrations.AddField(
            model_name='child',
            name='first_name',
            field=models.CharField(max_length=100, null=True, blank=True, verbose_name='Prénom'),
        ),
        migrations.AddField(
            model_name='child',
            name='last_name',
            field=models.CharField(max_length=100, null=True, blank=True, verbose_name='Nom'),
        ),
        # Step 2: Migrate data
        migrations.RunPython(migrate_name_to_first_last_name, reverse_migrate),
        # Step 3: Make fields non-nullable
        migrations.AlterField(
            model_name='child',
            name='first_name',
            field=models.CharField(max_length=100, verbose_name='Prénom'),
        ),
        migrations.AlterField(
            model_name='child',
            name='last_name',
            field=models.CharField(max_length=100, verbose_name='Nom'),
        ),
        # Step 4: Remove old name field
        migrations.RemoveField(
            model_name='child',
            name='name',
        ),
        # Step 5: Update ordering
        migrations.AlterModelOptions(
            name='child',
            options={'ordering': ['last_name', 'first_name'], 'verbose_name': 'Enfant', 'verbose_name_plural': 'Enfants'},
        ),
    ]

