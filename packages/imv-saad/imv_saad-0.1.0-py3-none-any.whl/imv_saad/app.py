import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import random

# --- Handle dirs.py persistence ---
DIRS_FILE = os.path.join(os.path.dirname(__file__), "dirs.py")

def ensure_dirs_file():
    """Create dirs.py if not exists with empty defaults."""
    if not os.path.exists(DIRS_FILE):
        with open(DIRS_FILE, "w") as f:
            f.write('image_dir = ""\n')
            f.write('mask_dir = ""\n')
            f.write('pred_dir = ""\n')

def load_dirs():
    """Load folder paths from dirs.py safely."""
    ensure_dirs_file()
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("dirs", DIRS_FILE)
        dirs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dirs)
        return dirs.image_dir, dirs.mask_dir, dirs.pred_dir
    except Exception:
        return "", "", ""

def save_dirs(image_dir, mask_dir, pred_dir):
    """Save folder paths to dirs.py."""
    with open(DIRS_FILE, "w") as f:
        f.write(f'image_dir = r"""{image_dir}"""\n')
        f.write(f'mask_dir = r"""{mask_dir}"""\n')
        f.write(f'pred_dir = r"""{pred_dir}"""\n')


class ImageMaskViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image & Mask Viewer")

        # File lists
        self.image_files = []
        self.mask_files = []
        self.pred_files = []
        self.index = 0

        # Folder dirs
        self.image_dir, self.mask_dir, self.pred_dir = load_dirs()

        # If dirs exist, preload
        if self.image_dir and os.path.exists(self.image_dir):
            self.image_files = self.list_images(self.image_dir)
        if self.mask_dir and os.path.exists(self.mask_dir):
            self.mask_files = self.list_images(self.mask_dir)
        if self.pred_dir and os.path.exists(self.pred_dir):
            self.pred_files = self.list_images(self.pred_dir)

        # Zoom & pan state
        self.zoom = 1.0
        self.base_scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.dragging = False

        # Cached PIL images
        self.curr_image = None
        self.curr_mask = None
        self.curr_pred = None
        self.curr_overlay = None
        self.curr_pred_overlay = None

        # Colormap cache
        self.color_map = {}
        self.color_names = {}

        # Info text buffer
        self.pixel_info = "Pointer: NaN"
        self.iou_info = "IoU: NaN"
        self.info_text_base = ""

        # Layout 3x2 grid
        for r in range(3):
            self.root.grid_rowconfigure(r, weight=1)
        for c in range(2):
            self.root.grid_columnconfigure(c, weight=1)

        # Panels
        self.info_text = self.create_panel("Info", 0, 0, text_widget=True)
        self.image_canvas = self.create_panel("Image", 0, 1)
        self.mask_canvas = self.create_panel("Mask", 1, 0)
        self.overlay_canvas = self.create_panel("Mask Overlay", 1, 1)
        self.pred_canvas = self.create_panel("Predicted Mask", 2, 0)
        self.pred_overlay_canvas = self.create_panel("Predicted Overlay", 2, 1)

        # Store references
        self.tk_img_image = None
        self.tk_img_mask = None
        self.tk_img_overlay = None
        self.tk_img_pred = None
        self.tk_img_pred_overlay = None

        # Menubar
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Image Folder", command=self.load_images)
        filemenu.add_command(label="Open Mask Folder", command=self.load_masks)
        filemenu.add_command(label="Open Predicted Folder", command=self.load_preds)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)

        # Bindings
        root.bind("<Right>", self.next_image)
        root.bind("<Left>", self.prev_image)
        root.bind("r", lambda e: self.reset_view())
        root.bind("<Configure>", self.refresh_display)

        for canvas in (self.image_canvas, self.mask_canvas,
                       self.overlay_canvas, self.pred_canvas, self.pred_overlay_canvas):
            canvas.bind("<ButtonPress-1>", self.start_pan)
            canvas.bind("<B1-Motion>", self.do_pan)
            canvas.bind("<MouseWheel>", self.do_zoom)  # Windows
            canvas.bind("<Button-4>", self.do_zoom)    # Linux scroll up
            canvas.bind("<Button-5>", self.do_zoom)    # Linux scroll down
            canvas.bind("<Motion>", self.show_pixel_info)

        # If we loaded some dirs already → load first image
        if self.image_files or self.mask_files or self.pred_files:
            self.reset_and_load()

    def list_images(self, folder):
        return sorted([os.path.join(folder, f)
                       for f in os.listdir(folder)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    def create_panel(self, title, row, col, text_widget=False):
        frame = tk.Frame(self.root, bg="black")
        frame.grid(row=row, column=col, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        label = tk.Label(frame, text=title, bg="gray20", fg="white",
                         font=("Consolas", 11, "bold"))
        label.grid(row=0, column=0, sticky="ew")

        if text_widget:
            text = tk.Text(frame, bg="black", fg="lime",
                           font=("Consolas", 10), wrap="word")
            text.grid(row=1, column=0, sticky="nsew")
            text.config(state="disabled")
            scrollbar = tk.Scrollbar(frame, command=text.yview)
            scrollbar.grid(row=1, column=1, sticky="ns")
            text.config(yscrollcommand=scrollbar.set)
            return text
        else:
            canvas = tk.Canvas(frame, bg="black")
            canvas.grid(row=1, column=0, sticky="nsew")
            return canvas

    def load_images(self):
        folder = filedialog.askdirectory(title="Select Image Folder")
        if folder:
            self.image_dir = folder
            self.image_files = self.list_images(folder)
            save_dirs(self.image_dir, self.mask_dir, self.pred_dir)
            self.index = 0
            self.reset_and_load()

    def load_masks(self):
        folder = filedialog.askdirectory(title="Select Mask Folder")
        if folder:
            self.mask_dir = folder
            self.mask_files = self.list_images(folder)
            save_dirs(self.image_dir, self.mask_dir, self.pred_dir)
            self.index = 0
            self.reset_and_load()

    def load_preds(self):
        folder = filedialog.askdirectory(title="Select Predicted Mask Folder")
        if folder:
            self.pred_dir = folder
            self.pred_files = self.list_images(folder)
            save_dirs(self.image_dir, self.mask_dir, self.pred_dir)
            self.index = 0
            self.reset_and_load()

    def reset_and_load(self):
        self.zoom = 1.0
        self.base_scale = 1.0
        self.pan_x = self.pan_y = 0
        self.load_current_images()
        self.refresh_display()

    def load_current_images(self):
        total_images = max(len(self.image_files), len(self.mask_files), len(self.pred_files))
        if total_images == 0 or self.index >= total_images:
            return

        # Image
        self.curr_image = None
        if self.index < len(self.image_files):
            self.curr_image = Image.open(self.image_files[self.index]).convert("RGB")

        # Mask
        self.curr_mask = None
        if self.index < len(self.mask_files):
            mask = Image.open(self.mask_files[self.index]).convert("L")
            mask_np = np.array(mask)
            if mask_np.max() > 0 and mask_np.max() != 255:
                mask_np = (mask_np.astype(np.float32) / mask_np.max()) * 255
                mask_np = mask_np.astype(np.uint8)
            self.curr_mask = Image.fromarray(mask_np)

        # Predicted Mask
        self.curr_pred = None
        if self.index < len(self.pred_files):
            pred = Image.open(self.pred_files[self.index]).convert("L")
            pred_np = np.array(pred)
            if pred_np.max() > 0 and pred_np.max() != 255:
                pred_np = (pred_np.astype(np.float32) / pred_np.max()) * 255
                pred_np = pred_np.astype(np.uint8)
            self.curr_pred = Image.fromarray(pred_np)

        # Resize to match image
        if self.curr_image:
            if self.curr_mask and self.curr_mask.size != self.curr_image.size:
                self.curr_mask = self.curr_mask.resize(self.curr_image.size, Image.NEAREST)
            if self.curr_pred and self.curr_pred.size != self.curr_image.size:
                self.curr_pred = self.curr_pred.resize(self.curr_image.size, Image.NEAREST)

        # Overlays
        self.curr_overlay = self.make_overlay(self.curr_image, self.curr_mask) if self.curr_image and self.curr_mask else None
        self.curr_pred_overlay = self.make_overlay(self.curr_image, self.curr_pred) if self.curr_image and self.curr_pred else None

        # IoU
        if self.curr_mask is not None and self.curr_pred is not None:
            mask_bin = (np.array(self.curr_mask) > 0).astype(np.uint8)
            pred_bin = (np.array(self.curr_pred) > 0).astype(np.uint8)
            inter = np.logical_and(mask_bin, pred_bin).sum()
            union = np.logical_or(mask_bin, pred_bin).sum()
            iou = inter / union if union > 0 else 0.0
            self.iou_info = f"IoU: {iou:.4f}"
        else:
            self.iou_info = "IoU: NaN"

        # Info section
        info_lines = []
        if self.curr_image:
            img_size_kb = os.path.getsize(self.image_files[self.index]) / 1024
            info_lines.extend([
                f"Image: {os.path.basename(self.image_files[self.index])}",
                f" - Resolution: {self.curr_image.width}x{self.curr_image.height}",
                f" - Size: {img_size_kb:.1f} KB"
            ])
        if self.curr_mask:
            mask_size_kb = os.path.getsize(self.mask_files[self.index]) / 1024
            mask_vals = np.unique(np.array(self.curr_mask))
            info_lines.extend([
                "",
                f"Mask: {os.path.basename(self.mask_files[self.index])}",
                f" - Resolution: {self.curr_mask.width}x{self.curr_mask.height}",
                f" - Size: {mask_size_kb:.1f} KB",
                f" - Unique values ({len(mask_vals)}):"
            ])
            for val in mask_vals:
                rgb, cname = self.get_color(val)
                info_lines.append(f"   {val}: {cname} RGB{rgb}")
        if self.curr_pred:
            pred_size_kb = os.path.getsize(self.pred_files[self.index]) / 1024
            pred_vals = np.unique(np.array(self.curr_pred))
            info_lines.extend([
                "",
                f"Predicted Mask: {os.path.basename(self.pred_files[self.index])}",
                f" - Resolution: {self.curr_pred.width}x{self.curr_pred.height}",
                f" - Size: {pred_size_kb:.1f} KB",
                f" - Unique values ({len(pred_vals)}):"
            ])
            for val in pred_vals:
                rgb, cname = self.get_color(val)
                info_lines.append(f"   {val}: {cname} RGB{rgb}")

        self.info_text_base = "\n".join(info_lines)
        self.pixel_info = "Pointer: NaN"
        self.update_info_panel()

    def get_color(self, label_val):
        if label_val not in self.color_map:
            random.seed(int(label_val))
            r = random.randint(50, 255)
            g = random.randint(50, 255)
            b = random.randint(50, 255)
            self.color_map[label_val] = (r, g, b)
            self.color_names[label_val] = f"Class{label_val}"
        return self.color_map[label_val], self.color_names[label_val]

    def make_overlay(self, img_pil, mask_pil):
        if mask_pil is None or img_pil is None:
            return None
        img_np = np.array(img_pil).astype(np.float32)
        mask_np = np.array(mask_pil)

        overlay = img_np.copy()
        unique_vals = np.unique(mask_np)

        for val in unique_vals:
            if val == 0:
                continue
            (r, g, b), _ = self.get_color(val)
            region = mask_np == val
            overlay[region] = 0.8 * overlay[region] + 0.2 * np.array([r, g, b])

        edges = np.zeros_like(mask_np, dtype=bool)
        edges[:-1, :] |= mask_np[:-1, :] != mask_np[1:, :]
        edges[:, :-1] |= mask_np[:, :-1] != mask_np[:, 1:]
        overlay[edges] = [20, 20, 20]

        return Image.fromarray(overlay.astype(np.uint8))

    def start_pan(self, event):
        self.dragging = True
        self.start_x, self.start_y = event.x, event.y

    def do_pan(self, event):
        if self.dragging:
            dx, dy = event.x - self.start_x, event.y - self.start_y
            self.pan_x += dx
            self.pan_y += dy
            self.start_x, self.start_y = event.x, event.y
            self.refresh_display()

    def do_zoom(self, event):
        if event.num == 4 or event.delta > 0:
            self.zoom *= 1.1
        elif event.num == 5 or event.delta < 0:
            self.zoom /= 1.1
        self.refresh_display()

    def draw_on_canvas(self, canvas, img, which):
        if img is None:
            canvas.delete("all")
            return
        cw, ch = max(canvas.winfo_width(), 1), max(canvas.winfo_height(), 1)

        if self.base_scale == 1.0:
            self.base_scale = min(cw / img.width, ch / img.height)

        total_scale = self.base_scale * self.zoom
        new_w, new_h = int(img.width * total_scale), int(img.height * total_scale)
        if new_w < 2 or new_h < 2:
            return

        img_resized = img.resize((new_w, new_h), Image.NEAREST)
        tk_img = ImageTk.PhotoImage(img_resized)
        canvas.delete("all")
        x, y = cw // 2 + self.pan_x, ch // 2 + self.pan_y
        canvas.create_image(x, y, image=tk_img, anchor="center")

        if which == "image":
            self.tk_img_image = tk_img
        elif which == "mask":
            self.tk_img_mask = tk_img
        elif which == "overlay":
            self.tk_img_overlay = tk_img
        elif which == "pred":
            self.tk_img_pred = tk_img
        elif which == "pred_overlay":
            self.tk_img_pred_overlay = tk_img

    def show_pixel_info(self, event):
        if self.curr_image is None:
            return
        cw, ch = event.widget.winfo_width(), event.widget.winfo_height()
        total_scale = self.base_scale * self.zoom
        img_w, img_h = self.curr_image.size
        x_img = int((event.x - cw // 2 - self.pan_x) / total_scale + img_w // 2)
        y_img = int((event.y - ch // 2 - self.pan_y) / total_scale + img_h // 2)
        if 0 <= x_img < img_w and 0 <= y_img < img_h:
            rgb = np.array(self.curr_image)[y_img, x_img].tolist()
            if self.curr_mask is not None:
                mval = int(np.array(self.curr_mask)[y_img, x_img])
                (r, g, b), cname = self.get_color(mval)
                self.pixel_info = f"Pointer: ({x_img},{y_img}) Image RGB={rgb}, Mask={mval} ({cname} RGB({r},{g},{b}))"
            else:
                self.pixel_info = f"Pointer: ({x_img},{y_img}) Image RGB={rgb}, Mask=NaN"
        else:
            self.pixel_info = "Pointer: NaN"
        self.update_info_panel()

    def update_info_panel(self):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, self.pixel_info + "\n" + self.iou_info + "\n\n" + self.info_text_base)
        self.info_text.config(state="disabled")

    def refresh_display(self, event=None):
        self.draw_on_canvas(self.image_canvas, self.curr_image, "image")
        self.draw_on_canvas(self.mask_canvas, self.curr_mask, "mask")
        self.draw_on_canvas(self.overlay_canvas, self.curr_overlay, "overlay")
        self.draw_on_canvas(self.pred_canvas, self.curr_pred, "pred")
        self.draw_on_canvas(self.pred_overlay_canvas, self.curr_pred_overlay, "pred_overlay")

    def next_image(self, event=None):
        total_images = max(len(self.image_files), len(self.mask_files), len(self.pred_files))
        if self.index < total_images - 1:
            self.index += 1
            self.reset_and_load()

    def prev_image(self, event=None):
        if self.index > 0:
            self.index -= 1
            self.reset_and_load()


def main():
    root = tk.Tk()
    app = ImageMaskViewer(root)
    root.geometry("1600x1200")
    root.mainloop()