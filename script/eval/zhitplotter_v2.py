import pandas as pd
import pyperclip
import io
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
import addcopyfighandler

def save_and_plot_clipboard_csv():
    """
    Reads CSV data from clipboard, saves it to a user-chosen file, and plots it.
    The data is expected to have columns: f (Hz), real_error (%), imag_error (%)
    """
    try:
        # Get clipboard content
        clipboard_text = pyperclip.paste()
        
        # Read CSV data from clipboard text
        df = pd.read_csv(io.StringIO(clipboard_text))
        
        # Create Tk root window and hide it
        root = Tk()
        root.withdraw()
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            title='Save Frequency Error Data As',
            initialfile='frequency_error_data.csv'
        )
        
        # If the user provided a file path
        if file_path:
            # Save to CSV file
            df.to_csv(file_path, index=False)
            print(f"Data successfully saved to {file_path}")
            
            # Display first few rows as confirmation
            print("\nFirst few rows of the saved data:")
            print(df.head())

            # Plot the data
            fig, ax1 = plt.subplots(figsize=(12, 8))
            ax2 = ax1.twinx()
            
            # Plot real and imaginary errors
            ax1.semilogx(df['f (Hz)'], df['real_error (%)'], color='blue', label='Real Error', marker='o', markersize=4, linestyle='-', linewidth=1)
            ax2.semilogx(df['f (Hz)'], df['imag_error (%)'], color='red', label='Imaginary Error', marker='o', markersize=4, linestyle='-', linewidth=1)
            
            # Define y-axis limits based on the largest error
            max_abs_error = max(abs(df['real_error (%)']).max(), abs(df['imag_error (%)']).max())
            limit = max_abs_error * 1.1
            ax1.set_ylim(-limit, limit)
            ax2.set_ylim(-limit, limit)
            
            # Set labels and title
            ax1.set_xlabel('Frequency (Hz)')
            ax1.set_ylabel('Re(Z) residual (%)', color='blue')
            ax2.set_ylabel('Im(Z) residual (%)', color='red')
            plt.title('Z-HIT')

            # Add grid and customize ticks
            ax1.grid(True, which="both", ls="-", alpha=0.2)
            ax1.tick_params(axis='y', colors='blue')
            ax2.tick_params(axis='y', colors='red')

            # Show the plot
            plt.tight_layout()
            plt.show()
        else:
            print("Save operation cancelled by user")
        
        # Clean up the Tk window
        root.destroy()

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    save_and_plot_clipboard_csv()
