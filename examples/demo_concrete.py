from concreteproperties.material import Concrete, SteelBar
from concreteproperties.concrete_section import ConcreteSection
from sectionproperties.pre.library.concrete_sections import concrete_rectangular_section
import matplotlib.pyplot as plt

def demo_rc_column():
    print("Generating RC Column Interaction Diagram...")
    
    # 1. Define Materials
    # Simplified material definition compatible with v0.7.0
    from concreteproperties.stress_strain_profile import ConcreteLinear, RectangularStressBlock, SteelElasticPlastic
    
    conc_profile = ConcreteLinear(elastic_modulus=30e3)
    conc_ultimate = RectangularStressBlock(compressive_strength=30, alpha=0.85, gamma=0.85, ultimate_strain=0.003)
    steel_profile = SteelElasticPlastic(yield_strength=400, elastic_modulus=200e3, fracture_strain=0.05)
    
    concrete = Concrete(
        name='C30', 
        density=2.4e-6, 
        stress_strain_profile=conc_profile, 
        ultimate_stress_strain_profile=conc_ultimate, 
        flexural_tensile_strength=3.0, 
        colour='lightgrey'
    )
    steel = SteelBar(name='CB400V', density=7.85e-6, stress_strain_profile=steel_profile, colour='grey')

    # 2. Create Geometry (REC 300x400)
    geom = concrete_rectangular_section(
        b=300, d=400,
        dia_top=20, n_top=3,
        dia_bot=20, n_bot=3,
        dia_side=20, n_side=0,
        c_top=30, c_bot=30, c_side=30,
        area_top=314, area_bot=314, area_side=314,
        conc_mat=concrete, steel_mat=steel
    )

    # 3. Create Section
    sec = ConcreteSection(geom)
    
    # 4. Plot Section
    print("Plotting section geometry...")
    sec.plot_section(filename="examples/rc_section.png", render=False)
    
    # 5. Calculate Interaction Diagram
    print("Calculating interaction diagram...")
    mi_res = sec.moment_interaction_diagram()
    
    # 6. Plot Interaction Diagram
    print("Plotting interaction diagram...")
    mi_res.plot_diagram(filename="examples/rc_interaction.png", render=False)
    
    print("Success! Check examples/rc_section.png and examples/rc_interaction.png")

if __name__ == "__main__":
    demo_rc_column()
