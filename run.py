"""
Main Application Entry Point
Nepal Trek Recommendation System
"""

import os
import sys
import pandas as pd
from app import create_app, db
from app.models import Trek, User, Rating

app = create_app()

def init_database():
    """Initialize database with trek data from CSV"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Trek.query.count() > 0:
            print(f"Database already has {Trek.query.count()} treks loaded.")
            return
        
        # Find the nepal_treks_official.csv file
        csv_paths = [
            os.path.join(os.path.dirname(__file__), 'data', 'nepal_treks_official.csv'),
            os.path.join(os.path.dirname(__file__), '..', 'data', 'nepal_treks_official.csv'),
        ]
        
        csv_path = None
        for path in csv_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if not csv_path:
            print("Warning: nepal_treks_official.csv not found. Creating sample data...")
            create_sample_data()
            return
        
        print(f"Loading treks from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"Found {len(df)} treks in CSV")
            
            # Column mapping from nepal_treks_official.csv to database model
            column_mapping = {
                'name': 'name',
                'region': 'region',
                'difficulty': 'difficulty',
                'duration_days': 'duration_days',
                'max_altitude_m': 'max_altitude',
                'best_season': 'best_seasons',
                'cost_min_usd': 'cost_min',
                'cost_max_usd': 'cost_max',
                'cultural_score': 'cultural_score',
                'nature_score': 'nature_score',
                'adventure_score': 'adventure_score',
                'requires_permit': 'permit_required',
                'requires_guide': 'guide_required',
                'accommodation_type': 'accommodation_type',
                'fitness_required': 'physical_fitness',
                'technical_skill': 'technical_skills',
                'description': 'description'
            }
            
            # Rename columns
            df_renamed = df.rename(columns=column_mapping)
            
            treks_added = 0
            seen_names = set()
            
            for _, row in df_renamed.iterrows():
                try:
                    trek_name = str(row.get('name', 'Unknown Trek'))
                    
                    # Skip duplicates
                    if trek_name in seen_names:
                        continue
                    seen_names.add(trek_name)
                    
                    # Handle boolean conversions
                    permit_required = row.get('permit_required', 'No')
                    if isinstance(permit_required, str):
                        permit_required = permit_required.lower() in ['yes', 'true', '1']
                    
                    guide_required = row.get('guide_required', 'No')
                    if isinstance(guide_required, str):
                        guide_required = guide_required.lower() in ['yes', 'true', '1']
                    
                    trek = Trek(
                        name=trek_name,
                        region=str(row.get('region', 'Nepal')),
                        difficulty=str(row.get('difficulty', 'Moderate')),
                        duration_days=int(row.get('duration_days', 7)),
                        max_altitude=int(row.get('max_altitude', 3000)),
                        best_seasons=str(row.get('best_seasons', 'Spring|Autumn')).replace('|', ','),
                        cost_min=float(row.get('cost_min', 500)),
                        cost_max=float(row.get('cost_max', 2000)),
                        cultural_score=float(row.get('cultural_score', 0.5)),
                        nature_score=float(row.get('nature_score', 0.5)),
                        adventure_score=float(row.get('adventure_score', 0.5)),
                        permit_required=bool(permit_required),
                        guide_required=bool(guide_required),
                        accommodation_type=str(row.get('accommodation_type', 'Teahouse')),
                        physical_fitness=str(row.get('physical_fitness', 'Moderate')),
                        technical_skills=str(row.get('technical_skills', 'Basic')),
                        description=str(row.get('description', '')),
                        highlights=''
                    )
                    db.session.add(trek)
                    treks_added += 1
                except Exception as e:
                    print(f"Error adding trek: {e}")
                    continue
            
            db.session.commit()
            print(f"Successfully loaded {treks_added} treks into database")
            
            # Create sample users
            create_sample_users()
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            create_sample_data()

def create_sample_users():
    """Create sample users for testing"""
    sample_users = [
        {
            'name': 'John Explorer',
            'age': 28,
            'nationality': 'USA',
            'experience_level': 'Intermediate',
            'fitness_level': 'High',
            'altitude_experience': 4000,
            'budget_min': 1000,
            'budget_max': 3000,
            'available_days': 14,
            'cultural_interest': 0.7,
            'nature_interest': 0.9,
            'adventure_interest': 0.8
        },
        {
            'name': 'Sarah Beginner',
            'age': 25,
            'nationality': 'UK',
            'experience_level': 'Beginner',
            'fitness_level': 'Moderate',
            'altitude_experience': 2000,
            'budget_min': 500,
            'budget_max': 1500,
            'available_days': 7,
            'cultural_interest': 0.9,
            'nature_interest': 0.7,
            'adventure_interest': 0.4
        },
        {
            'name': 'Mike Expert',
            'age': 35,
            'nationality': 'Canada',
            'experience_level': 'Expert',
            'fitness_level': 'High',
            'altitude_experience': 6000,
            'budget_min': 2000,
            'budget_max': 5000,
            'available_days': 21,
            'cultural_interest': 0.5,
            'nature_interest': 0.8,
            'adventure_interest': 1.0
        }
    ]
    
    for user_data in sample_users:
        user = User(**user_data)
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(sample_users)} sample users")

def create_sample_data():
    """Create sample trek data if CSV not found"""
    sample_treks = [
        {
            'name': 'Everest Base Camp Trek',
            'region': 'Everest Region',
            'difficulty': 'Moderate',
            'duration_days': 14,
            'max_altitude': 5364,
            'best_seasons': 'Spring,Autumn',
            'cost_min': 1200,
            'cost_max': 3000,
            'cultural_score': 0.8,
            'nature_score': 0.9,
            'adventure_score': 0.8
        },
        {
            'name': 'Annapurna Circuit',
            'region': 'Annapurna Region',
            'difficulty': 'Moderate',
            'duration_days': 18,
            'max_altitude': 5416,
            'best_seasons': 'Spring,Autumn',
            'cost_min': 1000,
            'cost_max': 2500,
            'cultural_score': 0.9,
            'nature_score': 0.95,
            'adventure_score': 0.85
        },
        {
            'name': 'Langtang Valley Trek',
            'region': 'Langtang Region',
            'difficulty': 'Easy',
            'duration_days': 10,
            'max_altitude': 4984,
            'best_seasons': 'Spring,Autumn,Winter',
            'cost_min': 600,
            'cost_max': 1500,
            'cultural_score': 0.85,
            'nature_score': 0.85,
            'adventure_score': 0.6
        }
    ]
    
    for trek_data in sample_treks:
        trek = Trek(**trek_data)
        db.session.add(trek)
    
    db.session.commit()
    create_sample_users()
    print("Created sample treks and users")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Nepal Trek Recommendation System")
    print("="*60)
    
    # Initialize database
    init_database()
    
    # Get port from environment or default
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\nStarting server on http://localhost:{port}")
    print("Open this URL in your browser to access the application")
    print("="*60 + "\n")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=port)
