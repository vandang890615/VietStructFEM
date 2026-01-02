
import ezdxf
from ezdxf.enums import TextEntityAlignment

class FrameDXFExporter:
    """
    Exports a 2D Frame (anastruct SystemElements) to DXF
    """
    
    @staticmethod
    def export(ss, params, filename="exports/frame_layout.dxf"):
        """
        ss: anastruct SystemElements object
        params: dict of input params (L, H)
        """
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Define layers
        if 'GRID' not in doc.layers:
            doc.layers.add('GRID', color=1, linetype='DASHED') # Red
        if 'FRAME' not in doc.layers:
            doc.layers.add('FRAME', color=2, lineweight=35) # Yellow
        if 'TEXT' not in doc.layers:
            doc.layers.add('TEXT', color=7) # White/Black
            
        L = params.get('L', 6.0) * 1000 # Convert to mm
        H = params.get('H', 4.0) * 1000 # Convert to mm
        
        # 1. Draw Grid
        # Vertical Grids (A, B)
        msp.add_line((0, -1000), (0, H+1000), dxfattribs={'layer': 'GRID'})
        msp.add_text("A", height=300).set_placement((0, -1500), align=TextEntityAlignment.CENTER)
        
        msp.add_line((L, -1000), (L, H+1000), dxfattribs={'layer': 'GRID'})
        msp.add_text("B", height=300).set_placement((L, -1500), align=TextEntityAlignment.CENTER)
        
        # Horizontal Grids (1, 2)
        msp.add_line((-1000, 0), (L+1000, 0), dxfattribs={'layer': 'GRID'})
        msp.add_text("1", height=300).set_placement((-1500, 0), align=TextEntityAlignment.MIDDLE_RIGHT)

        msp.add_line((-1000, H), (L+1000, H), dxfattribs={'layer': 'GRID'})
        msp.add_text("2", height=300).set_placement((-1500, H), align=TextEntityAlignment.MIDDLE_RIGHT)
        
        # 2. Draw Frame Members
        # Extract elements from ss
        for element in ss.element_map.values():
            node_id1, node_id2 = element.node_id1, element.node_id2
            node1 = ss.node_map[node_id1]
            node2 = ss.node_map[node_id2]
            
            # Convert m to mm
            p1 = (node1.vertex[0] * 1000, node1.vertex[1] * 1000)
            p2 = (node2.vertex[0] * 1000, node2.vertex[1] * 1000)
            
            msp.add_line(p1, p2, dxfattribs={'layer': 'FRAME'})
            
        # 3. Add Supports (Symbols)
        support_supports = ss.supports_fixed + ss.supports_hinged + ss.supports_roll
        # anastruct support structure varies, checking node_id
        
        for node_id in ss.supports_fixed:
            node = ss.node_map[node_id]
            x, y = node.vertex[0]*1000, node.vertex[1]*1000
            # Draw rectangle for fixed
            msp.add_lwpolyline([(x-200, y), (x+200, y), (x+200, y-100), (x-200, y-100), (x-200, y)], dxfattribs={'layer': 'FRAME'})
            
        for node_id in ss.supports_hinged:
            node = ss.node_map[node_id]
            x, y = node.vertex[0]*1000, node.vertex[1]*1000
            # Draw triangle for pinned
            msp.add_lwpolyline([(x, y), (x-150, y-200), (x+150, y-200), (x, y)], dxfattribs={'layer': 'FRAME'})

        # 4. Dimensions
        dim = msp.add_linear_dim(
            base=(0, -800),
            p1=(0, 0),
            p2=(L, 0),
            dimstyle='EZDXF',
            dxfattribs={'layer': 'TEXT'}
        )
        dim.render()
        
        doc.saveas(filename)
        return filename
