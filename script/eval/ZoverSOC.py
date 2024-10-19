# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 16:45:38 2024

@author: Jaehyun
"""

import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import matplotlib.pyplot as plt

# Hide the main tkinter window
root = Tk()
root.withdraw()

# Ask the user to select the files
file_paths = askopenfilenames(title="Select CSV files", filetypes=[("CSV files", "*.csv")])

# Load the first selected file (you can modify this to process multiple files)
if file_paths:
    file_path = file_paths[0]
    df = pd.read_csv(file_path)

    # Identify segments with non-zero frequency
    non_zero_segments = df[df['Frequency (Hz)'] != 0]['Segment'].unique()

    # Define the SOC values, starting from 100%, down to 0%, then back up to 100%
    soc_values = list(range(100, -1, -5)) + list(range(5, 101, 5))

    # Define the direction values
    direction_values = (
        ['dch'] * (len(range(100, 0, -5))) + 
        ['empty'] +  # Special case for 0%
        ['ch'] * (len(range(5, 101, 5)))
    )

    # Assign SOC and direction values to each segment with non-zero frequency
    segment_to_soc = {segment: soc for segment, soc in zip(non_zero_segments, soc_values)}
    segment_to_direction = {segment: direction for segment, direction in zip(non_zero_segments, direction_values)}

    # Create new 'SOC' and 'direction' columns in the dataframe
    df['SOC'] = df['Segment'].map(segment_to_soc)
    df['direction'] = df['Segment'].map(segment_to_direction)

    # Save the modified dataframe to a new CSV file
    output_file_path = file_path.replace('.csv', '_with_SOC_and_direction.csv')
    df.to_csv(output_file_path, index=False)

    print(f"Modified file saved as: {output_file_path}")

    # Function to plot |Z| (ohms) over SOC for each frequency
    def plot_z_over_soc(df):
        # Find the unique frequency values, excluding the zero frequencies
        unique_frequencies = df[df['Frequency (Hz)'] != 0]['Frequency (Hz)'].unique()

        # Sort SOC values for consistent x-axis plotting
        sorted_soc_values = sorted(list(range(100, -1, -5)) + list(range(5, 101, 5)))

        # Prepare a plot for each frequency
        for frequency in unique_frequencies:
            # Filter the dataframe for the current frequency
            df_freq = df[(df['Frequency (Hz)'] == frequency) & df['SOC'].notna()]
            
            # Plot |Z| (ohms) over SOC
            plt.figure(figsize=(10, 6))
            plt.plot(df_freq['SOC'], df_freq['|Z| (ohms)'], marker='o')
            plt.title(f'|Z| (ohms) vs SOC at {frequency} Hz')
            plt.xlabel('SOC (%)')
            plt.ylabel('|Z| (ohms)')
            plt.xticks(sorted_soc_values)
            plt.grid(True)
            plt.show()

    # Call the function to plot
    plot_z_over_soc(df)
    
else:
    print("No files selected.")




