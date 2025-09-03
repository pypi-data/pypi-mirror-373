import pandas as pd
import os

def check_csv_columns(csv_path):
    """Check what columns are actually in the CSV file"""
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
    
    try:
        df = pd.read_csv(csv_path)
        print(f"CSV file: {csv_path}")
        print(f"Shape: {df.shape}")
        print(f"Columns ({len(df.columns)}):")
        
        # Show all columns
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")
        
        # Check for probability columns
        prob_cols = [col for col in df.columns if col.startswith('Probability_')]
        print(f"\nProbability columns ({len(prob_cols)}):")
        for col in prob_cols:
            print(f"  - {col}")
        
        # Check for classifier columns (without Probability_ prefix)
        classifier_cols = [col for col in df.columns if not col.startswith('Probability_') and col not in ['scorer', 'DLC_resnet50']]
        print(f"\nPotential classifier columns ({len(classifier_cols)}):")
        for col in classifier_cols[:10]:  # Show first 10
            print(f"  - {col}")
        if len(classifier_cols) > 10:
            print(f"  ... and {len(classifier_cols)-10} more")
            
    except Exception as e:
        print(f"Error reading CSV: {e}")

if __name__ == "__main__":
    # Check the problematic file
    csv_path = r"C:\troubleshooting\RAT_NOR\project_folder\csv\machine_results\03152021_NOB_IOT_8.csv"
    check_csv_columns(csv_path) 