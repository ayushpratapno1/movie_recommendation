from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.preference_service import RealTimePreferenceService
import json
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Export user behavior data for AI model training'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv'],
            default='json',
            help='Output format (json or csv)'
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='Output file path'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of users to export'
        )
        parser.add_argument(
            '--include-inactive',
            action='store_true',
            help='Include users with no interactions'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Exporting user training data...')
        
        # Get training data
        training_data = RealTimePreferenceService.prepare_ai_training_data(
            user_limit=options['limit']
        )
        
        # Filter out inactive users if needed
        if not options['include_inactive']:
            training_data = [
                data for data in training_data 
                if data.get('engagement_score', 0) > 0
            ]
        
        # Generate filename if not provided
        if not options['output']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            options['output'] = f'training_data_{timestamp}.{options["format"]}'
        
        # Export data
        if options['format'] == 'json':
            self.export_json(training_data, options['output'])
        else:
            self.export_csv(training_data, options['output'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported {len(training_data)} user records to {options["output"]}'
            )
        )
    
    def export_json(self, data, filename):
        """Export data as JSON"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_users': len(data),
            'data': data
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def export_csv(self, data, filename):
        """Export data as CSV"""
        if not data:
            return
        
        # Get all possible keys for CSV headers
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
            # Flatten nested dictionaries
            if 'genre_preferences' in item:
                for genre in item['genre_preferences'].keys():
                    all_keys.add(f'genre_pref_{genre}')
            if 'recent_interactions' in item:
                for interaction in item['recent_interactions'].keys():
                    all_keys.add(f'interaction_{interaction}')
        
        # Remove nested keys from main headers
        csv_keys = [k for k in all_keys if not isinstance(data[0].get(k), dict)]
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(csv_keys))
            writer.writeheader()
            
            for item in data:
                row = {}
                for key in csv_keys:
                    if key.startswith('genre_pref_'):
                        genre = key.replace('genre_pref_', '')
                        row[key] = item.get('genre_preferences', {}).get(genre, 0)
                    elif key.startswith('interaction_'):
                        interaction = key.replace('interaction_', '')
                        row[key] = item.get('recent_interactions', {}).get(interaction, 0)
                    else:
                        row[key] = item.get(key, '')
                writer.writerow(row)
