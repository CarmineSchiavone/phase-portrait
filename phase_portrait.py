import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

def main():
    st.set_page_config(page_title="Phase Portrait Plotter", layout="wide")
    
    st.title("Math Sandbox: 2D ODE Phase Portraits")

    # --- Sidebar: System Configuration ---
    st.sidebar.header("1. Define System")
    # Using 'sin' instead of 'np.sin' is now supported via local_scope
    eq_x = st.sidebar.text_input("dx/dt =", value="y")
    eq_y = st.sidebar.text_input("dy/dt =", value="-x - 0.5*y") # Damped oscillator default

    # --- Sidebar: Trajectory Settings ---
    st.sidebar.header("2. Add Trajectory")
    show_traj = st.sidebar.checkbox("Show Specific Solution", value=True)
    
    # Grid columns for compact layout
    col1, col2 = st.sidebar.columns(2)
    with col1:
        x0 = st.number_input("Start X", value=2.0, step=0.1)
    with col2:
        y0 = st.number_input("Start Y", value=2.0, step=0.1)
        
    t_max = st.sidebar.slider("Time Duration", 1.0, 50.0, 10.0)

    # --- Sidebar: Plot Settings ---
    st.sidebar.header("3. Plot Settings")
    x_range = st.sidebar.slider("X Range", -10.0, 10.0, (-5.0, 5.0))
    y_range = st.sidebar.slider("Y Range", -10.0, 10.0, (-5.0, 5.0))
    density = st.sidebar.slider("Arrow Density", 0.5, 3.0, 1.5)

    # --- Computation ---
    
    # 1. Prepare the Grid
    x = np.linspace(x_range[0], x_range[1], 20)
    y = np.linspace(y_range[0], y_range[1], 20)
    X, Y = np.meshgrid(x, y)
    
    # 2. Define Scope for eval()
    local_scope = {
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi,
        "x": X, "y": Y  # These will be overwritten during trajectory calc
    }

    try:
        # --- A. Vector Field (Grid Calculation) ---
        # Eval uses meshgrid X, Y
        U = eval(eq_x, {"__builtins__": None}, local_scope)
        V = eval(eq_y, {"__builtins__": None}, local_scope)
        
        # --- B. Trajectory (Point Calculation) ---
        sol_forward, sol_backward = None, None
        
        if show_traj:
            # We need a function wrapper for odeint
            # state is [x, y], t is time
            def system_func(state, t):
                # Update scope to use scalar values (current point)
                # We copy scope to avoid modifying the original for the grid
                step_scope = local_scope.copy()
                step_scope["x"] = state[0]
                step_scope["y"] = state[1]
                
                # Eval returns a scalar here, not a grid
                dxdt = eval(eq_x, {"__builtins__": None}, step_scope)
                dydt = eval(eq_y, {"__builtins__": None}, step_scope)
                return [dxdt, dydt]

            # Time points
            t_span_fwd = np.linspace(0, t_max, 200)
            t_span_bwd = np.linspace(0, -t_max, 200) # Go backward in time too!
            
            # Solve IVP
            sol_forward = odeint(system_func, [x0, y0], t_span_fwd)
            sol_backward = odeint(system_func, [x0, y0], t_span_bwd)

        # --- Visualization ---
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 1. Plot Vector Field (Background)
        strm = ax.streamplot(X, Y, U, V, color=np.sqrt(U**2 + V**2), cmap='viridis', density=density)
        fig.colorbar(strm.lines, label='Velocity Magnitude')
        
        # 2. Plot Trajectory (Foreground)
        if show_traj and sol_forward is not None:
            # Forward path (solid red)
            ax.plot(sol_forward[:, 0], sol_forward[:, 1], 'r-', linewidth=2, label='Future')
            # Backward path (dashed red)
            ax.plot(sol_backward[:, 0], sol_backward[:, 1], 'r--', linewidth=2, alpha=0.5, label='Past')
            # Start point (green dot)
            ax.plot(x0, y0, 'go', markersize=8, label='Start')
            ax.legend(loc='upper right')

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_xlim(x_range)
        ax.set_ylim(y_range)
        ax.set_title('Phase Portrait & Trajectory')
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Ensure your equations use 'x' and 'y' and valid math functions like 'sin(x)'.")

if __name__ == "__main__":
    main()