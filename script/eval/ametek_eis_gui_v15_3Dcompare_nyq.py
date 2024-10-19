# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 07:51:21 2024

@author: Jaehyun
"""

import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.colors as mcolors
import mplcursors
from mpl_toolkits.mplot3d import Axes3D
import re

# Colors extracted from TU_color.pdf
TU_COLORS = {
    'TU-Rot': '#c40d1e',
    'Schwarz': '#000000',
    'Dunkelgrau': '#434343',
    'Hellgrau': '#b2b2b2',
    'Orange': '#ff6c00',
    'Violett': '#9013fe',
    'Blau': '#1f90cc',
    'Grün': '#49cb40',
    'Combi-0a': '#00ffff',
    'Combi-0b': '#000080',
    'Combi-1a': '#C33764',
    'Combi-1b': '#1D2671',
    'Combi-2a': '#350068',
    'Combi-2b': '#FF6978',
    'Combi-3a': '#DA3068',
    'Combi-3b': '#14469F',
    'Combi-4a': '#301847',
    'Combi-4b': '#C10214',
    'Combi-5a': '#662D8C',
    'Combi-5b': '#ED1E79',
    'Combi-6a': '#EA8D8D',
    'Combi-6b': '#A890FE',
}

class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Nyquist Plotter")

        self.selected_color1 = None
        self.selected_color2 = None
        self.color_chosen = False
        self.gradient_enabled = tk.BooleanVar()
        self.legend_entries = {}
        self.file_data = {}
        self.segment_labels = self.generate_segment_labels()
        
        # Add new variables for elevation and azimuth angles
        self.elevation_angle = tk.StringVar(value="30")
        self.azimuth_angle = tk.StringVar(value="-60")

        self.create_widgets()
        
        self.fig = None
        self.ax = None
        self.legend = None
        
    def generate_segment_labels(self):
        labels = []
        # Discharge cycle (100% to 0%)
        for i in range(20, 0, -1):
            labels.append(f"d_{i*5}%")
        labels.append("0%")  # Fully discharged state
        # Charge cycle (5% to 100%)
        for i in range(1, 21):
            labels.append(f"c_{i*5}%")
        return labels

    def create_widgets(self):
        # File selection
        self.file_button = tk.Button(self.root, text="Select Files", command=self.load_files)
        self.file_button.grid(row=0, column=0, padx=5, pady=5)
    
        # File listbox
        self.file_listbox_label = tk.Label(self.root, text="Selected Files:")
        self.file_listbox_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
    
        self.file_listbox_frame = tk.Frame(self.root)
        self.file_listbox_frame.grid(row=2, column=0, columnspan=6, padx=5, pady=5, sticky='nsew')
    
        self.file_listbox_scrollbar = tk.Scrollbar(self.file_listbox_frame, orient=tk.VERTICAL)
        self.file_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        self.file_listbox = tk.Listbox(self.file_listbox_frame, width=50, height=5, yscrollcommand=self.file_listbox_scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        self.file_listbox_scrollbar.config(command=self.file_listbox.yview)
    
        # Color selection
        self.color_label1 = tk.Label(self.root, text="Select Line Color 1:")
        self.color_label1.grid(row=3, column=0, padx=5, pady=5)
    
        self.color_combobox1 = ttk.Combobox(self.root, values=list(TU_COLORS.keys()), width=10)
        self.color_combobox1.grid(row=3, column=1, padx=5, pady=5)
        self.color_combobox1.bind("<<ComboboxSelected>>", self.on_color_selected1)
    
        self.color_label2 = tk.Label(self.root, text="Select Line Color 2:")
        self.color_label2.grid(row=3, column=2, padx=5, pady=5)
    
        self.color_combobox2 = ttk.Combobox(self.root, values=list(TU_COLORS.keys()), width=10)
        self.color_combobox2.grid(row=3, column=3, padx=5, pady=5)
        self.color_combobox2.bind("<<ComboboxSelected>>", self.on_color_selected2)
    
        self.gradient_enabled = tk.BooleanVar()
        self.gradient_checkbutton = tk.Checkbutton(self.root, text="Enable Gradient", variable=self.gradient_enabled)
        self.gradient_checkbutton.grid(row=3, column=4, padx=5, pady=5)
    
        self.invert_var = tk.BooleanVar()
        self.invert_checkbutton = tk.Checkbutton(self.root, text="Invert Colors", variable=self.invert_var)
        self.invert_checkbutton.grid(row=3, column=5, padx=5, pady=5)
    
        # Segment selection
        self.segment_label = tk.Label(self.root, text="Segment Selection:")
        self.segment_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
    
        self.segment_frame = tk.Frame(self.root)
        self.segment_frame.grid(row=5, column=0, columnspan=6, padx=5, pady=5, sticky='nsew')
    
        self.segment_scrollbar = tk.Scrollbar(self.segment_frame, orient=tk.VERTICAL)
        self.segment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        self.segment_listbox = tk.Listbox(self.segment_frame, selectmode=tk.EXTENDED, yscrollcommand=self.segment_scrollbar.set, height=10)
        self.segment_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.segment_listbox.bind("<<ListboxSelect>>", self.on_segment_selected)
    
        self.segment_scrollbar.config(command=self.segment_listbox.yview)
    
        # Legend frame
        self.legend_frame = tk.Frame(self.root)
        self.legend_frame.grid(row=6, column=0, columnspan=6, padx=5, pady=5)
    
        self.legend_canvas = tk.Canvas(self.legend_frame, height=200)
        self.legend_scrollbar = tk.Scrollbar(self.legend_frame, orient=tk.VERTICAL, command=self.legend_canvas.yview)
        self.scrollable_legend_frame = tk.Frame(self.legend_canvas)
    
        self.scrollable_legend_frame.bind(
            "<Configure>",
            lambda e: self.legend_canvas.configure(
                scrollregion=self.legend_canvas.bbox("all")
            )
        )
    
        self.legend_canvas.create_window((0, 0), window=self.scrollable_legend_frame, anchor="nw")
        self.legend_canvas.configure(yscrollcommand=self.legend_scrollbar.set)
    
        self.legend_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.legend_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Plot settings
        self.title_label = tk.Label(self.root, text="Plot Title:")
        self.title_label.grid(row=7, column=0, padx=5, pady=5)
        self.title_entry = tk.Entry(self.root)
        self.title_entry.grid(row=7, column=1, columnspan=5, padx=5, pady=5, sticky='we')
    
        self.xlabel_label = tk.Label(self.root, text="X-axis Label:")
        self.xlabel_label.grid(row=8, column=0, padx=5, pady=5)
        self.xlabel_entry = tk.Entry(self.root)
        self.xlabel_entry.grid(row=8, column=1, columnspan=5, padx=5, pady=5, sticky='we')
    
        self.ylabel_label = tk.Label(self.root, text="Y-axis Label:")
        self.ylabel_label.grid(row=9, column=0, padx=5, pady=5)
        self.ylabel_entry = tk.Entry(self.root)
        self.ylabel_entry.grid(row=9, column=1, columnspan=5, padx=5, pady=5, sticky='we')
    
        # Font size settings
        self.fontsize_title_label = tk.Label(self.root, text="Title Font Size:")
        self.fontsize_title_label.grid(row=10, column=0, padx=5, pady=5)
        self.fontsize_title_spinbox = tk.Spinbox(self.root, from_=10, to=20, width=5)
        self.fontsize_title_spinbox.grid(row=10, column=1, padx=5, pady=5)
    
        self.fontsize_labels_label = tk.Label(self.root, text="Labels Font Size:")
        self.fontsize_labels_label.grid(row=10, column=2, padx=5, pady=5)
        self.fontsize_labels_spinbox = tk.Spinbox(self.root, from_=10, to=20, width=5)
        self.fontsize_labels_spinbox.grid(row=10, column=3, padx=5, pady=5)
    
        self.fontsize_legend_label = tk.Label(self.root, text="Legend Font Size:")
        self.fontsize_legend_label.grid(row=11, column=0, padx=5, pady=5)
        self.fontsize_legend_spinbox = tk.Spinbox(self.root, from_=10, to=20, width=5)
        self.fontsize_legend_spinbox.grid(row=11, column=1, padx=5, pady=5)
    
        self.fontsize_ticks_label = tk.Label(self.root, text="Ticks Font Size:")
        self.fontsize_ticks_label.grid(row=11, column=2, padx=5, pady=5)
        self.fontsize_ticks_spinbox = tk.Spinbox(self.root, from_=10, to=20, width=5)
        self.fontsize_ticks_spinbox.grid(row=11, column=3, padx=5, pady=5)
    
        # Legend and grid settings
        self.legend_var = tk.BooleanVar()
        self.legend_checkbutton = tk.Checkbutton(self.root, text="Show Legend", variable=self.legend_var)
        self.legend_checkbutton.grid(row=12, column=0, padx=5, pady=5)
    
        self.legend_columns_label = tk.Label(self.root, text="Legend Columns:")
        self.legend_columns_label.grid(row=12, column=1, padx=5, pady=5)
        self.legend_columns_spinbox = tk.Spinbox(self.root, from_=1, to=10, width=5)
        self.legend_columns_spinbox.grid(row=12, column=2, padx=5, pady=5)
    
        self.grid_var = tk.BooleanVar()
        self.grid_checkbutton = tk.Checkbutton(self.root, text="Show Grid", variable=self.grid_var)
        self.grid_checkbutton.grid(row=12, column=3, padx=5, pady=5)
    
        # Axis limits
        self.xmin_label = tk.Label(self.root, text="X-axis Min:")
        self.xmin_label.grid(row=13, column=0, padx=5, pady=5)
        self.xmin_entry = tk.Entry(self.root, width=10)
        self.xmin_entry.grid(row=13, column=1, padx=5, pady=5)
    
        self.xmax_label = tk.Label(self.root, text="X-axis Max:")
        self.xmax_label.grid(row=13, column=2, padx=5, pady=5)
        self.xmax_entry = tk.Entry(self.root, width=10)
        self.xmax_entry.grid(row=13, column=3, padx=5, pady=5)
    
        self.ymin_label = tk.Label(self.root, text="Y-axis Min:")
        self.ymin_label.grid(row=14, column=0, padx=5, pady=5)
        self.ymin_entry = tk.Entry(self.root, width=10)
        self.ymin_entry.grid(row=14, column=1, padx=5, pady=5)
    
        self.ymax_label = tk.Label(self.root, text="Y-axis Max:")
        self.ymax_label.grid(row=14, column=2, padx=5, pady=5)
        self.ymax_entry = tk.Entry(self.root, width=10)
        self.ymax_entry.grid(row=14, column=3, padx=5, pady=5)
    
        # Figure size
        self.width_label = tk.Label(self.root, text="Figure Width:")
        self.width_label.grid(row=15, column=0, padx=5, pady=5)
        self.width_entry = tk.Entry(self.root, width=10)
        self.width_entry.grid(row=15, column=1, padx=5, pady=5)
    
        self.height_label = tk.Label(self.root, text="Figure Height:")
        self.height_label.grid(row=15, column=2, padx=5, pady=5)
        self.height_entry = tk.Entry(self.root, width=10)
        self.height_entry.grid(row=15, column=3, padx=5, pady=5)
    
        # Grid interval
        self.grid_interval_label = tk.Label(self.root, text="Grid Interval:")
        self.grid_interval_label.grid(row=16, column=0, padx=5, pady=5)
        self.grid_interval_entry = tk.Entry(self.root, width=10)
        self.grid_interval_entry.grid(row=16, column=1, padx=5, pady=5)
    
        # Plot button
        self.plot_button = tk.Button(self.root, text="Plot", command=self.plot_data)
        self.plot_button.grid(row=17, column=0, columnspan=6, padx=5, pady=5)
    
        # Configure grid weights
        for i in range(18):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(6):
            self.root.grid_columnconfigure(i, weight=1)
        
        # Add new widgets for angle control
        self.angle_frame = tk.Frame(self.root)
        self.angle_frame.grid(row=18, column=0, columnspan=6, padx=5, pady=5)
        
        tk.Label(self.angle_frame, text="Elevation Angle:").grid(row=0, column=0, padx=5, pady=5)
        self.elevation_entry = tk.Entry(self.angle_frame, textvariable=self.elevation_angle, width=5)
        self.elevation_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.angle_frame, text="Azimuth Angle:").grid(row=0, column=2, padx=5, pady=5)
        self.azimuth_entry = tk.Entry(self.angle_frame, textvariable=self.azimuth_angle, width=5)
        self.azimuth_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.update_angle_button = tk.Button(self.angle_frame, text="Update View", command=self.update_plot_angle)
        self.update_angle_button.grid(row=0, column=4, padx=5, pady=5)

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def load_files(self):
        self.file_paths = filedialog.askopenfilenames()
        if self.file_paths:
            self.file_listbox.delete(0, tk.END)
            self.file_data.clear()
            self.segment_listbox.delete(0, tk.END)
            
            for file_path in self.file_paths:
                data = pd.read_csv(file_path)
                data = data[data['Frequency (Hz)'] != 0]  # Filter out rows with frequency 0
                segments = data['Segment'].unique()
                
                # Assign labels to segments
                segment_label_map = {seg: label for seg, label in zip(sorted(segments), self.segment_labels)}
                data['SegmentLabel'] = data['Segment'].map(segment_label_map)
                
                # Extract temperature from filename
                temp_match = re.search(r'(\d+)grad', file_path)
                temperature = int(temp_match.group(1)) if temp_match else None
                
                self.file_data[file_path] = {
                    'data': data, 
                    'segments': segments, 
                    'segment_label_map': segment_label_map,
                    'temperature': temperature
                }
                
                filename = file_path.split('/')[-1]
                self.file_listbox.insert(tk.END, filename)
                
                # Count and print the number of segments
                segment_count = len(segments)
                print(f"File: {filename}, Number of segments: {segment_count}, Temperature: {temperature}°C")
            
            # Update segment listbox with labels
            for label in self.segment_labels:
                self.segment_listbox.insert(tk.END, label)

    def on_color_selected1(self, event):
        self.selected_color1 = self.color_combobox1.get()
        self.color_chosen = True

    def on_color_selected2(self, event):
        self.selected_color2 = self.color_combobox2.get()
        self.color_chosen = True

    def on_segment_selected(self, event):
        selected_indices = self.segment_listbox.curselection()
        for widget in self.scrollable_legend_frame.winfo_children():
            widget.destroy()

        self.legend_entries = {}
        for index in selected_indices:
            label = self.segment_listbox.get(index)
            legend_label = tk.Label(self.scrollable_legend_frame, text=f"Legend for {label}:")
            legend_label.grid(row=index, column=0, padx=5, pady=5)
            entry = tk.Entry(self.scrollable_legend_frame)
            entry.grid(row=index, column=1, padx=5, pady=5)
            entry.bind('<Tab>', self.focus_next_widget)
            self.legend_entries[label] = entry

    def adjust_lightness(self, color, factor, invert=False):
        try:
            c = mcolors.cnames[color]
        except KeyError:
            c = color
        c = np.array(mcolors.to_rgb(c))
        if invert:
            # Darker shade calculation
            white = np.array([1, 1, 1])
            adjusted_color = white * (1 - factor) + c * factor
        else:
            # Lighter shade calculation
            white = np.array([1, 1, 1])
            adjusted_color = c + (white - c) * factor
        return mcolors.to_hex(adjusted_color.clip(0, 0.9))

    def compute_gradient_colors(self, color1, color2, steps):
        c1 = np.array(mcolors.to_rgb(color1))
        c2 = np.array(mcolors.to_rgb(color2))
        return [mcolors.to_hex(c1 + (c2 - c1) * i / (steps - 1)) for i in range(steps)]


    def plot_data(self):
        self.selected_labels = [self.segment_listbox.get(i) for i in self.segment_listbox.curselection()]
        if not self.selected_labels:
            messagebox.showwarning("No Segments Selected", "Please select at least one segment to plot.")
            return
    
        try:
            width = float(self.width_entry.get()) if self.width_entry.get() else 10
            height = float(self.height_entry.get()) if self.height_entry.get() else 6
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for figure width and height.")
            return
    
        self.fig = plt.figure(figsize=(width, height))
        self.ax = self.fig.add_subplot(111, projection='3d')
        # Set initial view angle
        self.ax.view_init(elev=float(self.elevation_angle.get()), azim=float(self.azimuth_angle.get()))
        invert_colors = self.invert_var.get()
    
        if self.color_chosen:
            base_color1 = TU_COLORS[self.selected_color1]
            base_color2 = TU_COLORS[self.selected_color2] if self.selected_color2 else base_color1
        else:
            base_color1 = '#1f77b4'  # Default Matplotlib color
            base_color2 = '#ff7f0e'  # Another default Matplotlib color
    
        self.lines_by_segment = {label: [] for label in self.selected_labels}
        self.scatters_by_segment = {label: [] for label in self.selected_labels}
    
        for file_path, file_info in self.file_data.items():
            temperature = file_info['temperature']
            if temperature is None:
                continue

            gradient_colors = self.compute_gradient_colors(base_color1, base_color2, len(self.selected_labels))
            
            for i, label in enumerate(self.selected_labels):
                segment = next((seg for seg, seg_label in file_info['segment_label_map'].items() if seg_label == label), None)
                if segment is not None:
                    segment_data = file_info['data'][file_info['data']['SegmentLabel'] == label]
                    legend_text = self.legend_entries.get(label, None)
                    legend_text = legend_text.get() if legend_text and legend_text.get() else label
                    
                    # Remove 'c_' or 'd_' prefix and keep only percentage
                    legend_text = re.sub(r'^[cd]_', '', legend_text)
                    
                    line_color = gradient_colors[i % len(gradient_colors)]
                    
                    # Exchange Z_re and Temperature axes
                    line, = self.ax.plot([temperature] * len(segment_data),
                                         segment_data['Zre (ohms)'], 
                                         -segment_data['Zim (ohms)'],
                                         label=legend_text,  # Use only the modified legend_text
                                         linewidth=1, color=line_color)
                    
                    self.lines_by_segment[label].append(line)
    
                    # Exchange Z_re and Temperature axes for scatter plot
                    scatter = self.ax.scatter([temperature] * len(segment_data),
                                              segment_data['Zre (ohms)'], 
                                              -segment_data['Zim (ohms)'],
                                              s=20, color=line_color)
                    self.scatters_by_segment[label].append(scatter)
    
        title = self.title_entry.get() if self.title_entry.get() else "3D Nyquist Plot"
        xlabel = self.ylabel_entry.get() if self.ylabel_entry.get() else 'Temperature (°C)'  # Swapped with ylabel
        ylabel = self.xlabel_entry.get() if self.xlabel_entry.get() else '$Z_{re}$ (Ω)'  # Swapped with xlabel
        zlabel = '$-Z_{im}$ (Ω)'
    
        self.ax.set_title(title, fontsize=int(self.fontsize_title_spinbox.get()))
        self.ax.set_xlabel(xlabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        self.ax.set_ylabel(ylabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        self.ax.set_zlabel(zlabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        self.ax.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))
    
        # Create legend
        legend_columns = int(self.legend_columns_spinbox.get()) if self.legend_columns_spinbox.get() else 1
        self.legend = self.ax.legend(fontsize=int(self.fontsize_legend_spinbox.get()), ncol=legend_columns)
        
        # Set initial legend visibility based on checkbox state
        self.legend.set_visible(self.legend_var.get())
    
        # Handle grid visibility
        if self.grid_var.get():
            self.ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5)
        else:
            self.ax.grid(False)
    
        # Set axis limits
        try:
            xmin = float(self.ymin_entry.get()) if self.ymin_entry.get() else None  # Swapped with ymin
            xmax = float(self.ymax_entry.get()) if self.ymax_entry.get() else None  # Swapped with ymax
            ymin = float(self.xmin_entry.get()) if self.xmin_entry.get() else None  # Swapped with xmin
            ymax = float(self.xmax_entry.get()) if self.xmax_entry.get() else None  # Swapped with xmax
            
            if xmin is not None and xmax is not None:
                self.ax.set_xlim(left=xmin, right=xmax)
            if ymin is not None and ymax is not None:
                self.ax.set_ylim(bottom=ymin, top=ymax)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for axis limits.")
    

        
        # Create check buttons in a separate window for visibility control
        self.create_visibility_control_window()
    
        # Disconnect any existing callbacks to avoid duplicates
        self.legend_checkbutton.config(command=None)
        # Connect legend visibility toggle to checkbox
        self.legend_checkbutton.config(command=self.toggle_legend_visibility)
        
        # Update legend to show only first and last visible segments
        self.update_legend()
        
        plt.show(block=False)
        
        plt.tight_layout()
        
    def toggle_legend_visibility(self):
        if self.legend:
            self.legend.set_visible(self.legend_var.get())
            self.fig.canvas.draw_idle()
    
    def create_visibility_control_window(self):
        if hasattr(self, 'check_window') and self.check_window.winfo_exists():
            self.check_window.destroy()

        self.check_window = tk.Toplevel(self.root)
        self.check_window.title("Show/Hide Segments")
        self.check_window.geometry("300x530")  # Adjust the size of the window as needed

        self.visibility_vars = {}
        for label in self.selected_labels:
            var = tk.BooleanVar(value=True)  # Set default value to True
            cb = tk.Checkbutton(self.check_window, text=label, variable=var,
                                command=lambda l=label, v=var: self.toggle_segment_visibility(l, v))
            cb.pack(anchor='w')
            self.visibility_vars[label] = var

    def toggle_segment_visibility(self, label, var):
        visible = var.get()
        for line in self.lines_by_segment.get(label, []):
            line.set_visible(visible)
        for scatter in self.scatters_by_segment.get(label, []):
            scatter.set_visible(visible)
        self.update_legend()
        self.fig.canvas.draw_idle()

    def update_legend(self):
        visible_labels = [label for label, var in self.visibility_vars.items() if var.get()]
        if len(visible_labels) >= 2:
            legend_labels = [visible_labels[0], visible_labels[-1]]
        elif len(visible_labels) == 1:
            legend_labels = visible_labels
        else:
            legend_labels = []

        handles, labels = [], []
        for label in legend_labels:
            for line in self.lines_by_segment[label]:
                if line.get_visible():
                    handles.append(line)
                    # Remove 'c_' or 'd_' prefix from the label
                    clean_label = re.sub(r'^[cd]_', '', line.get_label())
                    labels.append(clean_label)
                    break  # Only add the first visible line for each segment

        self.legend = self.ax.legend(handles, labels, 
                                     fontsize=int(self.fontsize_legend_spinbox.get()), 
                                     ncol=int(self.legend_columns_spinbox.get()))
        self.legend.set_visible(self.legend_var.get())
        self.fig.canvas.draw_idle()
    
    def update_plot_angle(self):
        if self.ax is not None:
            try:
                elev = float(self.elevation_angle.get())
                azim = float(self.azimuth_angle.get())
                self.ax.view_init(elev=elev, azim=azim)
                self.fig.canvas.draw_idle()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers for elevation and azimuth angles.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()