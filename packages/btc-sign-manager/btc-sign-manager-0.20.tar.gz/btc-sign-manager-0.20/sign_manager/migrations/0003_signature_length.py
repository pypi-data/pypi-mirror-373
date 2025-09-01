from django.db import migrations, models
import sign_manager.models


class Migration(migrations.Migration):
    dependencies = [
        ('sign_manager', '0002_signature_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signmanagersignature',
            name='signature',
            field=models.FileField(upload_to=sign_manager.models.get_signature_file_path, verbose_name='Подпись'),
        ),
    ]
