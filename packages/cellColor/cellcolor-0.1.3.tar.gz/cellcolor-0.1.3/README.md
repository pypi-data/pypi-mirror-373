# Gene Visualization Tool (`cellColor`)

An interactive desktop application for visualizing **spatial transcriptomics data**, **cell segmentation masks**, and **microscopy images**.  
Perfect for verifying cell segmentation accuracy and exploring spatial gene expression patterns.

---

## 👥 Credits & Project Team

- **Developer:** Anthea Guo  
- **Mentor:** Kushal Nimkar  
- **Principal Investigator (PI):** Prof. Karthik Shekhar

---

## ✨ Features

- **Image Loading & Zooming:**  
  Load tissue/microscopy images, zoom into regions, and reset to full view.

- **Cellpose Segmentation Overlay:**  
  Overlay Cellpose-generated segmentation masks or outlines with smooth, cached zooming.

- **Transcript Visualization:**  
  Import transcript coordinates (`x`, `y`, `gene`), align with images using transformation matrices, and overlay selected genes.

- **Single-Cell Integration:**  
  Load AnnData cell center positions (`.h5ad`), toggle display, and customize appearance.

- **User-Friendly Toolbar:**  
  Intuitive controls for overlays and zoom, live status feedback, and collapsible navigation frames.

- **Data Alignment:**  
  Load transformation matrices for accurate transcript-image alignment.

---

## 🚀 Installation

**Option 1: Local Development (Editable Mode)**

```bash
git clone https://github.com/crocodile27/cellColor.git
cd cellColor
conda create -n cellcolor python=3.10
conda activate cellcolor
pip install -e .
```
Run locally:
```bash
cellColor
```

**Option 2: Install via PyPI (v0.1.0)**

```bash
pip install cellColor
```
Release: September 1, 2025 ([PyPI link](https://pypi.org/project/cellColor/0.1.0/))

Launch:
```bash
cellColor
```

---

## 📂 Supported Data Formats

- **Images:** `.png`, `.jpg`, `.tif`, etc.
- **Cellpose Masks:** `.npy` arrays or image masks.
- **Detected Transcripts:** CSV/TSV with `x`, `y`, `gene` columns.
- **Transformation Matrix:** CSV/TSV for alignment.
- **AnnData:** `.h5ad` with cell coordinates.

---

## 🧪 Example Workflow

1. **Open the app:** `cellColor`
2. **Load image:**  
   *File → Load Image* to display tissue section.
3. **Load transcripts & matrix:**  
   *File → Load Detected Transcripts* and *Transformation Matrix*.
4. **Load Cellpose masks:**  
   *File → Load Cellpose Masks*, then enable *Show Cellpose Masks*.
5. **Overlay gene transcripts:**  
   Select a gene from the dropdown to view transcript spots.
6. **(Optional) Load cell centers:**  
   *File → Load AnnData Cell Centers*, enable *Show Cell Centers*.
7. **Zoom & reset:**  
   Zoom into areas of interest; use *Reset Zoom* to return.

