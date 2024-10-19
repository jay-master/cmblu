# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 17:05:50 2024

@author: Jaehyun
"""

import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.colors as mcolors
import mplcursors

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
        self.root.title("Nyquist Plotter")

        self.selected_color1 = None  # To store the first chosen color
        self.selected_color2 = None  # To store the second chosen color
        self.color_chosen = False  # Flag to check if colors are chosen
        self.gradient_enabled = tk.BooleanVar()  # Flag to check if gradient is enabled
        self.legend_entries = {}  # Dictionary to store legend entries

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        self.invert_var = tk.BooleanVar()
        self.invert_checkbutton = tk.Checkbutton(self.root, text="Invert Colors", variable=self.invert_var)
        self.invert_checkbutton.grid(row=9, column=4, padx=5, pady=5)
        
        self.file_button = tk.Button(self.root, text="Select File", command=self.load_file)
        self.file_button.grid(row=0, column=0, padx=5, pady=5)
    
        self.color_label1 = tk.Label(self.root, text="Select Line Color 1:")
        self.color_label1.grid(row=0, column=1, padx=5, pady=5)
    
        self.color_combobox1 = ttk.Combobox(self.root, values=list(TU_COLORS.keys()), width=10)
        self.color_combobox1.grid(row=0, column=2, padx=5, pady=5)
        self.color_combobox1.bind("<<ComboboxSelected>>", self.on_color_selected1)
    
        self.color_label2 = tk.Label(self.root, text="Select Line Color 2:")
        self.color_label2.grid(row=0, column=3, padx=5, pady=5)
    
        self.color_combobox2 = ttk.Combobox(self.root, values=list(TU_COLORS.keys()), width=10)
        self.color_combobox2.grid(row=0, column=4, padx=5, pady=5)
        self.color_combobox2.bind("<<ComboboxSelected>>", self.on_color_selected2)
    
        self.gradient_checkbutton = tk.Checkbutton(self.root, text="Enable Gradient", variable=self.gradient_enabled)
        self.gradient_checkbutton.grid(row=0, column=5, padx=5, pady=5)
    
        self.segment_label = tk.Label(self.root, text="Select Segments:")
        self.segment_label.grid(row=1, column=0, padx=5, pady=5)
    
        self.segment_frame = tk.Frame(self.root)
        self.segment_frame.grid(row=1, column=1, padx=5, pady=5)
    
        self.segment_scrollbar = tk.Scrollbar(self.segment_frame, orient=tk.VERTICAL)
        self.segment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        self.segment_listbox = tk.Listbox(self.segment_frame, selectmode=tk.EXTENDED, yscrollcommand=self.segment_scrollbar.set, height=10)
        self.segment_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.segment_listbox.bind("<<ListboxSelect>>", self.on_segment_selected)
        self.segment_listbox.bind('<Tab>', self.focus_next_widget)
    
        self.segment_scrollbar.config(command=self.segment_listbox.yview)
    
        self.legend_frame = tk.Frame(self.root)
        self.legend_frame.grid(row=2, column=0, columnspan=6, padx=5, pady=5)
    
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
    
        self.title_label = tk.Label(self.root, text="Plot Title:")
        self.title_label.grid(row=3, column=0, padx=5, pady=5)
        self.title_entry = tk.Entry(self.root)
        self.title_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=5)
        self.title_entry.bind('<Tab>', self.focus_next_widget)
    
        self.xlabel_label = tk.Label(self.root, text="X-axis Label:")
        self.xlabel_label.grid(row=4, column=0, padx=5, pady=5)
        self.xlabel_entry = tk.Entry(self.root)
        self.xlabel_entry.grid(row=4, column=1, padx=5, pady=5, columnspan=5)
        self.xlabel_entry.bind('<Tab>', self.focus_next_widget)
    
        self.ylabel_label = tk.Label(self.root, text="Y-axis Label:")
        self.ylabel_label.grid(row=5, column=0, padx=5, pady=5)
        self.ylabel_entry = tk.Entry(self.root)
        self.ylabel_entry.grid(row=5, column=1, padx=5, pady=5, columnspan=5)
        self.ylabel_entry.bind('<Tab>', self.focus_next_widget)
    
        self.fontsize_title_label = tk.Label(self.root, text="Title Font Size:")
        self.fontsize_title_label.grid(row=6, column=0, padx=5, pady=5)
        self.fontsize_title_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10, width=5)
        self.fontsize_title_spinbox.grid(row=6, column=1, padx=5, pady=5, columnspan=5)
        self.fontsize_title_spinbox.bind('<Tab>', self.focus_next_widget)
    
        self.fontsize_labels_label = tk.Label(self.root, text="Labels Font Size:")
        self.fontsize_labels_label.grid(row=7, column=0, padx=5, pady=5)
        self.fontsize_labels_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10, width=5)
        self.fontsize_labels_spinbox.grid(row=7, column=1, padx=5, pady=5, columnspan=5)
        self.fontsize_labels_spinbox.bind('<Tab>', self.focus_next_widget)
    
        self.fontsize_legend_label = tk.Label(self.root, text="Legend Font Size:")
        self.fontsize_legend_label.grid(row=8, column=0, padx=5, pady=5)
        self.fontsize_legend_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10, width=5)
        self.fontsize_legend_spinbox.grid(row=8, column=1, padx=5, pady=5, columnspan=5)
        self.fontsize_legend_spinbox.bind('<Tab>', self.focus_next_widget)
    
        self.fontsize_ticks_label = tk.Label(self.root, text="Ticks Font Size:")
        self.fontsize_ticks_label.grid(row=9, column=0, padx=5, pady=5)
        self.fontsize_ticks_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10, width=5)
        self.fontsize_ticks_spinbox.grid(row=9, column=1, padx=5, pady=5, columnspan=5)
        self.fontsize_ticks_spinbox.bind('<Tab>', self.focus_next_widget)
    
        self.legend_var = tk.BooleanVar()
        self.legend_checkbutton = tk.Checkbutton(self.root, text="Show Legend", variable=self.legend_var)
        self.legend_checkbutton.grid(row=10, column=0, padx=5, pady=5)
        self.legend_checkbutton.bind('<Tab>', self.focus_next_widget)

        self.legend_columns_label = tk.Label(self.root, text="Legend Columns:")
        self.legend_columns_label.grid(row=10, column=2, padx=5, pady=5)
        self.legend_columns_spinbox = tk.Spinbox(self.root, from_=1, to_=10, value=1, width=5)
        self.legend_columns_spinbox.grid(row=10, column=3, padx=5, pady=5)
        self.legend_columns_spinbox.bind('<Tab>', self.focus_next_widget)
    
        self.grid_var = tk.BooleanVar()
        self.grid_checkbutton = tk.Checkbutton(self.root, text="Show Grid", variable=self.grid_var)
        self.grid_checkbutton.grid(row=10, column=1, padx=5, pady=5)
        self.grid_checkbutton.bind('<Tab>', self.focus_next_widget)
    
        # Add entry widgets for x-axis and y-axis limits
        self.xmin_label = tk.Label(self.root, text="X-axis Min:")
        self.xmin_label.grid(row=11, column=0, padx=5, pady=5)
        self.xmin_entry = tk.Entry(self.root)
        self.xmin_entry.grid(row=11, column=1, padx=5, pady=5)
        self.xmin_entry.bind('<Tab>', self.focus_next_widget)
    
        self.xmax_label = tk.Label(self.root, text="X-axis Max:")
        self.xmax_label.grid(row=11, column=2, padx=5, pady=5)
        self.xmax_entry = tk.Entry(self.root)
        self.xmax_entry.grid(row=11, column=3, padx=5, pady=5)
        self.xmax_entry.bind('<Tab>', self.focus_next_widget)
    
        self.ymin_label = tk.Label(self.root, text="Y-axis Min:")
        self.ymin_label.grid(row=12, column=0, padx=5, pady=5)
        self.ymin_entry = tk.Entry(self.root)
        self.ymin_entry.grid(row=12, column=1, padx=5, pady=5)
        self.ymin_entry.bind('<Tab>', self.focus_next_widget)
    
        self.ymax_label = tk.Label(self.root, text="Y-axis Max:")
        self.ymax_label.grid(row=12, column=2, padx=5, pady=5)
        self.ymax_entry = tk.Entry(self.root)
        self.ymax_entry.grid(row=12, column=3, padx=5, pady=5)
        self.ymax_entry.bind('<Tab>', self.focus_next_widget)
      
        # Add entry widgets for figure width and height
        self.width_label = tk.Label(self.root, text="Figure Width:")
        self.width_label.grid(row=13, column=0, padx=5, pady=5)
        self.width_entry = tk.Entry(self.root)
        self.width_entry.grid(row=13, column=1, padx=5, pady=5)
        self.width_entry.bind('<Tab>', self.focus_next_widget)
    
        self.height_label = tk.Label(self.root, text="Figure Height:")
        self.height_label.grid(row=13, column=2, padx=5, pady=5)
        self.height_entry = tk.Entry(self.root)
        self.height_entry.grid(row=13, column=3, padx=5, pady=5)
        self.height_entry.bind('<Tab>', self.focus_next_widget)
    
        # Add entry widget for grid interval
        self.grid_interval_label = tk.Label(self.root, text="Grid Interval:")
        self.grid_interval_label.grid(row=14, column=0, padx=5, pady=5)
        self.grid_interval_entry = tk.Entry(self.root)
        self.grid_interval_entry.grid(row=14, column=1, padx=5, pady=5)
        self.grid_interval_entry.bind('<Tab>', self.focus_next_widget)
      
        self.plot_button = tk.Button(self.root, text="Plot", command=self.plot_data)
        self.plot_button.grid(row=15, column=0, columnspan=4, padx=5, pady=5)
        self.plot_button.bind('<Tab>', self.focus_next_widget)

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
            label = tk.Label(self.scrollable_legend_frame, text=f"Legend for Segment {segment}:")
            label.grid(row=index, column=0, padx=5, pady=5)
            entry = tk.Entry(self.scrollable_legend_frame)
            entry.grid(row=index, column=1, padx=5, pady=5)
            entry.bind('<Tab>', self.focus_next_widget)
            self.legend_entries[segment] = entry

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
        selected_segments = [int(self.segment_listbox.get(i)) for i in self.segment_listbox.curselection()]
        if not selected_segments:
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
            default_width = 10
            width = float(self.width_entry.get()) if self.width_entry.get() else default_width
            height = width / aspect_ratio * 1.15  # Adjust height based on aspect ratio
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for figure width.")
            return
    
        fig, ax = plt.subplots(figsize=(width, height))
        invert_colors = self.invert_var.get()
    
        if self.color_chosen:
            base_color1 = TU_COLORS[self.selected_color1]
            if self.gradient_enabled.get():
                base_color2 = TU_COLORS[self.selected_color2] if self.selected_color2 else base_color1
                gradient_colors = self.compute_gradient_colors(base_color1, base_color2, len(selected_segments))
            else:
                gradient_colors = [self.adjust_lightness(base_color1, (i + 1) / (len(selected_segments) + 1), invert=invert_colors) for i in range(len(selected_segments))]
    
            line_style = '-'
            lines = []
            scatters = []
            red_dots = []
            line_labels = []
            for i, segment in enumerate(selected_segments):
                segment_data = self.data[self.data['Segment'] == segment]
                line_color = gradient_colors[i]
                legend_text = self.legend_entries.get(str(segment), None)
                legend_text = legend_text.get() if legend_text and legend_text.get() else f'Segment {segment}'
                line, = ax.plot(segment_data['Zre (ohms)'], segment_data['Zim (ohms)'],
                                label=legend_text, linestyle=line_style, linewidth=1, color=line_color)
                lines.append(line)
                line_labels.append(legend_text)
    
                scatter = ax.scatter(segment_data['Zre (ohms)'], segment_data['Zim (ohms)'],
                                     marker='o', s=20, color=line_color)
                scatters.append(scatter)
                specific_data = segment_data[segment_data['Frequency (Hz)'].apply(
                    lambda x: any(10**j - 0.1*10**j <= x <= 10**j + 0.1*10**j for j in range(-6, 7)))]
                red_dot = ax.scatter(specific_data['Zre (ohms)'], specific_data['Zim (ohms)'],
                                     marker='o', s=20, color='red')
                red_dots.append(red_dot)
    
                cursor = mplcursors.cursor([scatter], multiple=True)
                @cursor.connect("add")
                def on_add(sel):
                    sel.annotation.set_text(f"{segment_data.iloc[sel.target.index]['Frequency (Hz)']:.0e}")
        else:
            line_styles = ['-', '--', '-.', ':']
            markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h']
            lines = []
            scatters = []
            red_dots = []
            line_labels = []
            for i, segment in enumerate(selected_segments):
                segment_data = self.data[self.data['Segment'] == segment]
                legend_text = self.legend_entries.get(str(segment), None)
                legend_text = legend_text.get() if legend_text and legend_text.get() else f'Segment {segment}'
                line, = ax.plot(segment_data['Zre (ohms)'], segment_data['Zim (ohms)'],
                                label=legend_text, linestyle=line_styles[i % len(line_styles)], linewidth=1)
                lines.append(line)
                line_labels.append(legend_text)
                scatter = ax.scatter(segment_data['Zre (ohms)'], segment_data['Zim (ohms)'],
                                     marker=markers[i % len(markers)], s=20)
                scatters.append(scatter)
                specific_data = segment_data[segment_data['Frequency (Hz)'].apply(
                    lambda x: any(10**j - 0.1*10**j <= x <= 10**j + 0.1*10**j for j in range(-6, 7)))]
                red_dot = ax.scatter(specific_data['Zre (ohms)'], specific_data['Zim (ohms)'],
                                     marker=markers[i % len(markers)], s=20, color='red')
                red_dots.append(red_dot)
    
                cursor = mplcursors.cursor([scatter], multiple=True)
                @cursor.connect("add")
                def on_add(sel):
                    sel.annotation.set_text(f"{segment_data.iloc[sel.target.index]['Frequency (Hz)']:.0e}")
    
        title = self.title_entry.get() if self.title_entry.get() else self.file_path.split('/')[-1]
        xlabel = self.xlabel_entry.get() if self.xlabel_entry.get() else '$Z_{re}$ (Ω)'
        ylabel = self.ylabel_entry.get() if self.ylabel_entry.get() else '$Z_{im}$ (Ω)'
    
        ax.set_title(title, fontsize=int(self.fontsize_title_spinbox.get()))
        ax.set_xlabel(xlabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        ax.set_ylabel(ylabel, fontsize=int(self.fontsize_ticks_spinbox.get()))
        ax.invert_yaxis()
        ax.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))
    
        if self.legend_var.get():
            legend_columns = int(self.legend_columns_spinbox.get()) if self.legend_columns_spinbox.get() else 1
            ax.legend(fontsize=int(self.fontsize_legend_spinbox.get()), ncol=legend_columns)
        if self.grid_var.get():
            ax.grid(color='lightgray', linestyle='--', linewidth=0.5)
    
        # Set axis limits
        if xmin is not None and xmax is not None:
            ax.set_xlim(left=xmin, right=xmax)
        if ymin is not None and ymax is not None:
            ax.set_ylim(bottom=ymin, top=ymax)
    
        ax.set_aspect('auto')  # Set aspect ratio to 'auto' to allow for custom width and height
    
        try:
            interval = float(self.grid_interval_entry.get()) if self.grid_interval_entry.get() else None
            if interval:
                ax.xaxis.set_major_locator(plt.MultipleLocator(interval))
                ax.yaxis.set_major_locator(plt.MultipleLocator(interval))
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for grid interval.")
    
        plt.tight_layout()
    
        cursor = mplcursors.cursor(lines, multiple=True)
        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set_text(sel.artist.get_label())
        @cursor.connect("remove")
        def on_remove(sel):
            pass
        
        # Adding check buttons in a separate window
        check_window = tk.Toplevel(self.root)
        check_window.title("Select Lines to Show/Hide")
        check_window.geometry("200x500")  # Adjust the size of the window as needed
        
        def func(label):
            index = line_labels.index(label)
            lines[index].set_visible(not lines[index].get_visible())
            scatters[index].set_visible(not scatters[index].get_visible())
            red_dots[index].set_visible(not red_dots[index].get_visible())
            plt.draw()
        
        checkbuttons = []
        for i, label in enumerate(line_labels):
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(check_window, text=label, variable=var,
                                command=lambda l=label: func(l))
            cb.pack(anchor='w')
            checkbuttons.append(cb)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()
