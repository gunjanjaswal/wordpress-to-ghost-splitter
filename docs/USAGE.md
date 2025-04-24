# WordPress to Ghost XML Splitter - Usage Guide

This guide provides detailed instructions for using the WordPress to Ghost XML Splitter tool to migrate your WordPress content to Ghost.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Exporting Your WordPress Content](#exporting-your-wordpress-content)
3. [Using the Web Interface](#using-the-web-interface)
4. [Using the Command Line Tools](#using-the-command-line-tools)
5. [Importing to Ghost](#importing-to-ghost)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

## Prerequisites

Before you begin, make sure you have:

- Python 3.6 or higher installed
- Flask and Werkzeug installed (for the web interface)
- PowerShell 5.0 or higher (for Windows users who prefer the PowerShell script)
- A WordPress XML export file
- Access to your Ghost admin dashboard

## Exporting Your WordPress Content

1. Log in to your WordPress admin dashboard
2. Go to **Tools** > **Export**
3. Select **All content** (or choose specific content types)
4. Click **Download Export File**
5. Save the XML file to your computer

## Using the Web Interface

The web interface provides a user-friendly way to split your WordPress XML export file.

### Starting the Web Server

1. Open a terminal or command prompt
2. Navigate to the project directory
3. Install dependencies (if you haven't already):
   ```
   pip install -r requirements.txt
   ```
4. Start the web server:
   ```
   python app.py
   ```
5. Open your web browser and go to `http://localhost:5000`

### Uploading and Analyzing Your XML File

1. On the home page, click the **Choose File** button
2. Select your WordPress XML export file
3. Click **Upload & Analyze**
4. The tool will analyze your file and show you a content summary

### Splitting Your XML File

1. On the analysis page, you'll see a recommended chunk size based on your file size
2. You can adjust the chunk size if needed (smaller chunks are safer but create more files)
3. Select which content types to include (posts, pages, attachments)
4. Click **Split XML File**
5. The tool will process your file and create smaller chunks

### Downloading the Split Files

1. Once the splitting is complete, you'll be taken to the download page
2. Click **Download ZIP File** to download all the split files as a ZIP archive
3. Extract the ZIP file to a location on your computer

## Using the Command Line Tools

For advanced users, the tool provides command-line interfaces in both Python and PowerShell.

### Python Command Line

```bash
# Basic usage
python wp_xml_splitter.py wordpress-export.xml

# Analyze without splitting
python wp_xml_splitter.py wordpress-export.xml --analyze

# Specify chunk size (50 items per chunk)
python wp_xml_splitter.py wordpress-export.xml --chunk-size 50

# Only include specific post types
python wp_xml_splitter.py wordpress-export.xml --post-types post page

# Specify output directory
python wp_xml_splitter.py wordpress-export.xml --output-dir my_chunks

# Create a ZIP archive of the split files
python wp_xml_splitter.py wordpress-export.xml --zip
```

### PowerShell Command Line (Windows)

```powershell
# Basic usage
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml

# Analyze without splitting
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -Analyze

# Specify chunk size (50 items per chunk)
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -ChunkSize 50

# Only include specific post types
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -PostTypes post,page

# Specify output directory
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -OutputDir my_chunks

# Create a ZIP archive of the split files
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -CreateZip
```

## Importing to Ghost

After splitting your WordPress XML export file, you'll need to import each chunk into Ghost.

1. Log in to your Ghost admin dashboard
2. Go to **Settings** > **Labs**
3. Under **Import content**, click **Select File**
4. Upload the first XML chunk file (e.g., `wordpress_export_chunk_1_of_10.xml`)
5. Wait for the import to complete
6. Repeat steps 3-5 for each XML chunk file, in sequential order

## Troubleshooting

### Common Issues

#### "Your file has too many posts" Error in Ghost

This is the exact error this tool is designed to solve. If you're still seeing this error, try:
- Reducing the chunk size (e.g., from 100 to 50 or even 25)
- Filtering to only include specific post types

#### XML Parsing Errors

If you encounter XML parsing errors:
- Make sure your WordPress XML export file is valid
- Try re-exporting from WordPress
- Check for any special characters or encoding issues

#### Import Issues in Ghost

If you have issues importing to Ghost:
- Make sure you're importing the chunks in sequential order
- Check that each chunk contains the necessary WordPress metadata
- Verify that your Ghost version supports WordPress imports

### Getting Help

If you encounter issues not covered in this guide:
- Check the [GitHub repository](https://github.com/gunjanjaswal/wordpress-to-ghost-splitter) for known issues
- Open a new issue on GitHub with details about your problem
- Contact the developer at [hello@gunjanjaswal.me](mailto:hello@gunjanjaswal.me)

## Advanced Usage

### Filtering Content Types

You can filter which content types are included in the split files:

- **Posts**: Regular blog posts (`post`)
- **Pages**: Static pages (`page`)
- **Attachments**: Media files (`attachment`)
- **Other**: Custom post types and other content

This is useful if you only want to import specific content types to Ghost.

### Custom Chunk Sizes

The default chunk size is 100 items per file, but you can adjust this based on your needs:

- **Smaller chunks** (e.g., 25-50): Safer for import, but creates more files
- **Larger chunks** (e.g., 100-200): Fewer files, but higher risk of import issues

For large WordPress sites (3000+ posts), a chunk size of 50 is recommended.

### Preserving Metadata

Each chunk file preserves all necessary WordPress metadata, including:

- XML namespaces and headers
- Blog information
- Categories and tags
- Author information

This ensures that Ghost can properly import your content with all associated metadata.

---

## Need More Help?

If you need additional assistance, please contact:

- **Developer**: Gunjan Jaswal
- **Email**: [hello@gunjanjaswal.me](mailto:hello@gunjanjaswal.me)
- **Website**: [https://gunjanjaswal.me](https://gunjanjaswal.me)
