# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:48:43 2024

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
    'Grün': '#49cb40'
}

class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")
        self.root.geometry("1600x800")  # Set window size to a landscape ratio

        self.selected_color = None  # To store the chosen color
        self.color_chosen = False  # Flag to check if a color is chosen
        self.legend_entries = {}  # Dictionary to store legend entries

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        self.file_button = tk.Button(self.root, text="Select File", command=self.load_file)
        self.file_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.color_label = tk.Label(self.root, text="Select Line Color:")
        self.color_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.color_combobox = ttk.Combobox(self.root, values=list(TU_COLORS.keys()))
        self.color_combobox.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.color_combobox.bind("<<ComboboxSelected>>", self.on_color_selected)

        self.plot_type_label = tk.Label(self.root, text="Select Plot Type:")
        self.plot_type_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        self.plot_type_combobox = ttk.Combobox(self.root, values=["Elapsed Time vs Potential", "Elapsed Time vs Current", "Elapsed Time vs Both"])
        self.plot_type_combobox.grid(row=0, column=4, padx=10, pady=10, sticky="w")
        self.plot_type_combobox.current(0)

        self.segment_label = tk.Label(self.root, text="Select Segments:")
        self.segment_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Create a frame for the listbox and scrollbar
        self.segment_frame = tk.Frame(self.root)
        self.segment_frame.grid(row=1, column=1, padx=10, pady=10, columnspan=3, sticky="w")

        self.segment_scrollbar = tk.Scrollbar(self.segment_frame, orient=tk.VERTICAL)
        self.segment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.segment_listbox = tk.Listbox(self.segment_frame, selectmode=tk.EXTENDED, yscrollcommand=self.segment_scrollbar.set, height=10)
        self.segment_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.segment_listbox.bind("<<ListboxSelect>>", self.on_segment_selected)

        self.segment_scrollbar.config(command=self.segment_listbox.yview)

        self.legend_label = tk.Label(self.root, text="Legends:")
        self.legend_label.grid(row=1, column=4, padx=10, pady=10, sticky="nw")

        self.legend_frame = tk.Frame(self.root, height=100, width=300, relief=tk.SUNKEN, borderwidth=1)
        self.legend_frame.grid(row=1, column=5, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.legend_canvas = tk.Canvas(self.legend_frame)
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
        self.title_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.title_entry = tk.Entry(self.root)
        self.title_entry.grid(row=2, column=1, padx=10, pady=10, columnspan=3, sticky="w")

        self.xlabel_label = tk.Label(self.root, text="X-axis Label:")
        self.xlabel_label.grid(row=2, column=4, padx=10, pady=10, sticky="w")
        self.xlabel_entry = tk.Entry(self.root)
        self.xlabel_entry.grid(row=2, column=5, padx=10, pady=10, columnspan=2, sticky="w")

        self.ylabel_label = tk.Label(self.root, text="Y-axis Label:")
        self.ylabel_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.ylabel_entry = tk.Entry(self.root)
        self.ylabel_entry.grid(row=3, column=1, padx=10, pady=10, columnspan=3, sticky="w")

        self.fontsize_title_label = tk.Label(self.root, text="Title Font Size:")
        self.fontsize_title_label.grid(row=3, column=4, padx=10, pady=10, sticky="w")
        self.fontsize_title_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_title_spinbox.grid(row=3, column=5, padx=10, pady=10, columnspan=2, sticky="w")

        self.fontsize_labels_label = tk.Label(self.root, text="Labels Font Size:")
        self.fontsize_labels_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.fontsize_labels_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_labels_spinbox.grid(row=4, column=1, padx=10, pady=10, columnspan=3, sticky="w")

        self.fontsize_legend_label = tk.Label(self.root, text="Legend Font Size:")
        self.fontsize_legend_label.grid(row=4, column=4, padx=10, pady=10, sticky="w")
        self.fontsize_legend_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_legend_spinbox.grid(row=4, column=5, padx=10, pady=10, columnspan=2, sticky="w")

        self.fontsize_ticks_label = tk.Label(self.root, text="Ticks Font Size:")
        self.fontsize_ticks_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.fontsize_ticks_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_ticks_spinbox.grid(row=5, column=1, padx=10, pady=10, columnspan=3, sticky="w")

        self.legend_var = tk.BooleanVar()
        self.legend_checkbutton = tk.Checkbutton(self.root, text="Show Legend", variable=self.legend_var)
        self.legend_checkbutton.grid(row=5, column=4, padx=10, pady=10, sticky="w")

        self.grid_var = tk.BooleanVar()
        self.grid_checkbutton = tk.Checkbutton(self.root, text="Show Grid", variable=self.grid_var)
        self.grid_checkbutton.grid(row=5, column=5, padx=10, pady=10, sticky="w")

        self.plot_button = tk.Button(self.root, text="Plot", command=self.plot_data)
        self.plot_button.grid(row=6, column=0, columnspan=7, padx=10, pady=10, sticky="we")

    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.data = pd.read_csv(self.file_path)
            segments = self.data['Segment'].unique()
            self.segment_listbox.delete(0, tk.END)
            for segment in segments:
                self.segment_listbox.insert(tk.END, segment)

    def on_color_selected(self, event):
        self.selected_color = self.color_combobox.get()
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
            self.legend_entries[segment] = entry

    def plot_data(self):
        selected_segments = [int(self.segment_listbox.get(i)) for i in self.segment_listbox.curselection()]
        if not selected_segments:
            messagebox.showwarning("No Segments Selected", "Please select at least one segment to plot.")
            return

        plot_type = self.plot_type_combobox.get()

        if plot_type == "Elapsed Time vs Both":
            fig, ax1 = plt.subplots(figsize=(10, 6))
            ax2 = ax1.twinx()

            combined_data = pd.concat([self.data[self.data['Segment'] == segment] for segment in selected_segments])

            voltage_line, = ax1.plot(combined_data['Elapsed Time (s)'], combined_data['Potential (V)'],
                                     label="Voltage", color=TU_COLORS['TU-Rot'])
            current_line, = ax2.plot(combined_data['Elapsed Time (s)'], combined_data['Current (A)'],
                                     label="Current", color=TU_COLORS['Blau'], linestyle='--')

            ax1.set_xlabel("Elapsed Time (s)")
            ax1.set_ylabel("Voltage (V)", color=TU_COLORS['TU-Rot'])
            ax2.set_ylabel("Current (A)", color=TU_COLORS['Blau'])

            title = self.title_entry.get() if self.title_entry.get() else self.file_path.split('/')[-1]
            ax1.set_title(title, fontsize=int(self.fontsize_title_spinbox.get()))

            if self.legend_var.get():
                lines = [voltage_line, current_line]
                labels = [line.get_label() for line in lines]
                ax1.legend(lines, labels, loc='best')

            if self.grid_var.get():
                ax1.grid(color='lightgray', linestyle='--', linewidth=0.5)
                # ax2.grid(color='lightgray', linestyle='--', linewidth=0.5)

            plt.tight_layout()
            plt.show()

        else:
            fig, ax = plt.subplots(figsize=(10, 6))

            combined_data = pd.concat([self.data[self.data['Segment'] == segment] for segment in selected_segments])

            if plot_type == "Elapsed Time vs Potential":
                ax.plot(combined_data['Elapsed Time (s)'], combined_data['Potential (V)'],
                        label="Voltage",
                        linestyle='-',
                        linewidth=1,
                        color=TU_COLORS['TU-Rot'])
            elif plot_type == "Elapsed Time vs Current":
                ax.plot(combined_data['Elapsed Time (s)'], combined_data['Current (A)'],
                        label="Current",
                        linestyle='-',
                        linewidth=1,
                        color=TU_COLORS['Blau'])

            title = self.title_entry.get() if self.title_entry.get() else self.file_path.split('/')[-1]
            xlabel = self.xlabel_entry.get() if self.xlabel_entry.get() else 'X-axis'
            ylabel = self.ylabel_entry.get() if self.ylabel_entry.get() else 'Y-axis'

            ax.set_title(title, fontsize=int(self.fontsize_title_spinbox.get()))
            ax.set_xlabel(xlabel, fontsize=int(self.fontsize_labels_spinbox.get()))
            ax.set_ylabel(ylabel, fontsize=int(self.fontsize_ticks_spinbox.get()))
            ax.tick_params(axis='both', which='major', labelsize=int(self.fontsize_ticks_spinbox.get()))

            if self.legend_var.get():
                ax.legend(fontsize=int(self.fontsize_legend_spinbox.get()))

            if self.grid_var.get():
                ax.grid(color='lightgray', linestyle='--', linewidth=0.5)

            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()

