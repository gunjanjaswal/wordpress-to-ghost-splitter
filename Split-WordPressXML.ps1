#Requires -Version 5.0
<#
.SYNOPSIS
    Splits a WordPress XML export file into smaller chunks for Ghost import.

.DESCRIPTION
    WordPress to Ghost XML Splitter (PowerShell Version)
    Author: Gunjan Jaswal
    Email: hello@gunjanjaswal.me
    Website: gunjanjaswal.me

    This script splits a WordPress XML export file into smaller chunks for Ghost import.
    It preserves all necessary XML headers and namespaces for proper import.

.PARAMETER XmlFile
    Path to the WordPress XML export file to split.

.PARAMETER OutputDir
    Directory to save the split XML files. If not specified, a new directory will be created.

.PARAMETER ChunkSize
    Number of items per chunk. Default is 100.

.PARAMETER PostTypes
    Array of post types to include (e.g., "post", "page", "attachment").
    If not specified, all post types will be included.

.PARAMETER Analyze
    Only analyze the XML file without splitting.

.PARAMETER CreateZip
    Create a ZIP archive of the split files.

.EXAMPLE
    .\Split-WordPressXML.ps1 -XmlFile "wordpress-export.xml" -ChunkSize 50

.EXAMPLE
    .\Split-WordPressXML.ps1 -XmlFile "wordpress-export.xml" -PostTypes "post","page" -CreateZip

.EXAMPLE
    .\Split-WordPressXML.ps1 -XmlFile "wordpress-export.xml" -Analyze

.NOTES
    This script requires PowerShell 5.0 or later.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$XmlFile,
    
    [Parameter(Mandatory = $false)]
    [string]$OutputDir,
    
    [Parameter(Mandatory = $false)]
    [int]$ChunkSize = 100,
    
    [Parameter(Mandatory = $false)]
    [string[]]$PostTypes,
    
    [Parameter(Mandatory = $false)]
    [switch]$Analyze,
    
    [Parameter(Mandatory = $false)]
    [switch]$CreateZip
)

# Check if the XML file exists
if (-not (Test-Path $XmlFile)) {
    Write-Error "File not found: $XmlFile"
    exit 1
}

# Create output directory if not specified
if (-not $OutputDir) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $OutputDir = "wp_split_$timestamp"
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Load the XML file
try {
    Write-Host "Loading WordPress XML file: $XmlFile"
    [xml]$xml = Get-Content -Path $XmlFile -Encoding UTF8
}
catch {
    Write-Error "Error loading XML file: $_"
    exit 1
}

# Count items by type
function Count-XmlItems {
    param (
        [xml]$Xml
    )
    
    $channel = $Xml.rss.channel
    if (-not $channel) {
        return @{
            total = 0
            posts = 0
            pages = 0
            attachments = 0
            other = 0
        }
    }
    
    $items = $channel.item
    $totalCount = $items.Count
    
    $postCount = 0
    $pageCount = 0
    $attachmentCount = 0
    $otherCount = 0
    
    foreach ($item in $items) {
        $postType = $item.SelectSingleNode("wp:post_type", $Xml.rss.NamespaceManager)
        if ($postType) {
            switch ($postType.InnerText) {
                "post" { $postCount++ }
                "page" { $pageCount++ }
                "attachment" { $attachmentCount++ }
                default { $otherCount++ }
            }
        }
        else {
            $otherCount++
        }
    }
    
    return @{
        total = $totalCount
        posts = $postCount
        pages = $pageCount
        attachments = $attachmentCount
        other = $otherCount
    }
}

# Analyze the XML file
$counts = Count-XmlItems -Xml $xml

Write-Host "`nAnalysis of $(Split-Path $XmlFile -Leaf):"
Write-Host "Total items: $($counts.total)"
Write-Host "Posts: $($counts.posts)"
Write-Host "Pages: $($counts.pages)"
Write-Host "Attachments: $($counts.attachments)"
Write-Host "Other items: $($counts.other)"

if ($Analyze) {
    exit 0
}

# Recommend chunk size for large files
if ($counts.total -gt 500 -and $ChunkSize -gt 50) {
    Write-Host "`nWarning: Your file has $($counts.total) items. For Ghost import, a smaller chunk size is recommended."
    Write-Host "Consider using -ChunkSize 50 for better results."
}

# Split the XML file
Write-Host "`nSplitting XML file into chunks of $ChunkSize items..."

# Get all items
$channel = $xml.rss.channel
$items = $channel.item

# Filter items by post type if specified
if ($PostTypes) {
    $filteredItems = @()
    foreach ($item in $items) {
        $postType = $item.SelectSingleNode("wp:post_type", $xml.rss.NamespaceManager)
        if ($postType -and $PostTypes -contains $postType.InnerText) {
            $filteredItems += $item
        }
    }
    $items = $filteredItems
}

# Calculate number of chunks
$totalItems = $items.Count
if ($totalItems -eq 0) {
    Write-Host "No items to split (after filtering)"
    exit 1
}

$numChunks = [Math]::Ceiling($totalItems / $ChunkSize)
$outputFiles = @()

for ($i = 0; $i -lt $numChunks; $i++) {
    # Create a copy of the original XML
    $chunkXml = $xml.Clone()
    $chunkChannel = $chunkXml.rss.channel
    
    # Remove all existing items from the channel
    $itemsToRemove = $chunkChannel.item
    foreach ($item in $itemsToRemove) {
        $chunkChannel.RemoveChild($item) | Out-Null
    }
    
    # Add items for this chunk
    $startIdx = $i * $ChunkSize
    $endIdx = [Math]::Min($startIdx + $ChunkSize, $totalItems)
    
    for ($j = $startIdx; $j -lt $endIdx; $j++) {
        $itemNode = $items[$j].Clone()
        $importedNode = $chunkXml.ImportNode($itemNode, $true)
        $chunkChannel.AppendChild($importedNode) | Out-Null
    }
    
    # Write the chunk to a file
    $outputFile = Join-Path $OutputDir "wordpress_export_chunk_$($i+1)_of_$numChunks.xml"
    $chunkXml.Save($outputFile)
    $outputFiles += $outputFile
    
    Write-Host "Created chunk $($i+1) of $numChunks: $outputFile"
}

# Create a ZIP archive if requested
if ($CreateZip) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $zipFile = Join-Path $OutputDir "wordpress_export_chunks_$timestamp.zip"
    
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::CreateFromDirectory($OutputDir, $zipFile)
        Write-Host "`nCreated ZIP archive: $zipFile"
    }
    catch {
        Write-Error "Error creating ZIP archive: $_"
    }
}

Write-Host "`nDone!"
