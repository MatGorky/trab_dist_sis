import os
import platform
from typing import Callable, TypeAlias
import rpyc

HOST = 'localhost'  # maquina onde esta o servidor
PORT = 10001    # porta que o servidor esta escutando

clear = ""
userID = None
UserId: TypeAlias = str

Topic: TypeAlias = str

# como é um sistema simples, irei utilizar números para definir a ação
# 0 é tela inicial, 1 é registro, 2 é consultar, 3 é remover e 4 é finalizar o sistema
modo = 0


class Content:
    author: UserId
    topic: Topic
    data: str


def iniciaCliente():
    conn = rpyc.connect(HOST, PORT)
    # apenas definindo o comando para limpeza do console
    global clear
    if platform.system() == 'Windows':
        clear = 'cls'
    else:
        clear = 'clear'

    return conn


# código da interface de usuário

def print_interface():
    global modo
    os.system(clear)
    print("Bem vindo," + userID + "!\n")
    print("O que deseja fazer?")
    print("1 - Listar tópicos")
    print("2 - Inscrever-se em um tópico")
    print("3 - Publicar")
    print("4 - Desinscrever-se de um tópico")
    print("5 - Sair")

    entrada = input("\nDigite o número da sua escolha: ")

    # enquanto entrada não for um número, ou for um número fora das escolhas possíveis
    while True:
        try:  # usando try except porque se a entrada não for um número, o cast para inteiro ira causar uma exception
            entrada = int(entrada.strip())
            if entrada <= 5 and entrada >= 1:
                modo = entrada
                break
            else:
                entrada = input("Por favor, digite uma opção válida: ")
        except Exception as e:
            entrada = input("Por Favor, digite o número da sua escolha: ")

    return


def notify_callback(content_list: list[Content]) -> None:
    print("Received content:")
    for element in content_list:
        print("Topico:", element.topic)
        print("Autor:", element.author)
        print("Content:", element.data)
        print("--------------------------")


def login(conn):
    while(not userID):
        userID = input("Digite seu nome:\n ")
    if(conn.root.login(userID, notify_callback)):
        print("Usuário logado")
    else:
        print("Login não foi possível, talvez já exista alguem logado com esse usuário")


def subscribe(conn):
    global modo

    topico = input("Digite o nome do tópico:\n")
    if(conn.root.subscribe_to(userID, topico)):
        print("Inscrição feita com sucesso")
    else:
        print("Um erro ocorreu, confira se o nome do tópico foi escrito corretamente")

    modo = 0


def unsubscribe(conn):
    global modo

    topico = input("Digite o nome do tópico:\n")
    if(conn.root.unsubscribe_to(userID, topico)):
        print("Inscrição desfeita com sucesso")
    else:
        print("Um erro ocorreu, confira se o nome do tópico foi escrito corretamente")

    modo = 0


def publish(conn):
    global modo

    topico = input("Digite o nome do tópico:\n")
    conteudo = input("Digite o conteúdo do tópico\n")
    if(conn.root.publish(userID, topico, conteudo)):
        print("Publicação feita com sucesso")
    else:
        print("Algum erro ocorreu, confira se o nome do tópico foi escrito corretamente")

    modo = 0


def list_topics(conn):
    global modo

    print("Tópicos:\n")
    lista = conn.root.list_topics(conn)
    print(*lista, sep=", ")

    modo = 0


def confirm_exit():
    global modo
    print("Gostaria mesmo de sair da aplicação?")

    while True:
        confirm_exit = input("1 - Sim\n2 - Não, voltar para o menu inicial")
        if confirm_exit == 1:
            return True
        else:
            modo = 0
            return False


def main():
    '''Funcao principal do cliente'''
    # inicia o cliente
    conn = iniciaCliente()
    # interage com o servidor ate encerrar

    print("Bem vindo ao sistema de anúncios\n")
    print("Neste sistema, você pode registrar seu interesse em quantos tópicos quiser e receber seus anúncios.\n")
    login(conn)

    while modo != 4:
        if modo == 0:
            print_interface()
        if modo == 1:
            list_topics(conn)
        if modo == 2:
            subscribe(conn)
        if modo == 3:
            publish(conn)
        if modo == 4:
            unsubscribe(conn)
        if modo == 5:
            if(confirm_exit()):
                break

    # encerra a conexao
    conn.close()


if __name__ == '__main__':
    main()
