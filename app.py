import sys

from PySide6 import QtWidgets

from database import init_db
from ui.main_window import MainWindow

# Sovelluksen käynnistyspiste:
# 1) alustetaan tietokanta (taulut luodaan tarvittaessa)
# 2) käynnistetään Qt-tapahtumasilmukka
# 3) luodaan ja näytetään pääikkuna

if __name__ == "__main__":
    init_db()

    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())