from sqlalchemy import select
from sqlalchemy.orm import Session
from Banco_de_dados import conectar
from Banco_de_dados import Cliente_bd
from Banco_de_dados import Mensagem_bd
from time import sleep
from threading import Thread
from datetime import datetime
import socket


class Cliente:
    def __init__(self, id_cliente, nome, login):
        self.id_cliente = id_cliente
        self.nome = nome
        self.login = login

engine = conectar()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = 'localhost'
port = 8080


def iniciar():
    cliente_socket, cliente_endereco = s.accept()
    run_cliente(cliente_socket, cliente_endereco)

def run_cliente(socket, endereco):
    print(f'Conectado com {endereco}')
    while True:
        cliente_login = socket.recv(2024).decode('UTF-8')
        cliente = get_cliente_by_login(cliente_login)

        while not cliente:
            socket.send('Não foi possivel achar esse cliente'.encode())
            cliente_nome = socket.recv(2024).decode()
            adicionar_cliente(cliente_login, cliente_nome)
            cliente = get_cliente_by_login(cliente_login)

        socket.send('Cliente encontrado'.encode())

        destinatario_id = socket.recv(2024).decode('UTF-8')
        destinatario_id = int(destinatario_id)
        destinatario = get_cliente_by_id(destinatario_id)

        while not destinatario:
            socket.send('Não foi possivel achar esse destinatário'.encode())
            destinatario_id = socket.recv(2024).decode('UTF-8')
            destinatario_id = int(destinatario_id)
            destinatario = get_cliente_by_id(destinatario_id)

        socket.send('Destinatário encontrado'.encode())
        thread_mensagem = Thread(target=esta_atualizado, args=(0, cliente.id_cliente, destinatario.id_cliente, socket))
        thread_mensagem.start()
        while True:
            mensagem = socket.recv(2024).decode('UTF-8')
            print("opa")
            salvar_mensagem(cliente.id_cliente, destinatario.id_cliente, mensagem)

def adicionar_cliente(login, nome):
    with Session(engine) as session:
        cliente_bd = Cliente_bd(login=login, nome=nome)
        session.add(cliente_bd)
        session.commit()
        session.close()
        print('Cliente criado com sucesso')


def get_cliente_by_login(login):
    with Session(engine) as session:
        stmt = select(Cliente_bd)
        try:
            for i in session.scalars(stmt):
                if i.login == login:
                    usuario = Cliente(i.id, i.nome, i.login)
                    session.close()
                    return usuario
            session.close()
            return False
        except Exception as e:
            print(e)


def get_cliente_by_id(cliente_id):
    with Session(engine) as session:
        stmt = select(Cliente_bd)
        try:
            for i in session.scalars(stmt):
                if i.id == cliente_id:
                    usuario = Cliente(i.id, i.nome, i.login)
                    session.close()
                    return usuario

            session.close()
            return False
        except Exception as e:
            print(e)
def salvar_mensagem(cliente_id, destinatario_id, mensagem):
    try:
        with Session(engine) as session:
            mensagem = Mensagem_bd(id_emissor=cliente_id, id_destinatario=destinatario_id, mensagem=mensagem, data=datetime.now())
            session.add(mensagem)
            session.commit()
            session.close()
        print("Mensagem salva com sucesso")
    except Exception as e:
        print(e)

def get_conversa(cliente_id, destinatario_id):
    conversa = []
    with Session(engine) as session:
        stmt = select(Mensagem_bd) \
            .where(Mensagem_bd.id_emissor.in_([destinatario_id, cliente_id])) \
            .where(Mensagem_bd.id_destinatario.in_([cliente_id, destinatario_id]))\
            .order_by(Mensagem_bd.data)
        for i in session.scalars(stmt):
            emissor = get_cliente_by_id(i.id_emissor)
            mensagem = [emissor.nome, i.mensagem]
            conversa.append(mensagem)
        session.close()
        return conversa

def esta_atualizado(numero_mensagens, cliente_id, destinatario_id, cliente_socket):
    while True:
        mensagens = get_conversa(cliente_id, destinatario_id)
        sleep(0.1)
        if len(mensagens) > numero_mensagens:
            faltam = len(mensagens) - numero_mensagens
            atualizar_mensagens(faltam, cliente_id, destinatario_id, cliente_socket)


def atualizar_mensagens(mensagens_faltando, cliente_id, destinatario_id, socket):
    conversa = get_conversa(cliente_id, destinatario_id)

    print(conversa[0])
    if mensagens_faltando == len(conversa):
        for mensagem in conversa:
            if mensagens_faltando == 0:
                break
            mensagens_faltando -= 1
            print(mensagem)
            socket.send(f'{mensagem[0]}: {mensagem[1]}'.encode())
        esta_atualizado(len(conversa), cliente_id, destinatario_id, socket)
    else:
        for mensagem in reversed(conversa):
            if mensagens_faltando == 0:
                break
            mensagens_faltando -= 1
            print(mensagem)
            socket.send(f'{mensagem[0]}: {mensagem[1]}'.encode())
        esta_atualizado(len(conversa), cliente_id, destinatario_id, socket)



s.bind((host, port))

s.listen()

print('aguardando conexão...')
while True:

    thread_inicio = Thread(target=iniciar)
    thread_inicio.start()


