import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def main():
    st.set_page_config(page_title="Phase Portrait Plotter", layout="wide")
    
    st.title("Math Sandbox: 2D ODE Phase Portraits")
    st.markdown("""
    Visualize the system of differential equations:
    $$ 
    \\begin{cases} 
    \\dot{x} = f(x, y) \\\\ 
    \\dot{y} = g(x, y) 
    \\end{cases} 
    $$
    """)

    # --- Sidebar: User Inputs ---
    st.sidebar.header("System Configuration")
    
    # 1. Equation Inputs
    # We use default values corresponding to a simple harmonic oscillator
    st.sidebar.subheader("Define Equations")
    st.sidebar.caption("Use 'x' and 'y' as variables. Supports numpy functions as 'np.sin', etc.")
    eq_x = st.sidebar.text_input("dx/dt =", value="y")
    eq_y = st.sidebar.text_input("dy/dt =", value="-x")

    # 2. Plotting Parameters
    st.sidebar.subheader("Plot Settings")
    x_range = st.sidebar.slider("X Axis Range", -10.0, 10.0, (-5.0, 5.0))
    y_range = st.sidebar.slider("Y Axis Range", -10.0, 10.0, (-5.0, 5.0))
    density = st.sidebar.slider("Streamline Density", 0.5, 3.0, 1.5)
    
    # --- Computation Area ---
    
    # 1. Create the Meshgrid
    # We create a grid of 20x20 points to compute the arrows
    x = np.linspace(x_range[0], x_range[1], 20)
    y = np.linspace(y_range[0], y_range[1], 20)
    X, Y = np.meshgrid(x, y)
    
    # 2. Evaluate the Equations
    # WARNING: eval() is powerful but risky. In a local app, it's fine. 
    # In a public web app, sanitize inputs to prevent code injection.
    try:
    # Create a dictionary of allowed variables and functions

        # Create a dictionary of allowed variables and functions
        local_scope = {
            "x": X,
            "y": Y,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "sqrt": np.sqrt,
            "log": np.log,
            "pi": np.pi
        }
        
        # Calculate vector components using the new scope
        U = eval(eq_x, {"__builtins__": None}, local_scope)
        V = eval(eq_y, {"__builtins__": None}, local_scope)
        
        # --- Visualization ---
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Streamplot creates the flow lines
        # color maps to velocity magnitude
        strm = ax.streamplot(X, Y, U, V, color=np.sqrt(U**2 + V**2), cmap='viridis', density=density)
        fig.colorbar(strm.lines, label='Velocity Magnitude')
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'Phase Portrait')
        ax.grid(True, alpha=0.3)
        
        # Display in Streamlit
        st.pyplot(fig)

    except Exception as e:
        # This block catches errors (like typing "sinn(x)" instead of "sin(x)")
        st.error(f"Error parsing equations: {e}")
        st.info("Check your syntax. Example: 'sin(x)' or 'y - x'")
        
        # Normalize arrows for cleaner visualization (optional, keeps arrows same size)
        magnitude = np.sqrt(U**2 + V**2)
        U_norm = U / magnitude
        V_norm = V / magnitude
        
        # --- Visualization ---
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Streamplot creates the flow lines
        # X, Y are the grid; U, V are the vector components
        strm = ax.streamplot(X, Y, U, V, color=np.sqrt(U**2 + V**2), cmap='viridis', density=density)
        fig.colorbar(strm.lines, label='Velocity Magnitude')
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'Phase Portrait')
        ax.grid(True, alpha=0.3)
        
        # Display in Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error parsing equations: {e}")
        st.info("Check your syntax. Make sure to use 'x' and 'y'. Example: 'x - x*y'")

if __name__ == "__main__":
    main()