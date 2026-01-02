import ezdxf

def demo_dxf_export():
    print("Creating DXF file...")
    
    # 1. Create new DXF document
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # 2. Draw Grid
    # Horizontal lines
    for i in range(5):
        y = i * 4000
        msp.add_line((0, y), (20000, y), dxfattribs={'color': 1}) # Red
        
    # Vertical lines
    for j in range(6):
        x = j * 4000
        msp.add_line((x, 0), (x, 16000), dxfattribs={'color': 3}) # Green
        
    # 3. Add Text
    msp.add_text("VietStructFEM Output", height=500).set_placement((0, -1000))
    
    # 4. Save
    filename = "examples/output_layout.dxf"
    doc.saveas(filename)
    
    print(f"Success! DXF saved to {filename}")

if __name__ == "__main__":
    demo_dxf_export()
