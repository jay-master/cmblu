# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 21:46:51 2024

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
    def __init__(self, master, scroll_frame):
        self.master = master
        self.master.title("Nyquist and Bode Plotter")
        
        # Set the initial window size
        window_width = 600
        window_height = 930
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.master.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Initialize variables
        self.selected_color1 = None
        self.selected_color2 = None
        self.color_chosen = False
        self.gradient_enabled = tk.BooleanVar(value=False)
        self.gradient_enabled.trace_add('write', self.on_gradient_change)
        self.invert_var = tk.BooleanVar(value=False)

        # Use the provided scroll_frame
        self.scroll_frame = scroll_frame

        # Create widgets
        self.create_widgets()
    
    def plot_bode(self):
        selected_segments = [int(self.segment_listbox.get(i)) for i in self.segment_listbox.curselection()]
        if not selected_segments:
            messagebox.showwarning("No Segments Selected", "Please select at least one segment to plot.")
            return
    
        # try:
        #     default_width = 15
        #     width = float(self.width_entry.get()) if self.width_entry.get() else default_width
        #     height = width * 0.5  # Set figure ratio
        try:
            width = float(self.width_entry.get()) if self.width_entry.get() else 10
            height = float(self.height_entry.get()) if self.height_entry.get() else 12
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for figure width.")
            return
    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width, height), sharex=True)
        invert_colors = self.invert_var.get()
    
        if self.color_chosen:
            base_color1 = TU_COLORS[self.selected_color1]
            if self.gradient_enabled.get():
                base_color2 = TU_COLORS[self.selected_color2] if self.selected_color2 else base_color1
                gradient_colors = self.compute_gradient_colors(base_color1, base_color2, len(selected_segments))
            else:
                gradient_colors = [self.adjust_lightness(base_color1, (i + 1) / (len(selected_segments) + 1), invert=invert_colors) for i in range(len(selected_segments))]
        else:
            gradient_colors = plt.cm.viridis(np.linspace(0, 1, len(selected_segments)))
    
        line_style = '-'
        lines_mag = []
        lines_phase = []
        scatters_mag = []
        scatters_phase = []
        line_labels = []
    
        for i, segment in enumerate(selected_segments):
            segment_data = self.data[self.data['Segment'] == segment]
            legend_text = self.legend_entries.get(str(segment), None)
            legend_text = legend_text.get() if legend_text and legend_text.get() else f'Segment {segment}'
            
            line_color = gradient_colors[i]
    
            # Magnitude plot
            line_mag, = ax1.semilogx(segment_data['Frequency (Hz)'], segment_data['|Z| (ohms)'],
                                     label=legend_text, linestyle=line_style, linewidth=1, color=line_color, visible=True)
            scatter_mag = ax1.scatter(segment_data['Frequency (Hz)'], segment_data['|Z| (ohms)'],
                                      marker='o', s=20, color=line_color, visible=True)
            
            # Phase plot
            line_phase, = ax2.semilogx(segment_data['Frequency (Hz)'], segment_data['Phase of Z (deg)'],
                                       label=legend_text, linestyle=line_style, linewidth=1, color=line_color, visible=True)
            scatter_phase = ax2.scatter(segment_data['Frequency (Hz)'], segment_data['Phase of Z (deg)'],
                                        marker='o', s=20, color=line_color, visible=True)
    
            lines_mag.append(line_mag)
            lines_phase.append(line_phase)
            scatters_mag.append(scatter_mag)
            scatters_phase.append(scatter_phase)
            line_labels.append(legend_text)
    
            cursor_mag = mplcursors.cursor([scatter_mag], multiple=True)
            @cursor_mag.connect("add")
            def on_add(sel):
                sel.annotation.set_text(f"Freq: {sel.target[0]:.2e} Hz\n|Z|: {sel.target[1]:.2f} Ω")
    
            cursor_phase = mplcursors.cursor([scatter_phase], multiple=True)
            @cursor_phase.connect("add")
            def on_add(sel):
                sel.annotation.set_text(f"Freq: {sel.target[0]:.2e} Hz\nPhase: {sel.target[1]:.2f}°")
    
        title = self.title_entry.get() if self.title_entry.get() else self.file_path.split('/')[-1]
        fig.suptitle(title, fontsize=int(self.fontsize_title_spinbox.get()))
    
        ax1.set_ylabel('|Z| (Ω)', fontsize=int(self.fontsize_labels_spinbox.get()))
        ax2.set_xlabel('Frequency (Hz)', fontsize=int(self.fontsize_labels_spinbox.get()))
        ax2.set_ylabel('Phase (°)', fontsize=int(self.fontsize_labels_spinbox.get()))
    
        ax1.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))
        ax2.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))
    
        if self.legend_var.get():
            self.legend_columns = int(self.legend_columns_spinbox.get()) if self.legend_columns_spinbox.get() else 1
            self.legend = ax1.legend(fontsize=int(self.fontsize_legend_spinbox.get()), ncol=self.legend_columns)
            self.legend.set_visible(False)  # Hide legend initially
    
        if self.grid_var.get():
            ax1.grid(color='lightgray', linestyle='--', linewidth=0.5)
            ax2.grid(color='lightgray', linestyle='--', linewidth=0.5)
    
        plt.tight_layout()
    
        # Adding check buttons in a separate window
        self.check_window = tk.Toplevel(self.root)
        self.check_window.title("Select Lines to Show/Hide")
        self.check_window.geometry("200x500")  # Adjust the size of the window as needed
        
        self.checkbuttons = []
        self.line_labels = line_labels
        self.lines_mag = lines_mag
        self.lines_phase = lines_phase
        self.scatters_mag = scatters_mag
        self.scatters_phase = scatters_phase
        for i, label in enumerate(line_labels):
            var = tk.BooleanVar(value=True)  # Set default value to True
            cb = tk.Checkbutton(self.check_window, text=label, variable=var,
                                command=lambda l=label, v=var: self.toggle_visibility_bode(l, v))
            cb.pack(anchor='w')
            self.checkbuttons.append(cb)
    
    def toggle_visibility_bode(self, label, var):
        index = self.line_labels.index(label)
        visible = var.get()
        self.lines_mag[index].set_visible(visible)
        self.lines_phase[index].set_visible(visible)
        self.scatters_mag[index].set_visible(visible)
        self.scatters_phase[index].set_visible(visible)
        self.update_legend_bode()
        plt.draw()
    
    def update_legend_bode(self):
        if self.legend_var.get():
            handles, labels = [], []
            first_visible_index = None
            last_visible_index = None
            
            for i, line in enumerate(self.lines_mag):
                if line.get_visible():
                    if first_visible_index is None:
                        first_visible_index = i
                    last_visible_index = i
            
            if first_visible_index is not None:
                handles.append(self.lines_mag[first_visible_index])
                labels.append(self.line_labels[first_visible_index])
                
                if last_visible_index != first_visible_index:
                    handles.append(self.lines_mag[last_visible_index])
                    labels.append(self.line_labels[last_visible_index])
            
            if handles:
                if hasattr(self, 'legend'):
                    self.legend.remove()
                self.legend = plt.gca().legend(handles=handles, labels=labels, fontsize=int(self.fontsize_legend_spinbox.get()), ncol=self.legend_columns)
                self.legend.set_visible(True)
            else:
                if hasattr(self, 'legend'):
                    self.legend.set_visible(False)
            plt.draw()
        else:
            if hasattr(self, 'legend'):
                self.legend.set_visible(False)
            plt.draw()

    def create_widgets(self):
        frame = self.scroll_frame.scrollable_frame

        # File selection
        self.file_button = ttk.Button(frame, text="Select File", command=self.load_file)
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

    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.data = pd.read_csv(self.file_path)
            self.data = self.data[self.data['Frequency (Hz)'] != 0]  # Filter out rows with frequency 0
            segments = self.data['Segment'].unique()
            self.segment_listbox.delete(0, tk.END)
            for segment in segments:
                self.segment_listbox.insert(tk.END, segment)
                
    def on_gradient_toggle(self):
        print(f"Gradient checkbox toggled. New state: {self.gradient_enabled.get()}")
        # Trigger a redraw of the plot if it exists
        if hasattr(self, 'fig'):
            self.plot_data()

    def on_gradient_change(self, *args):
        print(f"Gradient enabled variable changed. New value: {self.gradient_enabled.get()}")

    def on_gradient_change(self):
        print(f"Gradient enabled: {self.gradient_enabled.get()}")

    def on_color_selected1(self, event):
        self.selected_color1 = self.color_combobox1.get()
        self.color_chosen = True
        print(f"Color 1 selected: {self.selected_color1}")
    
    def on_color_selected2(self, event):
        self.selected_color2 = self.color_combobox2.get()
        self.color_chosen = True
        print(f"Color 2 selected: {self.selected_color2}")

    def on_segment_selected(self, event):
        selected_indices = self.segment_listbox.curselection()
        for widget in self.scrollable_legend_frame.winfo_children():
            widget.destroy()

        self.legend_entries = {}
        for index in selected_indices:
            segment = self.segment_listbox.get(index)
            label = tk.Label(self.scrollable_legend_frame, text=f"Legend for Segment {segment}:")
            label.grid(row=index, column=0, padx=5, pady=5)
            entry = tk.Entry(self.scrollable_legend_frame)
            entry.grid(row=index, column=1, padx=5, pady=5)
            entry.bind('<Tab>', self.focus_next_widget)
            self.legend_entries[segment] = entry

    def adjust_lightness(self, color, factor, invert=False):
        print(f"Adjusting lightness of {color} with factor {factor}, invert={invert}")
        c = np.array(mcolors.to_rgb(color))
        if invert:
            # Darker shade calculation
            adjusted_color = c * (1 - factor)
        else:
            # Lighter shade calculation
            adjusted_color = c + (1 - c) * factor
        result = mcolors.to_hex(adjusted_color.clip(0, 1))
        print(f"Adjusted color: {result}")
        return result

    def compute_gradient_colors(self, color1, color2, steps, invert=False):
        print(f"Computing gradient from {color1} to {color2} with {steps} steps")
        c1 = np.array(mcolors.to_rgb(color1))
        c2 = np.array(mcolors.to_rgb(color2))
        if invert:
            c1, c2 = c2, c1
        gradient = [mcolors.to_hex(c1 + (c2 - c1) * i / (steps - 1)) for i in range(steps)]
        print(f"Computed gradient: {gradient}")
        return gradient
  
    def plot_data(self):
        selected_segments = [int(self.segment_listbox.get(i)) for i in self.segment_listbox.curselection()]
        if not selected_segments:
            messagebox.showwarning("No Segments Selected", "Please select at least one segment to plot.")
            return

        try:
            xmin = float(self.xmin_entry.get()) if self.xmin_entry.get() else None
            xmax = float(self.xmax_entry.get()) if self.xmax_entry.get() else None
            ymin = float(self.ymin_entry.get()) if self.ymin_entry.get() else None
            ymax = float(self.ymax_entry.get()) if self.ymax_entry.get() else None
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for axis limits.")
            return

        try:
            width = float(self.width_entry.get()) if self.width_entry.get() else 10
            height = float(self.height_entry.get()) if self.height_entry.get() else 6
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for figure size.")
            return

        fig, ax = plt.subplots(figsize=(width, height))

        gradient_enabled = self.gradient_enabled.get()
        invert_colors = self.invert_var.get()
        
        print(f"Plotting with gradient enabled: {gradient_enabled}")
        print(f"Invert colors: {invert_colors}")
        print(f"Selected color 1: {self.selected_color1}")
        print(f"Selected color 2: {self.selected_color2}")

        lines = []
        scatters = []
        red_dots = []
        line_labels = []

        if self.selected_color1:
            base_color1 = TU_COLORS[self.selected_color1]
            base_color2 = TU_COLORS.get(self.selected_color2, base_color1)
            
            print(f"Base color 1: {base_color1}")
            print(f"Base color 2: {base_color2}")
        
            if gradient_enabled:
                print("Calculating gradient between two colors")
                gradient_colors = self.compute_gradient_colors(base_color1, base_color2, len(selected_segments), invert=invert_colors)
            else:
                print("Using single color (no gradient)")
                gradient_colors = [base_color1] * len(selected_segments)
            
            print(f"Computed gradient colors: {gradient_colors}")

            for i, segment in enumerate(selected_segments):
                segment_data = self.data[self.data['Segment'] == segment]
                legend_text = self.legend_entries.get(str(segment), None)
                legend_text = legend_text.get() if legend_text and legend_text.get() else f'Segment {segment}'
                
                line_color = gradient_colors[i]
                print(f"Color for segment {segment}: {line_color}")
                
                line, = ax.plot(segment_data['Zre (ohms)'], -segment_data['Zim (ohms)'],
                                label=legend_text, linestyle='-', linewidth=1, color=line_color, visible=True)
                lines.append(line)
                line_labels.append(legend_text)

                scatter = ax.scatter(segment_data['Zre (ohms)'], -segment_data['Zim (ohms)'],
                                     marker='o', s=20, color=line_color, visible=True)
                scatters.append(scatter)

                specific_data = segment_data[segment_data['Frequency (Hz)'].apply(
                    lambda x: any(abs(x - 10**j) <= 0.1*10**j for j in range(-6, 7)))]
                red_dot = ax.scatter(specific_data['Zre (ohms)'], -specific_data['Zim (ohms)'],
                                     marker='o', s=20, color='red', visible=True)
                red_dots.append(red_dot)

                cursor = mplcursors.cursor([scatter], multiple=True)
                @cursor.connect("add")
                def on_add(sel):
                    index = sel.target.index
                    freq = segment_data.iloc[index]['Frequency (Hz)']
                    zre = segment_data.iloc[index]['Zre (ohms)']
                    zim = segment_data.iloc[index]['Zim (ohms)']
                    sel.annotation.set_text(f"Freq: {freq:.2e} Hz\nZre: {zre:.2f} Ω\nZim: {zim:.2f} Ω")

        else:
            print("No color selected, using default color scheme")
            for i, segment in enumerate(selected_segments):
                segment_data = self.data[self.data['Segment'] == segment]
                legend_text = self.legend_entries.get(str(segment), None)
                legend_text = legend_text.get() if legend_text and legend_text.get() else f'Segment {segment}'
                line, = ax.plot(segment_data['Zre (ohms)'], -segment_data['Zim (ohms)'],
                                label=legend_text, linewidth=1, visible=True)
                lines.append(line)
                line_labels.append(legend_text)
                scatter = ax.scatter(segment_data['Zre (ohms)'], -segment_data['Zim (ohms)'],
                                     s=20, visible=True)
                scatters.append(scatter)
                specific_data = segment_data[segment_data['Frequency (Hz)'].apply(
                    lambda x: any(abs(x - 10**j) <= 0.1*10**j for j in range(-6, 7)))]
                red_dot = ax.scatter(specific_data['Zre (ohms)'], -specific_data['Zim (ohms)'],
                                     s=20, color='red', visible=True)
                red_dots.append(red_dot)

                cursor = mplcursors.cursor([scatter], multiple=True)
                @cursor.connect("add")
                def on_add(sel):
                    index = sel.target.index
                    freq = segment_data.iloc[index]['Frequency (Hz)']
                    zre = segment_data.iloc[index]['Zre (ohms)']
                    zim = segment_data.iloc[index]['Zim (ohms)']
                    sel.annotation.set_text(f"Freq: {freq:.2e} Hz\nZre: {zre:.2f} Ω\nZim: {zim:.2f} Ω")

        title = self.title_entry.get() if self.title_entry.get() else self.file_path.split('/')[-1]
        xlabel = self.xlabel_entry.get() if self.xlabel_entry.get() else "Z' (Ω)"
        ylabel = self.ylabel_entry.get() if self.ylabel_entry.get() else "-Z'' (Ω)"

        ax.set_title(title, fontsize=int(self.fontsize_title_spinbox.get()))
        ax.set_xlabel(xlabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        ax.set_ylabel(ylabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        ax.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))

        if self.legend_var.get():
            self.legend_columns = int(self.legend_columns_spinbox.get()) if self.legend_columns_spinbox.get() else 1
            self.legend = ax.legend(fontsize=int(self.fontsize_legend_spinbox.get()), ncol=self.legend_columns)
            self.legend.set_visible(True)

        if self.grid_var.get():
            ax.grid(color='lightgray', linestyle='--', linewidth=0.5)

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

        self.check_window = tk.Toplevel(self.master)
        self.check_window.title("Select Lines to Show/Hide")
        self.check_window.geometry("200x500")
        
        self.checkbuttons = []
        self.line_labels = line_labels
        self.lines = lines
        self.scatters = scatters
        self.red_dots = red_dots
        for i, label in enumerate(line_labels):
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self.check_window, text=label, variable=var,
                                command=lambda l=label, v=var: self.toggle_visibility(l, v))
            cb.pack(anchor='w')
            self.checkbuttons.append(cb)

        cursor = mplcursors.cursor(lines, multiple=True)
        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set_text(sel.artist.get_label())
        @cursor.connect("remove")
        def on_remove(sel):
            pass

        plt.show()

    def toggle_visibility(self, label, var):
        index = self.line_labels.index(label)
        visible = var.get()
        self.lines[index].set_visible(visible)
        self.scatters[index].set_visible(visible)
        self.red_dots[index].set_visible(visible)
        self.update_legend()
        plt.draw()

    def update_legend(self):
        if self.legend_var.get():
            handles, labels = [], []
            first_visible_index = None
            last_visible_index = None
            
            for i, line in enumerate(self.lines):
                if line.get_visible():
                    if first_visible_index is None:
                        first_visible_index = i
                    last_visible_index = i
            
            if first_visible_index is not None:
                handles.append(self.lines[first_visible_index])
                labels.append(self.line_labels[first_visible_index])
                
                if last_visible_index != first_visible_index:
                    handles.append(self.lines[last_visible_index])
                    labels.append(self.line_labels[last_visible_index])
            
            if handles:
                if hasattr(self, 'legend'):
                    self.legend.remove()
                self.legend = plt.legend(handles=handles, labels=labels, fontsize=int(self.fontsize_legend_spinbox.get()), ncol=self.legend_columns)
                self.legend.set_visible(True)
            else:
                if hasattr(self, 'legend'):
                    self.legend.set_visible(False)
            plt.draw()
        else:
            if hasattr(self, 'legend'):
                self.legend.set_visible(False)
            plt.draw()

if __name__ == "__main__":
    root = tk.Tk()
    scroll_frame = ScrollableFrame(root)
    scroll_frame.pack(fill="both", expand=True)
    app = PlotApp(root, scroll_frame)
    root.mainloop()