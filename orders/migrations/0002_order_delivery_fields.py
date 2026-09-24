from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='revision_feedback',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('Pending', 'Pending'),
                    ('In_progress', 'In_progress'),
                    ('Delivered', 'Delivered'),
                    ('Completed', 'Completed'),
                    ('Canceled', 'Canceled'),
                ],
                default='Pending',
                max_length=15,
            ),
        ),
    ]
