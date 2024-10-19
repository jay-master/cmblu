# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 12:09:30 2024

@author: Jaehyun
"""

import tkinter as tk
from tkinter import ttk, filedialog, font
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Time vs. Voltage/Current Plotter")

        # Initialize empty dataframe
        self.data = pd.DataFrame()

        # Configure grid layout
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        # Frame for controls
        control_frame = tk.Frame(root)
        control_frame.grid(row=0, column=0, sticky="nw")

        # Variables
        self.plot_type = tk.StringVar(value="Voltage")
        self.segments = tk.StringVar(value="1")
        self.grid_on = tk.BooleanVar(value=True)
        self.font_size = tk.IntVar(value=10)

        # Controls
        ttk.Button(control_frame, text="Load Data", command=self.load_data).grid(row=0, column=0, sticky="we")
        
        ttk.Label(control_frame, text="Select Plot Type:").grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(control_frame, text="Voltage", variable=self.plot_type, value="Voltage").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(control_frame, text="Current", variable=self.plot_type, value="Current").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(control_frame, text="Both", variable=self.plot_type, value="Both").grid(row=2, column=2, sticky="w")

        ttk.Label(control_frame, text="Select Segment:").grid(row=3, column=0, sticky="w")
        self.segment_menu = ttk.Combobox(control_frame, textvariable=self.segments)
        self.segment_menu.grid(row=4, column=0, sticky="we")

        ttk.Label(control_frame, text="Font Size:").grid(row=5, column=0, sticky="w")
        self.font_size_spinbox = ttk.Spinbox(control_frame, from_=6, to_=20, textvariable=self.font_size)
        self.font_size_spinbox.grid(row=6, column=0, sticky="we")

        self.grid_check = ttk.Checkbutton(control_frame, text="Grid On", variable=self.grid_on)
        self.grid_check.grid(row=7, column=0, sticky="w")

        self.plot_button = ttk.Button(control_frame, text="Plot", command=self.plot)
        self.plot_button.grid(row=8, column=0, sticky="we")

        # Frame for plot
        self.plot_frame = tk.Frame(root)
        self.plot_frame.grid(row=1, column=0, sticky="nsew")

    def load_data(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        if file_paths:
            # Load data from the selected files
            data_list = [pd.read_csv(file) for file in file_paths]
            self.data = pd.concat(data_list, ignore_index=True)

            # Update the segment menu
            segments = list(self.data['Segment'].unique())
            self.segment_menu['values'] = segments
            if segments:
                self.segments.set(segments[0])

    def plot(self):
        plot_type = self.plot_type.get()
        selected_segment = self.segments.get()
        font_size = self.font_size.get()
        grid_on = self.grid_on.get()

        selected_data = self.data[self.data['Segment'] == int(selected_segment)]

        fig, ax1 = plt.subplots()

        ax1.set_xlabel('Time (s)', fontsize=font_size)
        color = '#c40d1e'  # TU-red
        if plot_type in ["Voltage", "Both"]:
            ax1.set_ylabel('Voltage (V)', color=color, fontsize=font_size)
            ax1.plot(selected_data['Time'], selected_data['Voltage'], color=color, label='Voltage (V)')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.legend(fontsize=font_size)

        if plot_type == "Both":
            ax2 = ax1.twinx()
            color = '#1f90cc'  # Blue
            ax2.set_ylabel('Current (A)', color=color, fontsize=font_size)
            ax2.plot(selected_data['Time'], selected_data['Current'], color=color, label='Current (A)')
            ax2.tick_params(axis='y', labelcolor=color)
            ax2.legend(fontsize=font_size)
        elif plot_type == "Current":
            color = '#1f90cc'  # Blue
            ax1.set_ylabel('Current (A)', color=color, fontsize=font_size)
            ax1.plot(selected_data['Time'], selected_data['Current'], color=color, label='Current (A)')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.legend(fontsize=font_size)

        if grid_on:
            ax1.grid()

        for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
            label.set_fontsize(font_size)

        plt.tight_layout()
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = PlotGUI(root)
    root.mainloop()
make GUI to plot elapsed time vs voltage or time vs current or both. Requirements: