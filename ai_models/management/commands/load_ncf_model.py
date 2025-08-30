from django.core.management.base import BaseCommand
from ai_models.ncf_service import NCFModelService

class Command(BaseCommand):
    help = 'Load and verify NCF model'
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Loading Maximum Performance NCF model...")
        
        service = NCFModelService()
        
        if service.is_model_loaded():
            self.stdout.write(
                self.style.SUCCESS("✅ NCF model loaded successfully!")
            )
            self.stdout.write(f"   Model parameters: {service._model.count_params():,}")
        else:
            self.stdout.write(
                self.style.ERROR("❌ Failed to load NCF model")
            )
