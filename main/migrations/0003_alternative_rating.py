# Generated by Django 5.2.1 on 2025-05-18 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_alternative_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternative',
            name='rating',
            field=models.IntegerField(default=0, help_text='Рейтинг альтернативи (ціле число)'),
        ),
    ]
