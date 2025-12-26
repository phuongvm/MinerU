# MinerU Supported File Formats

This document outlines the file formats supported by MinerU for both input (documents to be parsed) and output (extraction results).

## Supported Input File Extensions

MinerU accepts the following file types for processing. Note that image inputs are internally converted to PDF before the extraction pipeline begins.

| Document Type | Supported Extensions |
| :--- | :--- |
| **PDF Documents** | `.pdf` |
| **Image Documents** | `.png`, `.jpg`, `.jpeg`, `.jp2`, `.webp`, `.gif`, `.bmp`, `.tiff` |

## Supported Export Formats

MinerU generates a set of structured files for every processed document.

| Export Type | File Name Pattern | Description |
| :--- | :--- | :--- |
| **Markdown** | `{filename}.md` | High-fidelity Markdown with preserved structure, formulas (LaTeX), and tables (HTML/MD). |
| **Content List** | `{filename}_content_list.json` | A structured sequence of all document elements (text, tables, images) sorted by reading order. |
| **Intermediate Data** | `{filename}_middle.json` | Comprehensive metadata, including bounding box coordinates (bboxes) for every detected element. |
| **Model Output** | `{filename}_model.json` | Raw output data directly from the inference models. |
| **Layout Visualization** | `{filename}_layout.pdf` | A PDF copy of the original with bounding boxes drawn around detected layout elements (titles, paragraphs, etc.). |
| **Span Visualization** | `{filename}_span.pdf` | A PDF copy showing more granular text span detections. |
| **Extracted Images** | `images/*.jpg` | All images found within the document are extracted and saved as individual JPEG files in an `images` subdirectory. |
