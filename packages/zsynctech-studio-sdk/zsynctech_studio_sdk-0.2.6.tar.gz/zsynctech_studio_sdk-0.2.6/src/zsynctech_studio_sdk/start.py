from zsynctech_studio_sdk.utils import wait_until_file_stable
from watchdog.events import PatternMatchingEventHandler
from zsynctech_studio_sdk.loggers import logger
from watchdog.observers import Observer
from zsynctech_studio_sdk import client
from appdirs import AppDirs
from queue import Queue
import json
import os


APPS_DIR = AppDirs()
SDK_DIR = os.path.join(APPS_DIR.user_data_dir, "zsynctech")


class StartEventHandler:
    def __init__(self):
        self.observer = Observer()
        self._recursive = False
        self.queue = Queue()

        if client._instance_id is None:
            raise RuntimeError("Credentials not set. Call set_credentials() first.")

        self.sdk_path = os.path.join(SDK_DIR, client._instance_id)
        os.makedirs(self.sdk_path, exist_ok=True)

    @property
    def recursive(self):
        return self._recursive

    class JSONHandler(PatternMatchingEventHandler):
        def __init__(self, queue):
            super().__init__(patterns=["*.json"], ignore_directories=True)
            self.queue = queue
            self._processed_files = {}

        def _load_json(self, src_path):
            if wait_until_file_stable(src_path, check_interval=0.5, timeout=10):
                try:
                    with open(src_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    logger.exception("An error occurred while loading the file", stack_info=True)
            return None

        def _should_process(self, src_path):
            try:
                mtime = os.path.getmtime(src_path)
            except FileNotFoundError:
                return False
            last_mtime = self._processed_files.get(src_path, 0)
            if mtime > last_mtime:
                self._processed_files[src_path] = mtime
                return True
            return False

        def on_modified(self, event):
            logger.info(f"Novo evento recebido: {event.dest_path} - {event.event_type}")
            if self._should_process(event.src_path):
                data = self._load_json(event.src_path)
                if data:
                    self.queue.put(data)
                    logger.info(f"Dados adicionados a fila: {data}")
                else:
                    logger.error("Nenhum dado encontrado no evento")

    def __start_observer(self):
        event_handler = self.JSONHandler(self.queue)
        self.observer.schedule(event_handler, self.sdk_path, recursive=self.recursive)
        self.observer.start()
        logger.info(f"Aguardando eventos em: {self.sdk_path}")

    def listen_events(self, timeout=None):
        self.__start_observer()
        try:
            while True:
                try:
                    data = self.queue.get(timeout=timeout)
                    yield data
                except KeyboardInterrupt:
                    break
                except Exception:
                    pass
        finally:
            self.observer.stop()
            self.observer.join()
