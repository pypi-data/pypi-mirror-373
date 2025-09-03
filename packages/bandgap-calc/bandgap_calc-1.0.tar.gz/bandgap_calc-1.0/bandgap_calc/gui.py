import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QFileDialog,
    QSlider, QColorDialog, QGroupBox, QMessageBox, QCheckBox,
    QMainWindow, QAction, QTabWidget, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

# Set up a professional, publication-quality Matplotlib style
plt.style.use('default')  # Use default style as a clean base
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['axes.labelweight'] = 'normal'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['grid.color'] = '#dddddd'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['axes.edgecolor'] = '#555555'


class TaucPlotGUI(QMainWindow):
    """
    A PyQt5-based GUI for performing Tauc plot analysis on UV-Vis data.
    This tool allows users to load data, adjust plot parameters,
    interactively fit a line to the plot, and export the result.
    """

    def __init__(self):
        super().__init__()

        # Initialize key variables for data and plotting
        self.wavelength = None
        self.absorbance = None
        self.transmittance = None
        self.E = None
        self.y = None

        # Initialize default colors for all plots and fit line
        self.abs_color = "#4CAF50"  # Absorbance plot color
        self.trans_color = "#FFC107"  # Transmittance plot color
        self.tauc_color = "#336699"  # Tauc plot color
        self.fit_color = "#E54F3D"  # Fit line color

        self.dragging = False
        self.dragged_point = None
        self.fit_line = None
        self.fit_line_data_x = None
        self.fit_line_data_y = None
        self.model = None

        # Store the current bandgap type and wavelength range to detect changes
        self.current_bandgap_type = None
        self.current_wavelength_range = (None, None)
        self.user_adjusted_fit = False  # Track if user has manually adjusted the fit

        self.setWindowTitle("App Developed by ABNX Lab: Bandgap-Calc V 1.0")
        self.setGeometry(100, 100, 1400, 800)
        self.create_menu()
        self.init_ui()

    def create_menu(self):
        """Create the main menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        load_action = QAction('Load Data', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_data)
        file_menu.addAction(load_action)

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        self.abs_action = QAction('Show Absorbance Plot', self, checkable=True)
        self.abs_action.setChecked(True)
        self.abs_action.triggered.connect(self.toggle_abs_plot)
        view_menu.addAction(self.abs_action)

        self.trans_action = QAction('Show Transmittance Plot', self, checkable=True)
        self.trans_action.setChecked(True)
        self.trans_action.triggered.connect(self.toggle_trans_plot)
        view_menu.addAction(self.trans_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def toggle_abs_plot(self, state):
        """Toggle absorbance plot visibility."""
        if hasattr(self, 'abs_checkbox'):
            self.abs_checkbox.setChecked(state)
            self.update_plot()

    def toggle_trans_plot(self, state):
        """Toggle transmittance plot visibility."""
        if hasattr(self, 'trans_checkbox'):
            self.trans_checkbox.setChecked(state)
            self.update_plot()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Tauc Plot Analyzer",
                          "Tauc Plot Analyzer\n\n"
                          "A tool for analyzing UV-Vis data and calculating band gap energy using Tauc plot methodology.\n\n"
                          "For any assistance please contact: advancedbionanoxplore@gmail.com\n\n"
                          "Visit our site: https://abnxlab.com/"
                          "Version 1.0.0")

    def init_ui(self):
        """
        Sets up the main layout and widgets of the GUI.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)

        # Create a tab widget for controls
        self.tabs = QTabWidget()
        self.tabs.setMaximumWidth(400)
        self.main_layout.addWidget(self.tabs, 1)

        # Add tabs
        self.tabs.addTab(self.create_data_tab(), "Data")
        self.tabs.addTab(self.create_plot_tab(), "Plot Settings")
        self.tabs.addTab(self.create_style_tab(), "Styling")
        self.tabs.addTab(self.create_export_tab(), "Export")

        # Right-side plot canvas, using a grid for multiple plots
        plot_container = QWidget()
        plot_layout = QVBoxLayout(plot_container)

        self.canvas_figure = Figure(figsize=(8, 6), dpi=120, facecolor='white', constrained_layout=True)
        self.canvas = Canvas(self.canvas_figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a grid of subplots
        gs = self.canvas_figure.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1, 1], hspace=0.3, wspace=0.3)
        self.ax_abs = self.canvas_figure.add_subplot(gs[0, 0], facecolor='#f7f7f7')
        self.ax_trans = self.canvas_figure.add_subplot(gs[0, 1], facecolor='#f7f7f7')
        self.ax_tauc = self.canvas_figure.add_subplot(gs[1, :], facecolor='#f7f7f7')  # Tauc plot spans both columns

        plot_layout.addWidget(self.canvas)

        # Add the bandgap label at the bottom with updated styling
        self.bandgap_label = QLabel("Estimated Band Gap: -- eV")
        self.bandgap_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #36a2eb; padding: 10px;")
        plot_layout.addWidget(self.bandgap_label)

        self.main_layout.addWidget(plot_container, 3)

        # Connect mouse events for interactive fit adjustment, specifically on the Tauc plot axis
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    def create_data_tab(self):
        """Creates the data tab with file loading options."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Data loading
        data_group = QGroupBox("Data Controls")
        data_layout = QVBoxLayout()
        load_btn = QPushButton("Load UV-Vis CSV")
        load_btn.clicked.connect(self.load_data)
        data_layout.addWidget(load_btn)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Wavelength range
        range_group = QGroupBox("Wavelength Range")
        range_layout = QFormLayout()
        self.min_wl_input = QLineEdit()
        self.max_wl_input = QLineEdit()
        self.step_wl_input = QLineEdit()  # Default step size
        self.min_wl_input.editingFinished.connect(self.update_plot)
        self.max_wl_input.editingFinished.connect(self.update_plot)
        self.step_wl_input.editingFinished.connect(self.update_plot)
        range_layout.addRow("Min WL (nm):", self.min_wl_input)
        range_layout.addRow("Max WL (nm):", self.max_wl_input)
        range_layout.addRow("Step Size:", self.step_wl_input)
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)

        # Energy range for Tauc plot
        energy_group = QGroupBox("Tauc Plot Energy Range")
        energy_layout = QFormLayout()
        self.min_energy_input = QLineEdit()
        self.max_energy_input = QLineEdit()
        self.min_energy_input.editingFinished.connect(self.update_plot)
        self.max_energy_input.editingFinished.connect(self.update_plot)
        energy_layout.addRow("Min Energy (eV):", self.min_energy_input)
        energy_layout.addRow("Max Energy (eV):", self.max_energy_input)
        energy_group.setLayout(energy_layout)
        layout.addWidget(energy_group)

        layout.addStretch()
        return tab

    def create_plot_tab(self):
        """Creates the plot settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Transition type
        mode_group = QGroupBox("Bandgap Type")
        mode_layout = QVBoxLayout()
        self.mode_box = QComboBox()
        self.mode_box.addItems(["Direct", "Indirect"])
        self.mode_box.currentTextChanged.connect(self.update_plot)
        mode_layout.addWidget(QLabel("Transition Type:"))
        mode_layout.addWidget(self.mode_box)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Plot visibility toggles
        visibility_group = QGroupBox("Plot Visibility")
        visibility_layout = QVBoxLayout()
        self.abs_checkbox = QCheckBox("Show Absorbance Plot")
        self.abs_checkbox.setChecked(True)
        self.abs_checkbox.stateChanged.connect(self.update_plot)

        self.trans_checkbox = QCheckBox("Show Transmittance Plot")
        self.trans_checkbox.setChecked(True)
        self.trans_checkbox.stateChanged.connect(self.update_plot)

        visibility_layout.addWidget(self.abs_checkbox)
        visibility_layout.addWidget(self.trans_checkbox)
        visibility_group.setLayout(visibility_layout)
        layout.addWidget(visibility_group)

        # Axis ranges
        axis_group = QGroupBox("Axis Ranges")
        axis_layout = QFormLayout()

        # Absorbance Y-axis range
        self.min_abs_y_input = QLineEdit()
        self.max_abs_y_input = QLineEdit()
        self.min_abs_y_input.editingFinished.connect(self.update_plot)
        self.max_abs_y_input.editingFinished.connect(self.update_plot)
        axis_layout.addRow("Absorbance Min Y:", self.min_abs_y_input)
        axis_layout.addRow("Absorbance Max Y:", self.max_abs_y_input)

        # Transmittance Y-axis range
        self.min_trans_y_input = QLineEdit()
        self.max_trans_y_input = QLineEdit()
        self.min_trans_y_input.editingFinished.connect(self.update_plot)
        self.max_trans_y_input.editingFinished.connect(self.update_plot)
        axis_layout.addRow("Transmittance Min Y:", self.min_trans_y_input)
        axis_layout.addRow("Transmittance Max Y:", self.max_trans_y_input)

        axis_group.setLayout(axis_layout)
        layout.addWidget(axis_group)

        # Y-axis labels customization
        labels_group = QGroupBox("Y-Axis Labels")
        labels_layout = QFormLayout()

        self.abs_ylabel_input = QLineEdit("Absorbance (a.u.)")
        self.abs_ylabel_input.editingFinished.connect(self.update_plot)
        labels_layout.addRow("Absorbance Y-label:", self.abs_ylabel_input)

        self.trans_ylabel_input = QLineEdit("Transmittance (%)")
        self.trans_ylabel_input.editingFinished.connect(self.update_plot)
        labels_layout.addRow("Transmittance Y-label:", self.trans_ylabel_input)

        labels_group.setLayout(labels_layout)
        layout.addWidget(labels_group)

        # Display options
        options_group = QGroupBox("Display Options")
        options_layout = QVBoxLayout()
        self.hide_y_labels_checkbox = QCheckBox("Hide Y-Axis Labels")
        self.hide_y_labels_checkbox.setChecked(False)
        self.hide_y_labels_checkbox.stateChanged.connect(self.update_plot)

        self.hide_abs_title_checkbox = QCheckBox("Hide Absorbance Title")
        self.hide_abs_title_checkbox.setChecked(False)
        self.hide_abs_title_checkbox.stateChanged.connect(self.update_plot)

        self.hide_trans_title_checkbox = QCheckBox("Hide Transmittance Title")
        self.hide_trans_title_checkbox.setChecked(False)
        self.hide_trans_title_checkbox.stateChanged.connect(self.update_plot)

        self.hide_tauc_title_checkbox = QCheckBox("Hide Tauc Title")
        self.hide_tauc_title_checkbox.setChecked(False)
        self.hide_tauc_title_checkbox.stateChanged.connect(self.update_plot)

        # Add grid options
        self.grid_abs_checkbox = QCheckBox("Show Grid in Absorbance Plot")
        self.grid_abs_checkbox.setChecked(False)
        self.grid_abs_checkbox.stateChanged.connect(self.update_plot)

        self.grid_trans_checkbox = QCheckBox("Show Grid in Transmittance Plot")
        self.grid_trans_checkbox.setChecked(False)
        self.grid_trans_checkbox.stateChanged.connect(self.update_plot)

        self.grid_tauc_checkbox = QCheckBox("Show Grid in Tauc Plot")
        self.grid_tauc_checkbox.setChecked(False)
        self.grid_tauc_checkbox.stateChanged.connect(self.update_plot)

        options_layout.addWidget(self.hide_y_labels_checkbox)
        options_layout.addWidget(self.hide_abs_title_checkbox)
        options_layout.addWidget(self.hide_trans_title_checkbox)
        options_layout.addWidget(self.hide_tauc_title_checkbox)
        options_layout.addWidget(self.grid_abs_checkbox)
        options_layout.addWidget(self.grid_trans_checkbox)
        options_layout.addWidget(self.grid_tauc_checkbox)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        layout.addStretch()
        return tab

    def create_style_tab(self):
        """Creates the styling tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Line widths
        width_group = QGroupBox("Line Widths")
        width_layout = QFormLayout()

        self.abs_width_slider = QSlider(Qt.Horizontal)
        self.abs_width_slider.setRange(1, 10)
        self.abs_width_slider.setValue(2)
        self.abs_width_slider.valueChanged.connect(self.update_plot)
        width_layout.addRow("Absorbance:", self.abs_width_slider)

        self.trans_width_slider = QSlider(Qt.Horizontal)
        self.trans_width_slider.setRange(1, 10)
        self.trans_width_slider.setValue(2)
        self.trans_width_slider.valueChanged.connect(self.update_plot)
        width_layout.addRow("Transmittance:", self.trans_width_slider)

        self.tauc_width_slider = QSlider(Qt.Horizontal)
        self.tauc_width_slider.setRange(1, 10)
        self.tauc_width_slider.setValue(2)
        self.tauc_width_slider.valueChanged.connect(self.update_plot)
        width_layout.addRow("Tauc Plot:", self.tauc_width_slider)

        self.fit_width_slider = QSlider(Qt.Horizontal)
        self.fit_width_slider.setRange(1, 10)
        self.fit_width_slider.setValue(2)
        self.fit_width_slider.valueChanged.connect(self.update_plot)
        width_layout.addRow("Fit Line:", self.fit_width_slider)
        width_group.setLayout(width_layout)
        layout.addWidget(width_group)

        # Font sizes
        font_group = QGroupBox("Font Sizes")
        font_layout = QFormLayout()

        self.title_size_slider = QSlider(Qt.Horizontal)
        self.title_size_slider.setRange(8, 24)
        self.title_size_slider.setValue(16)
        self.title_size_slider.valueChanged.connect(self.update_plot)
        font_layout.addRow("Title:", self.title_size_slider)

        self.label_size_slider = QSlider(Qt.Horizontal)
        self.label_size_slider.setRange(8, 24)
        self.label_size_slider.setValue(14)
        self.label_size_slider.valueChanged.connect(self.update_plot)
        font_layout.addRow("Label:", self.label_size_slider)

        self.legend_size_slider = QSlider(Qt.Horizontal)
        self.legend_size_slider.setRange(8, 24)
        self.legend_size_slider.setValue(12)
        self.legend_size_slider.valueChanged.connect(self.update_plot)
        font_layout.addRow("Legend:", self.legend_size_slider)

        self.tick_size_slider = QSlider(Qt.Horizontal)
        self.tick_size_slider.setRange(8, 24)
        self.tick_size_slider.setValue(12)
        self.tick_size_slider.valueChanged.connect(self.update_plot)
        font_layout.addRow("Tick:", self.tick_size_slider)
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        # Colors
        color_group = QGroupBox("Colors")
        color_layout = QVBoxLayout()

        self.abs_color_btn = QPushButton("Choose Absorbance Color")
        self.abs_color_btn.clicked.connect(self.pick_abs_color)
        color_layout.addWidget(self.abs_color_btn)

        self.trans_color_btn = QPushButton("Choose Transmittance Color")
        self.trans_color_btn.clicked.connect(self.pick_trans_color)
        color_layout.addWidget(self.trans_color_btn)

        self.tauc_color_btn = QPushButton("Choose Tauc Plot Color")
        self.tauc_color_btn.clicked.connect(self.pick_tauc_color)
        color_layout.addWidget(self.tauc_color_btn)

        self.fit_color_btn = QPushButton("Choose Fit Line Color")
        self.fit_color_btn.clicked.connect(self.pick_fit_color)
        color_layout.addWidget(self.fit_color_btn)
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        layout.addStretch()
        return tab

    def create_export_tab(self):
        """Creates the export tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        format_group = QGroupBox("Export Format")
        format_layout = QHBoxLayout()
        self.format_box = QComboBox()
        self.format_box.addItems(["png", "jpg", "jpeg", "pdf", "svg", "eps", "tiff"])
        format_layout.addWidget(QLabel("Select Format:"))
        format_layout.addWidget(self.format_box)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Add a separate button for each plot
        self.save_abs_btn = QPushButton("Save Absorbance Plot")
        self.save_abs_btn.clicked.connect(lambda: self.export_plot('absorbance'))
        layout.addWidget(self.save_abs_btn)

        self.save_trans_btn = QPushButton("Save Transmittance Plot")
        self.save_trans_btn.clicked.connect(lambda: self.export_plot('transmittance'))
        layout.addWidget(self.save_trans_btn)

        self.save_tauc_btn = QPushButton("Save Tauc Plot")
        self.save_tauc_btn.clicked.connect(lambda: self.export_plot('tauc'))
        layout.addWidget(self.save_tauc_btn)

        layout.addStretch()
        return tab

    def pick_abs_color(self):
        """Opens a color dialog to choose the absorbance plot line color."""
        color = QColorDialog.getColor(QColor(self.abs_color), self, "Choose Absorbance Plot Color")
        if color.isValid():
            self.abs_color = color.name()
            self.update_plot()

    def pick_trans_color(self):
        """Opens a color dialog to choose the transmittance plot line color."""
        color = QColorDialog.getColor(QColor(self.trans_color), self, "Choose Transmittance Plot Color")
        if color.isValid():
            self.trans_color = color.name()
            self.update_plot()

    def pick_tauc_color(self):
        """Opens a color dialog to choose the Tauc plot line color."""
        color = QColorDialog.getColor(QColor(self.tauc_color), self, "Choose Tauc Plot Color")
        if color.isValid():
            self.tauc_color = color.name()
            self.update_plot()

    def pick_fit_color(self):
        """Opens a color dialog to choose the fit line color."""
        color = QColorDialog.getColor(QColor(self.fit_color), self, "Choose Fit Line Color")
        if color.isValid():
            self.fit_color = color.name()
            self.update_plot()

    def load_data(self):
        """
        Loads data from a selected CSV file, assuming the first column
        is wavelength and the second is absorbance.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Open UV-Vis CSV File", "", "CSV Files (*.csv)")
        if path:
            try:
                df = pd.read_csv(path)
                self.wavelength = df.iloc[:, 0].values
                self.absorbance = df.iloc[:, 1].values
                # Calculate transmittance immediately after loading data
                self.transmittance = np.exp(-2.303 * self.absorbance) * 100

                # Reset fit line when new data is loaded
                self.fit_line_data_x = None
                self.fit_line_data_y = None
                self.user_adjusted_fit = False
                self.current_bandgap_type = None
                self.current_wavelength_range = (None, None)

                # Set default wavelength range
                self.min_wl_input.setText(str(self.wavelength.min()))
                self.max_wl_input.setText(str(self.wavelength.max()))

                # Calculate and set default energy range
                E_min = 1240 / self.wavelength.max()
                E_max = 1240 / self.wavelength.min()
                self.min_energy_input.setText(f"{E_min:.2f}")
                self.max_energy_input.setText(f"{E_max:.2f}")

                self.update_plot()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

    def update_plot(self):
        """
        Recalculates and redraws the plots based on user input.
        This function is called whenever a control is changed.
        """
        if self.wavelength is None:
            return

        # --- Data Filtering based on wavelength range ---
        try:
            min_wl = float(self.min_wl_input.text()) if self.min_wl_input.text() else self.wavelength.min()
            max_wl = float(self.max_wl_input.text()) if self.max_wl_input.text() else self.wavelength.max()
            step_wl = float(self.step_wl_input.text()) if self.step_wl_input.text() else 1
        except ValueError:
            self.bandgap_label.setText("Estimated Band Gap: Invalid Range")
            return

        # Check if we need to recalculate the fit line
        current_bandgap_type = self.mode_box.currentText()
        current_wavelength_range = (min_wl, max_wl)

        # If bandgap type or wavelength range has changed, reset the fit line
        if (current_bandgap_type != self.current_bandgap_type or
                current_wavelength_range != self.current_wavelength_range):
            self.fit_line_data_x = None
            self.fit_line_data_y = None
            self.user_adjusted_fit = False
            self.current_bandgap_type = current_bandgap_type
            self.current_wavelength_range = current_wavelength_range

        # Filter data based on wavelength range (no interpolation)
        mask = (self.wavelength >= min_wl) & (self.wavelength <= max_wl)
        wl_filtered = self.wavelength[mask]
        ab_filtered = self.absorbance[mask]
        trans_filtered = self.transmittance[mask]

        if len(wl_filtered) == 0:
            self.bandgap_label.setText("Estimated Band Gap: No Data")
            for ax in [self.ax_abs, self.ax_trans, self.ax_tauc]:
                ax.clear()
            self.canvas.draw()
            return

        # Calculate Tauc plot parameters for the filtered data
        self.E = 1240 / wl_filtered
        alpha = 2.303 * ab_filtered
        power = 2 if self.mode_box.currentText() == "Direct" else 0.5

        # For indirect bandgap, filter out negative values to avoid sqrt of negative numbers
        if power == 0.5:
            # Only use points where (alpha * self.E) is non-negative
            valid_mask = (alpha * self.E) >= 0
            E_filtered = self.E[valid_mask]
            alpha_filtered = alpha[valid_mask]

            # Check if we have valid data points
            if len(E_filtered) == 0:
                self.bandgap_label.setText("Estimated Band Gap: No Valid Data")
                self.ax_tauc.clear()
                self.canvas.draw()
                return

            self.y = (alpha_filtered * E_filtered) ** power
            self.E = E_filtered  # Update self.E to the filtered values
        else:
            self.y = (alpha * self.E) ** power

        # Apply energy range filter for Tauc plot
        try:
            min_energy = float(self.min_energy_input.text()) if self.min_energy_input.text() else min(self.E)
            max_energy = float(self.max_energy_input.text()) if self.max_energy_input.text() else max(self.E)

            energy_mask = (self.E >= min_energy) & (self.E <= max_energy)
            self.E = self.E[energy_mask]
            self.y = self.y[energy_mask]
        except ValueError:
            pass  # Silently ignore invalid energy range input

        # Only perform automatic linear fit if we don't have a user-adjusted fit
        if not self.user_adjusted_fit and len(self.E) > 0:
            # Perform automatic linear fit on top 20% of the data
            threshold = np.percentile(self.y, 80)
            linear_mask = self.y > threshold
            E_fit = self.E[linear_mask].reshape(-1, 1)
            y_fit = self.y[linear_mask]

            # --- Recalculate and update the linear fit line ---
            if len(E_fit) > 1:
                self.model = LinearRegression().fit(E_fit, y_fit)
                m, c = self.model.coef_[0], self.model.intercept_
                Eg = -c / m

                # Update the bandgap label
                self.bandgap_label.setText(f"Estimated Band Gap: <b>{Eg:.2f} eV</b>")

                # Store initial fit line data for interactive dragging
                self.fit_line_data_x = np.array([Eg, max(self.E)])
                self.fit_line_data_y = np.array([0, self.model.predict(np.array(max(self.E)).reshape(-1, 1))[0]])
            else:
                self.fit_line_data_x = None
                self.fit_line_data_y = None
                self.bandgap_label.setText("Estimated Band Gap: Fit Failed")

        # --- Clear and redraw all plots ---
        self.ax_abs.clear()
        self.ax_trans.clear()
        self.ax_tauc.clear()

        # Get states of new checkboxes
        hide_y_labels = self.hide_y_labels_checkbox.isChecked()
        hide_abs_title = self.hide_abs_title_checkbox.isChecked()
        hide_trans_title = self.hide_trans_title_checkbox.isChecked()
        hide_tauc_title = self.hide_tauc_title_checkbox.isChecked()

        # Apply grid settings
        self.ax_abs.grid(self.grid_abs_checkbox.isChecked())
        self.ax_trans.grid(self.grid_trans_checkbox.isChecked())
        self.ax_tauc.grid(self.grid_tauc_checkbox.isChecked())

        # Get custom Y-axis labels
        abs_ylabel = self.abs_ylabel_input.text() if self.abs_ylabel_input.text() else "Absorbance (a.u.)"
        trans_ylabel = self.trans_ylabel_input.text() if self.trans_ylabel_input.text() else "Transmittance (%)"

        # --- Plot 1: Absorbance vs. Wavelength (if enabled) ---
        if self.abs_checkbox.isChecked():
            self.ax_abs.plot(wl_filtered, ab_filtered, color=self.abs_color, linewidth=self.abs_width_slider.value())
            self.ax_abs.set_xlabel("Wavelength (nm)", fontsize=self.label_size_slider.value())
            self.ax_abs.set_ylabel(abs_ylabel, fontsize=self.label_size_slider.value())

            if not hide_abs_title:
                self.ax_abs.set_title("UV-Vis Absorbance Spectrum", fontsize=self.title_size_slider.value())
            else:
                self.ax_abs.set_title("")

            # Conditionally hide y-axis labels
            if hide_y_labels:
                self.ax_abs.set_yticklabels([])
            else:
                self.ax_abs.tick_params(axis='y', which='both', left=True, labelleft=True)

            # Set custom y-axis limits
            try:
                min_y = float(self.min_abs_y_input.text()) if self.min_abs_y_input.text() else None
                max_y = float(self.max_abs_y_input.text()) if self.max_abs_y_input.text() else None
                self.ax_abs.set_ylim(bottom=min_y, top=max_y)
            except ValueError:
                pass  # Silently ignore invalid input

            # Set x-axis ticks based on step size
            try:
                step = float(self.step_wl_input.text()) if self.step_wl_input.text() else 100
                self.ax_abs.set_xticks(np.arange(min_wl, max_wl + step, step))
            except ValueError:
                pass

        # --- Plot 2: Transmittance vs. Wavelength (if enabled) ---
        if self.trans_checkbox.isChecked():
            self.ax_trans.plot(wl_filtered, trans_filtered, color=self.trans_color,
                               linewidth=self.trans_width_slider.value())
            self.ax_trans.set_xlabel("Wavelength (nm)", fontsize=self.label_size_slider.value())
            self.ax_trans.set_ylabel(trans_ylabel, fontsize=self.label_size_slider.value())

            if not hide_trans_title:
                self.ax_trans.set_title("UV-Vis Transmittance Spectrum", fontsize=self.title_size_slider.value())
            else:
                self.ax_trans.set_title("")

            # Conditionally hide y-axis labels
            if hide_y_labels:
                self.ax_trans.set_yticklabels([])
            else:
                self.ax_trans.tick_params(axis='y', which='both', left=True, labelleft=True)

            # Set custom y-axis limits
            try:
                min_y = float(self.min_trans_y_input.text()) if self.min_trans_y_input.text() else None
                max_y = float(self.max_trans_y_input.text()) if self.max_trans_y_input.text() else None
                self.ax_trans.set_ylim(bottom=min_y, top=max_y)
            except ValueError:
                pass  # Silently ignore invalid input

            # Set x-axis ticks based on step size
            try:
                step = float(self.step_wl_input.text()) if self.step_wl_input.text() else 100
                self.ax_trans.set_xticks(np.arange(min_wl, max_wl + step, step))
            except ValueError:
                pass

        # --- Plot 3: Tauc Plot ---
        if len(self.E) > 0:
            self.ax_tauc.plot(self.E, self.y, label="Tauc Plot", color=self.tauc_color,
                              linewidth=self.tauc_width_slider.value())

        # Redraw the fit line with markers on the endpoints
        if self.fit_line_data_x is not None and len(self.E) > 0:
            self.fit_line, = self.ax_tauc.plot(self.fit_line_data_x, self.fit_line_data_y,
                                               linestyle='--', color=self.fit_color,
                                               linewidth=self.fit_width_slider.value(),
                                               marker='o', markersize=8, markerfacecolor=self.fit_color,
                                               markeredgecolor='white', label="Adjustable Fit Line")

        # Set plot labels, titles, and visual style for Tauc plot
        power = 2 if self.mode_box.currentText() == "Direct" else 0.5

        # Set x-axis label with bold hν (eV)
        self.ax_tauc.set_xlabel(r"$\mathbf{h\nu\ (eV)}$", fontsize=self.label_size_slider.value())

        # Create bold unit labels for Tauc plot y-axis
        if power == 2:
            ylabel = r"$\mathbf{(\alpha h\nu)^2\ (eV^2 cm^{-2})}$"
        else:
            ylabel = r"$\mathbf{(\alpha h\nu)^{1/2}\ (eV^{1/2} cm^{-1/2})}$"

        self.ax_tauc.set_ylabel(ylabel, fontsize=self.label_size_slider.value())

        if not hide_tauc_title:
            self.ax_tauc.set_title("Tauc Plot", fontsize=self.title_size_slider.value())
        else:
            self.ax_tauc.set_title("")

        if len(self.E) > 0:
            self.ax_tauc.set_ylim(bottom=0)
        self.ax_tauc.legend(fontsize=self.legend_size_slider.value())

        # Adjust tick and label colors for all plots
        for ax in [self.ax_abs, self.ax_trans, self.ax_tauc]:
            ax.set_facecolor('#f7f7f7')
            for spine in ax.spines.values():
                spine.set_edgecolor('#555555')
            ax.tick_params(colors='#2b2b2b', labelsize=self.tick_size_slider.value())
            ax.xaxis.label.set_color('#2b2b2b')
            ax.yaxis.label.set_color('#2b2b2b')
            ax.title.set_color('#2b2b2b')

        self.apply_bold_font()
        self.canvas.draw()

    def on_click(self, event):
        """
        Handles the initial mouse button press to start dragging.
        Checks if the click is near either endpoint of the fit line.
        """
        if event.inaxes != self.ax_tauc or not self.fit_line:
            self.dragging = False
            self.dragged_point = None
            return

        x_data, y_data = self.fit_line.get_data()
        x_click, y_click = event.xdata, event.ydata

        # Calculate distance to each endpoint in display coordinates
        # Use a tolerance in pixel space to make it easier to click
        tolerance = 10  # pixels

        start_point_display = self.ax_tauc.transData.transform((x_data[0], y_data[0]))
        end_point_display = self.ax_tauc.transData.transform((x_data[1], y_data[1]))

        click_point_display = (event.x, event.y)

        dist_start = np.linalg.norm(np.array(click_point_display) - np.array(start_point_display))
        dist_end = np.linalg.norm(np.array(click_point_display) - np.array(end_point_display))

        if dist_start <= tolerance and self.fit_line_data_x is not None:
            self.dragging = True
            self.dragged_point = 'start'
        elif dist_end <= tolerance and self.fit_line_data_x is not None:
            self.dragging = True
            self.dragged_point = 'end'
        else:
            self.dragging = False
            self.dragged_point = None

    def on_drag(self, event):
        """
        Handles mouse movement while the button is pressed, moving only the selected endpoint.
        """
        if not self.dragging or event.xdata is None or event.ydata is None or self.dragged_point is None:
            return

        if self.dragged_point == 'start':
            # Update the starting point of the line
            self.fit_line_data_x[0] = event.xdata
            self.fit_line_data_y[0] = event.ydata
        elif self.dragged_point == 'end':
            # Update the ending point of the line
            self.fit_line_data_x[1] = event.xdata
            self.fit_line_data_y[1] = event.ydata

        # Update the plot line with the new data
        self.fit_line.set_data(self.fit_line_data_x, self.fit_line_data_y)
        self.canvas.draw()

    def on_release(self, event):
        """Handles the mouse button release to stop dragging and recalculate."""
        if self.dragging:
            self.dragging = False
            self.dragged_point = None
            self.user_adjusted_fit = True  # Mark that the user has adjusted the fit

            # Recalculate and update the band gap based on the new line position
            x1, x2 = self.fit_line_data_x
            y1, y2 = self.fit_line_data_y

            # Simple linear equation: y = m*x + c
            # We can find m and c from the two points
            if x2 != x1:
                m = (y2 - y1) / (x2 - x1)
                c = y1 - m * x1

                # The band gap is the x-intercept where y = 0
                if m != 0:
                    Eg = -c / m
                    self.bandgap_label.setText(f"Estimated Band Gap: <b>{Eg:.2f} eV</b>")

    def export_plot(self, plot_type):
        """
        Exports a specific plot to a file based on the plot_type argument.
        """
        if self.wavelength is None:
            QMessageBox.warning(self, "Export Error", "No plot to export. Please load data first.")
            return

        file_format = self.format_box.currentText()

        # Choose the axis to export
        if plot_type == 'absorbance':
            ax_to_save = self.ax_abs
            file_name = "Absorbance_Plot"
            if not self.abs_checkbox.isChecked():
                QMessageBox.warning(self, "Export Error", "Absorbance plot is not visible.")
                return
        elif plot_type == 'transmittance':
            ax_to_save = self.ax_trans
            file_name = "Transmittance_Plot"
            if not self.trans_checkbox.isChecked():
                QMessageBox.warning(self, "Export Error", "Transmittance plot is not visible.")
                return
        elif plot_type == 'tauc':
            ax_to_save = self.ax_tauc
            file_name = "Tauc_Plot"
        else:
            return  # Should not happen

        # Temporarily create a new figure with only the selected axis
        temp_fig = Figure(figsize=(8, 6), dpi=120)
        temp_ax = temp_fig.add_subplot(111)

        # Copy the contents of the selected axis
        temp_ax.set_xlabel(ax_to_save.get_xlabel(), fontsize=ax_to_save.xaxis.label.get_fontsize(), fontweight='bold')
        temp_ax.set_ylabel(ax_to_save.get_ylabel(), fontsize=ax_to_save.yaxis.label.get_fontsize(), fontweight='bold')

        # Conditionally set the title based on the state of the original checkbox
        if plot_type == 'absorbance' and not self.hide_abs_title_checkbox.isChecked():
            temp_ax.set_title("UV-Vis Absorbance Spectrum", fontsize=ax_to_save.title.get_fontsize())
        elif plot_type == 'transmittance' and not self.hide_trans_title_checkbox.isChecked():
            temp_ax.set_title("UV-Vis Transmittance Spectrum", fontsize=ax_to_save.title.get_fontsize())
        elif plot_type == 'tauc' and not self.hide_tauc_title_checkbox.isChecked():
            temp_ax.set_title("Tauc Plot", fontsize=ax_to_save.title.get_fontsize())
        else:
            temp_ax.set_title("")

        # Copy the data lines
        for line in ax_to_save.get_lines():
            temp_ax.plot(line.get_xdata(), line.get_ydata(), color=line.get_color(),
                         linestyle=line.get_linestyle(), linewidth=line.get_linewidth(),
                         marker=line.get_marker(), markersize=line.get_markersize(),
                         markerfacecolor=line.get_markerfacecolor(), markeredgecolor=line.get_markeredgecolor())

        # Copy the legend and other properties
        if ax_to_save.get_legend():
            handles, labels = ax_to_save.get_legend_handles_labels()
            temp_ax.legend(handles, labels, fontsize=ax_to_save.get_legend().get_texts()[0].get_fontsize())

        # Copy the grid setting
        if plot_type == 'absorbance':
            temp_ax.grid(self.grid_abs_checkbox.isChecked())
        elif plot_type == 'transmittance':
            temp_ax.grid(self.grid_trans_checkbox.isChecked())
        elif plot_type == 'tauc':
            temp_ax.grid(self.grid_tauc_checkbox.isChecked())

        temp_ax.set_facecolor('#f7f7f7')
        temp_ax.set_ylim(ax_to_save.get_ylim())

        # Make tick labels bold for the exported plot
        for tick in temp_ax.get_xticklabels():
            tick.set_fontweight('bold')
        for tick in temp_ax.get_yticklabels():
            tick.set_fontweight('bold')

        # Conditionally hide y-axis labels
        if self.hide_y_labels_checkbox.isChecked():
            temp_ax.set_yticklabels([])

        temp_fig.tight_layout()

        path, _ = QFileDialog.getSaveFileName(self, f"Save {file_name} as .{file_format}", f"{file_name}.{file_format}",
                                              f"Images (*.{file_format})")

        if path:
            try:
                temp_fig.savefig(path, format=file_format, dpi=300)
                QMessageBox.information(self, "Export Successful", f"Plot successfully exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save plot: {e}")

        # Close the temporary figure to free up memory
        plt.close(temp_fig)

    def apply_bold_font(self):
        """
        Applies bold font weight to the x and y-axis labels and tick values
        for all three plots.
        """
        plots = [self.ax_abs, self.ax_trans, self.ax_tauc]
        for ax in plots:
            if ax.lines:
                ax.xaxis.label.set_fontweight('bold')
                ax.yaxis.label.set_fontweight('bold')
                for tick in ax.get_xticklabels():
                    tick.set_fontweight('bold')
                for tick in ax.get_yticklabels():
                    tick.set_fontweight('bold')


def main():
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    gui = TaucPlotGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
