#!/usr/bin/env python3
"""
Convert the existing CSV loot data to the new JSON dungeon format.
This script reads the CSV groups (separated by blank lines) and converts them
to numbered dungeons in JSON format.
"""

import csv
import json

def read_csv_groups(filename):
    """Read the CSV and group items by blank line separators."""
    groups = []
    current_group = []
    
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
    # Skip the header line
    header = lines[0].strip().split(',')
    
    for i, line in enumerate(lines[1:], 1):
        line = line.strip()
        
        # Check if this is a blank line
        if not line:
            # Blank line found - end current group if it has items
            if current_group:
                print(f"  Found group ending at line {i} with {len(current_group)} items")
                groups.append(current_group)
                current_group = []
        else:
            # Parse the CSV line
            parts = [part.strip() for part in line.split(',')]
            
            if len(parts) >= 3 and parts[1]:  # Make sure we have item name
                try:
                    points = float(parts[2]) if parts[2] else None
                except (ValueError, TypeError):
                    points = None
                    
                current_group.append({
                    'loot_type': parts[0],
                    'item_name': parts[1],
                    'points': points
                })
    
    # Don't forget the last group
    if current_group:
        print(f"  Found final group with {len(current_group)} items")
        groups.append(current_group)
    
    return groups

def calculate_default_points(items):
    """Calculate a reasonable default point value for a dungeon based on its items."""
    point_values = [item['points'] for item in items if item['points'] is not None]
    
    if not point_values:
        return 1.0  # Default fallback
    
    # Use median as default
    point_values.sort()
    n = len(point_values)
    if n % 2 == 0:
        default = (point_values[n//2 - 1] + point_values[n//2]) / 2
    else:
        default = point_values[n//2]
    
    return round(default, 1)

def convert_groups_to_json(groups):
    """Convert grouped items to the target JSON format with numbered dungeons."""
    result = {}
    
    for i, group in enumerate(groups, 1):
        dungeon_name = f"dungeon{i}"
        default_points = calculate_default_points(group)
        
        json_items = []
        for item in group:
            json_item = {
                'name': item['item_name'],
                'type': item['loot_type']
            }
            
            # Only add points if they differ from default (with some tolerance)
            if item['points'] is not None and abs(item['points'] - default_points) > 0.1:
                json_item['points'] = item['points']
            
            json_items.append(json_item)
        
        result[dungeon_name] = {
            'default_points': default_points,
            'items': json_items
        }
    
    return result

def main():
    print("Converting CSV to JSON dungeon format...")
    
    # Read the CSV data grouped by blank lines
    csv_filename = 'rotmg_loot_drops_updated.csv'
    groups = read_csv_groups(csv_filename)
    print(f"Found {len(groups)} dungeon groups from CSV")
    
    # Convert to JSON format with numbered dungeons
    json_data = convert_groups_to_json(groups)
    
    # Save to JSON file
    output_filename = 'dungeon_loot.json'
    with open(output_filename, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2, ensure_ascii=False)
    
    print(f"Conversion complete! Saved to {output_filename}")
    
    # Print summary
    print("\nDungeon Summary:")
    for dungeon, data in json_data.items():
        item_count = len(data['items'])
        default_pts = data['default_points']
        print(f"  {dungeon}: {item_count} items, default {default_pts} points")
    
    total_items = sum(len(data['items']) for data in json_data.values())
    print(f"\nTotal: {total_items} items in {len(json_data)} dungeons")
    print("\nYou can now manually replace 'dungeon1', 'dungeon2', etc. with actual dungeon names!")

if __name__ == '__main__':
    main()