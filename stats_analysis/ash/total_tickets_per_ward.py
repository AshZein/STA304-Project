import pandas as pd
import os


def calculate_total_fines_per_ward(ward_dataset_path, output_path):
    # Load ward dataset
    ward_df = pd.read_csv(ward_dataset_path)
    
    # Ensure 'set_fine_amount' column exists
    if 'set_fine_amount' not in ward_df.columns:
        raise ValueError("'set_fine_amount' column not found in the dataset.")
    
    # Group by ward and calculate total fines
    total_fines_per_ward = ward_df.groupby('AREA_L_CD')['set_fine_amount'].sum().reset_index()
    ward_counts = ward_df.groupby('AREA_L_CD').size().reset_index(name='ticket_count')
    ward_counts['ticket_percentage'] = (ward_counts['ticket_count'] / ward_counts['ticket_count'].sum()) * 100
    print("tickets per ward:")
    print(ward_counts)
    
    # Save to output file
    ward_counts.to_csv(output_path, index=False)
    print(f"Total tickets per ward saved to {output_path}")