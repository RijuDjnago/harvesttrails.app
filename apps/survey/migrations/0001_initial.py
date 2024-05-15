# Generated by Django 5.0 on 2024-04-11 11:01

import apps.core.validate
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('farms', '0001_initial'),
        ('field', '0001_initial'),
        ('grower', '0001_initial'),
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Entry Survey', 'Entry Survey'), ('Complete Survey', 'Complete Survey'), ('Sales Survey', 'Sales Survey')], max_length=255)),
            ],
            options={
                'verbose_name': 'Survey Type',
                'verbose_name_plural': 'Survey Types',
            },
        ),
        migrations.CreateModel(
            name='QuestionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_chosen', models.ManyToManyField(to='questions.option')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.question')),
            ],
            options={
                'verbose_name': 'Question Answer',
                'verbose_name_plural': 'Question Answers',
            },
        ),
        migrations.CreateModel(
            name='QuestionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='survey_files/')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('latitude', models.CharField(blank=True, max_length=200, null=True)),
                ('longitude', models.CharField(blank=True, max_length=200, null=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('question_answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='survey.questionanswer')),
            ],
            options={
                'verbose_name': 'Question File',
                'verbose_name_plural': 'Question Files',
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(validators=[apps.core.validate.validate_year])),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_rejected', models.BooleanField(default=True)),
                ('comment', models.TextField(default='No Comments')),
                ('sustainability_score', models.IntegerField(blank=True, null=True)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farms.farm')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='field.field')),
                ('grower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grower.grower')),
                ('survey_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.surveytype')),
            ],
            options={
                'verbose_name': 'Survey',
                'verbose_name_plural': 'Surveys',
            },
        ),
        migrations.AddField(
            model_name='questionanswer',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_answers', to='survey.survey'),
        ),
        migrations.CreateModel(
            name='GrowerNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('status', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grower_notifications', to='survey.survey')),
            ],
            options={
                'verbose_name': 'Grower Notification',
                'verbose_name_plural': 'Grower Notifications',
            },
        ),
        migrations.CreateModel(
            name='ConsultantNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('status', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultant_notifications', to='survey.survey')),
            ],
            options={
                'verbose_name': 'Consultant Notification',
                'verbose_name_plural': 'Consultant Notifications',
            },
        ),
        migrations.CreateModel(
            name='SurveyInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(validators=[apps.core.validate.validate_year])),
                ('survey_date', models.DateTimeField()),
                ('approve_status', models.BooleanField(default=False)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('cons_status', models.BooleanField(default=False)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farms.farm')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='field.field')),
                ('grower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grower.grower')),
            ],
            options={
                'verbose_name': 'Survey Info',
                'verbose_name_plural': 'Survey Info',
            },
        ),
        migrations.CreateModel(
            name='Sustainability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('land_saving', models.IntegerField(blank=True, null=True)),
                ('water_saving', models.IntegerField(blank=True, null=True)),
                ('co2_equivalents_reduced', models.IntegerField(blank=True, null=True)),
                ('grower', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grower.grower')),
            ],
            options={
                'verbose_name': 'Sustainability',
                'verbose_name_plural': 'Sustainability',
            },
        ),
    ]
