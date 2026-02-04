import streamlit as st
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go

# --- 1. The Math (Lorenz System) ---
def lorenz(state, t, sigma, rho, beta):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]

def main():
    st.set_page_config(page_title="Lorenz Attractor 3D", layout="wide")
    st.title("The Butterfly Effect: Lorenz Attractor")

    # --- 2. Sidebar Controls ---
    with st.sidebar:
        st.header("Parameters")
        # Classic values: sigma=10, rho=28, beta=8/3
        rho = st.slider("Rho (Rayleigh Number)", 0.0, 100.0, 28.0, help="Controls the chaos. Try 10, 28, or 99.")
        sigma = st.slider("Sigma (Prandtl Number)", 0.0, 50.0, 10.0)
        beta = st.slider("Beta", 0.0, 5.0, 8.0/3.0)
        
        st.header("Simulation Settings")
        dt = 0.01
        steps = st.slider("Number of Steps", 1000, 10000, 3000)
        speed = st.slider("Animation Speed (Skip Frames)", 1, 50, 10, help="Higher = Faster Animation")

    # --- 3. Compute Trajectory ---
    # Initial condition (slightly off-center to ensure movement)
    initial_state = [1.0, 1.0, 1.0]
    t = np.arange(0, steps * dt, dt)
    
    # Solve ODE
    sol = odeint(lorenz, initial_state, t, args=(sigma, rho, beta))
    x, y, z = sol[:, 0], sol[:, 1], sol[:, 2]

    # --- 4. 3D Visualization ---
    
    # A. The Static Path (The "Shape")
 
    fig = go.Figure()
    
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        name='Attractor Path',
        # Opacity belongs here, as a property of the Trace
        opacity=0.4, 
        # Line dictionary only handles color, width, etc.
        line=dict(color=z, colorscale='Viridis', width=2)
    ))

    # B. The Animation (The "Dynamics")
    # We create frames for the particle moving along the path
    frames = []
    # We skip points to make the animation lighter/faster
    progression_indices = range(0, len(t), speed)
    
    for k in progression_indices:
        frames.append(go.Frame(
            data=[go.Scatter3d(
                x=[x[k]], y=[y[k]], z=[z[k]],
                mode='markers',
                marker=dict(color='red', size=6, symbol='diamond'),
                name='Particle'
            )],
            name=str(k)
        ))

    # Add the initial particle
    fig.add_trace(go.Scatter3d(
        x=[x[0]], y=[y[0]], z=[z[0]],
        mode='markers',
        name='Particle',
        marker=dict(color='red', size=6, symbol='diamond')
    ))

    # C. Layout & Controls
    fig.update_layout(
        title=f"Lorenz Attractor (Rho={rho})",
        width=900, height=700,
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z'),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)) # Nice viewing angle
        ),
        template="plotly_dark",
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0.1, y=0.9,
            buttons=[
                dict(label="▶ Play",
                     method="animate",
                     args=[None, dict(frame=dict(duration=10, redraw=True), fromcurrent=True)]),
                dict(label="⏸ Pause",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))])
            ]
        )]
    )

    # Attach frames to figure
    fig.frames = frames

    # Show Plot
    col1, col2 = st.columns([3, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("### What are we seeing?")
        st.info("""
        **The Lorenz Attractor**
        
        This is a solution to a system of equations originally used to model atmospheric convection.
        
        * **The Particle:** Represents the state of the system at a moment in time.
        * **The Wings:** The particle orbits one wing, then unpredictably switches to the other.
        * **Chaos:** Note that the path never crosses itself!
        """)

if __name__ == "__main__":
    main()