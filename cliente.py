import os
import platform
import rpyc

HOST = 'localhost'  # maquina onde esta o servidor
PORT = 10001    # porta que o servidor esta escutando

clear = ""

# como é um sistema simples, irei utilizar números para definir a ação
# 0 é tela inicial, 1 é registro, 2 é consultar, 3 é remover e 4 é finalizar o sistema
modo = 0


def iniciaCliente():
    conn = rpyc.connect(HOST, PORT)
    # apenas definindo o comando para limpeza do console
    global clear
    if platform.system() == 'Windows':
        clear = 'cls'
    else:
        clear = 'clear'

    return conn


# código da interface de usuário,


def print_interface():
    global modo
    os.system(clear)
    print("Bem vindo ao sistema de dicionário de remoto\n")
    print("Neste sistema, você pode registrar uma chave e um texto, ou você pode consultar o texto de uma chave existente\n")
    print("1 - Registrar chave e texto")
    print("2 - Consultar chave")
    print("3 - Remover chave")
    print("4 - Sair")

    entrada = input("\nDigite o número da sua escolha: ")

    # enquanto entrada não for um número, ou for um número fora das escolhas possíveis
    while True:
        try:  # usando try except porque se a entrada não for um número, o cast para inteiro ira causar uma exception
            entrada = int(entrada.strip())
            if entrada <= 4 and entrada >= 1:
                modo = entrada
                break
            else:
                entrada = input("Por favor, digite uma opção válida: ")
        except Exception as e:
            entrada = input("Por Favor, digite o número da sua escolha: ")

    return


def print_remove(conn):
    global modo
    os.system(clear)
    print("Você está removendo. Para retornar a tela inicial, apenas entre com uma string vazia\n")

    # enquanto a string não for vazia, tentaremos remover chaves
    while True:
        chave = input("Digite a chave que deseja remover: ")
        if not chave:
            break
        print(conn.root.remove(chave))
    modo = 0


def print_consulta(conn):
    global modo
    os.system(clear)
    print("Você está consultando. Para retornar a tela inicial, apenas entre com uma string vazia\n")

    # enquanto a string não for vazia, tentaremos consultar chaves
    while True:
        chave = input("Digite a chave que deseja consultar: ")
        if not chave:
            break
        print(conn.root.consulta(chave))

    modo = 0
    # volta para a tela inicial
    return


def print_registro(conn):
    global modo
    os.system(clear)
    print("Você está registrando. Para retornar a tela inicial, apenas entre com uma string vazia\n")
    # enquanto a string não for vazia, tentaremos registrar
    while True:
        chave = input(
            "Digite a chave que deseja inserir: ")
        if not chave:
            break
        else:
            valor = input(
                "Digite o valor que deseja inserir: ")
            if not valor:
                break
            print(conn.root.insere(chave, valor))
    # volta para a tela inicial
    modo = 0
    return


def main():
    '''Funcao principal do cliente'''
    # inicia o cliente
    conn = iniciaCliente()
    # interage com o servidor ate encerrar

    while modo != 4:
        if modo == 0:
            print_interface()
        if modo == 1:
            print_registro(conn)
        if modo == 2:
            print_consulta(conn)
        if modo == 3:
            print_remove(conn)

    # encerra a conexao
    conn.close()


if __name__ == '__main__':
    main()
