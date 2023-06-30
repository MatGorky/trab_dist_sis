from __future__ import annotations
import rpyc  # type: ignore
from dataclasses import dataclass
from typing import Callable, TypeAlias
import threading
from threading import Thread
from rpyc.utils.server import ThreadedServer
import json
import time
from interface import *

PORTA = 10002


# Isso é para ser tipo uma struct
# Frozen diz que os campos são read-only


class CBrokerService(BrokerService):  # type: ignore

    usuarios = {}
    topicos = {}
    usuarios_off = {}

    # Implementação de exclusão mútua para impedir a condição de corrida na alteração de
    user_lock = threading.Lock()
    topic_lock = threading.Lock()

    def on_connect(self, conn):
        self.user_id = None

    # Não é exposed porque só o "admin" tem acesso

    def create_topic(topicname: str) -> Topic:
        CBrokerService.topicos[topicname] = set()
        return topicname

    # Handshake

    def exposed_login(self, id: UserId, callback: FnNotify) -> bool:
        with CBrokerService.user_lock:
            CBrokerService.usuarios[id] = callback
            if id in CBrokerService.usuarios_off:
                contents = CBrokerService.usuarios_off[id]
                CBrokerService.usuarios[id](contents)
                del CBrokerService.usuarios_off[id]

        self.user_id = id
        return True

    # Query operations

    def exposed_list_topics(self) -> list[Topic]:
        return list(CBrokerService.topicos.keys())

    # Publisher operations

    def exposed_publish(self, id: UserId, topic: Topic, data: str) -> bool:
        """
        Função responde se Anúncio conseguiu ser publicado
        """

        if(id != self.user_id):  # Autenticação muito boa
            return False
        try:
            usuarios = CBrokerService.topicos[topic]
            content = Content(author=id, topic=topic, data=data)
            for element in usuarios:
                with CBrokerService.user_lock:
                    if(element in CBrokerService.usuarios_off):
                        CBrokerService.usuarios_off[element].append(content)
                    else:
                        CBrokerService.usuarios[element]([content])
            return True
        except Exception as e:
            print(e)
            return False
            # Subscriber operations

    def exposed_subscribe_to(self, id: UserId, topic: Topic) -> bool:
        if(id != self.user_id):  # Autenticação muito boa
            return False

        try:
            with CBrokerService.topic_lock:
                CBrokerService.topicos[topic].add(id)
            return True
        except Exception as e:
            print(e)
            return False

    def exposed_unsubscribe_to(self, id: UserId, topic: Topic) -> bool:
        if(id != self.user_id):  # Autenticação muito boa
            return False
        try:
            with CBrokerService.topic_lock:
                CBrokerService.topicos[topic].remove(id)
            return True
        except Exception as e:
            print(e)
            return False

    def on_disconnect(self, conn):
        if self.user_id is not None:
            with CBrokerService.user_lock:
                CBrokerService.usuarios_off[self.user_id] = []

    def input_parallel():
        while True:
            user_input = input(
                "Escreva o nome do topico que deseja adicionar: ")
            if(user_input in CBrokerService.topicos) or user_input == "":
                print("ja existe um topico com esse nome")
            else:
                CBrokerService.create_topic(user_input)


if __name__ == "__main__":
    # Iniciando o servidor
    t = ThreadedServer(CBrokerService, port=PORTA,
                       protocol_config={'allow_getattr': True, 'allow_public_attrs': True})
    input_thread = Thread(target=CBrokerService.input_parallel)
    # Set the input thread as a daemon to exit with the main thread
    input_thread.daemon = True
    input_thread.start()
    t.start()
    # Wait for the server thread to finish
    t.join()
