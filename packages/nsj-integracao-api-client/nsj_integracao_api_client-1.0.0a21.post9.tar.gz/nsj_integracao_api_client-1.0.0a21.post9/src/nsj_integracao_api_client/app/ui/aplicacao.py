import sys

from PyQt5.QtWidgets import(
    QApplication, QWidget, QDialog
)

app = QApplication(sys.argv)

def render_view(builder):
    _view = QDialog()
    if builder:
        setattr(builder, "widget", _view)
        builder.setupUi(_view)
    return _view
