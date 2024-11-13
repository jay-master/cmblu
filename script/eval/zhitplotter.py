import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
import numpy as np

def plot_frequency_response():
    """
    Opens a CSV file via dialog and creates a frequency response plot
    with matched-scale dual y-axes for real and imaginary errors.
    Includes markers for each data point.
    """
    try:
        # Create Tk root window and hide it
        root = Tk()
        root.withdraw()
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            title='Select Frequency Response Data File'
        )
        
        if not file_path:
            print("No file selected")
            return
            
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Create the figure and primary y-axis
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # Create the secondary y-axis
        ax2 = ax1.twinx()
        
        # Plot data with both lines and markers
        line1 = ax1.semilogx(df['f (Hz)'], df['real_error (%)'], 
                            color='blue', label='Real Error',
                            marker='o', markersize=4, linestyle='-', linewidth=1)
        line2 = ax2.semilogx(df['f (Hz)'], df['imag_error (%)'], 
                            color='red', label='Imaginary Error',
                            marker='o', markersize=4, linestyle='-', linewidth=1)
        
        # Find the maximum absolute value across both real and imaginary errors
        max_abs_error = max(
            abs(df['real_error (%)']).max(),
            abs(df['imag_error (%)']).max()
        )
        
        # Add some padding to the limits (10%)
        limit = max_abs_error * 1.1
        
        # Set the same scale for both y-axes
        ax1.set_ylim(-limit, limit)
        ax2.set_ylim(-limit, limit)
        
        # Set labels and title
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Re(Z) residual (%)', color='blue')
        ax2.set_ylabel('Im(Z) residual (%)', color='red')
        plt.title('Z-HIT')
        
        # Add grid
        ax1.grid(True, which="both", ls="-", alpha=0.2)
        
        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        # ax1.legend(lines, labels, loc='upper right')
        
        # Color the tick labels to match their respective lines
        ax1.tick_params(axis='y', colors='blue')
        ax2.tick_params(axis='y', colors='red')
        
        # Adjust layout to prevent label clipping
        plt.tight_layout()
        
        # Show the plot
        plt.show()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    plot_frequency_response()
