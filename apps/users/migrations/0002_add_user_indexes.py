# Generated by Django 5.2.4 on 2025-07-10 09:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(
                db_index=True, default=django.utils.timezone.now
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                db_index=True, max_length=254, unique=True, verbose_name="Email Address"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                db_index=True, max_length=50, verbose_name="First Name"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_locked",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(
                db_index=True, max_length=50, verbose_name="Last Name"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                db_index=True, max_length=255, unique=True, verbose_name="Username"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["email", "is_active"], name="users_user_email_3f6199_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["username", "is_active"], name="users_user_usernam_6cca96_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["is_staff", "is_active"], name="users_user_is_staf_5f907d_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["date_joined", "is_active"],
                name="users_user_date_jo_dc0b93_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["is_locked", "failed_login_attempts"],
                name="users_user_is_lock_8f77a2_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["first_name", "last_name"], name="users_user_first_n_6d862e_idx"
            ),
        ),
    ]
