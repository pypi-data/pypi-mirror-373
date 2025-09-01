from .imports import *
from abstract_utilities import get_logFile
logger = get_logFile(__name__)

# ─── Size handlers ─────────────────────────────────────────────
def _on_main_size_changed(self, _):
    logger.info("_on_main_size_changed")
    w, h = self.main_w_spin.value(), self.main_h_spin.value()
    self.main_size = QtCore.QSize(w, h)
    # keep it as a minimum, not a fixed size, so it can grow
    self.image_preview.setMinimumSize(self.main_size)
    if getattr(self, "_last_image", None):
        self._show_image(self._last_image)

def _on_collapsed_changed(self, v):
    logger.info("_on_collapsed_changed")
    self.collapsed_thumb_size = v
    self._refresh()

def _on_expanded_changed(self, v):
    logger.info("_on_expanded_changed")
    self.expanded_thumb_size = v
    self.thumb_tree.setIconSize(QtCore.QSize(v, v))
    self.expanded_scroll.setFixedHeight(v + 20)
    self._refresh()

def _refresh(self):
    logger.info("_refresh")
    idx = self.tree.currentIndex()
    if idx.isValid():
        self.on_folder_selected(idx)

# ─── Folder selection ──────────────────────────────────────────
# functions.py
def on_folder_selected(self, idx_or_payload):
    
    logger.info("on_folder_selected")
    try:
        folder = None

        # A) Click from QFileSystemModel
        if isinstance(idx_or_payload, QtCore.QModelIndex):
            fp = self.model.filePath(idx_or_payload)
            folder = Path(fp) if fp else None

        # B) Explicit path
        elif isinstance(idx_or_payload, (str, Path)):
            folder = Path(str(idx_or_payload))

        # C) Defensive: tuple/list like (name, directory, files)
        elif isinstance(idx_or_payload, (tuple, list)) and len(idx_or_payload) >= 2:
            _, directory = idx_or_payload[0], idx_or_payload[1]
            folder = Path(str(directory))

        if not folder:
            logger.warning("on_folder_selected: no folder resolved from %r", idx_or_payload)
            return []

        folder_str = str(folder)
        logger.info("on_folder_selected → %s", folder_str)
        dirs_js = get_dirs_js(folder_str)
        for folder,files in self.DIRS_JS.items():
            if not os.path.exists(folder):
                logger.warning("on_folder_selected: path does not exist: %s", folder_str)
                return []

            self.current_dir = folder

            # Avoid redundant rescans
            if getattr(self, "displayed_directories", None) and folder_str in self.displayed_directories:
                logger.debug("on_folder_selected: already displayed, skipping rescan")
            else:
                # if you added _stop_scanner_thread, it’s fine to call inside _populate
                self._populate_thumb_tree(folder)

            
            return []

    except Exception:
        logger.exception("on_folder_selected crashed for %r", idx_or_payload)
        return []
def _add_collapsible_node_threaded(self, name: str, directory: str, files: list[Path]):
    try:
        if directory in self.displayed_directories:
            return
        # 1) Render the directory right away
        self._add_collapsible_node(name, Path(directory), files)
        self.displayed_directories.add(directory)

        # 2) Extend slideshow queue with full paths for these files
        for p in files:
            # p may already be Path; normalize to str
            s = str(p)
            # avoid dupes if your scanner can re-emit
            if s not in self.slideshow_images:
                self.slideshow_images.append(s)

        # 3) If nothing is showing yet, seed the first frame
        if self._last_image is None and self.slideshow_images:
            self.slideshow_index = 0
            self._show_image(self.slideshow_images[0])

        QtWidgets.QApplication.processEvents()
    except Exception as e:
        logger.error(f"Error adding node for {directory}: {e}")
def load_all_directories_async(self):
    pool = QtCore.QThreadPool.globalInstance()

    # Optional: cap threads so we don’t starve UI
    pool.setMaxThreadCount(max(2, os.cpu_count() // 2))

    for directory, files in self.DIRS_JS.items():
        if not directory or not files:
            continue
        task = DirTask(directory, files)
        task.s.directory_ready.connect(self._add_collapsible_node_threaded,
                                       QtCore.Qt.ConnectionType.QueuedConnection)
        pool.start(task)

# ─── Collapsible tree ──────────────────────────────────────────
def _safe_list(self, p: Path):
    logger.info("_safe_list")
    try:
        p = Path(p)
        return list(p.iterdir())
    except Exception as e:
        logger.exception("iterdir failed for %s", p)
        return []
def _stop_scanner_thread(self):
    t = getattr(self, "scanner_thread", None)
    if t and t.isRunning():
        t.requestInterruption()
        t.quit()
        t.wait(5)
    self.scanner_thread = None

def _populate_thumb_tree(self, folder: Path):
    try:
        folder_str = str(folder)
        if folder_str in self.displayed_directories:
            logger.debug("_populate_thumb_tree: already displayed %s, skipping", folder_str)
            return

        logger.info("_populate_thumb_tree: starting scan for %s", folder_str)
        self.displayed_directories.append(folder_str)

        # Stop any existing scanner thread to avoid conflicts
        self._stop_scanner_thread()

        # Create and start the scanner thread, passing the folder and defaultRoot
        self.scanner_thread = DirScanner(folder, defaultRoot=self.defaultRoot)
        self.scanner_thread.dir_processed.connect(self._add_collapsible_node_threaded)
        self.scanner_thread.finished.connect(self._on_scanning_finished)
        self.scanner_thread.start()
    except Exception:
        logger.exception("_populate_thumb_tree failed for %s", folder)      
def _add_collapsible_node_threaded(self, name: str, directory: str, files: list):
  
        if not hasattr(self, "displayed_directories"):
            self.displayed_directories = set()
        if directory in self.displayed_directories:
            return
        self._add_collapsible_node(name, Path(directory), files)
        self.displayed_directories.add(directory)
        # optional: let UI breathe during large bursts
        QtWidgets.QApplication.processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents)

def _on_scanning_finished(self):
    logger.info("_on_scanning_finished")
    try:
        folder = self.current_dir  # Use the stored current_dir
        if not folder:
            logger.warning("_on_scanning_finished: no current directory set")
            return

        # List images in the folder
        root_imgs = sorted(
            p for p in self._safe_list(folder)
            if p.is_file() and p.suffix.lower() in self.EXTS
        )
        if root_imgs:
            self._add_collapsible_node(os.path.basename(folder), folder, root_imgs)

        self.scanner_thread = None  # Clean up reference
    except Exception as e:
        logger.exception("_on_scanning_finished failed: %s", e)
def _stop_scanner_thread(self):
    logger.info("_stop_scanner_thread")
    try:
        t = getattr(self, "scanner_thread", None)
        if t and t.isRunning():
            t.requestInterruption()
            t.quit()
            t.wait(5000)
        self.scanner_thread = None
    except Exception as e:
        print(f"{e}")  
def _add_collapsible_node(self, title, dirpath: Path, imgs):
    logger.info("_add_collapsible_node")
    try:
        node = QtWidgets.QTreeWidgetItem(self.thumb_tree)
        
        node.setData(0, QtCore.Qt.ItemDataRole.UserRole, {"dir": str(dirpath), "loaded": False})

        # Build a light collapsed preview strip (icons; no full-size decode)
        cont = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(cont)
        hl.setContentsMargins(2, 2, 2, 2)
        hl.setSpacing(4)

        lbl = QtWidgets.QLabel(f"<b>{title}</b>")
        hl.addWidget(lbl)

        preview_cap = 100  # keep it snappy
        for img in imgs[:preview_cap]:
            thumb = QtWidgets.QLabel()
            thumb.setFixedSize(self.collapsed_thumb_size, self.collapsed_thumb_size)
            thumb.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            thumb.setStyleSheet("border:1px solid #ccc; background:#eee;")
            icon = QtGui.QIcon(str(img))
            pm = icon.pixmap(self.collapsed_thumb_size, self.collapsed_thumb_size)
            thumb.setPixmap(pm)
            thumb.setProperty("path", str(img))
            thumb.mousePressEvent = (lambda ev, p=str(img): self._show_from_thumb(p))
            hl.addWidget(thumb)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        self.expanded_scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.expanded_scroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setWidget(cont)
        scroll.setFixedHeight(self.collapsed_thumb_size + 20)

        self.thumb_tree.setItemWidget(node, 0, scroll)
    except Exception as e:
        print(f"{e}")
def on_item_expanded(self, item):
    logger.info("on_item_expanded")
    data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
    

    # Only parent nodes (dict payload) are expandable. Children carry a string path.
    if not isinstance(data, dict):
        return

    if data.get("loaded"):
        return

    dir_path = Path(data.get("dir", ""))
    if not dir_path.exists():
        data["loaded"] = True
        item.setData(0, QtCore.Qt.ItemDataRole.UserRole, data)
        return

    try:
        pics = sorted(
            p for p in dir_path.iterdir()
            if p.is_file() and p.suffix.lower() in self.EXTS
        )
    except Exception:
        logger.exception("Failed to list %s", dir_path)
        pics = []

    for img in pics:
        ch = QtWidgets.QTreeWidgetItem(item)
        ch.setText(0, img.name)
        ch.setIcon(0, QtGui.QIcon(str(img)))  # cheap icon; avoids full decode
        ch.setData(0, QtCore.Qt.ItemDataRole.UserRole, str(img))

    # Remove the heavy inline preview widget once expanded
    self.thumb_tree.setItemWidget(item, 0, None)

    data["loaded"] = True
    item.setData(0, QtCore.Qt.ItemDataRole.UserRole, data)

def on_tree_thumb_clicked(self, item, _):
    logger.info("on_tree_thumb_clicked")
    try:
        val = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
       
        if isinstance(val, str):
            self._show_image(val)
            self._select_index(val)
    except Exception as e:
        print(f"{e}")
# ─── Expanded strip ────────────────────────────────────────────
def _populate_expanded_strip(self, folder: Path):
    logger.info("_populate_expanded_strip")
    try:
        # clear existing widgets
        for i in reversed(range(self.expanded_layout.count())):
            w = self.expanded_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        try:
            imgs = sorted(
                p for p in folder.iterdir()
                if p.is_file() and p.suffix.lower() in self.EXTS
            )
        except Exception:
            logger.exception("iterdir failed for %s", folder)
            imgs = []

        self.current_images = [str(p) for p in imgs]
        self.current_index = 0

        for path in self.current_images:
            lbl = QtWidgets.QLabel()
            lbl.setFixedSize(self.expanded_thumb_size, self.expanded_thumb_size)
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("border:1px solid #ccc; background:#eee;")
            icon = QtGui.QIcon(path)
            pm = icon.pixmap(self.expanded_thumb_size, self.expanded_thumb_size)
            if not pm.isNull():
                lbl.setPixmap(pm)
            lbl.setProperty("path", path)
            lbl.mousePressEvent = (lambda ev, p=path: self._show_image(p))
            self.expanded_layout.addWidget(lbl)

        if self.current_images:
            self._show_image(self.current_images[0])
    except Exception as e:
        print(f"{e}")
# ─── Image viewing helpers ─────────────────────────────────────
def _show_from_thumb(self, path: str):
    logger.info("_show_from_thumb")
    try:
        self._select_index(path)

        
        self._show_image(path)
    except Exception as e:
        print(f"{e}")
def _select_index(self, path: str):
        logger.info("_select_index")
        try:
            
            self.current_index = self.current_images.index(path)
        except ValueError:
            self.current_index = 0
        except Exception as e:
            print(f"{e}")
def _show_image(self, path: str):
    # store last path for resize redraw
    logger.info("_show_image")
    try:
        self._last_image = path
        pm = QtGui.QPixmap(path)
        if not pm.isNull():
            self.image_preview.setPixmap(
                pm.scaled(self.image_preview.size(),
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                          QtCore.Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.image_preview.setText("Failed to load image")
    except Exception as e:
        print(f"{e}")
# ─── Slideshow / navigation ────────────────────────────────────
def next_image(self):
    logger.info("next_image")
    try:
        if not self.current_images:
            return
        
        self.current_index = (self.current_index + 1) % len(self.current_images)
        self._show_image(self.current_images[self.current_index])
    except Exception as e:
        print(f"{e}")
def prev_image(self):
    logger.info("prev_image")
    try:
        if not self.current_images:
            return
        
        self.current_index = (self.current_index - 1) % len(self.current_images)
        self._show_image(self.current_images[self.current_index])
    except Exception as e:
        print(f"{e}")
def toggle_slideshow(self):
    logger.info("toggle_slideshow")
    for directory,files in self.DIRS_JS.items():
        if directory and files:
           
            self._add_collapsible_node_threaded(os.path.basename(directory), directory, files)
           
##    try:
##        if self.slideshow_timer.isActive():
##            logger.info("toggle_slideshow")
##            self.slideshow_timer.stop()
##            self.play_btn.setText("▶ Play")
##        else:
##            self.slideshow_timer.start()
##            self.play_btn.setText("⏸ Pause")
##    except Exception as e:
##        print(f"{e}")
# ─── Open folder ───────────────────────────────────────────────
def open_folder(self):
    logger.info("open_folder")
    try:
        if self.current_dir:
            logger.info("open_folder")
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.current_dir)))
    except Exception as e:
        print(f"{e}")
# ─── Renaming / undo ───────────────────────────────────────────
def undo_last_renaming(self):
    logger.info("undo_last_renaming")
    try:
        idx = self.tree.currentIndex()
        logger.info("undo_last_renaming")
        folder = Path(self.model.filePath(idx))
        log = folder / "rename_log.json"
        if not log.exists():
            QtWidgets.QMessageBox.warning(self, "Undo Failed", "No rename log found.")
            return
        try:
            mapping = json.loads(log.read_text(encoding='utf-8'))
            for new, old in mapping.items():
                pnew = folder / new
                pold = folder / old
                if pnew.exists():
                    pnew.rename(pold)
            log.unlink()
            QtWidgets.QMessageBox.information(self, "Undo Complete", "Restored names.")
            self.on_folder_selected(idx)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Undo Error", str(e))
    except Exception as e:
        print(f"{e}")
def _renumber_images(self, folder: Path):
    logger.info("_renumber_images")
    try:
        if not self.renumber_cb.isChecked():
            return
        logger.info("_renumber_images")
        imgs = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in self.EXTS)
        prefix = (self.prefix_inp.text().strip() if self.prefix_cb.isChecked() else "") or folder.name
        log = {}
        for i, old in enumerate(imgs, 1):
            num = f"{i:03d}"
            new = f"{prefix}_{num}{old.suffix.lower()}"
            pnew = folder / new
            if old.name != new:
                try:
                    old.rename(pnew)
                    log[new] = old.name
                except Exception:
                    pass
        if log:
            (folder / "rename_log.json").write_text(json.dumps(log, indent=2), encoding='utf-8')
            QtWidgets.QMessageBox.information(self, "Renamed", f"Renamed {len(log)} files.")
    except Exception as e:
        print(f"{e}")
    
