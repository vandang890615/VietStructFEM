"""
Basic Floor System Example
Simple example showing how to use Steel Deck FEM Calculator
"""

from steeldeckfem.core import FloorSystemFEMAnalyzer, get_wind_pressure
from types import SimpleNamespace

def main():
    print("=" * 60)
    print("Steel Deck FEM - Basic Example")
    print("=" * 60)
    
    # 1. Define floor system layout
    layout = SimpleNamespace(
        length=20,  # m
        width=15,  # m  
        floor_height=4.0,  # m
        column_spacing_x=5.0,  # m
        column_spacing_y=5.0,  # m
        main_beam_direction='X',  # X or Y
        secondary_beam_spacing=2.5  # m
    )
    
    # 2. Define member sections
    # Column section
    layout.column_spec = SimpleNamespace(
        h=300,  # mm
        b=300,  # mm
        tf=10,  # mm
        tw=15,  # mm
        area=0,  # Will be calculated
        ix=0    # Will be calculated
    )
    
    # Calculate column properties
    h_cm, b_cm = layout.column_spec.h/10, layout.column_spec.b/10
    tf_cm, tw_cm = layout.column_spec.tf/10, layout.column_spec.tw/10
    layout.column_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
    layout.column_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
    
    # Main beam section
    layout.main_beam_spec = SimpleNamespace(
        h=500, b=200, tf=10, tw=8, area=0, ix=0
    )
    h_cm, b_cm = layout.main_beam_spec.h/10, layout.main_beam_spec.b/10
    tf_cm, tw_cm = layout.main_beam_spec.tf/10, layout.main_beam_spec.tw/10
    layout.main_beam_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
    layout.main_beam_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
    
    # Secondary beam section
    layout.secondary_beam_spec = SimpleNamespace(
        h=300, b=150, tf=8, tw=6, area=0, ix=0
    )
    h_cm, b_cm = layout.secondary_beam_spec.h/10, layout.secondary_beam_spec.b/10
    tf_cm, tw_cm = layout.secondary_beam_spec.tf/10, layout.secondary_beam_spec.tw/10
    layout.secondary_beam_spec.area = 2*b_cm*tf_cm + (h_cm-2*tf_cm)*tw_cm
    layout.secondary_beam_spec.ix = (b_cm*h_cm**3/12) - ((b_cm-tw_cm)*(h_cm-2*tf_cm)**3/12)
    
    # 3. Get wind load for location
    wind_data = get_wind_pressure("Hà Nội")
    print(f"\nVùng gió: {wind_data['zone']} - Wo = {wind_data['Wo']} kg/m2")
    
    # 4. Define loads
    loads = {
        'live_load': 400,  # kg/m2
        'dead_load_finish': 30  # kg/m2
    }
    
    print(f"Live load: {loads['live_load']} kg/m2")
    print(f"Dead load: {loads['dead_load_finish']} kg/m2\n")
    
    # 5. Create analyzer and build model
    print("Building FEM model...")
    analyzer = FloorSystemFEMAnalyzer()
    analyzer.build_fem_model(layout, loads)
    
    # 6. Run analysis
    print("Running FEM analysis...")
    results = analyzer.run_analysis()
    
    # 7. Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    max_def = results['max_deflection']
    print(f"\nMax deflection: {max_def['value']:.2f} mm")
    print(f"At node: {max_def['node']}")
    print(f"Limit: {max_def['limit']}")
    
    # Critical members
    if 'critical_members' in results:
        critical = results['critical_members']
        failed_count = len(critical['failed_members'])
        
        print(f"\nFailed members: {failed_count}")
        
        if critical['columns']['name']:
            col = critical['columns']
            print(f"\nCritical column: {col['name']}")
            print(f"  Unity check: {col['unity']:.3f}")
            print(f"  Status: {col['status']}")
        
        if critical['main_beams']['name']:
            beam = critical['main_beams']
            print(f"\nCritical main beam: {beam['name']}")
            print(f"  Unity check: {beam['unity']:.3f}")
            print(f"  Status: {beam['status']}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
