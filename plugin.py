import shutil
import os
import tempfile
import threading
import random
import json
import requests
import sublime

from LSP.plugin.core.handlers import LanguageHandler
from LSP.plugin.core.settings import ClientConfig, read_client_config

SERENATA_UPLOAD_HASH = '7499ecf1275983f26efd930446a3693d'


def get_expanding_variables(window):
    variables = window.extract_variables()
    variables.update({
        "home": os.path.expanduser('~'),
        "temp_dir": tempfile.gettempdir(),
    })
    return variables


def lsp_expand_variables(window, var):
    if isinstance(var, dict):
        for key, value in var.items():
            if isinstance(value, (dict, list, str)):
                var[key] = lsp_expand_variables(window, value)
    elif isinstance(var, list):
        for idx, value in enumerate(var):
            if isinstance(value, (dict, list, str)):
                var[idx] = lsp_expand_variables(window, value)
    elif isinstance(var, str):
        var = sublime.expand_variables(var, get_expanding_variables(window))

    return var


def plugin_loaded():
    server_path = os.path.join(sublime.cache_path(), 'LSP-serenata', 'serenata.phar')

    is_server_installed = os.path.isfile(server_path)
    print('LSP-serenata: Server {} installed at {}.'.format('is' if is_server_installed else 'is not', server_path))

    if not is_server_installed:
        log_and_show_message('LSP-serenata: Installing server.')
        install_server(server_path, on_install_complete)


def install_server(server_path, callback):
    def download_server(server_path, callback):
        try:
            # Download serenata phar compatible with PHP 7.1+
            url = 'https://gitlab.com/Serenata/Serenata/uploads/{}/distribution-7.1.phar'.format(SERENATA_UPLOAD_HASH)
            response = requests.get(url)
            response.raise_for_status()

            if not os.path.exists(os.path.dirname(server_path)):
                os.makedirs(os.path.dirname(server_path), 0o700)

            with open(server_path, 'wb') as file:
                file.write(response.content)

            callback()
        except requests.exceptions.RequestException as error:
            log_and_show_message('LSP-serenata: Error while installing the server.', error)
        return

    thread = threading.Thread(target=download_server, args=(server_path, callback,))
    thread.start()

    return thread


def on_install_complete():
    log_and_show_message('LSP-serenata: Server installed.')


def is_php_installed(plugin) -> bool:
    php_path = plugin.config.settings['phpPath'] or 'php'

    found = shutil.which(php_path) or os.path.isfile(php_path)

    return found


def log_and_show_message(msg, additional_logs=None):
    print(msg)

    if additional_logs:
        print(additional_logs)

    sublime.active_window().status_message(msg)


def get_initialization_options():
    folders = sublime.active_window().folders()

    for f in folders:
        config_file = None

        if os.path.isfile(f + '/.serenata.json'):
            config_file = f + '/.serenata.json'
        elif os.path.isfile(f + '/.serenata/config.json'):
            config_file = f + '/.serenata/config.json'

        if config_file is not None:
            with open(config_file) as config:
                return {
                    "configuration": json.load(config)
                }

    return {}

class LspSerenataPlugin(LanguageHandler):
    @property
    def name(self) -> str:
        return 'lsp-serenata'


    @property
    def config(self) -> ClientConfig:
        settings = sublime.load_settings("LSP-serenata.sublime-settings")
        client_configuration = settings.get('client')
        client_settings = client_configuration['settings']

        tcp_port = random.randrange(10000, 40000)

        server_path = os.path.join(sublime.cache_path(), 'LSP-serenata', 'serenata.phar')

        if 'phpPath' in client_settings:
            client_settings['phpPath'] = lsp_expand_variables(
                sublime.active_window(),
                client_settings['phpPath']
            )

        default_configuration = {
            "enabled": True,
            "command": [
                client_settings['phpPath'] or 'php',
                '-d',
                'memory_limit={}'.format(client_settings['memoryLimit'] or '1024M'),
                server_path,
                '--uri=tcp://127.0.0.1:{}'.format(tcp_port)
            ],
            "languages": [
                {
                    "languageId": "php",
                    "scopes": ["source.php"],
                    "syntaxes": ["Packages/PHP/PHP.sublime-syntax"]
                }
            ],
            "initializationOptions": get_initialization_options(),
            "tcp_host": '127.0.0.1',
            "tcp_port": tcp_port,
            "settings": {
                "phpPath": "php",
                "memoryLimit": "1024M"
            }
        }

        default_configuration.update(client_configuration)

        return read_client_config('lsp-serenata', default_configuration)


    def on_start(self, window) -> bool:
        if not is_php_installed(self):
            sublime.status_message(
                'Please install PHP 7.1 or later for the PHP Language Server to work.'
            )
            return False
        return True


    def on_initialized(self, client) -> None:
        pass
