import socket
from threading import Thread
from time import sleep
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = 'localhost'
port = 8080
s.connect((host, port))
login = input('Insira seu login: ')


def receber_mensagem():
    conversa = []
    while True:
        resposta_servidor = s.recv(2024).decode('UTF-8')
        conversa.append(resposta_servidor)
        if resposta_servidor == 'nullnullnull':
            break
        print(conversa[len(conversa)-1])


try:
    s.send(login.encode())
    resposta_servidor = s.recv(2024).decode('UTF-8')
    print(f'Servidor: {resposta_servidor}')

    if resposta_servidor == 'Não foi possivel achar esse cliente':
        nome = input('Insira seu nome: ')
        s.send(nome.encode())
        resposta_servidor = s.recv(2024).decode('UTF-8')
        print(f'Servidor: {resposta_servidor}')

    id_destinatario = input('Insira o id do destinatário: ')
    s.send(id_destinatario.encode())

    resposta_servidor = s.recv(2024).decode('UTF-8')
    print(f'Servidor: {resposta_servidor}')

    while resposta_servidor == 'Não foi possivel achar esse destinatário':
        id_destinatario = input('informe o id novamente: ')
        s.send(id_destinatario.encode())
        resposta_servidor = s.recv(2024).decode('UTF-8')
        print(f'Servidor: {resposta_servidor}')

    print('Servidor: Carregando as mensagens...')

    thread_receber_mensagem = Thread(target=receber_mensagem)
    thread_receber_mensagem.start()

    sleep(1)

    while True:
        sleep(0.2)
        mensagem = input('')
        while mensagem == '':
            mensagem = input('')
        s.send(f'{mensagem}'.encode())



except Exception as e:
    print(e)

finally:
    print('Encerrando a conexão')
