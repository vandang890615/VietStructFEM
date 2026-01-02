"""
Steel Deck FEM Calculator - Main entry point
"""

import sys
from PyQt5.QtWidgets import QApplication
from steeldeckfem.ui import MainWindow

def main():
    """Main application entry point"""
    # 1. Force UTF-8 for Windows Console (Fixes 'charmap' errors)
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # 2. Fix Matplotlib Fonts (Vietnamese support)
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 3. Suppress annoying font warnings
    import logging
    logging.getLogger('matplotlib.font_manager').disabled = True

    app = QApplication(sys.argv)
    app.setApplicationName("VietStructFEM Platform")
    app.setOrganizationName("VietStructFEM")
    
    # Global Exception Handler
    def excepthook(exc_type, exc_value, exc_tb):
        import traceback
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("Error:", tb)
        QMessageBox.critical(None, "Lỗi Không Mong Muốn (Critical Error)", 
                             f"Đã xảy ra lỗi nghiêm trọng:\n{exc_value}\n\nXem chi tiết trong console.")
        # Optional: Log to file
        with open("crash_log.txt", "a") as f:
            f.write(f"\n--- CRASH {sys.argv[0]} ---\n")
            f.write(tb)

    sys.excepthook = excepthook
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
