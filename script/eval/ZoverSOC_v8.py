# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 10:31:11 2024

@author: Jaehyun
"""


import pandas as pd
from tkinter import Tk, Label, Button, Listbox, EXTENDED, Checkbutton, StringVar, OptionMenu, Entry
from tkinter.filedialog import askopenfilenames
import matplotlib.pyplot as plt
import numpy as np
import addcopyfighandler

class ZoverSOCPlotter:
    def __init__(self):
        self.root = Tk()
        self.root.title("Select Frequencies to Plot")
        self.df = None
        self.show_legend = True
        self.use_simple_legend = False
        self.plot_type = StringVar(value="|Z| (ohms)")  # Default to |Z| (ohms)
        self.figure_width = StringVar(value="12")  # Default width
        self.figure_height = StringVar(value="8")  # Default height
        self.soc_dch_start = StringVar(value="100")  # Default start SOC for discharge
        self.soc_dch_end = StringVar(value="0")     # Default end SOC for discharge
        self.soc_ch_start = StringVar(value="5")    # Default start SOC for charge
        self.soc_ch_end = StringVar(value="100")    # Default end SOC for charge
        self.setup_gui()

    def setup_gui(self):
        label = Label(self.root, text="Select Frequencies:")
        label.pack()

        self.listbox = Listbox(self.root, selectmode=EXTENDED)
        self.listbox.pack()

        # Add input fields for SOC range in discharge direction
        dch_frame = Label(self.root, text="Discharge SOC Range (Start - End):")
        dch_frame.pack()
        dch_start_entry = Entry(self.root, textvariable=self.soc_dch_start, width=5)
        dch_start_entry.pack(side="left")
        dch_end_entry = Entry(self.root, textvariable=self.soc_dch_end, width=5)
        dch_end_entry.pack(side="left")

        # Add input fields for SOC range in charge direction
        ch_frame = Label(self.root, text="Charge SOC Range (Start - End):")
        ch_frame.pack()
        ch_start_entry = Entry(self.root, textvariable=self.soc_ch_start, width=5)
        ch_start_entry.pack(side="left")
        ch_end_entry = Entry(self.root, textvariable=self.soc_ch_end, width=5)
        ch_end_entry.pack(side="left")

        self.show_legend_checkbox = Checkbutton(
            self.root, 
            text="Show Legend", 
            command=self.toggle_legend
        )
        self.show_legend_checkbox.select()  # Start with checkbox selected
        self.show_legend_checkbox.pack()

        self.simple_legend_checkbox = Checkbutton(
            self.root, 
            text="Use Simple Legend", 
            command=self.toggle_simple_legend
        )
        self.simple_legend_checkbox.pack()

        # Add option menu for selecting plot type
        plot_type_label = Label(self.root, text="Select Plot Type:")
        plot_type_label.pack()
        plot_type_menu = OptionMenu(self.root, self.plot_type, "|Z| (ohms)", "Phase of Z (deg)")
        plot_type_menu.pack()

        # Add entries for figure dimensions
        dim_frame = Label(self.root)
        dim_frame.pack()
        
        width_label = Label(dim_frame, text="Figure Width:")
        width_label.grid(row=0, column=0)
        width_entry = Entry(dim_frame, textvariable=self.figure_width, width=5)
        width_entry.grid(row=0, column=1)
        
        height_label = Label(dim_frame, text="Figure Height:")
        height_label.grid(row=1, column=0)
        height_entry = Entry(dim_frame, textvariable=self.figure_height, width=5)
        height_entry.grid(row=1, column=1)

        plot_button = Button(self.root, text="Plot", command=self.on_plot_button_click)
        plot_button.pack()

    def toggle_legend(self):
        self.show_legend = not self.show_legend
        print(f"Legend toggled. Show legend: {self.show_legend}")

    def toggle_simple_legend(self):
        self.use_simple_legend = not self.use_simple_legend
        print(f"Simple legend toggled. Use simple legend: {self.use_simple_legend}")

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
        width = float(self.figure_width.get())
        height = float(self.figure_height.get())
        soc_dch_start = int(self.soc_dch_start.get())
        soc_dch_end = int(self.soc_dch_end.get())
        soc_ch_start = int(self.soc_ch_start.get())
        soc_ch_end = int(self.soc_ch_end.get())

        # Filter data based on user-defined SOC ranges
        self.plot_z_over_soc(selected_frequencies, soc_dch_start, soc_dch_end, soc_ch_start, soc_ch_end, self.show_legend, self.use_simple_legend, self.plot_type.get(), width, height)

    @staticmethod
    def format_frequency(freq):
        if freq < 1:
            formatted = f"{freq:.4f}".rstrip('0')
            if formatted.endswith('.'):
                formatted += '0'
        else:
            formatted = f"{freq:.2f}".rstrip('0')
            if formatted.endswith('.'):
                formatted += '0'
        return f"{formatted} Hz"

    def plot_z_over_soc(self, selected_frequencies, soc_dch_start, soc_dch_end, soc_ch_start, soc_ch_end, show_legend, use_simple_legend, plot_type, width, height):
        colors = np.linspace(0, 1, len(selected_frequencies))
        colormap = plt.get_cmap('coolwarm')

        plt.figure(figsize=(width, height))

        # Filter data for discharge based on SOC range
        df_dch = self.df[(self.df['direction'] == 'dch') & (self.df['SOC'] <= soc_dch_start) & (self.df['SOC'] >= soc_dch_end)]

        # Filter data for charge based on SOC range
        df_ch = self.df[(self.df['direction'] == 'ch') & (self.df['SOC'] >= soc_ch_start) & (self.df['SOC'] <= soc_ch_end)]

        for idx, frequency in enumerate(selected_frequencies):
            color = colormap(colors[idx])

            # Plot discharge data
            df_dch_freq = df_dch[df_dch['Frequency (Hz)'] == frequency]
            plt.plot(df_dch_freq['SOC'], df_dch_freq[plot_type], linestyle='-', marker='o', color=color)

            # Plot charge data
            df_ch_freq = df_ch[df_ch['Frequency (Hz)'] == frequency]
            plt.plot(df_ch_freq['SOC'], df_ch_freq[plot_type], linestyle='--', marker='s', color=color)

        plt.title(f'{plot_type} vs SOC for Selected Frequencies')
        plt.xlabel('SOC (%)')
        plt.ylabel(plot_type)
        plt.xticks(sorted_soc_values)
        plt.grid(True, which='both', linestyle='--', linewidth=0.7)
        
        if show_legend:
            # Create legend entries
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='gray', label='Discharge', markersize=8, linestyle='-'),
                plt.Line2D([0], [0], marker='s', color='gray', label='Charge', markersize=8, linestyle='--')
            ]
            
            if use_simple_legend:
                legend_elements.extend([
                    plt.Line2D([0], [0], color=colormap(colors[0]), label=f'{self.format_frequency(lowest_freq)}'),
                    plt.Line2D([0], [0], color=colormap(colors[-1]), label=f'{self.format_frequency(highest_freq)}')
                ])
            else:
                for idx, frequency in enumerate(selected_frequencies):
                    legend_elements.append(plt.Line2D([0], [0], color=colormap(colors[idx]), label=self.format_frequency(frequency)))
            
            plt.legend(handles=legend_elements, loc='best', fontsize='small')
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