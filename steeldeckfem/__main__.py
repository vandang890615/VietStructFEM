"""
Steel Deck FEM Calculator - Main entry point
"""

import sys
from PyQt5.QtWidgets import QApplication
from steeldeckfem.ui import SteelDeckCalculatorDialog

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Steel Deck FEM Calculator")
    app.setOrganizationName("SteelDeckFEM")
    
    dialog = SteelDeckCalculatorDialog()
    dialog.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
