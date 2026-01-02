
from handcalcs.decorator import handcalc
import os

@handcalc(jupyter_display=False)
def check_steel_beam_latex(M_max, V_max, fy, Zx, Aw):
    """
    Kiem tra ben dam thep (Steel Beam Check)
    """
    # 1. So lieu dau vao (Inputs)
    # ---------------------------
    Moment = M_max # kNm
    Shear = V_max # kN
    YieldStrength = fy # MPa
    PlasticModulus = Zx # cm3
    WebArea = Aw # cm2
    
    # 2. Kiem tra Ben Chi uon (Bending Capacity)
    # ------------------------------------------
    # M_pl = fy * Zx
    M_pl = (fy * (Zx * 1000)) / 1e6 # kNm
    
    # He so an toan (Safety Factor)
    phi_b = 0.9 
    M_n = phi_b * M_pl # kNm
    
    Is_Bending_Safe = M_n > Moment
    
    # 3. Kiem tra Chi cat (Shear Capacity)
    # ------------------------------------
    # V_n = 0.6 * fy * Aw
    V_n = (0.6 * fy * (Aw * 100)) / 1000 # kN
    phi_v = 0.9
    V_cap = phi_v * V_n # kN
    
    Is_Shear_Safe = V_cap > Shear
    
    return locals()

class SteelDeckReportGenerator:
    """Generates HTML reports for Steel Deck Analysis"""
    
    @staticmethod
    def generate_report(params, output_path="reports/steel_deck_report.html"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Calculate simplified checks for demonstration
        # Assume these values come from the FEM analysis
        # For demo, we estimate them based on simplified beam theory
        L = params.get('L_beam', 6.0)
        q = params.get('q_load', 10.0)
        
        M_max = (q * L**2) / 8
        V_max = (q * L) / 2
        
        # Beam properties (Approximation for a generic I-section)
        h = params.get('h', 300)
        tw = params.get('tw', 6)
        bf = params.get('b', 150)
        tf = params.get('tf', 8)
        
        # Zx approx
        Zx = (bf * tf * (h - tf) + tw * (h - 2*tf)**2 / 4) / 1000 # cm3 approx
        Aw = (h - 2*tf) * tw / 100 # cm2
        
        latex_code, results = check_steel_beam_latex(
            M_max=M_max,
            V_max=V_max,
            fy=245, # SS400
            Zx=Zx,
            Aw=Aw
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Steel Deck Analysis Report</title>
            <meta charset="utf-8">
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{ font-family: 'Segoe UI'; max-width: 900px; margin: 0 auto; padding: 40px; background-color: #f5f6fa; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .calc-box {{ background: #ffffff; border: 1px solid #ddd; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
                .summary {{ background: #e8f6f3; padding: 15px; border-radius: 5px; border-left: 5px solid #1abc9c; margin-top: 20px; }}
                .pass {{ color: green; font-weight: bold; }}
                .fail {{ color: red; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Thuyết minh Tính toán Sàn Deck</h1>
            <p><b>Dự án:</b> VietStructFEM Verification</p>
            <p><b>Cấu kiện:</b> Dầm phụ điển hình (Secondary Beam)</p>
            
            <h2>1. Thông số đầu vào (Input Data)</h2>
            <ul>
                <li>Nhịp dầm (L): {L:.2f} m</li>
                <li>Tải trọng phân bố (q): {q:.2f} kN/m</li>
                <li>Vật liệu: Thép hình (Giả định SS400, fy=245 MPa)</li>
                <li>Tiết diện: H{h}x{bf}x{tw}x{tf}</li>
            </ul>
            
            <h2>2. Kiểm tra Khả năng chịu lực (Capacity Check)</h2>
            <div class="calc-box">
                {latex_code}
            </div>
            
            <div class="summary">
                <h3>Kết luận:</h3>
                <p>Khả năng chịu uốn: <span class="{ 'pass' if results['Is_Bending_Safe'] else 'fail' }">
                    { 'ĐẠT (OK)' if results['Is_Bending_Safe'] else 'KHÔNG ĐẠT (FAIL)' }
                </span></p>
                <p>Khả năng chịu cắt: <span class="{ 'pass' if results['Is_Shear_Safe'] else 'fail' }">
                    { 'ĐẠT (OK)' if results['Is_Shear_Safe'] else 'KHÔNG ĐẠT (FAIL)' }
                </span></p>
            </div>
            
            <p><i>Lưu ý: Tính toán trên là tự động dựa trên thư viện <b>handcalcs</b>.</i></p>
            
        </body>
        </html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return os.path.abspath(output_path)
