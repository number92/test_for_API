# Generated by Django 2.2.19 on 2023-02-07 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20230206_1445'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='text',
            new_name='description',
        ),
    ]
