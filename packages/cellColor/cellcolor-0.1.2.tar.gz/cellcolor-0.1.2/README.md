# Gene Visualization Tool (`cellColor`)

An interactive desktop application to visualize **spatial transcriptomics data**, **cell segmentation masks**, and **microscopy images**.  
Ideal for verifying cell segmentation accuracy and exploring spatial gene expression patterns.

---

## 👥 Credits & Project Team

Developer: Anthea Guo

Mentor: Kushal Nimkar

Principal Investigator (PI): Prof. Karthik Shekhar

## ✨ Features

- **Image Loading & Zooming**
  - Load tissue/microscopy images.
  - Zoom into image regions by clicking and dragging.
  - Reset zoom to full view.

- **Cellpose Segmentation Overlay**
  - Load and overlay Cellpose-generated segmentation **masks** (colored regions) or **outlines** (borders).
  - Smooth zooming with cached mask resizing.

- **Transcript Visualization**
  - Import detected transcript coordinates (e.g., CSV/TSV with `x`, `y`, `gene` fields).
  - Apply transformation matrices to align transcript data with image.
  - Select genes from a dropdown to overlay their transcript locations.
  - Manage multiple gene overlays via a scrollable panel.

- **Single-Cell Integration**
  - Load **AnnData** cell center positions (`.h5ad` files).
  - Toggle cell centers on/off with customizable color and size.

- **User-Friendly Toolbar**
  - Intuitive toggle buttons to control overlays and zoom actions.
  - Status bar for live feedback.
  - Organized layout with collapsible frames for easy navigation.

- **Data Alignment**
  - Supports loading transformation matrices to align transcript data accurately with images.

---

## 🚀 Installation

### Option 1: Local Development (Editable Mode)
Clone the repo and install in dev mode:

```bash
git clone https://github.com/crocodile27/cellColor.git
cd cellColor
conda create -n cellcolor python=3.10
conda activate cellcolor
pip install -e .
```
Run the app locally:

```cellColor```

### Option 2: Install via PyPI (v0.1.0)

Install directly from PyPI:

```pip install cellColor```

This corresponds to the release published on September 1, 2025, version 0.1.0 ([pypi.org](https://pypi.org/project/cellColor/0.1.0/)
).

Launching the App
```cellColor```

## 📂 Supported Data Formats

Image: .png, .jpg, .tif, etc.

Cellpose Masks: .npy arrays or image mask formats.

Detected Transcripts: CSV/TSV containing x, y, gene columns.

Transformation Matrix: CSV/TSV defining alignment matrix.

AnnData: .h5ad format with cell coordinate metadata.

## 🧪 Example Workflow (Happy Path)

Open the app: cellColor.

File → Load Image to display your tissue section.

File → Load Detected Transcripts and Transformation Matrix.

File → Load Cellpose Masks, then enable Show Cellpose Masks.

Choose a gene from the dropdown; its transcript spots should appear.

Optionally, File → Load AnnData Cell Centers and enable Show Cell Centers.

Zoom in on interesting areas; use Reset Zoom to go back.