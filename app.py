"""Imag to Text — Windows desktop OCR, with no document uploads."""
import os
import queue
import tempfile
import threading
import uuid
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from core import Page, OCR, render_pages, export, save_project, load_project


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Imag to Text · OCR local")
        width = min(1280, self.winfo_screenwidth() - 100)
        height = min(820, self.winfo_screenheight() - 140)
        self.geometry(f"{width}x{height}+40+40")
        self.minsize(900, 540)
        self.configure(bg="#edf2f7")
        self.cache = tempfile.TemporaryDirectory(prefix="imag-to-text-")
        self.pages = []
        self.current = None
        self.dirty = False
        self.busy = False
        self.events = queue.Queue()
        self.cancelled = threading.Event()
        self.engine = None
        self.photo = None
        self.zoom = tk.StringVar(value="Ajustar")
        self.boxes = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Abre imágenes o PDF escaneados para comenzar. Todo se procesa en tu PC.")
        self.region = tk.StringVar(value="Pulsa un recuadro de la imagen para identificar el texto original.")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#edf2f7")
        style.configure("TLabel", background="#edf2f7", foreground="#182c43", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 7))
        style.configure("Accent.TButton", background="#136b77", foreground="white")
        style.map("Accent.TButton", background=[("active", "#155965")])
        header = tk.Frame(self, bg="#132c43", padx=22, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="Imag to Text", font=("Segoe UI", 22, "bold"), bg="#132c43", fg="white").pack(side="left")
        tk.Label(header, text="IMAGEN → TEXTO EDITABLE     /     OCR LOCAL", font=("Segoe UI", 10), bg="#132c43", fg="#a8dce0").pack(side="right")
        toolbar = ttk.Frame(self, padding=(16, 12))
        toolbar.pack(fill="x")
        self.open_button = ttk.Button(toolbar, text="＋ Abrir archivos", style="Accent.TButton", command=self.open_files)
        self.open_button.pack(side="left", padx=(0, 8))
        self.project_button = ttk.Button(toolbar, text="Abrir proyecto", command=self.open_project)
        self.project_button.pack(side="left", padx=4)
        self.save_button = ttk.Button(toolbar, text="Guardar proyecto", command=self.save)
        self.save_button.pack(side="left", padx=4)
        self.export_button = ttk.Button(toolbar, text="Exportar texto…", command=self.export_all)
        self.export_button.pack(side="left", padx=4)
        self.cancel_button = ttk.Button(toolbar, text="Cancelar OCR", command=self.cancel, state="disabled")
        self.cancel_button.pack(side="right")
        body = ttk.Panedwindow(self, orient="horizontal")
        self.body = body
        body.pack(fill="both", expand=True, padx=16)
        sidebar = ttk.Frame(body, padding=(0, 0, 10, 0))
        ttk.Label(sidebar, text="PÁGINAS", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        self.page_list = tk.Listbox(sidebar, width=24, bg="white", fg="#182c43", font=("Segoe UI", 10), relief="flat", selectbackground="#136b77", exportselection=False)
        self.page_list.pack(fill="both", expand=True)
        self.page_list.bind("<<ListboxSelect>>", self.select_page)
        body.add(sidebar, weight=1)
        preview = ttk.Frame(body, padding=(6, 0))
        preview_bar = ttk.Frame(preview)
        preview_bar.pack(fill="x", pady=(0, 8))
        ttk.Label(preview_bar, text="ORIGINAL", font=("Segoe UI", 10, "bold")).pack(side="left")
        zoom = ttk.Combobox(preview_bar, textvariable=self.zoom, values=["Ajustar", "100%", "150%", "200%"], width=8, state="readonly")
        zoom.pack(side="right")
        zoom.bind("<<ComboboxSelected>>", lambda e: self.draw())
        ttk.Checkbutton(preview_bar, text="Zonas OCR", variable=self.boxes, command=self.draw).pack(side="right", padx=8)
        canvas_frame = ttk.Frame(preview)
        canvas_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg="#d9e2eb", highlightthickness=0)
        vertical = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        horizontal = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<Button-1>", self.pick_region)
        self.region_label = ttk.Label(preview, textvariable=self.region, wraplength=350)
        self.region_label.pack(fill="x", pady=8)
        body.add(preview, weight=3)
        editor_frame = ttk.Frame(body, padding=(10, 0, 0, 0))
        editbar = ttk.Frame(editor_frame)
        editbar.pack(fill="x", pady=(0, 8))
        ttk.Label(editbar, text="TEXTO EDITABLE", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(editbar, text="Copiar", command=self.copy_text).pack(side="right")
        self.editor = ScrolledText(editor_frame, width=20, height=12, wrap="word", undo=True, font=("Segoe UI", 12), padx=18, pady=16, relief="flat", bg="white", fg="#182c43", selectbackground="#b1e2e1")
        self.editor.pack(fill="both", expand=True)
        self.editor.bind("<<Modified>>", self.modified)
        self.editor.configure(state="disabled")
        ttk.Label(editor_frame, text="Revisa antes de exportar. Ctrl+Z: deshacer.").pack(anchor="w", pady=8)
        body.add(editor_frame, weight=3)
        bottom = ttk.Frame(self, padding=(16, 10))
        bottom.pack(fill="x", side="bottom", before=body)
        self.progress = ttk.Progressbar(bottom, mode="indeterminate", length=100)
        self.progress.pack(side="right", padx=8)
        ttk.Label(bottom, textvariable=self.status, wraplength=1040).pack(side="left")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Control-o>", lambda e: self.open_files())
        self.bind("<Control-s>", lambda e: self.save())
        self.after(100, self.poll)
        self.after(150, self.balance_panes)

    def balance_panes(self):
        width = self.body.winfo_width()
        self.body.sashpos(0, int(width * .18))
        self.body.sashpos(1, int(width * .59))

    def modified(self, event=None):
        if self.editor.edit_modified():
            if self.current is not None:
                self.pages[self.current].text = self.editor.get("1.0", "end-1c")
                self.dirty = True
            self.editor.edit_modified(False)

    def sync(self):
        if self.current is not None:
            self.pages[self.current].text = self.editor.get("1.0", "end-1c")

    def select_page(self, event=None):
        selection = self.page_list.curselection()
        if not selection:
            return
        self.sync()
        self.current = selection[0]
        self.editor.configure(state="normal")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", self.pages[self.current].text)
        self.editor.edit_reset()
        self.editor.edit_modified(False)
        self.region.set("Pulsa un recuadro para identificar el texto original.")
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        if hasattr(self, "region_label"):
            self.region_label.configure(wraplength=max(160, self.canvas.winfo_width() - 10))
        if self.current is None:
            self.canvas.create_text(self.canvas.winfo_width() / 2, 150, text="Tu documento aparecerá aquí\n\nPDF · PNG · JPG · TIFF\nBMP · WEBP", width=max(100, self.canvas.winfo_width() - 20), fill="#54708a", font=("Segoe UI", 12), justify="center")
            return
        with Image.open(self.pages[self.current].image) as source:
            if self.zoom.get() == "Ajustar":
                scale = min(max(100, self.canvas.winfo_width() - 24) / source.width, max(100, self.canvas.winfo_height() - 24) / source.height)
            else:
                scale = int(self.zoom.get()[:-1]) / 100
            self.scale = scale
            size = (max(1, int(source.width * scale)), max(1, int(source.height * scale)))
            self.photo = ImageTk.PhotoImage(source.resize(size, Image.Resampling.LANCZOS))
        self.canvas.create_image(12, 12, image=self.photo, anchor="nw")
        self.canvas.configure(scrollregion=(0, 0, size[0] + 24, size[1] + 24))
        if self.boxes.get():
            for i, region in enumerate(self.pages[self.current].regions):
                points = [coordinate * scale + 12 for point in region["box"] for coordinate in point]
                self.canvas.create_polygon(points, outline="#148a8a" if region["score"] >= .8 else "#cf830b", fill="", width=1, tags=(f"region:{i}",))

    def pick_region(self, event):
        if self.current is None:
            return
        x = (self.canvas.canvasx(event.x) - 12) / self.scale
        y = (self.canvas.canvasy(event.y) - 12) / self.scale
        for region in self.pages[self.current].regions:
            xs, ys = zip(*region["box"])
            if min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys):
                text = region["text"]
                self.region.set(f"OCR original · confianza {region['score']:.0%}: {text}")
                found = self.editor.search(text, "1.0", stopindex="end", exact=True)
                self.editor.tag_remove("sel", "1.0", "end")
                if found:
                    self.editor.tag_add("sel", found, f"{found}+{len(text)}c")
                    self.editor.see(found)
                    self.editor.focus_set()
                return

    def set_busy(self, busy):
        self.busy = busy
        for button in (self.open_button, self.project_button, self.save_button, self.export_button):
            button.configure(state="disabled" if busy else "normal")
        self.cancel_button.configure(state="normal" if busy else "disabled")
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def open_files(self):
        if self.busy:
            return
        paths = filedialog.askopenfilenames(title="Selecciona imágenes o PDF", filetypes=[("Imágenes y PDF", "*.pdf *.png *.jpg *.jpeg *.tif *.tiff *.bmp *.webp"), ("Todos los archivos", "*.*")])
        if not paths:
            return
        self.cancelled.clear()
        self.set_busy(True)
        self.status.set("Preparando motor OCR local…")
        threading.Thread(target=self.process, args=(paths,), daemon=True).start()

    def process(self, paths):
        errors = []
        count = 0
        try:
            if self.engine is None:
                self.engine = OCR()
            for path in paths:
                if self.cancelled.is_set():
                    break
                try:
                    for number, image in render_pages(path):
                        if self.cancelled.is_set():
                            break
                        self.events.put(("status", f"Reconociendo {Path(path).name} · página {number}…"))
                        text, regions = self.engine.recognize(image)
                        image_path = Path(self.cache.name) / f"{uuid.uuid4().hex}.png"
                        image.save(image_path)
                        self.events.put(("page", Page(str(path), number, str(image_path), text, regions)))
                        count += 1
                except Exception as exc:
                    errors.append(f"{Path(path).name}: {exc}")
        except Exception as exc:
            errors.append(str(exc))
        finally:
            self.events.put(("done", (count, errors, self.cancelled.is_set())))

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "status":
                    self.status.set(value)
                elif kind == "page":
                    self.pages.append(value)
                    self.page_list.insert("end", value.title + (" [sin texto]" if not value.text else ""))
                    self.dirty = True
                    if self.current is None:
                        self.page_list.selection_set(0)
                        self.select_page()
                elif kind == "done":
                    count, errors, cancelled = value
                    self.set_busy(False)
                    self.status.set(f"{'Cancelado' if cancelled else 'OCR terminado'} · {count} páginas procesadas · {len(errors)} errores. Revisa y exporta el texto.")
                    if errors:
                        messagebox.showwarning("Archivos con problemas", "\n\n".join(errors)[:4000])
        except queue.Empty:
            pass
        self.after(100, self.poll)

    def cancel(self):
        self.cancelled.set()
        self.status.set("Cancelando al terminar la página actual…")

    def copy_text(self):
        self.clipboard_clear()
        self.clipboard_append(self.editor.get("1.0", "end-1c"))
        self.status.set("Texto de la página copiado.")

    def export_all(self):
        if self.busy or not self.pages:
            return
        self.sync()
        path = filedialog.asksaveasfilename(title="Exportar todas las páginas", defaultextension=".docx", initialfile="texto.docx", filetypes=[("Word", "*.docx"), ("Markdown", "*.md"), ("Texto plano", "*.txt")])
        if path:
            try:
                export(self.pages, path)
                self.status.set(f"Exportado: {path}")
            except Exception as exc:
                messagebox.showerror("No se pudo exportar", str(exc))

    def save(self):
        if self.busy or not self.pages:
            return False
        self.sync()
        path = filedialog.asksaveasfilename(title="Guardar imágenes y texto editable", defaultextension=".itxt", initialfile="documento.itxt", filetypes=[("Proyecto Imag to Text", "*.itxt")])
        if not path:
            return False
        try:
            save_project(self.pages, path)
            self.dirty = False
            self.status.set(f"Proyecto guardado: {path}")
            return True
        except Exception as exc:
            messagebox.showerror("No se pudo guardar", str(exc))
            return False

    def confirm_discard(self):
        self.sync()
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel("Cambios sin guardar", "¿Guardar el proyecto antes de continuar?")
        return self.save() if answer is True else answer is False

    def open_project(self):
        if self.busy or not self.confirm_discard():
            return
        path = filedialog.askopenfilename(filetypes=[("Proyecto Imag to Text", "*.itxt")])
        if not path:
            return
        try:
            pages = load_project(path, self.cache.name)
        except Exception as exc:
            messagebox.showerror("No se pudo abrir", str(exc))
            return
        self.current = None
        self.pages = pages
        self.page_list.delete(0, "end")
        self.editor.configure(state="normal")
        self.editor.delete("1.0", "end")
        self.editor.edit_modified(False)
        self.editor.configure(state="disabled")
        for page in pages:
            self.page_list.insert("end", page.title)
        if pages:
            self.page_list.selection_set(0)
            self.select_page()
        self.dirty = False
        self.status.set(f"Proyecto abierto · {len(pages)} páginas")
        self.draw()

    def close(self):
        if self.busy:
            self.cancel()
            messagebox.showinfo("OCR en curso", "Se solicitó cancelar. Espera a que termine la página actual antes de cerrar.")
            return
        if self.confirm_discard():
            self.cache.cleanup()
            self.destroy()


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        from smoke import run
        run(Path(sys.argv[sys.argv.index("--self-test") + 1]))
    else:
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
        App().mainloop()
