import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models, connection
from django.db.models import UniqueConstraint


def insert_team_memberships(apps, schema_editor):
    if connection.vendor == 'postgresql':
        schema_editor.execute("""
            INSERT INTO users_teammembership (user_id, team_id, role)
            SELECT user_id, team_id, 'MB'
            FROM users_team_members;
            """)

        schema_editor.execute("""
            INSERT INTO users_teammembership (user_id, team_id, role)
            SELECT user_id, team_id, 'AD'
            FROM users_team_admins
            ON CONFLICT (user_id, team_id) DO UPDATE SET role = 'AD';
            """)

        schema_editor.execute("""
            INSERT INTO users_teammembership (user_id, team_id, role)
            SELECT pi_id, id, 'OW'
            FROM users_team
            ON CONFLICT (user_id, team_id) DO UPDATE SET role = 'OW';
        """)

    elif connection.vendor == 'sqlite':
        schema_editor.execute("""
            INSERT INTO users_teammembership (user_id, team_id, role)
            SELECT user_id, team_id, 'MB'
            FROM users_team_members;
        """)

        schema_editor.execute("""
            INSERT OR REPLACE INTO users_teammembership (user_id, team_id, role)
            SELECT user_id, team_id, 'AD'
            FROM users_team_admins;
        """)

        schema_editor.execute("""
            INSERT OR REPLACE INTO users_teammembership (user_id, team_id, role)
            SELECT pi_id, id, 'OW'
            FROM users_team;
        """)

class Migration(migrations.Migration):

    dependencies = [
        ('allocations', '0009_remove_allocationrequest_group'),
        ('research_products', '0003_remove_grant_group_remove_publication_group'),
        ('users', '0008_user_profile_image'),
    ]

    operations = [
        # "Research groups" have been renamed to "teams"
        migrations.RenameModel('ResearchGroup', 'Team'),

        # Teams have a new membership/role structure
        # Create a table for storing that structure
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('OW', 'Owner'), ('AD', 'Admin'), ('MB', 'Member')], max_length=2)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [
                    UniqueConstraint(fields=['user', 'team'], name='unique_user_team')
                ],
            },
        ),

        # Create relationships for the new table
        migrations.AddField(
            model_name='team',
            name='users',
            field=models.ManyToManyField(through='users.TeamMembership', to=settings.AUTH_USER_MODEL),
        ),

        # Move old user permissions to the new model
        migrations.RunPython(insert_team_memberships),

        # Remove models/fields used to track the old permissions
        migrations.RemoveField(model_name='Team', name='pi'),
        migrations.RemoveField(model_name='Team', name='admins'),
        migrations.RemoveField(model_name='Team', name='members'),
    ]
