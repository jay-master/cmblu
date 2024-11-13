import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

def process_and_save_data():
    # Hide the Tkinter root window
    Tk().withdraw()

    # Ask the user to select the file to process
    input_file_path = askopenfilename(title="Select the CSV file to process", filetypes=[("CSV files", "*.csv")])
    if not input_file_path:
        print("No file selected.")
        return

    # Load the data
    data = pd.read_csv(input_file_path)

    # Remove rows where 'Frequency (Hz)' is 0
    filtered_data = data[data['Frequency (Hz)'] != 0].copy()

    # Rename specified columns
    column_mapping = {
        "Frequency (Hz)": "freq",
        "Zre (ohms)": "zre",
        "Zim (ohms)": "zim",
        "|Z| (ohms)": "magnitude",
        "Phase of Z (deg)": "phase"
    }
    filtered_data.rename(columns=column_mapping, inplace=True)

    # Add the 'Direction' column based on 'Segment' value
    filtered_data['Direction'] = filtered_data['Segment'].apply(lambda x: 'dch' if x <= 72 else 'ch')

    # Initialize SOC values
    soc_dch_start = 100
    soc_ch_start = 5

    # Create a new SOC column and calculate SOC based on Direction and Segment
    soc_values = []
    last_segment = None
    dch_counter, ch_counter = 0, 0

    for _, row in filtered_data.iterrows():
        segment = row['Segment']
        direction = row['Direction']

        # Reset counter when segment changes
        if segment != last_segment:
            if direction == 'dch':
                dch_counter += 1
            else:
                ch_counter += 1
            last_segment = segment

        # Assign SOC based on direction and segment order
        if direction == 'dch':
            soc = soc_dch_start - (dch_counter - 1) * 5
        else:
            soc = soc_ch_start + (ch_counter - 1) * 5
        soc_values.append(soc)

    filtered_data['SOC'] = soc_values

    # Remove segments where any 'SOC' value exceeds 100
    valid_segments = filtered_data.groupby('Segment').filter(lambda x: x['SOC'].max() <= 100)

    # Prepare the output file path with "_modi" suffix
    output_file_path = asksaveasfilename(title="Save the amended file", defaultextension=".csv",
                                         initialfile=input_file_path.replace(".csv", "_modi.csv"),
                                         filetypes=[("CSV files", "*.csv")])
    if not output_file_path:
        print("No save location selected.")
        return

    # Save the filtered data
    valid_segments.to_csv(output_file_path, index=False)
    print(f"Filtered data saved to {output_file_path}")

# Run the function
process_and_save_data()







