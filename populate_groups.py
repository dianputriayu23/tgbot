"""
Script to populate database with groups from existing schedule files
"""
import os
import sys
from database.db import Database
from parser.parser import ScheduleParser

def populate_groups():
    """Populate database with groups from existing XLSX files"""
    db = Database()
    parser = ScheduleParser('https://test.com/', 'schedules')
    
    # Get all XLSX files in current directory
    xlsx_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if not xlsx_files:
        print("No XLSX files found")
        return
    
    print(f"Found {len(xlsx_files)} XLSX files")
    
    all_groups = {}  # {group_name: {'base': '9/11', 'course': 1/2/3}}
    
    for xlsx_file in xlsx_files:
        print(f"\nProcessing: {xlsx_file}")
        data = parser.parse_xlsx(xlsx_file)
        
        for sheet_name, sheet_data in data.items():
            course = sheet_data.get('course', 1)
            groups = sheet_data.get('groups', [])
            
            print(f"  Sheet '{sheet_name}': Course {course}, {len(groups)} groups")
            
            for group in groups:
                # Determine base from group pattern
                # Base 9: groups like Б1-25, Д1-24, Ю1-23 (letter + digit + dash)
                # Base 11: groups like БУ-25, ТД-24, Ю-25 (letters + dash)
                if group and '-' in group:
                    prefix = group.split('-')[0]
                    
                    # If prefix has digit in it (like Б1, Д1), it's base 9
                    has_digit_in_prefix = any(c.isdigit() for c in prefix)
                    base = '9' if has_digit_in_prefix else '11'
                    
                    # Store group info
                    if group not in all_groups:
                        all_groups[group] = {'base': base, 'course': course}
    
    # Add groups to database
    print(f"\n\nAdding {len(all_groups)} unique groups to database...")
    
    for group_name, info in sorted(all_groups.items()):
        db.add_group(group_name, info['base'], info['course'])
        print(f"  Added: {group_name} (Base {info['base']}, Course {info['course']})")
    
    print(f"\n✓ Database populated with {len(all_groups)} groups")
    
    # Show summary
    print("\n=== Summary ===")
    for base in ['9', '11']:
        for course in [1, 2, 3]:
            groups = db.get_groups_by_base_and_course(base, course)
            if groups:
                print(f"Base {base}, Course {course}: {len(groups)} groups")

if __name__ == '__main__':
    populate_groups()
