import pandas as pd
import pyperclip
import io
from tkinter import Tk, filedialog

def save_clipboard_csv():
    """
    Reads CSV data from clipboard and saves it to a file chosen by the user via dialog.
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
        
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')],
            title='Save CSV Data As',
            initialfile='frequency_error_data.csv'
        )
        
        # Check if a file was selected (user didn't cancel)
        if file_path:
            # Save to CSV file
            df.to_csv(file_path, index=False)
            print(f"Data successfully saved to {file_path}")
            
            # Display first few rows as confirmation
            print("\nFirst few rows of the saved data:")
            print(df.head())
            
            return df
        else:
            print("Save operation cancelled by user")
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    df = save_clipboard_csv()











