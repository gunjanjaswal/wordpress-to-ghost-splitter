# WordPress to Ghost XML Splitter

A tool to split large WordPress XML exports into smaller chunks for Ghost import.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## The Problem

When migrating from WordPress to Ghost, you might encounter this error:

> **Your file has too many posts, try a file with less posts**

This happens because Ghost has a limitation on the number of posts that can be imported at once. If you have a large WordPress site (like 3000+ posts), you need to split your export file into smaller chunks.

## The Solution

This tool splits your WordPress XML export into smaller, manageable chunks that Ghost can import. It preserves all necessary XML headers and namespaces for proper import.

## Features

- **Web Interface**: Easy-to-use web app for uploading and splitting XML files
- **Command Line**: Python and PowerShell scripts for advanced users
- **Content Analysis**: View a breakdown of your WordPress content before splitting
- **Customizable**: Choose chunk size and content types to include
- **Preserves Structure**: Each chunk contains all necessary metadata from the original file

## Getting Started

### Web Interface

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the web app: `python app.py`
4. Open your browser to `http://localhost:5000`
5. Follow the on-screen instructions

### Command Line (Python)

```bash
# Basic usage
python wp_xml_splitter.py wordpress-export.xml

# Specify chunk size
python wp_xml_splitter.py wordpress-export.xml --chunk-size 50

# Only include specific post types
python wp_xml_splitter.py wordpress-export.xml --post-types post page

# Analyze without splitting
python wp_xml_splitter.py wordpress-export.xml --analyze

# Create a ZIP archive
python wp_xml_splitter.py wordpress-export.xml --zip
```

### Command Line (PowerShell)

```powershell
# Basic usage
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml

# Specify chunk size
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -ChunkSize 50

# Only include specific post types
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -PostTypes post,page

# Analyze without splitting
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -Analyze

# Create a ZIP archive
.\Split-WordPressXML.ps1 -XmlFile wordpress-export.xml -CreateZip
```

## Importing to Ghost

1. Log in to your Ghost admin dashboard
2. Go to **Settings** > **Labs**
3. Under **Import content**, click **Select File**
4. Upload the first XML chunk file
5. Wait for the import to complete
6. Repeat steps 3-5 for each XML chunk file

## Recommendations

- For large exports (3000+ posts), a chunk size of 50 is recommended
- Import the chunks in sequential order for best results
- Ghost will skip any duplicate posts during import

## Requirements

- Python 3.6+
- Flask (for web interface)
- PowerShell 5.0+ (for PowerShell script)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Developed by [Gunjan Jaswal](https://gunjanjaswal.me) | [hello@gunjanjaswal.me](mailto:hello@gunjanjaswal.me)
