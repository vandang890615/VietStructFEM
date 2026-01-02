from anastruct import SystemElements
import matplotlib.pyplot as plt

def demo_2d_frame():
    print("Running 2D Frame Analysis (anaStruct)...")
    
    # 1. Create System
    ss = SystemElements()
    
    # 2. Define Elements (Portal Frame)
    # Column 1 (0,0) -> (0, 4)
    ss.add_element(location=[[0, 0], [0, 4]])
    # Beam (0, 4) -> (5, 4)
    ss.add_element(location=[[0, 4], [5, 4]])
    # Column 2 (5, 4) -> (5, 0)
    ss.add_element(location=[[5, 4], [5, 0]])
    
    # 3. Supports (Fixed at base)
    ss.add_support_fixed(node_id=1)
    ss.add_support_fixed(node_id=4)
    
    # 4. Loads
    # Distributed load on beam
    ss.q_load(element_id=2, q=-10) # 10 kN/m downward
    
    # 5. Solve
    ss.solve()
    
    # 6. Plotting
    print("Exporting diagrams...")
    # Structure
    fig1 = ss.show_structure(show=False)
    fig1.savefig("examples/frame_structure.png")
    
    # Bending Moment
    fig2 = ss.show_bending_moment(show=False)
    fig2.savefig("examples/frame_moment.png")
    
    # Displacement
    fig3 = ss.show_displacement(show=False)
    fig3.savefig("examples/frame_displacement.png")
    
    print("Success! Diagrams saved to examples/frame_*.png")

if __name__ == "__main__":
    demo_2d_frame()
