# MinerU Project Overview

MinerU (formerly magic-pdf) is a high-performance, open-source tool for converting PDF documents into machine-readable formats like Markdown and JSON. It is particularly optimized for scientific literature, capable of accurately extracting and reconstructing complex layouts, including:

*   **Text:** Preserving reading order and structure (headings, paragraphs, lists).
*   **Formulas:** Converting mathematical equations to LaTeX.
*   **Tables:** Converting tables to HTML/Markdown, handling complex structures (merged cells, borderless).
*   **Images:** Extracting images and their captions.
*   **Layout:** Removing headers, footers, and page numbers for semantic coherence.

## Key Features

*   **Dual Backends:**
    *   `pipeline`: A traditional deep learning pipeline using specialized models for layout (DocLayout-YOLO), formulas (UniMERNet), tables (RapidTable/StructureTable), and OCR (PaddleOCR/OCR-Pytorch).
    *   `vlm`: A visual language model-based approach (using vLLM, LMDeploy, or MLX) for end-to-end parsing (MinerU 2.x).
*   **Multi-Platform Support:** Windows, Linux, macOS.
*   **Hardware Acceleration:** CUDA (NVIDIA), MPS (Apple Silicon), NPU (Huawei Ascend), and CPU fallback.
*   **Input/Output:** Supports PDF, images (PNG, JPG) as input; outputs Markdown, JSON (content list, middle format), and layout visualizations.
*   **Language Support:** Extensive OCR language support (109+ languages).

## Architecture

*   `mineru/cli`: Command-line interfaces for the client, API server, Gradio app, and model management.
*   `mineru/backend`: Contains the core logic.
    *   `mineru/backend/pipeline`: The component-based pipeline (Layout -> OCR/Formula/Table -> Reconstruct).
    *   `mineru/backend/vlm`: The VLM-based extraction logic.
*   `mineru/model`: Model initialization and management.
*   `mineru/utils`: Utility functions for PDF handling, image processing, and configuration.

## Ecosystem

*   **Models:** Automatically managed and downloaded via `mineru-models-download`.
*   **Web/API:** Includes FastAPI (`mineru-api`) and Gradio (`mineru-gradio`) interfaces.
*   **Docker:** Official Docker images available for easy deployment.
