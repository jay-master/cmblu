# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 15:50:04 2024

@author: Jaehyun
"""

import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.colors as mcolors
import mplcursors
import addcopyfighandler
import colorsys
from matplotlib.legend_handler import HandlerTuple

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

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-file Nyquist and Bode Plotter")
        
        # Set the initial window size
        window_width = 600
        window_height = 930
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Create a scrollable frame
        self.scroll_frame = ScrollableFrame(self.root)
        self.scroll_frame.pack(fill="both", expand=True)

        self.selected_color1 = None
        self.selected_color2 = None
        self.color_chosen = False
        self.gradient_enabled = tk.BooleanVar()
        self.legend_entries = {}
        self.files_data = []  # List to store data from multiple files
        self.file_colors = {}  # Dictionary to store colors for each file

        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        frame = self.scroll_frame.scrollable_frame

        # File selection
        self.file_button = ttk.Button(frame, text="Select Files", command=self.load_files)
        self.file_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Color selection
        self.color_label1 = ttk.Label(frame, text="Select Line Color 1:")
        self.color_label1.grid(row=0, column=1, padx=5, pady=5)

        self.color_combobox1 = ttk.Combobox(frame, values=list(TU_COLORS.keys()), width=15)
        self.color_combobox1.grid(row=0, column=2, padx=5, pady=5)
        self.color_combobox1.bind("<<ComboboxSelected>>", self.on_color_selected1)

        self.color_label2 = ttk.Label(frame, text="Select Line Color 2:")
        self.color_label2.grid(row=0, column=3, padx=5, pady=5)

        self.color_combobox2 = ttk.Combobox(frame, values=list(TU_COLORS.keys()), width=15)
        self.color_combobox2.grid(row=0, column=4, padx=5, pady=5)
        self.color_combobox2.bind("<<ComboboxSelected>>", self.on_color_selected2)

        # Gradient and color inversion
        self.gradient_checkbutton = ttk.Checkbutton(frame, text="Enable Gradient", variable=self.gradient_enabled)
        self.gradient_checkbutton.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.invert_var = tk.BooleanVar()
        self.invert_checkbutton = ttk.Checkbutton(frame, text="Invert Colors", variable=self.invert_var)
        self.invert_checkbutton.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="w")

        # Segment selection
        self.segment_label = ttk.Label(frame, text="Select Segments:")
        self.segment_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.segment_frame = ttk.Frame(frame)
        self.segment_frame.grid(row=2, column=1, columnspan=4, padx=5, pady=5, sticky="nsew")

        self.segment_scrollbar = ttk.Scrollbar(self.segment_frame, orient=tk.VERTICAL)
        self.segment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.segment_listbox = tk.Listbox(self.segment_frame, selectmode=tk.EXTENDED, yscrollcommand=self.segment_scrollbar.set, height=5)
        self.segment_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.segment_listbox.bind("<<ListboxSelect>>", self.on_segment_selected)

        self.segment_scrollbar.config(command=self.segment_listbox.yview)

        # Legend frame
        self.legend_frame = ttk.LabelFrame(frame, text="Legend Entries")
        self.legend_frame.grid(row=3, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.legend_canvas = tk.Canvas(self.legend_frame)
        self.legend_scrollbar = ttk.Scrollbar(self.legend_frame, orient=tk.VERTICAL, command=self.legend_canvas.yview)
        self.scrollable_legend_frame = ttk.Frame(self.legend_canvas)

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

        # Plot customization
        self.title_label = ttk.Label(frame, text="Plot Title:")
        self.title_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = ttk.Entry(frame, width=40)
        self.title_entry.grid(row=4, column=1, columnspan=4, padx=5, pady=5, sticky="ew")

        self.xlabel_label = ttk.Label(frame, text="X-axis Label:")
        self.xlabel_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.xlabel_entry = ttk.Entry(frame, width=40)
        self.xlabel_entry.grid(row=5, column=1, columnspan=4, padx=5, pady=5, sticky="ew")

        self.ylabel_label = ttk.Label(frame, text="Y-axis Label:")
        self.ylabel_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.ylabel_entry = ttk.Entry(frame, width=40)
        self.ylabel_entry.grid(row=6, column=1, columnspan=4, padx=5, pady=5, sticky="ew")

        # Font sizes
        font_size_frame = ttk.LabelFrame(frame, text="Font Sizes")
        font_size_frame.grid(row=7, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.fontsize_title_label = ttk.Label(font_size_frame, text="Title:")
        self.fontsize_title_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fontsize_title_spinbox = ttk.Spinbox(font_size_frame, from_=6, to=20, width=5)
        self.fontsize_title_spinbox.grid(row=0, column=1, padx=5, pady=5)
        self.fontsize_title_spinbox.set(12)

        self.fontsize_labels_label = ttk.Label(font_size_frame, text="Labels:")
        self.fontsize_labels_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.fontsize_labels_spinbox = ttk.Spinbox(font_size_frame, from_=6, to=20, width=5)
        self.fontsize_labels_spinbox.grid(row=0, column=3, padx=5, pady=5)
        self.fontsize_labels_spinbox.set(10)

        self.fontsize_legend_label = ttk.Label(font_size_frame, text="Legend:")
        self.fontsize_legend_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.fontsize_legend_spinbox = ttk.Spinbox(font_size_frame, from_=6, to=20, width=5)
        self.fontsize_legend_spinbox.grid(row=1, column=1, padx=5, pady=5)
        self.fontsize_legend_spinbox.set(8)

        self.fontsize_ticks_label = ttk.Label(font_size_frame, text="Ticks:")
        self.fontsize_ticks_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.fontsize_ticks_spinbox = ttk.Spinbox(font_size_frame, from_=6, to=20, width=5)
        self.fontsize_ticks_spinbox.grid(row=1, column=3, padx=5, pady=5)
        self.fontsize_ticks_spinbox.set(8)

        # Plot options
        options_frame = ttk.LabelFrame(frame, text="Plot Options")
        options_frame.grid(row=8, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.legend_var = tk.BooleanVar(value=True)
        self.legend_checkbutton = ttk.Checkbutton(options_frame, text="Show Legend", variable=self.legend_var)
        self.legend_checkbutton.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.legend_columns_label = ttk.Label(options_frame, text="Legend Columns:")
        self.legend_columns_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.legend_columns_spinbox = ttk.Spinbox(options_frame, from_=1, to=10, width=5)
        self.legend_columns_spinbox.grid(row=0, column=2, padx=5, pady=5)
        self.legend_columns_spinbox.set(1)

        self.grid_var = tk.BooleanVar(value=True)
        self.grid_checkbutton = ttk.Checkbutton(options_frame, text="Show Grid", variable=self.grid_var)
        self.grid_checkbutton.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Axis limits
        limits_frame = ttk.LabelFrame(frame, text="Axis Limits")
        limits_frame.grid(row=9, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.xmin_label = ttk.Label(limits_frame, text="X-axis Min:")
        self.xmin_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.xmin_entry = ttk.Entry(limits_frame, width=10)
        self.xmin_entry.grid(row=0, column=1, padx=5, pady=5)

        self.xmax_label = ttk.Label(limits_frame, text="X-axis Max:")
        self.xmax_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.xmax_entry = ttk.Entry(limits_frame, width=10)
        self.xmax_entry.grid(row=0, column=3, padx=5, pady=5)

        self.ymin_label = ttk.Label(limits_frame, text="Y-axis Min:")
        self.ymin_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ymin_entry = ttk.Entry(limits_frame, width=10)
        self.ymin_entry.grid(row=1, column=1, padx=5, pady=5)

        self.ymax_label = ttk.Label(limits_frame, text="Y-axis Max:")
        self.ymax_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.ymax_entry = ttk.Entry(limits_frame, width=10)
        self.ymax_entry.grid(row=1, column=3, padx=5, pady=5)

        # Figure size
        size_frame = ttk.LabelFrame(frame, text="Figure Size")
        size_frame.grid(row=10, column=0, columnspan=5, padx=5, pady=5, sticky="nsew")

        self.width_label = ttk.Label(size_frame, text="Width:")
        self.width_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.width_entry = ttk.Entry(size_frame, width=10)
        self.width_entry.grid(row=0, column=1, padx=5, pady=5)
        self.width_entry.insert(0, "10")

        self.height_label = ttk.Label(size_frame, text="Height:")
        self.height_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.height_entry = ttk.Entry(size_frame, width=10)
        self.height_entry.grid(row=0, column=3, padx=5, pady=5)
        self.height_entry.insert(0, "6")

        # Grid interval
        self.grid_interval_label = ttk.Label(frame, text="Grid Interval:")
        self.grid_interval_label.grid(row=11, column=0, padx=5, pady=5, sticky="w")
        self.grid_interval_entry = ttk.Entry(frame, width=10)
        self.grid_interval_entry.grid(row=11, column=1, padx=5, pady=5)

        # Plot buttons
        self.plot_button = ttk.Button(frame, text="Plot Nyquist", command=self.plot_data)
        self.plot_button.grid(row=12, column=0, columnspan=2, padx=5, pady=5)

        self.plot_bode_button = ttk.Button(frame, text="Plot Bode", command=self.plot_bode)
        self.plot_bode_button.grid(row=12, column=2, columnspan=2, padx=5, pady=5)

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def load_files(self):
        self.file_paths = filedialog.askopenfilenames()
        if self.file_paths:
            self.files_data = []
            self.segment_listbox.delete(0, tk.END)
            for file_path in self.file_paths:
                data = pd.read_csv(file_path)
                data = data[data['Frequency (Hz)'] != 0]  # Filter out rows with frequency 0
                self.files_data.append(data)
                segments = data['Segment'].unique()
                for segment in segments:
                    self.segment_listbox.insert(tk.END, f"{file_path.split('/')[-1]}:{segment}")

    def on_closing(self):
        if hasattr(self, 'check_window') and self.check_window.winfo_exists():
            self.check_window.destroy()
        self.root.quit()
        self.root.destroy()

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
            segment = self.segment_listbox.get(index)
            label = tk.Label(self.scrollable_legend_frame, text=f"Legend for {segment}:")
            label.grid(row=index, column=0, padx=5, pady=5)
            entry = tk.Entry(self.scrollable_legend_frame)
            entry.grid(row=index, column=1, padx=5, pady=5)
            entry.bind('<Tab>', self.focus_next_widget)
            self.legend_entries[segment] = entry

    def adjust_lightness(self, color, amount):
        try:
            c = mcolors.cnames[color]
        except:
            c = color
        c = colorsys.rgb_to_hls(*mcolors.to_rgb(c))
        return mcolors.to_hex(colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2]))

    def compute_gradient_colors(self, color1, color2, steps, invert=False):
        c1 = np.array(mcolors.to_rgb(color1))
        c2 = np.array(mcolors.to_rgb(color2))
        if invert:
            c1, c2 = c2, c1
        return [mcolors.to_hex(c1 + (c2 - c1) * i / (steps - 1)) for i in range(steps)]
  
    def plot_data(self):
        selected_items = [self.segment_listbox.get(i) for i in self.segment_listbox.curselection()]
        if not selected_items:
            messagebox.showwarning("No Segments Selected", "Please select at least one segment to plot.")
            return
    
        # Get axis limits
        try:
            xmin = float(self.xmin_entry.get()) if self.xmin_entry.get() else None
            xmax = float(self.xmax_entry.get()) if self.xmax_entry.get() else None
            ymin = float(self.ymin_entry.get()) if self.ymin_entry.get() else None
            ymax = float(self.ymax_entry.get()) if self.ymax_entry.get() else None
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for axis limits.")
            return
    
        # Calculate aspect ratio based on axis limits
        if xmin is not None and xmax is not None and ymin is not None and ymax is not None:
            x_range = abs(xmax - xmin)
            y_range = abs(ymax - ymin)
            aspect_ratio = x_range / y_range
        else:
            aspect_ratio = 1  # Default aspect ratio if limits are not set
    
        try:
            width = float(self.width_entry.get()) if self.width_entry.get() else 10
            height = float(self.height_entry.get()) if self.height_entry.get() else (width / aspect_ratio)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for figure width and height.")
            return
    
        fig, ax = plt.subplots(figsize=(width, height))
        invert_colors = self.invert_var.get()
    
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'd', '|', '_']
        self.lines = []
        self.scatters = []
        self.red_dots = []
        self.line_labels = []
    
        # Group selected items by file
        file_segments = {}
        for item in selected_items:
            file, segment = item.split(':')
            if file not in file_segments:
                file_segments[file] = []
            file_segments[file].append(segment)
    
        if self.gradient_enabled.get() and self.color_chosen:
            base_color1 = TU_COLORS[self.selected_color1]
            base_color2 = TU_COLORS[self.selected_color2] if self.selected_color2 else base_color1
            use_gradient = True
        else:
            use_gradient = False
            # Use a color cycle for different files
            color_cycle = plt.cm.tab10(np.linspace(0, 1, len(file_segments)))
            self.file_colors = {file: mcolors.to_hex(color) for file, color in zip(file_segments.keys(), color_cycle)}
    
        for file_index, (file, segments) in enumerate(file_segments.items()):
            file_data = self.files_data[file_index]
            marker = markers[file_index % len(markers)]
    
            if use_gradient:
                gradient_colors = self.compute_gradient_colors(base_color1, base_color2, len(segments), invert=invert_colors)
            else:
                file_color = self.file_colors[file]
    
            for i, segment in enumerate(segments):
                segment_data = file_data[file_data['Segment'] == int(segment)]
                legend_text = self.legend_entries.get(f"{file}:{segment}", None)
                legend_text = legend_text.get() if legend_text and legend_text.get() else f'File {file_index+1}, Segment {segment}'
                
                line_color = gradient_colors[i] if use_gradient else file_color
    
                line, = ax.plot(segment_data['Zre (ohms)'], -segment_data['Zim (ohms)'],
                                label=legend_text, linestyle='-', linewidth=1, color=line_color, visible=True)
                
                self.lines.append(line)
                self.line_labels.append(legend_text)
    
                scatter = ax.scatter(segment_data['Zre (ohms)'], -segment_data['Zim (ohms)'],
                                     marker=marker, s=20, color=line_color, visible=True)
                self.scatters.append(scatter)
                
                specific_data = segment_data[segment_data['Frequency (Hz)'].apply(
                    lambda x: any(abs(x - 10**j) < 0.1 * 10**j for j in range(-6, 7)))]
                red_dot = ax.scatter(specific_data['Zre (ohms)'], -specific_data['Zim (ohms)'],
                                     marker=marker, s=20, color='red', visible=True)
                self.red_dots.append(red_dot)
    
                cursor = mplcursors.cursor([scatter], multiple=True)
                @cursor.connect("add")
                def on_add(sel):
                    index = sel.target.index
                    freq = segment_data.iloc[index]['Frequency (Hz)']
                    zre = segment_data.iloc[index]['Zre (ohms)']
                    zim = segment_data.iloc[index]['Zim (ohms)']
                    sel.annotation.set_text(f"Freq: {freq:.2e} Hz\nZ_re: {zre:.2f} Ω\nZ_im: {zim:.2f} Ω")
    
        title = self.title_entry.get() if self.title_entry.get() else "Nyquist Plot"
        xlabel = self.xlabel_entry.get() if self.xlabel_entry.get() else r"$Z_{re}$ (Ω)"
        ylabel = self.ylabel_entry.get() if self.ylabel_entry.get() else r"$-Z_{im}$ (Ω)"
    
        ax.set_title(title, fontsize=int(self.fontsize_title_spinbox.get()))
        ax.set_xlabel(xlabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        ax.set_ylabel(ylabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        ax.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))
    
        if self.grid_var.get():
            ax.grid(color='lightgray', linestyle='--', linewidth=0.5)
    
        # Set axis limits
        if xmin is not None and xmax is not None:
            ax.set_xlim(left=xmin, right=xmax)
        if ymin is not None and ymax is not None:
            ax.set_ylim(bottom=ymin, top=ymax)
    
        ax.set_aspect('equal')
    
        try:
            interval = float(self.grid_interval_entry.get()) if self.grid_interval_entry.get() else None
            if interval:
                ax.xaxis.set_major_locator(plt.MultipleLocator(interval))
                ax.yaxis.set_major_locator(plt.MultipleLocator(interval))
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for grid interval.")
    
        plt.tight_layout()
    
        self.fig = fig
        self.ax = ax
    
        # Create a new window for checkboxes
        self.check_window = tk.Toplevel(self.root)
        self.check_window.title("Show/Hide Segments")
        self.check_window.geometry("200x400")
    
        # Create checkboxes for each segment
        self.check_vars = []
        for i, label in enumerate(self.line_labels):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.check_window, text=label, variable=var,
                                 command=lambda idx=i: self.toggle_visibility(idx))
            cb.pack(anchor='w')
            self.check_vars.append(var)
    
        self.update_legend()
        plt.show()

    def toggle_visibility(self, index):
        visible = self.check_vars[index].get()
        self.lines[index].set_visible(visible)
        self.scatters[index].set_visible(visible)
        self.red_dots[index].set_visible(visible)
        self.update_legend()
        self.fig.canvas.draw()

    def update_legend(self):
        if self.legend_var.get():
            visible_lines = [line for line, check_var in zip(self.lines, self.check_vars) if check_var.get()]
            visible_labels = [label for label, check_var in zip(self.line_labels, self.check_vars) if check_var.get()]
            visible_scatters = [scatter for scatter, check_var in zip(self.scatters, self.check_vars) if check_var.get()]
            
            if visible_lines:
                handles = []
                labels = []
                file_segments = {}

                for line, scatter, label in zip(visible_lines, visible_scatters, visible_labels):
                    file = label.split(',')[0]
                    if file not in file_segments:
                        file_segments[file] = []
                    file_segments[file].append((line, scatter, label))

                for file, segments in file_segments.items():
                    if len(segments) == 1:
                        # If only one segment for this file, add it to the legend
                        line, scatter, label = segments[0]
                        handles.append((line, scatter))
                        labels.append(label)
                    else:
                        # Add first and last segment for this file
                        first_line, first_scatter, first_label = segments[0]
                        last_line, last_scatter, last_label = segments[-1]
                        handles.append((first_line, first_scatter))
                        labels.append(first_label)
                        handles.append((last_line, last_scatter))
                        labels.append(last_label)

                legend_cols = int(self.legend_columns_spinbox.get()) if self.legend_columns_spinbox.get() else 1
                self.ax.legend(handles, labels, fontsize=int(self.fontsize_legend_spinbox.get()), ncol=legend_cols,
                               handler_map={tuple: HandlerTuple(ndivide=None)})
            else:
                self.ax.legend().set_visible(False)
        else:
            self.ax.legend().set_visible(False)
        self.fig.canvas.draw()

    def plot_bode(self):
        selected_items = [self.segment_listbox.get(i) for i in self.segment_listbox.curselection()]
        if not selected_items:
            messagebox.showwarning("No Segments Selected", "Please select at least one segment to plot.")
            return
    
        try:
            width = float(self.width_entry.get()) if self.width_entry.get() else 10
            height = float(self.height_entry.get()) if self.height_entry.get() else 12
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for figure width and height.")
            return
    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width, height), sharex=True)
        invert_colors = self.invert_var.get()
    
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'd', '|', '_']
        line_style = '-'
        self.lines_mag = []
        self.lines_phase = []
        self.scatters_mag = []
        self.scatters_phase = []
        self.line_labels = []
    
        # Group selected items by file
        file_segments = {}
        for item in selected_items:
            file, segment = item.split(':')
            if file not in file_segments:
                file_segments[file] = []
            file_segments[file].append(segment)
    
        if self.gradient_enabled.get() and self.color_chosen:
            base_color1 = TU_COLORS[self.selected_color1]
            base_color2 = TU_COLORS[self.selected_color2] if self.selected_color2 else base_color1
            use_gradient = True
        else:
            use_gradient = False
            # Use a color cycle for different files
            color_cycle = plt.cm.tab10(np.linspace(0, 1, len(file_segments)))
            self.file_colors = {file: mcolors.to_hex(color) for file, color in zip(file_segments.keys(), color_cycle)}
    
        for file_index, (file, segments) in enumerate(file_segments.items()):
            file_data = self.files_data[file_index]
            marker = markers[file_index % len(markers)]
    
            if use_gradient:
                gradient_colors = self.compute_gradient_colors(base_color1, base_color2, len(segments), invert=invert_colors)
            else:
                file_color = self.file_colors[file]
    
            for i, segment in enumerate(segments):
                segment_data = file_data[file_data['Segment'] == int(segment)]
                legend_text = self.legend_entries.get(f"{file}:{segment}", None)
                legend_text = legend_text.get() if legend_text and legend_text.get() else f'File {file_index+1}, Segment {segment}'
                
                line_color = gradient_colors[i] if use_gradient else file_color
    
                # Magnitude plot
                line_mag, = ax1.semilogx(segment_data['Frequency (Hz)'], segment_data['|Z| (ohms)'],
                                         label=legend_text, linestyle=line_style, linewidth=1, color=line_color, visible=True)
                scatter_mag = ax1.scatter(segment_data['Frequency (Hz)'], segment_data['|Z| (ohms)'],
                                          marker=marker, s=20, color=line_color, visible=True)
                
                # Phase plot
                line_phase, = ax2.semilogx(segment_data['Frequency (Hz)'], segment_data['Phase of Z (deg)'],
                           label=legend_text, linestyle=line_style, linewidth=1, color=line_color, visible=True)
                scatter_phase = ax2.scatter(segment_data['Frequency (Hz)'], segment_data['Phase of Z (deg)'],
                             marker=marker, s=20, color=line_color, visible=True)
    
                self.lines_mag.append(line_mag)
                self.lines_phase.append(line_phase)
                self.scatters_mag.append(scatter_mag)
                self.scatters_phase.append(scatter_phase)
                self.line_labels.append(legend_text)
    
                cursor_mag = mplcursors.cursor([scatter_mag], multiple=True)
                @cursor_mag.connect("add")
                def on_add(sel):
                    index = sel.target.index
                    freq = segment_data.iloc[index]['Frequency (Hz)']
                    mag = segment_data.iloc[index]['|Z| (ohms)']
                    sel.annotation.set_text(f"Freq: {freq:.2e} Hz\n|Z|: {mag:.2f} Ω")
    
                cursor_phase = mplcursors.cursor([scatter_phase], multiple=True)
                @cursor_phase.connect("add")
                def on_add(sel):
                    index = sel.target.index
                    freq = segment_data.iloc[index]['Frequency (Hz)']
                    phase = -segment_data.iloc[index]['Phase of Z (deg)']
                    sel.annotation.set_text(f"Freq: {freq:.2e} Hz\nPhase: {phase:.2f}°")
    
        title = self.title_entry.get() if self.title_entry.get() else "Bode Plot"
        fig.suptitle(title, fontsize=int(self.fontsize_title_spinbox.get()))
    
        ax1.set_ylabel('|Z| (Ω)', fontsize=int(self.fontsize_labels_spinbox.get()))
        ax2.set_xlabel('Frequency (Hz)', fontsize=int(self.fontsize_labels_spinbox.get()))
        ax2.set_ylabel('Phase (°)', fontsize=int(self.fontsize_labels_spinbox.get()))
    
        ax1.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))
        ax2.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))
    
        if self.grid_var.get():
            ax1.grid(color='lightgray', linestyle='--', linewidth=0.5)
            ax2.grid(color='lightgray', linestyle='--', linewidth=0.5)
    
        plt.tight_layout()
    
        self.fig = fig
        self.ax1 = ax1
        self.ax2 = ax2
    
        # Create a new window for checkboxes
        self.check_window = tk.Toplevel(self.root)
        self.check_window.title("Show/Hide Segments")
        self.check_window.geometry("200x400")
    
        # Create checkboxes for each segment
        self.check_vars = []
        for i, label in enumerate(self.line_labels):
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.check_window, text=label, variable=var,
                                 command=lambda idx=i: self.toggle_visibility_bode(idx))
            cb.pack(anchor='w')
            self.check_vars.append(var)
    
        self.update_legend_bode()
        plt.show()

    def toggle_visibility_bode(self, index):
        visible = self.check_vars[index].get()
        self.lines_mag[index].set_visible(visible)
        self.lines_phase[index].set_visible(visible)
        self.scatters_mag[index].set_visible(visible)
        self.scatters_phase[index].set_visible(visible)
        self.update_legend_bode()
        self.fig.canvas.draw()

    def update_legend_bode(self):
        if self.legend_var.get():
            visible_lines = [line for line, check_var in zip(self.lines_mag, self.check_vars) if check_var.get()]
            visible_labels = [label for label, check_var in zip(self.line_labels, self.check_vars) if check_var.get()]
            visible_scatters = [scatter for scatter, check_var in zip(self.scatters_mag, self.check_vars) if check_var.get()]
            
            if visible_lines:
                handles = []
                labels = []
                file_segments = {}

                for line, scatter, label in zip(visible_lines, visible_scatters, visible_labels):
                    file = label.split(',')[0]
                    if file not in file_segments:
                        file_segments[file] = []
                    file_segments[file].append((line, scatter, label))

                for file, segments in file_segments.items():
                    if len(segments) == 1:
                        # If only one segment for this file, add it to the legend
                        line, scatter, label = segments[0]
                        handles.append((line, scatter))
                        labels.append(label)
                    else:
                        # Add first and last segment for this file
                        first_line, first_scatter, first_label = segments[0]
                        last_line, last_scatter, last_label = segments[-1]
                        handles.append((first_line, first_scatter))
                        labels.append(first_label)
                        handles.append((last_line, last_scatter))
                        labels.append(last_label)

                legend_cols = int(self.legend_columns_spinbox.get()) if self.legend_columns_spinbox.get() else 1
                self.ax1.legend(handles, labels, fontsize=int(self.fontsize_legend_spinbox.get()), ncol=legend_cols,
                                handler_map={tuple: HandlerTuple(ndivide=None)})
                self.ax2.legend().set_visible(False)  # Hide legend on phase plot
            else:
                self.ax1.legend().set_visible(False)
                self.ax2.legend().set_visible(False)
        else:
            self.ax1.legend().set_visible(False)
            self.ax2.legend().set_visible(False)
        self.fig.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()