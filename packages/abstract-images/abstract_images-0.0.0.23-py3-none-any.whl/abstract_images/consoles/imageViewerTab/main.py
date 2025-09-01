from .imports import *
from .initFuncs import initFuncs
class imageViewerTab(QtWidgets.QWidget):
    SLIDESHOW_INTERVAL_MS = 2000
    
        
    def __init__(self,defaultRoot=None,mapPath=None):
        super().__init__()

        try:

            logger.info("__init__")
            self.setWindowTitle("Directory Image Viewer")
            self.resize(1200, 900)
            self.defaultRoot = defaultRoot
            self.mapPath = mapPath
            self.EXTS = EXTS
            self.DIRS_JS= get_dirs_js(self.defaultRoot,defaultRoot=self.defaultRoot,mapPath=self.mapPath)
        except Exception as e:
            print(f"{e}")
        try:

            # state
            self.current_dir = self.defaultRoot
            self.current_images = []
            self.current_index = -1
            self.slideshow_timer = QtCore.QTimer(self)
            self.slideshow_timer.setInterval(self.SLIDESHOW_INTERVAL_MS)
            self.slideshow_timer.timeout.connect(self.next_image)
            self.displayed_directories=set()
        except Exception as e:
            print(f"{e}")
        try:

            # adjustable sizes
            self.main_size = QtCore.QSize(800, 450)
            self.collapsed_thumb_size = 128
            self.expanded_thumb_size = 256
            self.displayed_directories=set()
        except Exception as e:
            print(f"{e}")
        try:

            # ─── Left: folder tree ────────────────────────────────────────
            self.tree = QtWidgets.QTreeView()
            self.model = QtGui.QFileSystemModel()
            self.model.setRootPath(self.defaultRoot)
            self.model.setFilter(
                QtCore.QDir.Filter.NoDotAndDotDot | QtCore.QDir.Filter.AllDirs
            )
            
            self.tree.setModel(self.model)
            for c in range(1, self.model.columnCount()):
                self.tree.setColumnHidden(c, True)
            self.tree.clicked.connect(self.on_folder_selected)
        except Exception as e:
            print(f"{e}")
        try:
            
            # Main image
            self.image_preview = QtWidgets.QLabel("Select an image", alignment=Qt.AlignmentFlag.AlignCenter)
            self.image_preview.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            self.image_preview.setMinimumSize(100, 100)
        except Exception as e:
            print(f"{e}")
        try:

            # Prev / Next / Play-Pause / Open Folder buttons
            btn_bar = QtWidgets.QWidget()
            hb = QtWidgets.QHBoxLayout(btn_bar)
            hb.setContentsMargins(0, 0, 0, 0)
            self.prev_btn = QtWidgets.QPushButton("◀ Prev")
            self.play_btn = QtWidgets.QPushButton("▶ Play")
            self.next_btn = QtWidgets.QPushButton("Next ▶")
            self.open_btn = QtWidgets.QPushButton("📂 Open Folder")
            for w in (self.prev_btn, self.play_btn, self.next_btn, self.open_btn):
                hb.addWidget(w)
            hb.addStretch()
            self.prev_btn.clicked.connect(self.prev_image)
            self.play_btn.clicked.connect(self.toggle_slideshow)
            self.next_btn.clicked.connect(self.next_image)
            self.open_btn.clicked.connect(self.open_folder)
        except Exception as e:
            print(f"{e}")
        try:

            # Expanded strip
            self.expanded_container = QtWidgets.QWidget()
            self.expanded_layout = QtWidgets.QVBoxLayout(self.expanded_container)
            self.expanded_layout.setContentsMargins(2, 2, 2, 2)
            self.expanded_layout.setSpacing(4)
            self.expanded_scroll = QtWidgets.QScrollArea()
            self.expanded_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.expanded_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.expanded_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            self.expanded_scroll.setWidget(self.expanded_container)
            self.expanded_scroll.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        except Exception as e:
            print(f"{e}")
        try:

            # Collapsible tree of folders (thumbnails in collapsed rows)
            self.thumb_tree = QtWidgets.QTreeWidget()
            self.thumb_tree.setHeaderHidden(True)
            self.thumb_tree.setIconSize(QtCore.QSize(self.expanded_thumb_size, self.expanded_thumb_size))
            self.thumb_tree.itemClicked.connect(self.on_tree_thumb_clicked)
            self.thumb_tree.itemExpanded.connect(self.on_item_expanded)
            self.thumb_tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.thumb_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.thumb_tree.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            self.thumb_tree.setMinimumHeight(100)
        except Exception as e:
            print(f"{e}")
        try:

            # Renaming controls
            self.renumber_cb = QtWidgets.QCheckBox("Enable Renumbering")
            self.prefix_cb   = QtWidgets.QCheckBox("Use Prefix")
            self.prefix_inp  = QtWidgets.QLineEdit()
            self.prefix_inp.setPlaceholderText("Prefix (defaults to folder name)")
            self.prefix_inp.setEnabled(False)
            self.prefix_cb.stateChanged.connect(
                lambda s: self.prefix_inp.setEnabled(s == QtCore.Qt.Checked)
            )
            self.undo_btn = QtWidgets.QPushButton("Undo Renaming")
            self.undo_btn.clicked.connect(self.undo_last_renaming)
        except Exception as e:
            print(f"{e}")
        try:

            # Sizes panel
            size_group = QtWidgets.QGroupBox("Display Sizes")
            form = QtWidgets.QFormLayout()
            self.main_w_spin = QtWidgets.QSpinBox(); self.main_w_spin.setRange(100, 2000)
            self.main_h_spin = QtWidgets.QSpinBox(); self.main_h_spin.setRange(100, 2000)
            self.main_w_spin.setValue(self.main_size.width()); self.main_h_spin.setValue(self.main_size.height())
            self.main_w_spin.valueChanged.connect(self._on_main_size_changed)
            self.main_h_spin.valueChanged.connect(self._on_main_size_changed)
            self.collapsed_spin = QtWidgets.QSpinBox(); self.collapsed_spin.setRange(16, 512)
            self.collapsed_spin.setValue(self.collapsed_thumb_size)
            self.collapsed_spin.valueChanged.connect(self._on_collapsed_changed)
            self.expanded_spin = QtWidgets.QSpinBox(); self.expanded_spin.setRange(16, 512)
            self.expanded_spin.setValue(self.expanded_thumb_size)
            self.expanded_spin.valueChanged.connect(self._on_expanded_changed)
            form.addRow("Main width:", self.main_w_spin)
            form.addRow("Main height:", self.main_h_spin)
            form.addRow("Collapsed thumb:", self.collapsed_spin)
            form.addRow("Expanded thumb:", self.expanded_spin)
            size_group.setLayout(form)
        except Exception as e:
            print(f"{e}")
        try:

            # Layout right panel
            right_v = QtWidgets.QVBoxLayout()
            right_v.addWidget(self.image_preview)
            right_v.addWidget(btn_bar)
            right_v.addWidget(self.thumb_tree, 1)
        except Exception as e:
            print(f"{e}")
        try:

            # ── Collapsible Options (hidden by default) ─────────────────
            self.options_toggle = QtWidgets.QToolButton(text="Options")
            self.options_toggle.setCheckable(True)
            self.options_toggle.setChecked(False)
            self.options_toggle.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.options_toggle.setArrowType(QtCore.Qt.ArrowType.RightArrow)
        except Exception as e:
            print(f"{e}")
        try:

            self.options_panel = QtWidgets.QWidget()
            opt_v = QtWidgets.QVBoxLayout(self.options_panel)
            opt_v.setContentsMargins(6, 6, 6, 6)
            opt_v.setSpacing(6)
            for w in (self.renumber_cb, self.prefix_cb, self.prefix_inp, self.undo_btn, size_group):
                opt_v.addWidget(w)
            self.options_panel.setVisible(False)
        except Exception as e:
            print(f"{e}")
       

        try:

            self.options_toggle.toggled.connect(self._toggle_opts)

            right_v.addWidget(self.options_toggle)
            right_v.addWidget(self.options_panel)
       
            # preview + thumbs get the space, options stay compact
            right_v.setStretch(0, 6)   # image_preview
            right_v.setStretch(1, 0)   # buttons
            right_v.setStretch(2, 8)   # folder thumbs (thumb_tree)
            right_v.setStretch(3, 0)   # options toggle
            right_v.setStretch(4, 0)   # options panel (hidden by default)
            # (indices shifted down because expanded strip was removed)

            right_w = QtWidgets.QWidget()
            right_w.setLayout(right_v)

            # Main splitter
            splitter = QtWidgets.QSplitter()
            splitter.addWidget(self.tree)
            splitter.addWidget(right_w)
            # favor the right pane (preview) by default
            splitter.setStretchFactor(0, 1)
            splitter.setStretchFactor(1, 3)
            splitter.setSizes([300, 900])
            main_l = QtWidgets.QHBoxLayout(self)
            main_l.addWidget(splitter)
            self.load_all_thread = self.load_all_directories_async

            self.load_all_thread.start()
        except Exception as e:
            print(f"{e}")
        try:
            
            
            
            self._threads: list[QtCore.QThread] = []   # keep strong refs
            self._active_workers: list[DirScanWorker] = []
        except Exception as e:
            print(f"{e}")
    def _toggle_opts(self,checked):
                

                try:
                        self.options_panel.setVisible(checked)
                        self.options_toggle.setArrowType(QtCore.Qt.ArrowType.DownArrow if checked else QtCore.Qt.ArrowType.RightArrow)
                except Exception as e:
                    print(f"{e}")
imageViewerTab = initFuncs(imageViewerTab)

