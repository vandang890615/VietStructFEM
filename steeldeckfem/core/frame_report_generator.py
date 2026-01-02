# import handcalcs.render # Removed to avoid IPython dependency error
from handcalcs.decorator import handcalc
import os

@handcalc(jupyter_display=False)
def calculate_frame_checks_latex(L, H, q, support_type):
    """
    Shows a representative check for the frame.
    """
    # 1. Inputs
    # ---------
    Span = L
    Height = H
    Load = q
    
    # 2. Approximate Moments (for illustration)
    # ----------------------------------------
    # For a fixed portal frame under uniform load:
    if support_type == "Fixed":
        M_max_beam = (q * L**2) / 12  # Fixed ends approx
        M_max_col = (q * L**2) / 24   # Approx transfer driven
    else:
        M_max_beam = (q * L**2) / 8   # Simply supported beam approx
        M_max_col = 0                 # Pinned base (simplified)
        
    return locals()

class FrameReportGenerator:
    """Generates HTML reports for Frame Analysis"""
    
    @staticmethod
    def generate_report(params, output_path="reports/frame_report.html"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        latex_code, results = calculate_frame_checks_latex(
            L=params['L'],
            H=params['H'],
            q=params['q'],
            support_type=params['support']
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Frame Analysis Report</title>
            <meta charset="utf-8">
            <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{ font-family: 'Segoe UI'; max-width: 900px; margin: 0 auto; padding: 40px; }}
                h1, h2 {{ color: #2c3e50; }}
                .calc-box {{ background: #fdfdfd; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Thuyết minh Tính toán Khung (Frame Analysis)</h1>
            <p><b>Dự án:</b> VietStructFEM</p>
            <p><b>Loại khung:</b> Portal Frame 2D</p>
            
            <h2>1. Số liệu đầu vào & Nội lực Sơ bộ</h2>
            <div class="calc-box">
                {latex_code}
            </div>
            
            <h2>2. Kết quả từ Phân tích Phần tử Hữu hạn (FEM)</h2>
            <p>Đã thực hiện phân tích bằng phương pháp Matrix Stiffness Method (thư viện <i>anastruct</i>).</p>
            <p>Vui lòng xem biểu đồ nội lực chi tiết và chuyển vị trong phần mềm.</p>
            
        </body>
        </html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return os.path.abspath(output_path)
