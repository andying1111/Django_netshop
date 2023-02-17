# Generated by Django 4.1.5 on 2023-02-02 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookName', models.CharField(blank=True, max_length=100)),
                ('type', models.CharField(blank=True, max_length=20)),
                ('bookAddress', models.CharField(blank=True, max_length=200)),
                ('bookDate', models.CharField(blank=True, max_length=100)),
                ('author', models.CharField(blank=True, max_length=100)),
                ('info', models.TextField()),
                ('image', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='序号')),
                ('name', models.CharField(max_length=64, verbose_name='名称')),
                ('addr', models.CharField(max_length=64, verbose_name='地址')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(blank=True, max_length=10)),
                ('name', models.CharField(blank=True, max_length=20)),
                ('psd', models.CharField(blank=True, max_length=20)),
                ('phone', models.CharField(blank=True, max_length=11)),
            ],
        ),
        migrations.CreateModel(
            name='UserBookInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(blank=True, max_length=10)),
                ('bookId', models.IntegerField()),
                ('startDate', models.CharField(blank=True, max_length=100)),
                ('endDate', models.CharField(blank=True, max_length=100)),
                ('state', models.IntegerField()),
            ],
        ),
    ]
