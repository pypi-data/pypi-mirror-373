# isort: skip

import random
import tkinter as tk
import numpy as np
import pandas as pd
import anndata as ad
from qtpy.QtCore import Qt, QTimer, QRectF, QPointF
from qtpy.QtGui import QImage, QPixmap, QColor, QPainter, QPen
from qtpy.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QFileDialog,
                            QMenuBar, QAction, QStatusBar, QToolBar,
                            QComboBox, QHBoxLayout, QPushButton, QScrollArea,
                            QFrame, QColorDialog, QSlider)
import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2, 40).__str__()
import cv2
from cellpose import utils
from qtpy.QtWidgets import QApplication
import sys
root = tk.Tk()
screen_height = root.winfo_screenheight() - 50
screen_width = root.winfo_screenwidth()

colors_rgb = {
    "Dartmouth Green": (0, 102, 44),      # Hex: #00662c
    "Spring Bud": (175, 247, 17),         # Hex: #aff711
    "Pear": (214, 237, 86),               # Hex: #d6ed56
    "Apple Green": (142, 166, 4),         # Hex: #8ea604
    "Gamboge": (236, 159, 5),             # Hex: #ec9f05
    "Rust": (191, 49, 0),                 # Hex: #bf3100
    "OU Crimson": (128, 15, 15),          # Hex: #800f0f
    "Citrine": (229, 209, 44),            # Hex: #e5d12c
    "Vanilla": (255, 236, 159),           # Hex: #ffec9f
    "Sunglow": (255, 202, 97),            # Hex: #ffca61
    "Bittersweet": (248, 118, 92),        # Hex: #f8765c
    "Melon": (255, 192, 183),             # Hex: #ffc0b7
    "Indian Red": (192, 104, 105),        # Hex: #c06869
    "Folly": (255, 66, 85),               # Hex: #ff4255
    "Red": (255, 0, 0)
}


class ZoomableImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True)
        self.rubberband_active = False
        self.origin = QPointF()
        self.rubberband_rect = QRectF()
        self.setAlignment(Qt.AlignCenter)
        
    def mousePressEvent(self, event):
        if not hasattr(self.parent, 'resized_image') or self.parent.resized_image is None:
            return
            
        if event.button() == Qt.LeftButton:
            self.rubberband_active = True
            self.origin = event.pos()
            self.rubberband_rect = QRectF(self.origin, self.origin)
            self.update()
    
    def mouseMoveEvent(self, event):
        if self.rubberband_active:
            self.rubberband_rect = QRectF(self.origin, event.pos()).normalized()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rubberband_active:
            self.rubberband_active = False
            # Only process zoom if the rectangle has a reasonable size
            if self.rubberband_rect.width() > 10 and self.rubberband_rect.height() > 10:
                self.parent.zoom_to_selection(self.rubberband_rect)
            self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.rubberband_active:
            painter = QPainter(self)
            pen = QPen(Qt.red, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.rubberband_rect)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gene Visualization Tool")
        self.setGeometry(0, 0, screen_width, screen_height)
        self.screenWidth = screen_width
        self.screenHeight = screen_height
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Image Area
        self.image_area = QWidget()
        self.image_layout = QVBoxLayout(self.image_area)

        # Custom Zoomable Image Label
        self.image_label = ZoomableImageLabel(self)
        self.image_layout.addWidget(self.image_label)

        # Toolbar Area
        self.toolbar_area = QWidget()
        self.toolbar_layout = QVBoxLayout(self.toolbar_area)
        
        # Cellpose Mask Toggle Button
        self.toggle_cellpose_button = QPushButton("Show Cellpose Masks")
        self.toggle_cellpose_button.setCheckable(True)
        self.toggle_cellpose_button.clicked.connect(self.toggle_cellpose_masks)
        self.toggle_cellpose_button.setEnabled(False)  # Initially disabled until masks are loaded
        self.toolbar_layout.addWidget(self.toggle_cellpose_button)

        # Cellpose Outline Toggle Button
        self.toggle_cellpose_outline_button = QPushButton("Show Cellpose Outlines")
        self.toggle_cellpose_outline_button.setCheckable(True)
        self.toggle_cellpose_outline_button.clicked.connect(self.toggle_cellpose_outlines)
        self.toggle_cellpose_outline_button.setEnabled(False)
        self.toolbar_layout.addWidget(self.toggle_cellpose_outline_button)

        # Outline visibility state
        self.show_cellpose_outlines = False

        # Data storage
        self.cellpose_masks = None
        self.cellpose_colors = None
        self.cellpose_outlines = None
        self.show_cellpose_masks = False

        # Zoom Controls
        self.zoom_controls_frame = QFrame()
        self.zoom_controls_layout = QVBoxLayout(self.zoom_controls_frame)
        
        self.zoom_label = QLabel("Zoom Instructions:")
        self.zoom_instructions = QLabel("Click and drag to select an area to zoom into")
        self.zoom_controls_layout.addWidget(self.zoom_label)
        self.zoom_controls_layout.addWidget(self.zoom_instructions)
        
        # Reset Zoom Button
        self.reset_zoom_button = QPushButton("Reset Zoom")
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        self.reset_zoom_button.setEnabled(False)
        self.zoom_controls_layout.addWidget(self.reset_zoom_button)
        
        self.toolbar_layout.addWidget(self.zoom_controls_frame)

        # Gene Selection Dropdown
        self.gene_dropdown = QComboBox()
        self.gene_dropdown.setPlaceholderText("Select a Gene")
        self.gene_dropdown.currentTextChanged.connect(self.on_gene_selected)
        self.toolbar_layout.addWidget(self.gene_dropdown)
        self.gene_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        # Selected Genes Scroll Area
        self.selected_genes_scroll = QScrollArea()
        self.selected_genes_widget = QWidget()
        self.selected_genes_layout = QVBoxLayout(self.selected_genes_widget)
        self.selected_genes_scroll.setWidget(self.selected_genes_widget)
        self.selected_genes_scroll.setWidgetResizable(True)
        self.toolbar_layout.addWidget(self.selected_genes_scroll)

        # Main Layout Organization
        self.main_layout.addWidget(self.image_area, stretch=4)
        self.main_layout.addWidget(self.toolbar_area, stretch=1)

        # Menu Bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")

        # Load Image Action
        self.load_image_action = QAction("Load Image", self)
        self.load_image_action.triggered.connect(self.load_image)
        self.file_menu.addAction(self.load_image_action)

        # Other menu items...
        self.load_detected_transcripts_action = QAction("Load Detected Transcripts", self)
        self.load_detected_transcripts_action.triggered.connect(self.load_detected_transcripts)
        self.file_menu.addAction(self.load_detected_transcripts_action)

        self.load_transformation_matrix_action = QAction("Load Transformation Matrix", self)
        self.load_transformation_matrix_action.triggered.connect(self.load_transformation_matrix)
        self.file_menu.addAction(self.load_transformation_matrix_action)
        
        self.load_anndata_action = QAction('Load Anndata Cell Centers', self)
        self.load_anndata_action.triggered.connect(self.load_anndata)
        self.file_menu.addAction(self.load_anndata_action)

        # Load Cellpose Masks Action
        self.load_cellpose_masks_action = QAction('Load Cellpose Masks', self)
        self.load_cellpose_masks_action.triggered.connect(self.load_cellpose_masks)
        self.file_menu.addAction(self.load_cellpose_masks_action)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Data Storage
        self.image = None
        self.original_image = None
        self.gene_data = None
        self.transformation_matrix = None
        self.resized_image = None
        self.selected_genes = {}
        self.zoom_history = []  # Stack to track zoom levels
        
        self.cell_centers_frame = QFrame()
        self.cell_centers_layout = QVBoxLayout(self.cell_centers_frame)

        self.cell_centers_label = QLabel("Cell Centers:")
        self.cell_centers_layout.addWidget(self.cell_centers_label)

        self.toggle_cell_centers_button = QPushButton("Show Cell Centers")
        self.toggle_cell_centers_button.setCheckable(True)
        self.toggle_cell_centers_button.clicked.connect(self.toggle_cell_centers)
        self.cell_centers_layout.addWidget(self.toggle_cell_centers_button)

        self.toolbar_layout.addWidget(self.cell_centers_frame)

        # Add to data storage section
        self.show_cell_centers = False
        self.cell_center_color = (255, 0, 0)  # Don't know why but their color scheme is flipped
        self.cell_center_size = 2  # Default size
        self.x_coords_valid = []
        self.y_coords_valid = []
        
        self.cached_resized_mask_view = None  # cache per zoom

    def _generate_outlines_and_update(self):

        # Derive the original mask path from the color image path if available
        if hasattr(self, 'cellpose_mask_color_image') and hasattr(self, 'cellpose_masks'):
            # Guess filename from npy file (you could store this explicitly if unsure)
            mask_shape = self.cellpose_masks.shape
            color_image_shape = getattr(self.cellpose_mask_color_image, 'shape', None)
            if color_image_shape and color_image_shape[:2] == mask_shape:
                base_path = None
                for ext in ['_color.npy', '_masks.npy', '.npy']:
                    try:
                        color_path = next(
                            p for p in sys.argv if p.endswith(ext)
                        )
                        base_path = color_path.replace(ext, '')
                        break
                    except StopIteration:
                        continue
            else:
                base_path = None
        else:
            base_path = None

        outline_path = getattr(self, 'cellpose_mask_base_path', None)
        if outline_path:
            outline_path += "_outlines.npy"
            if os.path.exists(outline_path):
                print(f"Loading cached outlines from {outline_path}")
                self.cellpose_outlines = np.load(outline_path, allow_pickle=True).tolist()
                
            else:
                print("Generating outlines...")
                self.cellpose_outlines = utils.outlines_list(self.cellpose_masks)
                
               # new
                h_img, w_img = mask_shape[:2]
                h_m, w_m = self.cellpose_mask_color_image.shape[:2]
                scale_x = w_m / w_img
                scale_y = h_m / h_img
                print(f"Original mask shape: {mask_shape}, Color image shape: {color_image_shape}")
                print(f"Scale factors - X: {scale_x}, Y: {scale_y}")
                print(f"Scaling {len(self.cellpose_outlines)} outlines by (x={scale_x:.3f}, y={scale_y:.3f})")
                scaled = []
                for outline in self.cellpose_outlines:
                    pts = np.array(outline)
                    # multiply then cast back to int
                    pts_scaled = [(int(x * scale_x), int(y * scale_y)) for x, y in pts]
                    if len(pts_scaled) > 1:
                        scaled.append(pts_scaled)
                self.cellpose_outlines = scaled
                
                np.save(outline_path, np.array(self.cellpose_outlines, dtype=object))
                print(f"Saved scaled outlines to {outline_path}")
                
        else:
            print("No base path found; computing outlines without caching.")
            self.cellpose_outlines = utils.outlines_list(self.cellpose_masks)


        self.toggle_cellpose_button.setEnabled(True)
        self.toggle_cellpose_outline_button.setEnabled(True)
        self.status_bar.showMessage("Cellpose masks loaded successfully")
        self.update_display()
        
    def load_cellpose_masks(self):
        
        if self.original_image is None:
            self.status_bar.showMessage("Please make sure to upload an image to scale to.")
            return
        
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Cellpose Masks", "", "NumPy Files (*.npy)")
        if not file_name:
            return

        try:
            print(f"Attempting to load Cellpose masks from file: {file_name}")
            data = np.load(file_name)

            if isinstance(data, np.ndarray) and data.ndim == 2 and np.issubdtype(data.dtype, np.integer):
                self.cellpose_masks = data
                print(f"Loaded raw mask array. Shape: {data.shape}, Max label: {data.max()}")

                num_labels = int(data.max())
                rng = np.random.default_rng(42)
                self.cellpose_colors = rng.integers(0, 255, size=(num_labels, 3), dtype=np.uint8)

                # Try to load precomputed color image
                self.cellpose_mask_base_path = file_name.replace(".npy", "")
                color_path = self.cellpose_mask_base_path + "_color.npy"
                outline_path = self.cellpose_mask_base_path + "_outlines.npy"
                if os.path.exists(color_path):
                    print(f"Loading cached color image from {color_path}")
                    self.cellpose_mask_color_image = np.load(color_path)
                else:
                    print("Generating color image...")
                    color_lut = np.vstack(([0, 0, 0], self.cellpose_colors))  # Ensure background = black
                    indices = self.cellpose_masks.astype(np.int32)
                    self.cellpose_mask_color_image = color_lut[indices].astype(np.uint8)
                    # Save for future use
                
                h_img, w_img = self.original_image.shape[:2]
                h_m, w_m = self.cellpose_mask_color_image.shape[:2]
                if (h_img, w_img) != (h_m, w_m):
                    print(f"Scaling mask color from {(h_m, w_m)} → {(h_img, w_img)}")
                    self.cellpose_mask_color_image = cv2.resize(
                        self.cellpose_mask_color_image,
                        (w_img, h_img),
                        interpolation=cv2.INTER_NEAREST
                    )
                    # overwrite cache so next load is already scaled
                    np.save(color_path, self.cellpose_mask_color_image)
                    print(f"Resaved scaled color image to {color_path}")

                # … then queue outline generation as before …
                self.status_bar.showMessage("Generating Cellpose outlines... this may take a moment")
                QTimer.singleShot(100, self._generate_outlines_and_update)
                print(f"Cellpose mask dimensions: cellpose_mask_fill {self.cellpose_mask_color_image.shape[:2]}")
            else:
                raise ValueError("Unsupported mask format")

        except Exception as e:
            print(f"Error while loading Cellpose masks: {str(e)}")
            self.status_bar.showMessage(f"Error loading Cellpose masks: {str(e)}")


    def toggle_cellpose_masks(self):
        self.show_cellpose_masks = self.toggle_cellpose_button.isChecked()
        self.toggle_cellpose_button.setText("Hide Cellpose Masks" if self.show_cellpose_masks else "Show Cellpose Masks")
        self.update_display()

    def toggle_cellpose_outlines(self):
        self.show_cellpose_outlines = self.toggle_cellpose_outline_button.isChecked()
        self.toggle_cellpose_outline_button.setText("Hide Cellpose Outlines" if self.show_cellpose_outlines else "Show Cellpose Outlines")
        self.update_display()
    
    def update_display(self):
        print("Running update display")
        if self.resized_image is None:
            return
        base_image = self.resized_image.copy()
        print('Resized image size:', self.resized_image.shape[0], self.resized_image.shape[1])
        # Overlay genes
        if hasattr(self, 'visible_gene_x_coords'):
            for x, y, color in zip(self.visible_gene_x_coords, self.visible_gene_y_coords, self.visible_gene_colors):
                # Ensure color is a tuple of integers
                bgr_color = tuple(int(c) for c in color[::-1])  # Reverse RGB to BGR and convert to int
                cv2.circle(base_image, (x, y), 1, bgr_color, -1)

        # Overlay cell centers
        if self.show_cell_centers:
            self._draw_cell_centers(base_image)

        # Overlay Cellpose masks
        if self.show_cellpose_masks and self.cellpose_masks is not None:
            self._draw_cellpose_mask_fill(base_image)

        if self.show_cellpose_outlines and self.cellpose_outlines is not None:
            self._draw_cellpose_mask_outlines(base_image)

        # Display final image
        overlay_image_rgb = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)
        height, width, channel = overlay_image_rgb.shape
        q_img = QImage(overlay_image_rgb.data, width, height, 3 * width, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))


    def _draw_cellpose_mask_fill(self, image):

        if not hasattr(self, 'cellpose_mask_color_image'):
            return
        print(f"Cellpose mask image dimensions: {self.cellpose_mask_color_image.shape}")
        if hasattr(self, 'current_zoom') and self.current_zoom is not None:
            zoom = self.current_zoom
            crop = self.cellpose_mask_color_image[
                zoom['y_start']:zoom['y_end'],
                zoom['x_start']:zoom['x_end']
            ]
        else:
            crop = self.cellpose_mask_color_image

        if crop.size == 0:
            print("[Error] Zoomed-in region is empty — skipping mask fill.")
            return
        print(f"question about image width and height, width should be larger or else, this is flipped.Width:{image.shape[1]}, height:{image.shape[0]}" )
        # highlight
        resized = cv2.resize(crop, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)

        # Force both images to be np.uint8
        if resized.dtype != np.uint8:
            resized = resized.astype(np.uint8)
        if image.dtype != np.uint8:
            image[:] = image.astype(np.uint8)
        if image.dtype != np.uint8 or resized.dtype != np.uint8:
            print(f"[Warning] dtype mismatch: image={image.dtype}, resized={resized.dtype}")
        cv2.addWeighted(image, 0.5, resized, 0.5, 0, dst=image)
        
           
    def _draw_cellpose_mask_outlines(self, image):
        if self.cellpose_outlines is None:
            return

        if hasattr(self, 'current_zoom') and self.current_zoom is not None:
            zoom = self.current_zoom
            x0, y0 = zoom['x_start'], zoom['y_start']
            x1, y1 = zoom['x_end'], zoom['y_end']
            rect_width, rect_height = x1 - x0, y1 - y0

            scale_x = image.shape[1] / rect_width 
            scale_y = image.shape[0] / rect_height 
            print(f'scale_x: {scale_x}', f'scale_y: {scale_y}', "estimated to be > 1")
            for outline in self.cellpose_outlines:
                outline = np.array(outline)
                in_x = (outline[:, 0] >= x0) & (outline[:, 0] < x1)
                in_y = (outline[:, 1] >= y0) & (outline[:, 1] < y1)
                valid = in_x & in_y
                if not np.any(valid):
                    continue
                outline = outline[valid]
                outline_zoom = outline - np.array([x0, y0])
                # apply the *same* scaling that cv2.resize used
                outline_scaled = (outline_zoom * np.array([scale_x, scale_y])).astype(int)

                if len(outline_scaled) > 1:
                    cv2.polylines(image, [outline_scaled], isClosed=True, color=(0, 0, 255), thickness=1)
        else:
            print(f'no current zoom')
            
            # # scale_x = image.shape[1] / self.cellpose_.shape[1]
            # # scale_y = image.shape[0] / self.cellpose_masks.shape[0]
            # # print(f'scale{scale_x}, {scale_y}')
            # for outline in self.cellpose_outlines:
            #     outline = np.array(outline)
            #     outline_scaled = np.array([[int(x * 1), int(y * 1)] for x, y in outline])
            #     if len(outline_scaled) > 1:
            #         cv2.polylines(image, [outline_scaled], isClosed=True, color=(0, 0, 255), thickness=1)
            mask_h, mask_w = self.cellpose_mask_color_image.shape[:2]
            scale_x = image.shape[1] / mask_w
            scale_y = image.shape[0] / mask_h

            for outline in self.cellpose_outlines:
                outline = np.array(outline)
                # shift origin to (0,0)—not strictly necessary if mask coords already start at zero
                outline_zoom = outline  
                outline_scaled = (outline_zoom * np.array([scale_x, scale_y])).astype(int)
                if len(outline_scaled) > 1:
                    cv2.polylines(image, [outline_scaled], isClosed=True, color=(0, 0, 255), thickness=1)
                    
    def toggle_cell_centers(self):
        """Toggle display of cell centers"""
        self.show_cell_centers = self.toggle_cell_centers_button.isChecked()
        
        if self.show_cell_centers:
            self.toggle_cell_centers_button.setText("Hide Cell Centers")
            cell_centers = getattr(self, 'cell_centers', None)
            if cell_centers is not None:
                if self.image is not None:
                    self.display_cell_centers()
                else:
                    self.status_bar.showMessage("Please load an image first")
            else:
                self.status_bar.showMessage("No cell centers loaded. Please load anndata file first.")
        else:
            self.toggle_cell_centers_button.setText("Show Cell Centers")
            # If we're hiding cells, redisplay the image without cells
            if self.image is not None:
                self.display_image()
                # Reapply gene overlay if we have genes selected
                if self.gene_data is not None and self.selected_genes:
                    self.overlay_genes()

    
    def _process_cell_centers(self):
        """Process cell center coordinates for the current view."""
        if not hasattr(self, 'cell_centers') or self.cell_centers is None or self.cell_centers.empty:
            return
        
        # Process and overlay cell centers
        x_coords, y_coords = self.cell_centers[['global_x', 'global_y']].to_numpy().T
        
        if self.transformation_matrix is not None:
            coords = np.dot(self.transformation_matrix, np.hstack([x_coords[:, None], y_coords[:, None], np.ones((len(x_coords), 1))]).T).T[:, :2]
            x_coords, y_coords = coords[:, 0], coords[:, 1]
        
        if getattr(self, 'current_zoom', None):
            zoom = self.current_zoom
            in_zoom = (zoom['x_start'] <= x_coords) & (x_coords < zoom['x_end']) & \
                    (zoom['y_start'] <= y_coords) & (y_coords < zoom['y_end'])
            if not any(in_zoom):
                self.cell_center_visible = False
                return
            x_coords, y_coords = (x_coords[in_zoom] - zoom['x_start']) * zoom['scale_factor'], \
                                (y_coords[in_zoom] - zoom['y_start']) * zoom['scale_factor']
            
        else:
            scale_factor = getattr(self, 'full_view_scale_factor', None) or min(
                self.image_label.height() / self.original_image.shape[0],
                self.image_label.width() / self.original_image.shape[1])
            print(f"image label height{self.image_label.height()}, original image height{self.original_image.shape[0]}, scale factor = {self.image_label.height() / self.original_image.shape[0]}")
            print(f"image label width: {self.image_label.width()}, original image width: {self.original_image.shape[1]}, scale factor = {self.image_label.width() / self.original_image.shape[1]}")
            x_coords, y_coords = x_coords * scale_factor, y_coords * scale_factor
        
        x_coords, y_coords = x_coords.astype(int), y_coords.astype(int)
        
        # Filter valid coordinates
        height, width = self.resized_image.shape[:2]
        valid = (0 <= x_coords) & (x_coords < width) & (0 <= y_coords) & (y_coords < height)
        
        self.cell_center_x_coords = x_coords[valid]
        self.cell_center_y_coords = y_coords[valid]
        self.cell_center_visible = valid.sum() > 0


    def _draw_cell_centers(self, image):
        """Draw cell centers on the given image and display it."""
        if not hasattr(self, 'cell_center_x_coords') or not hasattr(self, 'cell_center_y_coords'):
            self._process_cell_centers()
        
        if hasattr(self, 'cell_center_x_coords') and hasattr(self, 'cell_center_y_coords'):
            for x, y in zip(self.cell_center_x_coords, self.cell_center_y_coords):
                cv2.circle(image, (x, y), self.cell_center_size, self.cell_center_color, -1)
        
        # Convert and display the final image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))
        
        num_points = len(getattr(self, 'cell_center_x_coords', []))
        self.status_bar.showMessage(f"Cell centers displayed: {num_points} visible points")

    def display_cell_centers(self):
        """Display cell centers from anndata on the image and overlay genes if enabled."""
        cell_centers = getattr(self, 'cell_centers', None)
        if cell_centers is None or cell_centers.empty:
            self.status_bar.showMessage("No cell centers loaded")
            return
        if self.transformation_matrix is None:
            self.status_bar.showMessage("Please load transformation matrix first")
            return
        if self.image is None or self.resized_image is None:
            self.status_bar.showMessage("Please load an image first")
            return
        
        # IMPORTANT: Start with a fresh copy of the display image
        # This ensures we don't lose color information from previous overlays
        base_image = self.resized_image.copy()
        
        # Process cell centers
        self._process_cell_centers()
        
        # First overlay genes if the gene data is available and there are selected genes
        if hasattr(self, 'gene_data') and self.gene_data is not None and hasattr(self, 'selected_genes') and self.selected_genes:
            # Draw visible genes first
            if hasattr(self, 'visible_gene_x_coords') and hasattr(self, 'visible_gene_y_coords') and hasattr(self, 'visible_gene_colors'):
                for x, y, color in zip(self.visible_gene_x_coords, self.visible_gene_y_coords, self.visible_gene_colors):
                    color = tuple(map(int, color))
                    color = (color[2], color[1], color[0])  # Convert RGB to BGR for OpenCV
                    cv2.circle(base_image, (x, y), 1, color, -1)
            else:
                # If we don't have cached gene coordinates, call overlay_genes but disable cell centers to avoid recursion
                temp_show_cell_centers = self.show_cell_centers
                self.show_cell_centers = False
                self.overlay_genes()  # This will calculate and store visible_gene_x_coords, etc.
                self.show_cell_centers = temp_show_cell_centers
                
                # Now draw the genes using the stored coordinates
                if hasattr(self, 'visible_gene_x_coords'):
                    for x, y, color in zip(self.visible_gene_x_coords, self.visible_gene_y_coords, self.visible_gene_colors):
                        color = tuple(map(int, color))
                        color = (color[2], color[1], color[0])  # Convert RGB to BGR for OpenCV
                        cv2.circle(base_image, (x, y), 1, color, -1)
        
        # Now draw cell centers on top
        self.update_display()
    
    def zoom_to_selection(self, rect):
        if self.resized_image is None or self.original_image is None:
            return

        pixmap = self.image_label.pixmap()
        if not pixmap:
            return

        pixmap_rect = self.get_pixmap_rect()
        if not pixmap_rect.isValid():
            return

        normalized_rect = QRectF(
            (rect.x() - pixmap_rect.x()) / pixmap_rect.width(),
            (rect.y() - pixmap_rect.y()) / pixmap_rect.height(),
            rect.width() / pixmap_rect.width(),
            rect.height() / pixmap_rect.height()
        )

        normalized_rect = QRectF(
            max(0, normalized_rect.x()),
            max(0, normalized_rect.y()),
            min(1 - normalized_rect.x(), normalized_rect.width()),
            min(1 - normalized_rect.y(), normalized_rect.height())
        )

        orig_height, orig_width = self.original_image.shape[:2]

        if hasattr(self, 'current_zoom') and self.current_zoom is not None:
            self.zoom_history.append(self.current_zoom.copy())
            cur = self.current_zoom
            orig_x1 = int(cur['x_start'] + normalized_rect.x() * (cur['x_end'] - cur['x_start']))
            orig_y1 = int(cur['y_start'] + normalized_rect.y() * (cur['y_end'] - cur['y_start']))
            orig_x2 = int(cur['x_start'] + (normalized_rect.x() + normalized_rect.width()) * (cur['x_end'] - cur['x_start']))
            orig_y2 = int(cur['y_start'] + (normalized_rect.y() + normalized_rect.height()) * (cur['y_end'] - cur['y_start']))
        else:
            orig_x1 = int(normalized_rect.x() * orig_width)
            orig_y1 = int(normalized_rect.y() * orig_height)
            orig_x2 = int((normalized_rect.x() + normalized_rect.width()) * orig_width)
            orig_y2 = int((normalized_rect.y() + normalized_rect.height()) * orig_height)
        
        orig_x1 = max(0, min(orig_x1, orig_width - 1))
        orig_x2 = max(0, min(orig_x2, orig_width))
        orig_y1 = max(0, min(orig_y1, orig_height - 1))
        orig_y2 = max(0, min(orig_y2, orig_height))

        if orig_x2 <= orig_x1 or orig_y2 <= orig_y1:
            print("[Warning] Invalid zoom box: zero width/height")
            return

        selected_region = self.original_image[orig_y1:orig_y2, orig_x1:orig_x2]
        view_height, view_width = self.image_label.height(), self.image_label.width()
        scale_factor = min(view_height / selected_region.shape[0], view_width / selected_region.shape[1])

        # ✅ Set current_zoom BEFORE resized_image
        self.current_zoom = {
            'x_start': orig_x1,
            'y_start': orig_y1,
            'x_end': orig_x2,
            'y_end': orig_y2,
            'scale_factor': scale_factor,
        }
        print(f"[DEBUG] Original Image Size: {orig_width}x{orig_height}")
        print(f"[DEBUG] Zoomed Region: x={orig_x1}:{orig_x2}, y={orig_y1}:{orig_y2}")
        print(f"[DEBUG] Selected Region Shape: {selected_region.shape}")
        print(f"[DEBUG] View Size: {view_width}x{view_height}")
        print(f"[DEBUG] Computed scale factor: {scale_factor}")
        self.resized_image = cv2.resize(
            selected_region, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR
        )

        self.reset_zoom_button.setEnabled(True)

        for attr in ['visible_gene_x_coords', 'visible_gene_y_coords', 'visible_gene_colors',
                    'cell_center_x_coords', 'cell_center_y_coords']:
            if hasattr(self, attr):
                delattr(self, attr)

        # ✅ Delay update until current_zoom is fully ready
        QTimer.singleShot(0, self.update_display)

        # Re-overlay gene data
        if self.gene_data is not None and self.selected_genes:
            QTimer.singleShot(0, self.overlay_genes)

        self.status_bar.showMessage(f"Zoomed to region. Zoom level: {len(self.zoom_history) + 1}")
        print(f"[DEBUG] Applying zoom: {self.current_zoom}")

    
    def get_pixmap_rect(self):
        """Calculate the actual rectangle of the pixmap within the label"""
        pixmap = self.image_label.pixmap()
        if not pixmap:
            return QRectF()
            
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        
        # Calculate position based on alignment
        x = (label_width - pixmap_width) / 2 if pixmap_width < label_width else 0
        y = (label_height - pixmap_height) / 2 if pixmap_height < label_height else 0
        
        return QRectF(x, y, pixmap_width, pixmap_height)

    def reset_zoom(self):
        # Check if we have zoom history
        if self.zoom_history:
            # Pop the last zoom level and apply it
            previous_zoom = self.zoom_history.pop()
            
            # If we're back at the first level, completely reset
            if not self.zoom_history:
                self.do_full_reset()
                return
                
            # Otherwise, go back to previous zoom level
            orig_x1 = previous_zoom['x_start']
            orig_y1 = previous_zoom['y_start']
            orig_x2 = previous_zoom['x_end']
            orig_y2 = previous_zoom['y_end']
            scale_factor = previous_zoom['scale_factor']
            
            # Extract region from original image
            selected_region = self.original_image[orig_y1:orig_y2, orig_x1:orig_x2]
            
            # Resize selected region
            self.resized_image = cv2.resize(
                selected_region, (0, 0),
                fx=scale_factor,
                fy=scale_factor,
                interpolation=cv2.INTER_LINEAR
            )
            
            # Update current zoom
            self.current_zoom = previous_zoom.copy()  # Use copy to avoid reference issues
            
        else:
            # No history, reset to original view
            self.do_full_reset()
            return  # do_full_reset handles everything else including cell centers display
        
        # Update display
        self.display_image()
        
        # Overlay genes if data is available
        if self.gene_data is not None and self.selected_genes:
            self.overlay_genes()
        # If no genes but showing cell centers, display them
        elif self.show_cell_centers:
            self.display_cell_centers()
            
        # Update status
        zoom_level = len(self.zoom_history) + (1 if hasattr(self, 'current_zoom') and self.current_zoom else 0)
        self.status_bar.showMessage(f"Zoom level: {zoom_level}")
        
        

    def do_full_reset(self):
        """Reset to original unzoomed state"""
        if self.original_image is not None:
            # Get the current dimensions of the image display area
            view_height = self.image_label.height()
            view_width = self.image_label.width()
            
            # If dimensions are too small, use minimum reasonable values
            if view_height < 100 or view_width < 100:
                view_height = max(view_height, 600)
                view_width = max(view_width, 800)
            
            # Get original image dimensions
            orig_height, orig_width = self.original_image.shape[:2]
            
            # Calculate scale factor to fit the image in the view while maintaining aspect ratio
            scale_factor = min(view_height / orig_height, view_width / orig_width)
            
            # Calculate new dimensions
            new_width = int(orig_width * scale_factor)
            new_height = int(orig_height * scale_factor)
            
            # Make sure new dimensions don't exceed view
            if new_height > view_height or new_width > view_width:
                scale_factor = min(view_height / orig_height, view_width / orig_width) * 0.9  # 10% margin
                new_width = int(orig_width * scale_factor)
                new_height = int(orig_height * scale_factor)
            
            # Resize the image
            self.resized_image = cv2.resize(
                self.original_image, 
                (new_width, new_height),
                interpolation=cv2.INTER_LINEAR
            )
            
            # Clear zoom state and history
            self.zoom_history = []
            self.current_zoom = None
            
            # Update UI
            self.reset_zoom_button.setEnabled(False)  # Disable since we're at base zoom
            
            # Store the scale factor for use in overlay_genes
            self.full_view_scale_factor = scale_factor
            
            # Clear any cached coordinates since we have a new zoom level
            if hasattr(self, 'visible_gene_x_coords'):
                delattr(self, 'visible_gene_x_coords')
            if hasattr(self, 'visible_gene_y_coords'):
                delattr(self, 'visible_gene_y_coords')
            if hasattr(self, 'visible_gene_colors'):
                delattr(self, 'visible_gene_colors')
            if hasattr(self, 'cell_center_x_coords'):
                delattr(self, 'cell_center_x_coords')
            if hasattr(self, 'cell_center_y_coords'):
                delattr(self, 'cell_center_y_coords')
            # Call overlay_genes to redraw genes if data exists
            self.update_display()
            if self.gene_data is not None and self.selected_genes:
                self.overlay_genes()
                
            self.status_bar.showMessage("View reset to original")

            
    def load_transformation_matrix(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.status_bar.showMessage("Loading Transformation Matrix...")
            QTimer.singleShot(0, lambda: self.process_csv(file_name))

    def load_detected_transcripts(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.status_bar.showMessage(
                "Loading Detected Transcripts...(this may take a while)")
            QTimer.singleShot(0, lambda: self.process_csv(file_name))
    
    def load_anndata(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Anndata File", "", "Anndata Files (*.h5ad);"
            "All Files (*)")
        if file_name:
            self.status_bar.showMessage(
                "Loading Anndata...")
            QTimer.singleShot(0, lambda: self.process_anndata(file_name))
            
    def process_anndata(self, file_name):
        """Process anndata file to extract cell centers"""
        try:
            adata = ad.read_h5ad(file_name)
            self.status_bar.showMessage("AnnData loaded successfully")
            
            # Check for spatial coordinates in different possible locations
            if 'spatial' in adata.obsm:
                cell_coords = adata.obsm['spatial']
                x_coords = cell_coords[:, 0]
                y_coords = cell_coords[:, 1]
            elif 'X_spatial' in adata.obsm:
                cell_coords = adata.obsm['X_spatial']
                x_coords = cell_coords[:, 0]
                y_coords = cell_coords[:, 1]
            elif 'center_x' in adata.obs and 'center_y' in adata.obs:
                x_coords = adata.obs['center_x'].values
                y_coords = adata.obs['center_y'].values
            elif 'x' in adata.obs and 'y' in adata.obs:
                x_coords = adata.obs['x'].values
                y_coords = adata.obs['y'].values
            else:
                # Last resort: try to find any columns that might contain coordinates
                potential_x_cols = [col for col in adata.obs.columns if 'x' in col.lower()]
                potential_y_cols = [col for col in adata.obs.columns if 'y' in col.lower()]
                
                if potential_x_cols and potential_y_cols:
                    x_coords = adata.obs[potential_x_cols[0]].values
                    y_coords = adata.obs[potential_y_cols[0]].values
                    self.status_bar.showMessage(f"Using columns '{potential_x_cols[0]}' and '{potential_y_cols[0]}' for coordinates")
                else:
                    self.status_bar.showMessage("Could not find cell center coordinates in AnnData file")
                    return
            
            # Create DataFrame to store cell centers
            self.cell_centers = pd.DataFrame({
                'global_x': x_coords,
                'global_y': y_coords
            })
            
            num_cells = len(self.cell_centers)
            self.status_bar.showMessage(f"Loaded {num_cells} cell centers from AnnData file")
            
            # Enable the cell centers button
            self.toggle_cell_centers_button.setEnabled(True)
            
            # If already toggled to show cells and we have an image, display them
            cell_centers = getattr(self, 'cell_centers', None)
            if (cell_centers is not None and not cell_centers.empty) and (self.image is not None):
                self.display_cell_centers()
                
        except ImportError:
            self.status_bar.showMessage("Please install the 'anndata' package to load AnnData files using `pip install anndata`")
        except Exception as e:
            self.status_bar.showMessage(f"Error processing AnnData file: {str(e)}")
            print(f"Error processing AnnData file: {str(e)}")
            
    def process_csv(self, file_name):
        try:
            if "transform" in file_name.lower():
                # Load transformation matrix
                self.transformation_matrix = pd.read_csv(
                    file_name, header=None)
                self.transformation_matrix = self.transformation_matrix[0].str.split(
                    expand=True).astype(float).values
                self.status_bar.showMessage(
                    "Transformation matrix loaded successfully")
            else:
                self.gene_data = pd.read_csv(file_name)

                unique_genes = self.gene_data['gene'].unique()
                self.gene_dropdown.clear()
                self.gene_dropdown.addItems(unique_genes)

                if self.image is not None:
                    self.overlay_genes()
                    
                self.status_bar.showMessage("Gene data loaded successfully")
        except Exception as e:
            self.status_bar.showMessage(
                f"Error loading file {file_name}: {str(e)}")
        
    def on_gene_selected(self, gene):
        if gene in self.selected_genes:
            self.status_bar.showMessage("Gene already selected, choose a different gene.")
            return
        elif not gene:
            self.status_bar.showMessage("Gene does not exist, choose a different gene.")
            return

        # Generate a unique color
        color = self.generate_unique_color()

        # Create a gene selection widget
        gene_widget = QFrame()
        gene_widget_layout = QHBoxLayout(gene_widget)

        # Color indicator
        color_label = QLabel()
        color_label.setFixedSize(20, 20)
        color_label.setStyleSheet(f"background-color: rgb({color[0]}, {color[1]}, {color[2]}); border-radius: 10px;")

        # Gene name label
        gene_name_label = QLabel(gene)

        # Remove button
        remove_button = QPushButton("cancel")
        remove_button.setFixedSize(75, 25)
        remove_button.clicked.connect(
            lambda _, g=gene: self.remove_gene_selection(g))

        gene_widget_layout.addWidget(color_label)
        gene_widget_layout.addWidget(gene_name_label)
        gene_widget_layout.addStretch()
        gene_widget_layout.addWidget(remove_button)

        # Store gene and color
        self.selected_genes[gene] = (color[0], color[1], color[2])

        # Add to selected genes layout
        self.selected_genes_layout.addWidget(gene_widget)

        # Overlay genes
        self.overlay_genes()

    def remove_gene_selection(self, gene):
        # Remove from selected genes
        if gene in self.selected_genes:
            del self.selected_genes[gene]

        # Remove widget from layout
        for i in range(self.selected_genes_layout.count()):
            widget = self.selected_genes_layout.itemAt(i).widget()
            if widget:
                # Find all labels in the widget
                labels = widget.findChildren(QLabel)
                # Check if any label contains our gene name
                for label in labels:
                    if label.text() == gene:  # Exact match instead of partial match
                        # Remove the widget from layout
                        self.selected_genes_layout.removeWidget(widget)
                        # Hide the widget first
                        widget.hide()
                        self.overlay_genes()
                        # Schedule for deletion
                        widget.deleteLater()#deferred
                        # Reoverlay genes
                        
                        return  # Exit after finding and removing
                        break

        self.overlay_genes()

    def generate_unique_color(self):
        # Define available colors from the palette
        available_colors = [value for key, value in colors_rgb.items() 
                            if value not in self.selected_genes.values()]
        
        # If all colors have been used, start reusing them
        if not available_colors:
            return random.choice(list(colors_rgb.values()))
        
        # Return a random color from the available ones
        return random.choice(available_colors)

    def overlay_genes(self):
        """Overlay genes on the image and display cell centers if enabled."""
        if self.gene_data is None or self.image is None or self.resized_image is None:
            print("Please make sure to upload the detected transcripts")
            return

        # Create a copy of the resized image to draw on
        overlay_image = self.resized_image.copy()

        # Filter out only selected genes to make it faster
        selected_gene_mask = self.gene_data["gene"].isin(self.selected_genes)
        filtered_data = self.gene_data[selected_gene_mask]

        if filtered_data.empty:
            self.status_bar.showMessage("No selected genes to overlay.")
            # Display the original resized image without any overlay
            # self.display_image()
            
            # Check if cell centers need to be displayed
            if self.show_cell_centers:
                self._draw_cell_centers(overlay_image)
            return

        # Extract coordinates and genes
        coords = filtered_data[["global_x", "global_y"]].to_numpy()
        genes = filtered_data["gene"].to_numpy()

        # Apply transformation matrix in bulk
        if self.transformation_matrix is not None:
            ones = np.ones((coords.shape[0], 1))
            transformed_coords = np.dot(self.transformation_matrix, np.hstack([coords, ones]).T).T
            x_coords, y_coords = transformed_coords[:, 0], transformed_coords[:, 1]
        else:
            self.status_bar.showMessage("There is no transformation matrix. Please load a transformation matrix.")
            return

        # Handle zoomed view differently from the full view
        if hasattr(self, 'current_zoom') and self.current_zoom is not None:
            # Filter for genes only in the zoomed region (in original image coordinates)
            zoom_x_start = self.current_zoom['x_start']
            zoom_y_start = self.current_zoom['y_start']
            zoom_x_end = self.current_zoom['x_end']
            zoom_y_end = self.current_zoom['y_end']
            
            # Create masks for genes inside the zoomed area
            in_zoom_region = (
                (x_coords >= zoom_x_start) & 
                (x_coords < zoom_x_end) & 
                (y_coords >= zoom_y_start) & 
                (y_coords < zoom_y_end)
            )
            
            # Filter to only include genes in the zoomed region
            if not any(in_zoom_region):
                self.status_bar.showMessage("No genes in the zoomed region")
                
                # Still display the zoomed image
                # self.display_image()
                
                # Check if cell centers need to be displayed
                if self.show_cell_centers:
                    self._draw_cell_centers(overlay_image)
                return
                
            x_coords = x_coords[in_zoom_region]
            y_coords = y_coords[in_zoom_region]
            genes = genes[in_zoom_region]
            
            # Adjust coordinates for zoomed view
            x_coords = (x_coords - zoom_x_start) * self.current_zoom['scale_factor']
            y_coords = (y_coords - zoom_y_start) * self.current_zoom['scale_factor']
        else:
            # Normal full-image view
            # Use the scale factor calculated in do_full_reset
            if hasattr(self, 'full_view_scale_factor'):
                scale_factor = self.full_view_scale_factor
            else:
                # Fall back to calculating scale factor if not already stored
                orig_height, orig_width = self.original_image.shape[:2]
                view_height = self.image_label.height()
                view_width = self.image_label.width()
                scale_factor = min(view_height / orig_height, view_width / orig_width)
                if scale_factor <= 0:
                    scale_factor = 0.5  # Fallback if calculation fails
                self.full_view_scale_factor = scale_factor
                
            x_coords = x_coords * scale_factor
            y_coords = y_coords * scale_factor

        # Vectorized color mapping
        colors = np.array([self.selected_genes[gene] for gene in genes])
        
        # Convert to integer coordinates
        x_coords = x_coords.astype(int)
        y_coords = y_coords.astype(int)

        # Filter out genes that would be outside the visible area
        height, width = overlay_image.shape[:2]
        valid_coords = (
            (x_coords >= 0) & 
            (x_coords < width) & 
            (y_coords >= 0) & 
            (y_coords < height)
        )
        
        x_coords = x_coords[valid_coords]
        y_coords = y_coords[valid_coords]
        colors = colors[valid_coords]

        # Store for potential use in other functions
        self.visible_gene_x_coords = x_coords
        self.visible_gene_y_coords = y_coords
        self.visible_gene_colors = colors

        # # Draw visible genes
        # for x, y, color in zip(x_coords, y_coords, colors):
        #     color = tuple(map(int, color))
        #     color = (color[2], color[1], color[0])  # Convert RGB to BGR for OpenCV
        #     cv2.circle(overlay_image, (x, y), 1, color, -1)

        # # Check if cell centers need to be displayed
        # if self.show_cell_centers:
        #     self._draw_cell_centers(overlay_image)
        # else:
        #     # Convert image for display
        self.update_display()
            
        self.status_bar.showMessage(f"Genes overlaid: {len(x_coords)} visible points")

    def load_image(self):
        self.status_bar.showMessage(f"Checking Image...")
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", "Images (*.png *.jpg *.bmp *.tif *.tiff)")
        self.status_bar.showMessage(f"Opening File...")
        if file_name:
            self.status_bar.showMessage("Please choose an image.")
            QTimer.singleShot(100, lambda: self.process_image(file_name))

    def process_image(self, file_name):
        try:
            # Create an image pyramid for large images
            if file_name.lower().endswith(('.tif', '.tiff')):
                print(f"Reading image, {file_name}")
                self.image = cv2.imread(file_name)
            
            print("making copy")
            self.original_image = self.image.copy()

            if self.image is not None:
                # Instead of using fixed screen dimensions, use the actual image label dimensions
                self.reset_zoom_button.setEnabled(False)  # Disable zoom reset initially
                self.do_full_reset()  # This will properly resize the image to fit
                
                # If gene data is already loaded, reoverlay genes
                if self.gene_data is not None:
                    self.overlay_genes()

                self.status_bar.showMessage("Image loaded and resized successfully")
            else:
                self.status_bar.showMessage("Failed to load image")
        except Exception as e:
            self.status_bar.showMessage(f"Error loading image: {str(e)}")
            print(f"Error loading image: {str(e)}")
    
    def display_image(self):
        if self.resized_image is not None:
            # Convert the image to RGB format
            resized_image_rgb = cv2.cvtColor(
                self.resized_image, cv2.COLOR_BGR2RGB)

            # Get image dimensions
            height, width, channel = resized_image_rgb.shape
            bytes_per_line = 3 * width

            # Create QImage from the RGB image data
            q_img = QImage(resized_image_rgb.data, width, height,
                        bytes_per_line, QImage.Format_RGB888)

            # Display the image in the QLabel
            self.image_label.setPixmap(QPixmap.fromImage(q_img))
            
            # Ensure the image label size hint is appropriate
            self.image_label.setMinimumSize(1, 1)  # Allow the label to shrink if needed
            
            self.status_bar.showMessage(f"Image displayed successfully ({width}x{height})")
        else:
            self.status_bar.showMessage("Resized image is None")

    def resizeEvent(self, event):
        """Handle window resize events to adjust the image size"""
        super().resizeEvent(event)
        
        # If we have an image loaded, resize it to fit the new dimensions
        if hasattr(self, 'original_image') and self.original_image is not None:
            # Delay the resize slightly to ensure all UI components have updated their sizes
            QTimer.singleShot(50, self.resize_image_to_fit)

    def resize_image_to_fit(self):
        """Resize the current image to fit the display after window resize"""
        if hasattr(self, 'current_zoom') and self.current_zoom is not None:
            # We're in a zoomed state, don't resize
            return
            
        # We're in the full view, resize to fit
        self.do_full_reset()
        
if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())