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

    # Remove rows where 'Freq' is 0
    filtered_data = data[data['Frequency (Hz)'] != 0]

    # Rename specified columns
    column_mapping = {
        "Frequency (Hz)": "freq",
        "Zre (ohms)": "zre",
        "Zim (ohms)": "zim",
        "|Z| (ohms)": "magnitude",
        "Phase of Z (deg)": "phase"
    }
    filtered_data.rename(columns=column_mapping, inplace=True)

    # Determine direction for each segment
    filtered_data['Direction'] = ''
    segments = filtered_data['Segment'].unique()
    
    # Initialize first segment with 'dch'
    filtered_data.loc[filtered_data['Segment'] == segments[0], 'Direction'] = 'dch'
    
    # Process each segment
    for i in range(1, len(segments)):
        prev_segment = filtered_data[filtered_data['Segment'] == segments[i - 1]]
        current_segment = filtered_data[filtered_data['Segment'] == segments[i]]
        
        # Compare Potential (V) values
        last_potential_prev = prev_segment['Potential (V)'].iloc[-1]
        first_potential_current = current_segment['Potential (V)'].iloc[0]
        
        # Assign 'Direction' based on the comparison
        direction = 'dch' if first_potential_current < last_potential_prev else 'ch'
        filtered_data.loc[filtered_data['Segment'] == segments[i], 'Direction'] = direction

    # Prepare the output file path with "_modi" suffix
    output_file_path = asksaveasfilename(title="Save the amended file", defaultextension=".csv",
                                         initialfile=input_file_path.replace(".csv", "_modi.csv"),
                                         filetypes=[("CSV files", "*.csv")])
    if not output_file_path:
        print("No save location selected.")
        return

    # Save the filtered data
    filtered_data.to_csv(output_file_path, index=False)
    print(f"Filtered data saved to {output_file_path}")

# Run the function
process_and_save_data()
