import os
import platform
from typing import Callable, TypeAlias
import rpyc

HOST = 'localhost'  # maquina onde esta o servidor
PORT = 10002    # porta que o servidor esta escutando

received_contents = []
clear = ""
userID = None

# como é um sistema simples, irei utilizar números para definir a ação
# 0 é tela inicial, 1 é registro, 2 é consultar, 3 é remover e 4 é finalizar o sistema
modo = 0

UserId: TypeAlias = str

Topic: TypeAlias = str


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
    print("5 - Visualizar anúncios (" + str(len(received_contents)) + ")")
    print("6 - Sair")

    entrada = input("\nDigite o número da sua escolha: ")

    # enquanto entrada não for um número, ou for um número fora das escolhas possíveis
    while True:
        try:  # usando try except porque se a entrada não for um número, o cast para inteiro ira causar uma exception
            entrada = int(entrada.strip())
            if entrada <= 6 and entrada >= 1:
                modo = entrada
                break
            else:
                entrada = input("Por favor, digite uma opção válida: ")
        except Exception as e:
            entrada = input("Por Favor, digite o número da sua escolha: ")

    return


def notify_callback(content_list: list[Content]) -> None:
    global received_contents
    global modo

    received_contents.extend(content_list)


def showContent():
    global modo
    global received_contents

    for element in received_contents:
        print("Author:", getattr(element, "author"))
        print("Data:", getattr(element, "data"))
        print("Topic:", getattr(element, "topic"))
        print("--------------------------")
        input("\n\nAperte Enter para prosseguir...")

    received_contents = []
    modo = 0


def login(conn):
    global userID
    global modo

    while(not userID):
        userID = input("Digite seu nome:\n")

    if(conn.root.login(userID, notify_callback)):
        print("Usuário logado")
        if(len(received_contents) > 0):
            print(
                "Alguns tópicos que você segue foram atualizados enquanto você esteve fora.")
            while(True):
                visualizar = input(
                    "Deseja visualizar os anúncios agora? (S/N)")
                if(visualizar == 'N'):
                    break
                elif (visualizar == 'S'):
                    print("Received content:")
                    showContent()
                    break
                else:
                    print("Comando inexistente.")

    else:
        print("Login não foi possível, talvez já exista alguem logado com esse usuário")
        input("\n\nAperte Enter para tentar novamente...")


def subscribe(conn):
    global modo

    topico = input("Digite o nome do tópico:\n")
    if(conn.root.subscribe_to(userID, topico)):
        print("Inscrição feita com sucesso")
    else:
        print("Um erro ocorreu, confira se o nome do tópico foi escrito corretamente")

    input("\n\nAperte Enter para retornar...")
    modo = 0


def unsubscribe(conn):
    global modo

    topico = input("Digite o nome do tópico:\n")
    if(conn.root.unsubscribe_to(userID, topico)):
        print("Inscrição desfeita com sucesso")
    else:
        print("Um erro ocorreu, confira se o nome do tópico foi escrito corretamente")
    input("\n\nAperte Enter para retornar...")
    modo = 0


def publish(conn):
    global modo

    topico = input("Digite o nome do tópico:\n")
    conteudo = input("Digite o conteúdo do tópico\n")
    if(conn.root.publish(userID, topico, conteudo)):
        print("Publicação feita com sucesso")
    else:
        print("Algum erro ocorreu, confira se o nome do tópico foi escrito corretamente")

    input("\n\nAperte Enter para retornar...")
    modo = 0


def list_topics(conn):
    global modo

    print("Tópicos:\n")
    lista = conn.root.list_topics()

    print(*lista, sep=", ")
    input("\n\nAperte Enter para retornar...")
    modo = 0


def confirm_exit():
    global modo
    print("Gostaria mesmo de sair da aplicação? Os anúncios não visualizados serão perdidos.")

    while True:
        confirm_exit = input("1 - Sim\n2 - Não, voltar para o menu inicial\n")
        confirm_exit = int(confirm_exit.strip())
        if confirm_exit == 1:
            return True
        elif confirm_exit == 2:
            modo = 0
            return False
        else:
            print("Por favor digite um número válido.\n")


def main():
    '''Funcao principal do cliente'''
    # inicia o cliente
    conn = iniciaCliente()
    # interage com o servidor ate encerrar

    print("Bem vindo ao sistema de anúncios\n")
    print("Neste sistema, você pode registrar seu interesse em quantos tópicos quiser e receber seus anúncios.\n")
    login(conn)

    while modo != 7:
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
            showContent()
        if modo == 6:
            if confirm_exit():
                break

    # encerra a conexao
    conn.close()


if __name__ == '__main__':
    main()
