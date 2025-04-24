#!/usr/bin/env python3
"""
WordPress to Ghost XML Splitter - Web Interface

Author: Gunjan Jaswal
Email: hello@gunjanjaswal.me
Website: gunjanjaswal.me

Flask web application for splitting WordPress XML export files into smaller chunks for Ghost import.
"""

import os
import sys
import uuid
import shutil
import tempfile
import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session

# Import the XML splitter module
from wp_xml_splitter import count_items, split_wordpress_xml, create_zip_archive

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# Add context processor to provide current date/time to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

@app.route('/')
def index():
    """Render the home page with file upload form"""
    # Clear any existing session data
    session.pop('xml_file', None)
    session.pop('counts', None)
    session.pop('filename', None)
    session.pop('output_dir', None)
    session.pop('zip_file', None)
    
    # Clean up temporary files
    cleanup_temp_files()
    
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analyze the WordPress XML file"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not file.filename.lower().endswith('.xml'):
        flash('Only XML files are allowed', 'error')
        return redirect(url_for('index'))
    
    try:
        # Save the uploaded file
        filename = str(uuid.uuid4()) + '.xml'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the XML file
        counts = count_items(filepath)
        
        if counts['total'] == 0:
            flash('Invalid WordPress XML file or no items found', 'error')
            return redirect(url_for('index'))
        
        # Store file info in session
        session['xml_file'] = filepath
        session['counts'] = counts
        session['filename'] = file.filename
        
        return redirect(url_for('analyze'))
    
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze')
def analyze():
    """Render the analysis page with content summary and splitting options"""
    if 'xml_file' not in session or 'counts' not in session:
        flash('Please upload a WordPress XML file first', 'warning')
        return redirect(url_for('index'))
    
    return render_template('analyze.html', 
                          filename=session['filename'],
                          counts=session['counts'])

@app.route('/split', methods=['POST'])
def split():
    """Split the WordPress XML file into smaller chunks"""
    if 'xml_file' not in session:
        flash('Please upload a WordPress XML file first', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Get form data
        chunk_size = int(request.form.get('chunk_size', 100))
        post_types = request.form.getlist('post_types')
        
        # Validate chunk size
        if chunk_size < 10:
            chunk_size = 10
        elif chunk_size > 500:
            chunk_size = 500
        
        # Create output directory
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
        os.makedirs(output_dir, exist_ok=True)
        
        # Split the XML file
        output_files = split_wordpress_xml(
            session['xml_file'],
            output_dir,
            chunk_size,
            post_types if post_types else None
        )
        
        if not output_files:
            flash('Failed to split XML file', 'error')
            return redirect(url_for('analyze'))
        
        # Create ZIP archive
        zip_file = create_zip_archive(output_files, output_dir)
        
        if not zip_file:
            flash('Failed to create ZIP archive', 'error')
            return redirect(url_for('analyze'))
        
        # Store output info in session
        session['output_dir'] = output_dir
        session['zip_file'] = zip_file
        session['num_chunks'] = len(output_files)
        session['chunk_size'] = chunk_size
        
        return redirect(url_for('download'))
    
    except Exception as e:
        flash(f'Error splitting file: {str(e)}', 'error')
        return redirect(url_for('analyze'))

@app.route('/download')
def download():
    """Render the download page with links to the split files"""
    if 'zip_file' not in session:
        flash('Please split your WordPress XML file first', 'warning')
        return redirect(url_for('index'))
    
    return render_template('download.html',
                          num_chunks=session.get('num_chunks', 0),
                          chunk_size=session.get('chunk_size', 0))

@app.route('/download-file')
def download_file():
    """Send the ZIP file to the user"""
    if 'zip_file' not in session:
        flash('No ZIP file available for download', 'error')
        return redirect(url_for('index'))
    
    try:
        filename = os.path.basename(session['zip_file'])
        return send_file(session['zip_file'], 
                        mimetype='application/zip',
                        as_attachment=True,
                        download_name=f"wordpress_export_chunks.zip")
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('download'))

@app.route('/reset')
def reset():
    """Reset the application state and return to the home page"""
    cleanup_temp_files()
    return redirect(url_for('index'))

def cleanup_temp_files():
    """Clean up temporary files and directories"""
    # Remove output directory if it exists
    if 'output_dir' in session and os.path.exists(session['output_dir']):
        try:
            shutil.rmtree(session['output_dir'])
        except:
            pass
    
    # Remove uploaded XML file if it exists
    if 'xml_file' in session and os.path.exists(session['xml_file']):
        try:
            os.remove(session['xml_file'])
        except:
            pass
    
    # Clear session data
    session.pop('xml_file', None)
    session.pop('counts', None)
    session.pop('filename', None)
    session.pop('output_dir', None)
    session.pop('zip_file', None)
    session.pop('num_chunks', None)
    session.pop('chunk_size', None)

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    flash('File too large. Maximum size is 500MB.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create temporary directory for uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='127.0.0.1', port=5000)
