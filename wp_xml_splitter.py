#!/usr/bin/env python3
"""
WordPress to Ghost XML Splitter

Author: Gunjan Jaswal
Email: hello@gunjanjaswal.me
Website: gunjanjaswal.me

This script splits a WordPress XML export file into smaller chunks for Ghost import.
It preserves all necessary XML headers and namespaces for proper import.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
import datetime
import uuid
import shutil
import tempfile
import zipfile
from pathlib import Path

# Register WordPress XML namespaces
NAMESPACES = {
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wfw': 'http://wellformedweb.org/CommentAPI/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'wp': 'http://wordpress.org/export/1.2/',
}

def register_namespaces():
    """Register XML namespaces for proper parsing and output"""
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)

def count_items(xml_file, post_types=None):
    """
    Count the number of items in the WordPress XML export file
    
    Args:
        xml_file (str): Path to WordPress XML export file
        post_types (list): List of post types to count (e.g., ['post', 'page'])
        
    Returns:
        dict: Count of items by type
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all items
        channel = root.find('channel')
        if channel is None:
            return {'total': 0, 'posts': 0, 'pages': 0, 'attachments': 0, 'other': 0}
            
        items = channel.findall('item')
        
        # Count by type
        counts = {
            'total': len(items),
            'posts': 0,
            'pages': 0,
            'attachments': 0,
            'other': 0
        }
        
        for item in items:
            post_type = item.find('.//{http://wordpress.org/export/1.2/}post_type')
            if post_type is not None:
                post_type_text = post_type.text
                if post_type_text == 'post':
                    counts['posts'] += 1
                elif post_type_text == 'page':
                    counts['pages'] += 1
                elif post_type_text == 'attachment':
                    counts['attachments'] += 1
                else:
                    counts['other'] += 1
            else:
                counts['other'] += 1
                
        return counts
    except Exception as e:
        print(f"Error counting items: {e}")
        return {'total': 0, 'posts': 0, 'pages': 0, 'attachments': 0, 'other': 0}

def split_wordpress_xml(xml_file, output_dir=None, chunk_size=100, post_types=None):
    """
    Split WordPress XML export file into smaller chunks
    
    Args:
        xml_file (str): Path to WordPress XML export file
        output_dir (str): Directory to save split files
        chunk_size (int): Number of items per chunk
        post_types (list): List of post types to include (e.g., ['post', 'page'])
        
    Returns:
        list: Paths to the generated XML files
    """
    register_namespaces()
    
    # Create output directory if not specified
    if output_dir is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"wp_split_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get channel element
        channel = root.find('channel')
        if channel is None:
            print("Error: Invalid WordPress XML export file (no channel element found)")
            return []
        
        # Get all items
        items = channel.findall('item')
        if not items:
            print("Error: No items found in WordPress XML export file")
            return []
        
        # Filter items by post type if specified
        if post_types:
            filtered_items = []
            for item in items:
                post_type = item.find('.//{http://wordpress.org/export/1.2/}post_type')
                if post_type is not None and post_type.text in post_types:
                    filtered_items.append(item)
            items = filtered_items
        
        # Calculate number of chunks
        total_items = len(items)
        if total_items == 0:
            print("No items to split (after filtering)")
            return []
            
        num_chunks = (total_items + chunk_size - 1) // chunk_size
        
        # Create a copy of the tree for each chunk
        output_files = []
        
        for i in range(num_chunks):
            # Create a deep copy of the original tree
            chunk_tree = ET.ElementTree(ET.fromstring(ET.tostring(root, encoding='utf-8')))
            chunk_root = chunk_tree.getroot()
            chunk_channel = chunk_root.find('channel')
            
            # Remove all existing items from the channel
            for item in chunk_channel.findall('item'):
                chunk_channel.remove(item)
            
            # Add items for this chunk
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, total_items)
            
            for j in range(start_idx, end_idx):
                # Add a deep copy of the item to the chunk
                item_copy = ET.fromstring(ET.tostring(items[j], encoding='utf-8'))
                chunk_channel.append(item_copy)
            
            # Write the chunk to a file
            output_file = os.path.join(output_dir, f"wordpress_export_chunk_{i+1}_of_{num_chunks}.xml")
            chunk_tree.write(output_file, encoding='utf-8', xml_declaration=True)
            output_files.append(output_file)
            
            print(f"Created chunk {i+1} of {num_chunks}: {output_file}")
        
        return output_files
    
    except Exception as e:
        print(f"Error splitting WordPress XML: {e}")
        return []

def create_zip_archive(files, output_dir=None):
    """
    Create a ZIP archive containing the split XML files
    
    Args:
        files (list): List of file paths to include in the ZIP
        output_dir (str): Directory to save the ZIP file
        
    Returns:
        str: Path to the ZIP file
    """
    if not files:
        return None
        
    if output_dir is None:
        output_dir = os.path.dirname(files[0])
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_file = os.path.join(output_dir, f"wordpress_export_chunks_{timestamp}.zip")
    
    try:
        with zipfile.ZipFile(zip_file, 'w') as zipf:
            for file in files:
                zipf.write(file, os.path.basename(file))
        
        return zip_file
    except Exception as e:
        print(f"Error creating ZIP archive: {e}")
        return None

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Split WordPress XML export file into smaller chunks for Ghost import')
    parser.add_argument('xml_file', help='Path to WordPress XML export file')
    parser.add_argument('-o', '--output-dir', help='Directory to save split files')
    parser.add_argument('-c', '--chunk-size', type=int, default=100, help='Number of items per chunk (default: 100)')
    parser.add_argument('-t', '--post-types', nargs='+', help='Post types to include (e.g., post page attachment)')
    parser.add_argument('-z', '--zip', action='store_true', help='Create a ZIP archive of the split files')
    parser.add_argument('-a', '--analyze', action='store_true', help='Only analyze the XML file without splitting')
    
    args = parser.parse_args()
    
    # Check if the XML file exists
    if not os.path.isfile(args.xml_file):
        print(f"Error: File not found: {args.xml_file}")
        return 1
    
    # Analyze the XML file
    counts = count_items(args.xml_file)
    
    print(f"\nAnalysis of {os.path.basename(args.xml_file)}:")
    print(f"Total items: {counts['total']}")
    print(f"Posts: {counts['posts']}")
    print(f"Pages: {counts['pages']}")
    print(f"Attachments: {counts['attachments']}")
    print(f"Other items: {counts['other']}")
    
    if args.analyze:
        return 0
    
    # Recommend chunk size for large files
    if counts['total'] > 500 and args.chunk_size > 50:
        print(f"\nWarning: Your file has {counts['total']} items. For Ghost import, a smaller chunk size is recommended.")
        print(f"Consider using --chunk-size 50 for better results.")
    
    # Split the XML file
    print(f"\nSplitting XML file into chunks of {args.chunk_size} items...")
    output_files = split_wordpress_xml(
        args.xml_file, 
        args.output_dir, 
        args.chunk_size, 
        args.post_types
    )
    
    if not output_files:
        print("Error: Failed to split XML file")
        return 1
    
    # Create a ZIP archive if requested
    if args.zip:
        zip_file = create_zip_archive(output_files)
        if zip_file:
            print(f"\nCreated ZIP archive: {zip_file}")
    
    print("\nDone!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
