# -*- coding: utf-8 -*-
"""
Created on Thu May 23 21:27:52 2024

@author: Jaehyun
"""

import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import mplcursors
import addcopyfighandler

class PlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nyquist Plotter")

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        self.file_button = tk.Button(self.root, text="Select File", command=self.load_file)
        self.file_button.grid(row=0, column=0, padx=10, pady=10)

        self.segment_label = tk.Label(self.root, text="Select Segments:")
        self.segment_label.grid(row=1, column=0, padx=10, pady=10)

        self.segment_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.segment_listbox.grid(row=1, column=1, padx=10, pady=10)

        self.title_label = tk.Label(self.root, text="Plot Title:")
        self.title_label.grid(row=2, column=0, padx=10, pady=10)
        self.title_entry = tk.Entry(self.root)
        self.title_entry.grid(row=2, column=1, padx=10, pady=10)

        self.xlabel_label = tk.Label(self.root, text="X-axis Label:")
        self.xlabel_label.grid(row=3, column=0, padx=10, pady=10)
        self.xlabel_entry = tk.Entry(self.root)
        self.xlabel_entry.grid(row=3, column=1, padx=10, pady=10)

        self.ylabel_label = tk.Label(self.root, text="Y-axis Label:")
        self.ylabel_label.grid(row=4, column=0, padx=10, pady=10)
        self.ylabel_entry = tk.Entry(self.root)
        self.ylabel_entry.grid(row=4, column=1, padx=10, pady=10)

        self.fontsize_title_label = tk.Label(self.root, text="Title Font Size:")
        self.fontsize_title_label.grid(row=5, column=0, padx=10, pady=10)
        self.fontsize_title_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_title_spinbox.grid(row=5, column=1, padx=10, pady=10)

        self.fontsize_labels_label = tk.Label(self.root, text="Labels Font Size:")
        self.fontsize_labels_label.grid(row=6, column=0, padx=10, pady=10)
        self.fontsize_labels_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_labels_spinbox.grid(row=6, column=1, padx=10, pady=10)

        self.fontsize_legend_label = tk.Label(self.root, text="Legend Font Size:")
        self.fontsize_legend_label.grid(row=7, column=0, padx=10, pady=10)
        self.fontsize_legend_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_legend_spinbox.grid(row=7, column=1, padx=10, pady=10)

        self.fontsize_ticks_label = tk.Label(self.root, text="Ticks Font Size:")
        self.fontsize_ticks_label.grid(row=8, column=0, padx=10, pady=10)
        self.fontsize_ticks_spinbox = tk.Spinbox(self.root, from_=6, to_=20, value=10)
        self.fontsize_ticks_spinbox.grid(row=8, column=1, padx=10, pady=10)

        self.legend_var = tk.BooleanVar()
        self.legend_checkbutton = tk.Checkbutton(self.root, text="Show Legend", variable=self.legend_var)
        self.legend_checkbutton.grid(row=9, column=0, padx=10, pady=10)

        self.grid_var = tk.BooleanVar()
        self.grid_checkbutton = tk.Checkbutton(self.root, text="Show Grid", variable=self.grid_var)
        self.grid_checkbutton.grid(row=9, column=1, padx=10, pady=10)

        self.plot_button = tk.Button(self.root, text="Plot", command=self.plot_data)
        self.plot_button.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.data = pd.read_csv(self.file_path)
            segments = self.data['Segment'].unique()
            self.segment_listbox.delete(0, tk.END)
            for segment in segments:
                self.segment_listbox.insert(tk.END, segment)

    def plot_data(self):
        selected_segments = [int(self.segment_listbox.get(i)) for i in self.segment_listbox.curselection()]
        if not selected_segments:
            messagebox.showwarning("No Segments Selected", "Please select at least one segment to plot.")
            return

        line_styles = ['-', '--', '-.', ':']
        markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h']
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, segment in enumerate(selected_segments):
            segment_data = self.data[self.data['Segment'] == segment]
            ax.plot(segment_data['Zre (ohms)'], segment_data['Zim (ohms)'], 
                     label=f'Segment {segment}' if self.legend_var.get() else f'{segment}', 
                     linestyle=line_styles[i % len(line_styles)], 
                     linewidth=1)

            # Plot every data point
            scatter = ax.scatter(segment_data['Zre (ohms)'], segment_data['Zim (ohms)'],
                                 marker=markers[i % len(markers)], s=20)

            # Filter data for specific frequencies within the range
            specific_data = segment_data[segment_data['Frequency (Hz)'].apply(
                lambda x: any(10**j - 0.1*10**j <= x <= 10**j + 0.1*10**j for j in range(-6, 7)))]

            # Highlight specific data points with a different color
            ax.scatter(specific_data['Zre (ohms)'], specific_data['Zim (ohms)'],
                       marker=markers[i % len(markers)], s=20, color='red')

            # Add interactive cursors for the scatter plot
            cursor = mplcursors.cursor([scatter], multiple=True)

            # Display annotation for each point clicked
            @cursor.connect("add")
            def on_add(sel):
                sel.annotation.set_text(f"{segment_data.iloc[sel.target.index]['Frequency (Hz)']:.0e}")

        title = self.title_entry.get() if self.title_entry.get() else self.file_path.split('/')[-1]
        xlabel = self.xlabel_entry.get() if self.xlabel_entry.get() else '$Z_{re}$ (Ω)'
        ylabel = self.ylabel_entry.get() if self.ylabel_entry.get() else '$Z_{im}$ (Ω)'
        
        ax.set_title(title, fontsize=int(self.fontsize_title_spinbox.get()))
        ax.set_xlabel(xlabel, fontsize=int(self.fontsize_labels_spinbox.get()))
        ax.set_ylabel(ylabel, fontsize=int(self.fontsize_ticks_spinbox.get()))
        ax.invert_yaxis()  # Flip the y-axis
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
