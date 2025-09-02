from PyQt5.QtWidgets import QMessageBox, QWidget
from nsj_integracao_api_client.app.ui.aplicacao import app as _app

def mostrar_erro(parent: QWidget, mensagem: str):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Erro")
    msg.setText("Ocorreu um erro")
    msg.setInformativeText(mensagem)
    msg.exec_()

def mostrar_aviso(parent: QWidget, mensagem: str):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Aviso")
    msg.setText("Atenção")
    msg.setInformativeText(mensagem)
    msg.exec_()

def mostrar_info(parent: QWidget, mensagem: str):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Informação")
    msg.setText("Informação")
    msg.setInformativeText(mensagem)
    msg.exec_()

def confirmar_acao(parent: QWidget, mensagem: str = "Confirma?", titulo: str = "Confirmação") -> bool:
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(titulo)
    msg_box.setText(mensagem)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    # Traduzindo os botões
    msg_box.button(QMessageBox.Yes).setText("Sim")
    msg_box.button(QMessageBox.No).setText("Não")

    resposta = msg_box.exec_()
    return resposta == QMessageBox.Yes
