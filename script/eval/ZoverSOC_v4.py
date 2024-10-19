# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 18:34:48 2024

@author: Jaehyun
"""

import pandas as pd
from tkinter import Tk, Label, Button, Listbox, EXTENDED, Checkbutton
from tkinter.filedialog import askopenfilenames
import matplotlib.pyplot as plt
import numpy as np

class ZoverSOCPlotter:
    def __init__(self):
        self.root = Tk()
        self.root.title("Select Frequencies to Plot")
        self.df = None
        self.show_legend = True
        self.setup_gui()

    def setup_gui(self):
        label = Label(self.root, text="Select Frequencies:")
        label.pack()

        self.listbox = Listbox(self.root, selectmode=EXTENDED)
        self.listbox.pack()

        self.show_legend_checkbox = Checkbutton(
            self.root, 
            text="Show Legend", 
            command=self.toggle_legend
        )
        self.show_legend_checkbox.select()  # Start with checkbox selected
        self.show_legend_checkbox.pack()

        plot_button = Button(self.root, text="Plot", command=self.on_plot_button_click)
        plot_button.pack()

    def toggle_legend(self):
        self.show_legend = not self.show_legend
        print(f"Legend toggled. New state: {self.show_legend}")

    def load_data(self):
        file_paths = askopenfilenames(title="Select CSV files", filetypes=[("CSV files", "*.csv")])
        if file_paths:
            file_path = file_paths[0]
            self.df = pd.read_csv(file_path)
            self.process_data()
            self.populate_frequency_list()
            return True
        return False

    def process_data(self):
        non_zero_segments = self.df[self.df['Frequency (Hz)'] != 0]['Segment'].unique()
        soc_values = list(range(100, -1, -5)) + list(range(5, 101, 5))
        direction_values = (['dch'] * (len(range(100, 0, -5))) + ['empty'] + ['ch'] * (len(range(5, 101, 5))))
        
        segment_to_soc = {segment: soc for segment, soc in zip(non_zero_segments, soc_values)}
        segment_to_direction = {segment: direction for segment, direction in zip(non_zero_segments, direction_values)}
        
        self.df['SOC'] = self.df['Segment'].map(segment_to_soc)
        self.df['direction'] = self.df['Segment'].map(segment_to_direction)

    def populate_frequency_list(self):
        unique_frequencies = sorted(self.df[self.df['Frequency (Hz)'] != 0]['Frequency (Hz)'].unique())
        for freq in unique_frequencies:
            self.listbox.insert('end', freq)

    def on_plot_button_click(self):
        selected_indices = self.listbox.curselection()
        selected_frequencies = [float(self.listbox.get(i)) for i in selected_indices]
        print(f"Plotting with show_legend: {self.show_legend}")
        self.plot_z_over_soc(selected_frequencies, self.show_legend)

    def plot_z_over_soc(self, selected_frequencies, show_legend):
        colors = np.linspace(0, 1, len(selected_frequencies))
        colormap = plt.get_cmap('coolwarm')
        sorted_soc_values = sorted(list(range(100, -1, -5)) + list(range(5, 101, 5)))
        
        plt.figure(figsize=(12, 8))

        for idx, frequency in enumerate(selected_frequencies):
            df_freq = self.df[(self.df['Frequency (Hz)'] == frequency) & self.df['SOC'].notna()]
            frequency_label = '0.1 Hz' if np.isclose(frequency, 0.1, atol=1e-7) else f'{frequency:.6f} Hz'
            
            df_dch = df_freq[df_freq['direction'] == 'dch']
            plt.plot(df_dch['SOC'], df_dch['|Z| (ohms)'], linestyle='-', marker='o', 
                     color=colormap(colors[idx]), label=f'{frequency_label} (dch)')
            
            df_ch = df_freq[df_freq['direction'] == 'ch']
            plt.plot(df_ch['SOC'], df_ch['|Z| (ohms)'], linestyle='--', marker='s', 
                     color=colormap(colors[idx]), label=f'{frequency_label} (ch)')
        
        plt.title('|Z| (ohms) vs SOC for Selected Frequencies')
        plt.xlabel('SOC (%)')
        plt.ylabel('|Z| (ohms)')
        plt.xticks(sorted_soc_values)
        plt.grid(True, which='both', linestyle='--', linewidth=0.7)
        
        print(f"show_legend in plot function: {show_legend}")
        
        if show_legend:
            plt.legend(loc='best', fontsize='small')
        else:
            plt.legend().set_visible(False)
        plt.tight_layout()
        plt.show()

    def run(self):
        if self.load_data():
            self.root.mainloop()
        else:
            print("No files selected.")

if __name__ == "__main__":
    plotter = ZoverSOCPlotter()
    plotter.run()