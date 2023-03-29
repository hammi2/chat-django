# Generated by Django 4.1.7 on 2023-02-23 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0030_alter_messageroom_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageroom',
            name='second_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='second_user', to='chat.userprofile'),
        ),
        migrations.AlterField(
            model_name='messageroom',
            name='users_active',
            field=models.ManyToManyField(blank=True, to='chat.userprofile'),
        ),
    ]