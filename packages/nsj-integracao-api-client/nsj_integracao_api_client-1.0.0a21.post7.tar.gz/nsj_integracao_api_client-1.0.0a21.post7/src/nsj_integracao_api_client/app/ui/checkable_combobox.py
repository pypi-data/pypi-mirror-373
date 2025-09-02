from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QMenu, QAction, QLineEdit, QWidgetAction,
    QCheckBox, QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt


class CheckableComboBox(QWidget):
    def __init__(self, items, parent=None, enable_search=True, placeholder="Selecionar entidades..."):
        super().__init__(parent)

        self.items = items
        self.checkboxes = []
        self.selected = set()
        self.placeholder = placeholder
        self.enable_search = enable_search

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.button = QToolButton(self)
        self.button.setText(self.placeholder)
        self.button.setPopupMode(QToolButton.InstantPopup)
        self.button.setStyleSheet("""
            QToolButton {
                background-color: white;
                border: 1px solid gray;
                padding: 2px 10px 2px 5px;
                border-radius: 2px;
            }
            QToolButton::menu-indicator {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                padding-left: 5px;
            }
        """)

        self.menu = QMenu(self)

        if self.enable_search:
            self.search = QLineEdit(self)
            self.search.setPlaceholderText("Buscar...")
            search_action = QWidgetAction(self.menu)
            search_action.setDefaultWidget(self.search)
            self.menu.addAction(search_action)
            self.menu.aboutToShow.connect(self.on_menu_open)
            self.search.textChanged.connect(self.filter_items)

        self.action_select_all = QAction("Marcar todos", self.menu)
        self.action_unselect_all = QAction("Desmarcar todos", self.menu)
        self.action_select_all.triggered.connect(self.select_all)
        self.action_unselect_all.triggered.connect(self.unselect_all)
        self.menu.addAction(self.action_select_all)
        self.menu.addAction(self.action_unselect_all)
        self.menu.addSeparator()

        self.populate_menu()
        self.button.setMenu(self.menu)
        self.layout.addWidget(self.button)


    def on_menu_open(self):
        if self.enable_search:
            self.search.clear()
            self.filter_items("")  # Opcional: garante que todos os itens fiquem visíveis


    def populate_menu_old(self):
        for item in self.items:
            checkbox = QCheckBox(item)
            checkbox.setStyleSheet("QCheckBox { margin: 4px 8px; }")
            checkbox.stateChanged.connect(self.handle_check_change)

            action = QWidgetAction(self.menu)
            action.setDefaultWidget(checkbox)

            self.menu.addAction(action)
            self.checkboxes.append(checkbox)


    def populate_menu(self):
        # Widget que conterá os checkboxes
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)
        self.scroll_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        #self.scroll_layout.addSpacerItem(self.scroll_spacer)


        self.checkboxes = []
        for item in self.items:
            checkbox = QCheckBox(item)
            checkbox.setStyleSheet("QCheckBox { margin: 4px 8px; }")
            checkbox.stateChanged.connect(self.handle_check_change)
            self.scroll_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setMaximumHeight(200)  # <-- altura máxima do menu

        # Adiciona ao menu
        scroll_action = QWidgetAction(self.menu)
        scroll_action.setDefaultWidget(self.scroll_area)
        self.menu.addAction(scroll_action)
        ##


    def handle_check_change(self):
        self.selected = {cb.text() for cb in self.checkboxes if cb.isChecked()}


    def filter_items_old(self, text):
        text = text.lower()
        for cb in self.checkboxes:
            cb.setVisible(text in cb.text().lower())
        self.scroll_widget.adjustSize()
        self.scroll_area.ensureVisible(0, 0)


    def filter_items(self, text):
        text = text.lower()
        visible_count = 0

        for cb in self.checkboxes:
            is_visible = text in cb.text().lower()
            cb.setVisible(is_visible)
            if is_visible:
                visible_count += 1

        self.scroll_widget.adjustSize()

        # Estima altura necessária (aproximadamente 30px por checkbox + margem)
        item_height = 30
        margin = 10
        max_height = 200
        desired_height = min(max_height, visible_count * item_height + margin)
        self.scroll_area.setFixedHeight(desired_height)

        self.scroll_area.ensureVisible(0, 0)


    def select_all(self):
        for cb in self.checkboxes:
            cb.setChecked(True)
        self.handle_check_change()


    def unselect_all(self):
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.handle_check_change()


    def checked_items(self):
        return sorted(self.selected)

