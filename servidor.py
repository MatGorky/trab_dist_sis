from __future__ import annotations
import rpyc
import rpyc  # type: ignore
from dataclasses import dataclass
from typing import Callable, TypeAlias
import threading
from rpyc.utils.server import ThreadedServer
import json
import time

PORTA = 10001
DICIONARIO = 'dicionario.json'


def inicializa_dicionario():
    try:
        # tenta abrir o arquivo
        with open(DICIONARIO, '+r') as infile:
            print("Arquivo existente")
            if infile.read().strip() == '':
                dicionario = {}  # Se o arquivo estiver vazio
            else:
                # Senão, carregamos o json
                infile.seek(0)
                dicionario = json.load(infile)
            return dicionario

    except FileNotFoundError:
        # se ocorrer um erro de arquivo não encontrado, cria o arquivo
        with open(DICIONARIO, '+w') as infile:
            print("Arquivo criado com sucesso!")
            if infile.read().strip() == '':
                dicionario = {}  # Se o arquivo estiver vazio
            else:
                # Senão, carregamos o json
                infile.seek(0)
                dicionario = json.load(infile)
            return dicionario


UserId: TypeAlias = str

Topic: TypeAlias = str

# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only


@dataclass(frozen=True, kw_only=True, slots=True)
class Content:
    author: UserId
    topic: Topic
    data: str


FnNotify: TypeAlias = Callable[[list[Content]], None]


class BrokerService(rpyc.Service):  # type: ignore

    usuarios = {}
    topicos = {}

    # Implementação de exclusão mútua para impedir a condição de corrida na alteração de
    user_lock = threading.Lock()
    topic_lock = threading.Lock()

    # Não é exposed porque só o "admin" tem acesso
    def create_topic(self, id: UserId, topicname: str) -> Topic:
        BrokerService.topicos[topicname] = set()
        return topicname

    # Handshake

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        with BrokerService.user_lock:
            BrokerService.usuarios[id] = [callback]
        return True

    # Query operations

    def exposed_list_topics(self) -> list[Topic]:
        return list(BrokerService.topicos.keys)

    # Publisher operations

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        """
        Função responde se Anúncio conseguiu ser publicado
        """
        assert False, "TO BE IMPLEMENTED"

    # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        try:
            with BrokerService.topic_lock:
                BrokerService.topicos[topic].add(id)
            return True
        except:
            return False

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        try:
            with BrokerService.topic_lock:
                BrokerService.topicos[topic].remove(id)
            return True
        except:
            return False


class DicionarioRemoto(rpyc.Service):

    # variável da classe(static do java), que irá guardar o dicionário na memória
    dicionario = {}

    # quantidade limite de alterações antes de salvar no disco.
    limite_alter = 2

    # contador de alterações
    contador_alter = 0

    # Implementação de exclusão mútua para impedir a condição de corrida na alteração do dicionário.
    mutex_lock = threading.Lock()

    def on_connect(self, conn):
        print("Conexao iniciada:")
        print(conn)

    def on_disconnect(self, conn):
        print("Conexao finalizada:")

    def exposed_consulta(self, chave):
        chave = chave.strip()
        if chave in DicionarioRemoto.dicionario:
            return f"Os valores da chave consultada, em ordem alfabética, são: {DicionarioRemoto.dicionario[chave]}"
        else:
            return f"Chave não encontrada"

    def exposed_insere(self, chave, valor):
        chave = chave.strip()
        valor = valor.strip()

        # Para evitar condição de corrida, só iremos modificar o dicionário utilizando de exclusão mútua
        with DicionarioRemoto.mutex_lock:
            if chave in DicionarioRemoto.dicionario:
                string_resposta = f"A chave '{chave}' já se encontrava no dicionário, valor inserido em chave existente"
                # pegamos o valor existente
                valor_existente = DicionarioRemoto.dicionario[chave]
                # colocamos o valor adicionado na lista
                valor_existente.append(valor)
                valor_novo = valor_existente
                valor_novo.sort()  # sort

            else:
                string_resposta = f"A chave '{chave}' não se encontrava no dicionário, valor inserido"
                valor_novo = [valor]

            DicionarioRemoto.dicionario[chave] = valor_novo
            # time.sleep(5)  espara para checar se o lock está funcionando
            self.guarda_dados()

        return string_resposta

    def exposed_remove(self, chave):
        chave = chave.strip()
        if chave in DicionarioRemoto.dicionario:
            with DicionarioRemoto.mutex_lock:
                del DicionarioRemoto.dicionario[chave]
                self.guarda_dados()
            string_resposta = f"A chave '{chave}' foi removida com sucesso"
        else:
            string_resposta = f"A chave {chave} não foi encontrada"
        return string_resposta

    # função para guardar dados no disco(só deve ser chamada em um bloco de exclusão mútua, senão pode causar condição de corrida)
    def guarda_dados(self):
        DicionarioRemoto.contador_alter += 1
        if DicionarioRemoto.contador_alter == DicionarioRemoto.limite_alter:
            with open(DICIONARIO, "w") as outfile:
                json.dump(DicionarioRemoto.dicionario, outfile)


if __name__ == "__main__":
    # Iniciando o servidor
    t = ThreadedServer(BrokerService, port=PORTA)
    t.start()
