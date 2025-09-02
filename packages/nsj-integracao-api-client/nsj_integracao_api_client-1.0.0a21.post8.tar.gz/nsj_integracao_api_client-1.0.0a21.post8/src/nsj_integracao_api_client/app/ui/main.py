import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestão de Eventos - PyQt5")
        self.setGeometry(100, 100, 800, 400)

        # Layout principal
        main_layout = QVBoxLayout()

        # Topo: seleção de ambiente e botões
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Ambiente:"))
        self.ambiente_combo = QComboBox()
        self.ambiente_combo.addItems(["Homologação", "Produção"])
        self.ambiente_combo.setCurrentText("Homologação")
        top_layout.addWidget(self.ambiente_combo)

        # Botões no topo
        for btn_text in ["Configurar", "Enviar Eventos", "Consultar Lotes"]:
            top_layout.addWidget(QPushButton(btn_text))

        main_layout.addLayout(top_layout)

        # Tabela
        self.table = QTableWidget(0, 6)  # 0 linhas, 6 colunas
        self.table.setHorizontalHeaderLabels(
            ["Empresa", "Grupo", "Evento", "Identificação", "Data/Hora Geração", "Enviar?"]
        )
        main_layout.addWidget(self.table)

        # Botão Enviar
        enviar_button = QPushButton("Enviar Eventos Selecionados")
        enviar_button.clicked.connect(self.enviar_eventos)
        main_layout.addWidget(enviar_button)

        # Preenchendo a tabela
        dados = [
            ("003", "Inicial/Tabela", "S-1010", "Cadastro Rubrica A", "06/08/2024 15:32:02"),
            ("003", "Não Periódico", "S-2200", "Admissão Funcionário 222", "20/09/2024 09:46:34"),
        ]
        self.preencher_tabela(dados)

        # Configurar o layout principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def preencher_tabela(self, dados):
        self.table.setRowCount(len(dados))
        for row_idx, (empresa, grupo, evento, identificacao, data_hora) in enumerate(dados):
            self.table.setItem(row_idx, 0, QTableWidgetItem(empresa))
            self.table.setItem(row_idx, 1, QTableWidgetItem(grupo))
            self.table.setItem(row_idx, 2, QTableWidgetItem(evento))
            self.table.setItem(row_idx, 3, QTableWidgetItem(identificacao))
            self.table.setItem(row_idx, 4, QTableWidgetItem(data_hora))

            # Checkbox na coluna "Enviar?"
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin-left:50%; margin-right:50%;")  # Centralizar o checkbox
            self.table.setCellWidget(row_idx, 5, checkbox)

    def enviar_eventos(self):
        selecionados = []
        for row_idx in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row_idx, 5)
            if checkbox and checkbox.isChecked():
                evento = self.table.item(row_idx, 2).text()  # Obter o valor da coluna "Evento"
                selecionados.append(evento)

        print("Eventos selecionados para envio:", selecionados)

def show_form():
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    show_form()