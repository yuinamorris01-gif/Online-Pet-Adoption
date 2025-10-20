#!/usr/bin/env python3
"""
Add sample pets to the database for modern UI demonstration
"""
import sqlite3
from datetime import datetime

def add_sample_pets():
    """Add sample pets with elegant names matching the modern UI design"""
    
    # Sample pets data inspired by the JARVIS pet in the UI mockup
    sample_pets = [
        {
            'name': 'JARVIS',
            'species': 'Dog',
            'breed': 'German Shepherd',
            'age': 3,
            'gender': 'Male',
            'size': 'Large',
            'description': 'Intelligent and loyal companion with beautiful amber eyes. JARVIS is well-trained, loves outdoor activities, and gets along great with children. He has a calm demeanor and protective instincts that make him an ideal family pet.',
            'special_needs': '',
            'vaccination_status': 'Up to date',
            'location': 'Downtown Shelter',
            'status': 'available'
        },
        {
            'name': 'ARIA',
            'species': 'Cat',
            'breed': 'Siamese',
            'age': 2,
            'gender': 'Female',
            'size': 'Medium',
            'description': 'Elegant and graceful feline with striking blue eyes. Aria is playful, intelligent, and enjoys interactive toys. She loves sunbathing and has a gentle purr that will melt your heart.',
            'special_needs': '',
            'vaccination_status': 'Up to date',
            'location': 'City Animal Center',
            'status': 'available'
        },
        {
            'name': 'THOR',
            'species': 'Dog',
            'breed': 'Golden Retriever',
            'age': 4,
            'gender': 'Male',
            'size': 'Large',
            'description': 'Strong and gentle giant with a heart of gold. Thor loves swimming, playing fetch, and is excellent with kids. His friendly nature makes him perfect for active families.',
            'special_needs': '',
            'vaccination_status': 'Up to date',
            'location': 'Riverside Shelter',
            'status': 'available'
        },
        {
            'name': 'LUNA',
            'species': 'Cat',
            'breed': 'Russian Blue',
            'age': 1,
            'gender': 'Female',
            'size': 'Small',
            'description': 'Mysterious and beautiful with silver-blue coat. Luna is curious, affectionate, and loves exploring. She has a playful spirit and would make a wonderful addition to any loving home.',
            'special_needs': '',
            'vaccination_status': 'Up to date',
            'location': 'Metro Pet Rescue',
            'status': 'available'
        },
        {
            'name': 'ATLAS',
            'species': 'Dog',
            'breed': 'Husky',
            'age': 5,
            'gender': 'Male',
            'size': 'Large',
            'description': 'Adventure-loving companion with striking blue eyes and thick coat. Atlas is energetic, intelligent, and loves hiking. He needs an active family who can match his enthusiasm for outdoor activities.',
            'special_needs': '',
            'vaccination_status': 'Up to date',
            'location': 'Mountain View Shelter',
            'status': 'available'
        },
        {
            'name': 'NOVA',
            'species': 'Cat',
            'breed': 'Maine Coon',
            'age': 3,
            'gender': 'Female',
            'size': 'Large',
            'description': 'Majestic and fluffy with a gentle personality. Nova is social, intelligent, and loves being around people. Her calm nature and beautiful coat make her a perfect indoor companion.',
            'special_needs': '',
            'vaccination_status': 'Up to date',
            'location': 'Westside Animal Haven',
            'status': 'available'
        }
    ]
    
    conn = sqlite3.connect('pet_adoption.db')
    cursor = conn.cursor()
    
    try:
        for pet in sample_pets:
            # Check if pet already exists
            existing = cursor.execute('SELECT id FROM pets WHERE name = ?', (pet['name'],)).fetchone()
            if existing:
                print(f"Pet {pet['name']} already exists, skipping...")
                continue
            
            # Insert new pet
            cursor.execute('''
                INSERT INTO pets (name, species, breed, age, gender, size, description,
                                special_needs, vaccination_status, location, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pet['name'],
                pet['species'],
                pet['breed'],
                pet['age'],
                pet['gender'],
                pet['size'],
                pet['description'],
                pet['special_needs'],
                pet['vaccination_status'],
                pet['location'],
                pet['status']
            ))
            
            print(f"Added pet: {pet['name']} ({pet['species']}, {pet['breed']})")
        
        conn.commit()
        
        # Display current total
        total_pets = cursor.execute('SELECT COUNT(*) FROM pets').fetchone()[0]
        print(f"\nTotal pets in database: {total_pets}")
        
    except Exception as e:
        print(f"Error adding pets: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("Adding sample pets for modern UI demonstration...")
    add_sample_pets()
    print("Sample pets added successfully!")
