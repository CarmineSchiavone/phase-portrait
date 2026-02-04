import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

def main():
    st.set_page_config(page_title="Interactive Phase Portrait", layout="wide")
    st.title("Math Sandbox: Interactive & Animated")

    # --- Sidebar: Configuration ---
    with st.sidebar:
        st.header("1. System")
        eq_x = st.text_input("dx/dt =", value="y")
        eq_y = st.text_input("dy/dt =", value="sin(x) - 0.2*y") # Damped pendulum
        
        st.header("2. Animation")
        t_max = st.slider("Time Duration", 5.0, 50.0, 20.0)
        frames = st.slider("Animation Speed (Frames)", 50, 200, 100)
        
        st.header("3. Initial Condition")
        col1, col2 = st.columns(2)
        x0 = col1.number_input("x0", value=2.0, step=0.5)
        y0 = col2.number_input("y0", value=0.0, step=0.5)

    # --- Computation ---
    
    # 1. Grid for Vector Field
    range_val = 6.0
    # Use fewer points for Plotly to keep interaction smooth
    x = np.linspace(-range_val, range_val, 20)
    y = np.linspace(-range_val, range_val, 20)
    X, Y = np.meshgrid(x, y)
    
    # 2. Safety & Eval Wrapper
    local_scope = {
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi,
        "x": X, "y": Y
    }
    
    try:
        # Compute Vector Field
        U = eval(eq_x, {"__builtins__": None}, local_scope)
        V = eval(eq_y, {"__builtins__": None}, local_scope)

        # 3. Trajectory Calculation (for Animation)
        def system_func(state, t):
            step_scope = local_scope.copy()
            step_scope["x"] = state[0]
            step_scope["y"] = state[1]
            dxdt = eval(eq_x, {"__builtins__": None}, step_scope)
            dydt = eval(eq_y, {"__builtins__": None}, step_scope)
            return [dxdt, dydt]

        t_span = np.linspace(0, t_max, frames)
        sol = odeint(system_func, [x0, y0], t_span)
        
        # --- Plotly Visualization ---
        
        # 1. Create Quiver Plot (The Arrows)
        # We use figure_factory for easy quiver plots
        fig = ff.create_quiver(
            x, y, U, V,
            scale=0.2,
            arrow_scale=0.3,
            name='Vector Field',
            line=dict(color='gray', width=1)
        )
        
        # 2. Add the Static Trajectory Line (The Path)
        fig.add_trace(go.Scatter(
            x=sol[:, 0], y=sol[:, 1],
            mode='lines',
            name='Trajectory',
            line=dict(color='red', width=2)
        ))

        # 3. Create Animation Frames (The Moving Dot)
        # This creates a list of "snapshots" for the play button
        animation_frames = []
        for i in range(len(t_span)):
            animation_frames.append(
                go.Frame(
                    data=[go.Scatter(
                        x=[sol[i, 0]], 
                        y=[sol[i, 1]], 
                        mode='markers',
                        marker=dict(color='blue', size=12)
                    )],
                    name=str(i)
                )
            )
            
        fig.frames = animation_frames

        # 4. Add the Dot (Initial Position) to the main figure
        fig.add_trace(go.Scatter(
            x=[x0], y=[y0],
            mode='markers',
            name='Particle',
            marker=dict(color='blue', size=12)
        ))

        # 5. Configure Layout & Buttons
        fig.update_layout(
            title="Phase Portrait (Click Play to Animate)",
            xaxis_title="x",
            yaxis_title="y",
            width=800,
            height=600,
            hovermode="closest",
            # Add Play/Pause Buttons
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                buttons=[dict(
                    label="Play",
                    method="animate",
                    args=[None, dict(frame=dict(duration=50, redraw=False), fromcurrent=True)]
                ),
                dict(
                    label="Pause",
                    method="animate",
                    args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))]
                )]
            )]
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Equation Error: {e}")

if __name__ == "__main__":
    main()