#!/usr/bin/env python3
"""
Converts the existing CSV loot data to JSON format while preserving the dungeon groupings.
Groups are determined by blank lines in the CSV file.
"""

import csv
import json
from typing import Dict, List, Any

def convert_csv_to_json(csv_file: str, output_file: str) -> None:
    """Convert CSV to JSON format with dungeon groupings based on blank lines."""
    
    dungeons_data = {}
    current_dungeon_num = 1
    current_items = []
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Check if this is a blank line (all values are empty or whitespace)
            if all(not str(value).strip() for value in row.values()):
                # We hit a blank line - save current group and start new one
                if current_items:
                    dungeon_name = f"dungeon{current_dungeon_num}"
                    dungeons_data[dungeon_name] = {
                        "default_points": 1.0,  # Default value, can be changed later
                        "items": current_items
                    }
                    current_dungeon_num += 1
                    current_items = []
                continue
            
            # Skip if item name is empty
            item_name = row['Item Name'].strip()
            if not item_name:
                continue
            
            # Create item entry
            item = {
                "name": item_name,
                "type": row['Loot Type'].strip()
            }
            
            # Add points if they exist and are different from what would be default
            points_str = row['Points'].strip()
            if points_str:
                try:
                    points = float(points_str)
                    if points != 1.0:  # Only store if different from default
                        item["points"] = points
                except ValueError:
                    pass
            
            current_items.append(item)
    
    # Don't forget the last group if the file doesn't end with a blank line
    if current_items:
        dungeon_name = f"dungeon{current_dungeon_num}"
        dungeons_data[dungeon_name] = {
            "default_points": 1.0,
            "items": current_items
        }
    
    # Write JSON output
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(dungeons_data, file, indent=2, ensure_ascii=False)
    
    print(f"Conversion complete!")
    print(f"- Input: {csv_file}")
    print(f"- Output: {output_file}")
    print(f"- Found {len(dungeons_data)} dungeon groups")
    
    # Show summary
    total_items = sum(len(dungeon["items"]) for dungeon in dungeons_data.values())
    print(f"- Total items: {total_items}")
    
    # Show first few groups as preview
    for i, (dungeon_name, dungeon_data) in enumerate(list(dungeons_data.items())[:3]):
        item_count = len(dungeon_data["items"])
        first_item = dungeon_data["items"][0]["name"] if dungeon_data["items"] else "No items"
        print(f"  {dungeon_name}: {item_count} items (first: {first_item})")

if __name__ == "__main__":
    convert_csv_to_json("rotmg_loot_drops_updated.csv", "rotmg_loot_data.json")