from django.core.management.base import BaseCommand
from django.core.cache import cache
from users.models import User

class Command(BaseCommand):
    help = 'Refresh NCF recommendation caches'
    
    def handle(self, *args, **options):
        self.stdout.write("♻️ Refreshing NCF recommendation caches...")
        
        # Clear all NCF-related caches
        cache_patterns = ['ncf_recommendations_*', 'hybrid_recommendations_*']
        
        # Note: This is simplified - in production use pattern-based deletion
        user_count = User.objects.count()
        cleared = 0
        
        for user in User.objects.all():
            for limit in [10, 20, 50]:
                cache.delete(f"ncf_recommendations_{user.id}_{limit}")
                cache.delete(f"hybrid_recommendations_{user.id}_{limit}")
                cleared += 2
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Cleared {cleared} cache entries for {user_count} users")
        )
