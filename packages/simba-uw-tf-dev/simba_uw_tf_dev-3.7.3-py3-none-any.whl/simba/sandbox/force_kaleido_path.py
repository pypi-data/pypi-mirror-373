import os
import sys
import plotly.graph_objects as go

def force_kaleido_conda_path():
    """Force Kaleido to look in the conda environment"""
    
    # Get the conda environment path
    conda_env_path = sys.prefix
    kaleido_path = os.path.join(conda_env_path, "lib", "site-packages", "kaleido")
    
    # Set environment variable to force Kaleido location
    os.environ['KALEIDO_PATH'] = kaleido_path
    
    print(f"Conda environment: {conda_env_path}")
    print(f"Kaleido path: {kaleido_path}")
    print(f"Environment variable set: KALEIDO_PATH={kaleido_path}")
    
    # Test if it works
    try:
        fig = go.Figure()
        img = fig.to_image(format="png")
        print("✅ Plotly/Kaleido working!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    force_kaleido_conda_path() 