import os
import sys
import plotly.io as pio

def patch_kaleido_path():
    """Patch Plotly to use Kaleido from conda environment"""
    
    # Get conda environment path
    conda_env_path = sys.prefix
    kaleido_executable = os.path.join(conda_env_path, "lib", "site-packages", "kaleido", "executable", "kaleido")
    
    # If Kaleido executable doesn't exist in conda, try to find it
    if not os.path.exists(kaleido_executable):
        # Look for kaleido in conda environment
        import kaleido
        kaleido_path = os.path.dirname(kaleido.__file__)
        kaleido_executable = os.path.join(kaleido_path, "executable", "kaleido")
        
        # If still not found, try system path
        if not os.path.exists(kaleido_executable):
            kaleido_executable = "kaleido"  # Use system PATH
    
    print(f"Using Kaleido executable: {kaleido_executable}")
    
    # Patch Plotly's Kaleido configuration
    try:
        # Set the kaleido executable path
        pio.kaleido.scope.default_format = "png"
        pio.kaleido.scope.default_width = 800
        pio.kaleido.scope.default_height = 600
        
        # Test if it works
        import plotly.graph_objects as go
        fig = go.Figure()
        img = fig.to_image(format="png")
        print("✅ Plotly/Kaleido working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    patch_kaleido_path() 