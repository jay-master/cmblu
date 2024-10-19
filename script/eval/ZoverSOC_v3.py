import pandas as pd
from tkinter import Tk, Label, Button, Listbox, EXTENDED
from tkinter.filedialog import askopenfilenames
import matplotlib.pyplot as plt
import numpy as np

# Hide the main tkinter window
root = Tk()
root.withdraw()

# Ask the user to select the files
file_paths = askopenfilenames(title="Select CSV files", filetypes=[("CSV files", "*.csv")])

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

    # Function to plot |Z| (ohms) over SOC for selected frequencies
    def plot_z_over_soc(df, selected_frequencies):
        colors = np.linspace(0, 1, len(selected_frequencies))
        colormap = plt.get_cmap('coolwarm')

        # Define sorted SOC values within the function
        sorted_soc_values = sorted(list(range(100, -1, -5)) + list(range(5, 101, 5)))
        
        plt.figure(figsize=(12, 8))

        for idx, frequency in enumerate(selected_frequencies):
            df_freq = df[(df['Frequency (Hz)'] == frequency) & df['SOC'].notna()]

            # Adjust the label for 0.1 Hz
            if np.isclose(frequency, 0.1, atol=1e-7):
                frequency_label = '0.1 Hz'
            else:
                frequency_label = f'{frequency:.6f} Hz'
            
            # Plot discharge data with circle markers
            df_dch = df_freq[df_freq['direction'] == 'dch']
            plt.plot(df_dch['SOC'], df_dch['|Z| (ohms)'], linestyle='-', marker='o', 
                     color=colormap(colors[idx]), label=f'{frequency_label} (dch)')
            
            # Plot charge data with square markers
            df_ch = df_freq[df_freq['direction'] == 'ch']
            plt.plot(df_ch['SOC'], df_ch['|Z| (ohms)'], linestyle='--', marker='s', 
                     color=colormap(colors[idx]), label=f'{frequency_label} (ch)')
        
        plt.title('|Z| (ohms) vs SOC for Selected Frequencies')
        plt.xlabel('SOC (%)')
        plt.ylabel('|Z| (ohms)')
        plt.xticks(sorted_soc_values)
        plt.grid(True, which='both', linestyle='--', linewidth=0.7)
        plt.legend(loc='best', fontsize='small')
        plt.show()

    # Function to handle frequency selection and plotting
    def on_plot_button_click():
        selected_indices = listbox.curselection()
        selected_frequencies = [float(listbox.get(i)) for i in selected_indices]
        plot_z_over_soc(df, selected_frequencies)

    # GUI to select frequencies
    root = Tk()
    root.title("Select Frequencies to Plot")

    label = Label(root, text="Select Frequencies:")
    label.pack()

    listbox = Listbox(root, selectmode=EXTENDED)
    unique_frequencies = sorted(df[df['Frequency (Hz)'] != 0]['Frequency (Hz)'].unique())
    for freq in unique_frequencies:
        listbox.insert('end', freq)
    listbox.pack()

    plot_button = Button(root, text="Plot", command=on_plot_button_click)
    plot_button.pack()

    root.mainloop()

else:
    print("No files selected.")
