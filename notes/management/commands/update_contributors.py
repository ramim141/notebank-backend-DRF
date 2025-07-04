# notes/management/commands/update_contributors.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notes.signals import update_contributor_stats  # আমাদের তৈরি করা ফাংশনটি ইমপোর্ট করুন

User = get_user_model()

class Command(BaseCommand):
    help = 'Updates or creates contributor profiles for all users with approved notes.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting contributor profile update...'))
        
        # শুধুমাত্র সেইসব ইউজারদের নিন যাদের অন্তত একটি অ্যাপ্রুভড নোট আছে
        users_with_notes = User.objects.filter(uploaded_notes__is_approved=True).distinct()
        
        if not users_with_notes.exists():
            self.stdout.write(self.style.WARNING('No users with approved notes found.'))
            return
            
        count = 0
        for user in users_with_notes:
            self.stdout.write(f'Updating stats for user: {user.username}')
            update_contributor_stats(user)
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} contributor profiles.'))