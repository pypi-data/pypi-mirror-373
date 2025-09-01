import asyncio
import base64
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import requests
import websockets

from ms_utils.logging_lib import Logger

logger = Logger.setup_logger(__name__, level=logging.INFO)  # logging.DEBUG
logger.propagate = False


class MicroServiceWs:
    """Client WebSocket pour communiquer avec un serveur WebSocket."""

    def __init__(
        self,
        host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        ssl: bool = True,
        need_token: bool = True,
        path: str = "",
    ):
        """
        Initialise le client WebSocket.

        Args:
            host: L'adresse du serveur WebSocket.
            username: Nom d'utilisateur pour l'authentification.
            password: Mot de passe pour l'authentification.
            ssl: Utiliser SSL/TLS pour la connexion.
            need_token: Indique si un token est nécessaire pour la connexion.
            path: Chemin additionnel pour l'URI WebSocket.
        """
        self.host = host
        self.ssl = ssl
        self.token = ""
        self.username = username
        self.password = password
        self.path = path
        self.need_token = need_token
        self.queue = asyncio.Queue()
        self.websocket = None
        self.is_connected = False
        self.chunk_dict = dict()
        self.lock = asyncio.Lock()
        self.response_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor()
        self.disconnect_event = asyncio.Event()

        # gestionnaire de reconnexion
        self._reconnection_manager_started = False

    def build_uri(self):
        """Construit l'URI pour la connexion WebSocket."""
        scheme = "wss" if self.ssl else "ws"
        token_param = (
            f"?token={self.token}" if self.need_token and self.token else ""
        )
        return f"{scheme}://{self.host}{self.path}/{token_param}"

    def get_token(self) -> str:
        """
        Récupère le token d'authentification.

        Args:
            self: L'instance de la classe.

        Returns:
            Le token d'authentification.

        Raises:
            ValueError: Si l'authentification échoue.
        """
        while True:
            try:
                url = f"{'https' if self.ssl else 'http'}://{self.host}/auth-ms/login"
                response = requests.post(
                    url,
                    json={"name": self.username, "password": self.password},
                )  # TODO: maybe use aiohttp for async requests to improve performance
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erreur lors de la requête : {e}")
                time.sleep(5)
                continue
            if response.status_code == 201:
                return response.json().get("access_token", "")
            logger.error(f"Erreur d'authentification : {response.json()}")
            raise ValueError("Credentials invalides")

    async def connect(self):
        """Établit la connexion au serveur WebSocket."""
        if self.is_connected:
            logger.warning("Déjà connecté.")
            return

        try:
            # Tente la première connexion. Une boucle n'est plus nécessaire ici.
            await self._perform_connection()

            # Lance le gestionnaire de reconnexion en tâche de fond s'il n'a pas déjà été lancé
            if not self._reconnection_manager_started:
                loop = asyncio.get_running_loop()
                loop.create_task(self._reconnection_manager())
                self._reconnection_manager_started = True

        except Exception as e:
            logger.error(
                f"La connexion initiale a échoué : {e}. Le manager tentera de se reconnecter en arrière-plan."
            )
            self.is_connected = False
            self.disconnect_event.set()
            # Lance le manager même si la première connexion échoue, pour qu'il puisse réessayer
            if not self._reconnection_manager_started:
                loop = asyncio.get_running_loop()
                loop.create_task(self._reconnection_manager())
                self._reconnection_manager_started = True
            # Propage l'erreur pour que l'appelant sache que la connexion initiale a échoué
            raise

    async def _reconnection_manager(self):
        """Gère la reconnexion automatique en tâche de fond."""
        while True:
            # Attend un signal de déconnexion.
            # Si déjà déconnecté au démarrage, il passe immédiatement.
            await self.disconnect_event.wait()

            logger.info("Déconnexion détectée. Tentative de reconnexion...")
            self.is_connected = False
            self.disconnect_event.clear()

            # Boucle de tentative de reconnexion
            while not self.is_connected:
                try:
                    await self._perform_connection()
                    logger.info("Reconnexion réussie !")
                except Exception as e:
                    logger.error(
                        f"Échec de la reconnexion : {e}. Nouvelle tentative dans 5 secondes..."
                    )
                    await asyncio.sleep(5)

    async def _perform_connection(self):
        """Effectue l'action de se connecter et de lancer les tâches d'écoute/envoi."""
        self.is_connected = False  # Ensure clean state
        if self.need_token:
            # Exécute la fonction synchrone get_token dans un thread pour ne pas bloquer la boucle asyncio
            loop = asyncio.get_running_loop()
            self.token = await loop.run_in_executor(
                self.executor, self.get_token
            )

        uri = self.build_uri()
        self.websocket = await websockets.connect(uri)
        self.is_connected = True

        # Réinitialise l'événement de déconnexion au cas où il serait encore positionné
        self.disconnect_event.clear()

        # Lance les tâches d'écoute et d'envoi dans la bonne boucle d'événements
        loop = asyncio.get_running_loop()
        loop.create_task(self.listen())
        loop.create_task(self.send_response())
        logger.info("Tâches d'écoute et d'envoi démarrées.")

    async def put_chunk_data(self, data) -> None:
        async with self.lock:
            max_index = int(data["max_index"])
            current_chunks = len(self.chunk_dict.get(data["jobId"], [])) + 1
            logger.info(f"Index {max_index}, current chunks {current_chunks}")
            if max_index == current_chunks:
                chunks = self.chunk_dict.pop(data["jobId"], []) + [data]
                data_chunked = json.loads(
                    b"".join(
                        bytes(x["chunk"]["data"])
                        for x in sorted(chunks, key=lambda c: c["index"])
                    ).decode("utf-8")
                    if isinstance(chunks[0]["chunk"], dict)
                    else base64.b64decode(
                        "".join(
                            x["chunk"]
                            for x in sorted(chunks, key=lambda c: c["index"])
                        )
                    ).decode("utf-8")
                )
                logger.info(f"Fragenmented data: {data_chunked.keys()}")
                return data_chunked
            else:
                if data["jobId"] not in self.chunk_dict.keys():
                    self.chunk_dict[data["jobId"]] = [data]
                else:
                    self.chunk_dict[data["jobId"]].append(data)
            return None

    async def listen(self):
        """Écoute les messages entrants du serveur WebSocket."""
        try:
            async for message in self.websocket:
                if isinstance(message, str):
                    data = json.loads(message)
                    if data.get("chunk", None) is not None:
                        chunk_data = await self.put_chunk_data(data)
                        if chunk_data is not None:
                            await self.queue.put(chunk_data)
                    else:
                        await self.queue.put(data)
                elif isinstance(message, bytes):
                    logger.warning(
                        f"Received binary data: {len(message)} bytes"
                    )
                else:
                    logger.warning("Received unidentified data")
        except websockets.ConnectionClosed:
            logger.info("La connexion WebSocket a été fermée.")
        except Exception as e:
            logger.error(f"Erreur lors de l'écoute : {e}")
        finally:
            logger.info(
                "Fin de l'écoute. Signalement au manager de reconnexion."
            )
            self.is_connected = False
            # Signale au manager que la connexion est rompue.
            self.disconnect_event.set()

    async def send(self, data: dict | str) -> None:
        if isinstance(data, str):
            await self.response_queue.put(data)
        else:
            await self.response_queue.put(json.dumps(data))

    async def send_response(self) -> None:
        """
        Envoie un message au serveur WebSocket.

        Args:
            data: the message to send
        """
        while self.is_connected:
            try:
                data = await asyncio.wait_for(
                    self.response_queue.get(), timeout=1.0
                )
                if self.websocket and self.is_connected:
                    async with self.lock:
                        logger.debug(f"Data send: {data}")
                        await self.websocket.send(data)
                else:
                    logger.warning(
                        "Impossible d'envoyer le message, le websocket n'est pas connecté."
                    )
                    await self.response_queue.put(data)
            except asyncio.TimeoutError:
                # Si la queue est vide, on continue à attendre
                continue
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du message : {e}")
                # En cas d'erreur, on signale aussi la déconnexion
                self.is_connected = False
                self.disconnect_event.set()

    async def send_task_to_ms(
        self, ms: str, reference_id: str, job_id: str, data: dict
    ):
        """
        Envoie un message au serveur WebSocket destiné à un autre MicroService

        Args:
            ms: the MicroService to send the task
            reference_id: the id of the running workflow or process
            job_id: the id of the running job
            data: the message to send
        """
        await self.send(
            {
                "event": "ms-send-task",
                "data": {
                    "to": ms,
                    "workflowId": reference_id,  # for compat; TODO remove after refactoring ids
                    "referenceId": reference_id,
                    "jobId": job_id,
                    "data": data,
                },
            }
        )

    async def receive(self) -> dict:
        """
        Reçoit un message du serveur WebSocket.

        Returns:
            Le message reçu.
        """
        return await self.queue.get()

    async def close(self):
        """Ferme la connexion au serveur WebSocket."""
        if self.websocket:
            await self.websocket.close()
        self.is_connected = False
        self.disconnect_event.set()
