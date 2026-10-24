"""
Bulk runner: reads numbers from Excel, normalises them, runs each platform
checker and writes one results row per number.
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add engine directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'engine'))
sys.path.append(os.path.dirname(__file__))

# Platform checkers live in engine/. Each exposes signal(number) -> bool.
# NOTE: in this public version they are stubs that return simulated results;
# the real platform checks are not included.
import whatsapp, telegram, instagram, facebook, snapchat
from normalizer import normalize_india



def _yes_no(engine, number):
    return "YES" if engine.signal(number) else "NO"


def run_bulk(input_file, output_file):
    """
    Process mobile numbers from input Excel and generate output Excel
    
    Args:
        input_file (str): Path to input Excel file with 'Mobile Number' column
        output_file (str): Path where output Excel should be saved
    """
    try:
        # Read input Excel
        print(f"Reading input file: {input_file}")
        df = pd.read_excel(input_file, dtype={'Mobile Number': str})
        
        if 'Mobile Number' not in df.columns:
            raise ValueError("Input Excel must contain 'Mobile Number' column")
        
        # Get mobile numbers
        mobile_numbers = df['Mobile Number'].dropna().astype(str).tolist()
        print(f"Found {len(mobile_numbers)} mobile numbers to process")
        
        # Process each number
        results = []
        for i, raw in enumerate(mobile_numbers, 1):
            mobile = normalize_india(raw)
            if mobile is None:
                print(f"Skipping invalid number at row {i}")
                continue
            print(f"Processing {i}/{len(mobile_numbers)}")
            
            # Call your existing engine functions
            result = {
                'Mobile Number': mobile,
                'WhatsApp': _yes_no(whatsapp, mobile),
                'Telegram': _yes_no(telegram, mobile),
                'Instagram': _yes_no(instagram, mobile),
                'Facebook': _yes_no(facebook, mobile),
                'Snapchat': _yes_no(snapchat, mobile),
                'Checked On': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            results.append(result)
        
        # Create output DataFrame
        output_df = pd.DataFrame(results)
        
        # Save to Excel
        print(f"Saving results to: {output_file}")
        output_df.to_excel(output_file, index=False)
        
        print(f"✓ Processing complete! Results saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error during processing: {str(e)}")
        raise


if __name__ == '__main__':
    # Test the function
    if len(sys.argv) != 3:
        print("Usage: python bulk_runner.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    run_bulk(input_file, output_file)