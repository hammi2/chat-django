# Generated by Django 4.1.7 on 2023-02-20 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0022_userprofile_block_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=150)),
                ('active_users', models.ManyToManyField(related_name='active_users', to='chat.userprofile')),
                ('users', models.ManyToManyField(related_name='group_users', to='chat.userprofile')),
            ],
        ),
    ]
