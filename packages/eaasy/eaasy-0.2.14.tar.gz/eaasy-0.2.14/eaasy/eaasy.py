from flask import Flask, request
from flask_restx import Api, Namespace, abort
from flask_restx._http import HTTPStatus
from flask_cors import CORS
from eaasy.api import liveness_ns
from gunicorn.app.base import BaseApplication
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_oidc import OpenIDConnect
import redis
import redis.exceptions
import logging
import json
import time
import os

limiter = Limiter(get_remote_address)

class ColoredFormatter(logging.Formatter): # pragma: no cover
    COLORS = {
        # Gray
        'DEBUG': '\033[90m',
        # Blue
        'INFO': '\033[94m',
        # Yellow
        'WARNING': '\033[93m',
        # Red
        'ERROR': '\033[91m',
        # Magenta
        'CRITICAL': '\033[91m',
    }
    RESET = '\033[0m'

    converter = time.gmtime

    def format(self, record):
        levelname_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{levelname_color}{record.levelname}{self.RESET}{f' File:{record.filename} Line:{record.lineno}' if record.levelname in ['ERROR', 'WARNING', 'CRITICAL'] else ''}"
        return super().format(record)

class Eaasy: # pragma: no cover
    def __init__(self, logger:logging.Logger | bool | None = None, **kwargs):
        self._logger = self.__init_logger(logger)

        # Get Flask app and API parameters from kwargs 
        name = kwargs.get('name', __name__)
        version = kwargs.get('version', '1.0')
        title = kwargs.get('title', 'API')
        description = kwargs.get('description', 'A simple API')
        doc=kwargs.get('doc', '/swagger')
        authorizations = kwargs.get('authorizations', None)
        security = kwargs.get('security', None)
        config = kwargs.get('config', {})
        oidc = kwargs.get('oidc', None)
        enable_limiter = kwargs.get('enable_limiter', False)

        # Create Flask app and API
        self._app = Flask(name)
        self._app.config.update(config)
        CORS(self._app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
        self._app.before_request(self.__before_request)
        self._api = Api( self._app, version=version, title=title, description=description, doc=doc, authorizations=authorizations, security=security)
        self._api.add_namespace(liveness_ns)
        
        # Initialize OpenID Connect
        self._oidc = OpenIDConnect(self._app) if oidc is True else oidc if isinstance(oidc, OpenIDConnect) else None

        if enable_limiter:
            # Initialize rate limiter
            self.__init_limiter()

    def __init_limiter(self):
        redis_uri = os.getenv("REDIS_URI", default=None)

        if redis_uri:
            try:
                r = redis.Redis.from_url(redis_uri)
                r.ping()
                self._app.config["RATELIMIT_STORAGE_URI"] = redis_uri
            except redis.exceptions.ConnectionError:
                print("Could not connect to Redis. Use in-memory storage. \033[93mNot recommended for production.\033[0m")
                redis_uri = None

        limiter.init_app(self._app)

    def __init_logger(self, logger:logging.Logger | bool | None) -> logging.Logger | None:
        if logger is None or logger is False:
            return None
        elif isinstance(logger, bool):
            logging.basicConfig(
                level=logging.INFO,
                format='[%(asctime)s] [%(levelname)s] %(message)s',
                handlers=[logging.StreamHandler()]
            )
            for handler in logging.getLogger().handlers:
                handler.setFormatter(ColoredFormatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S +0000"))
            return logging.getLogger(__name__)
        return logger

    def __before_request(self):
        if self._logger: 
            self._logger.info(f'{request.method} {request.endpoint} {request.remote_addr} {request.user_agent}')
        
        try:
            if request.method == 'POST' or request.method == 'PUT':
                if request.data:
                    if self._logger: self._logger.debug(f'Payload: {json.dumps(json.loads(request.data))}')
        except Exception as e:
            if self._logger: self._logger.error(f'{e}')
            abort(HTTPStatus.BAD_REQUEST, 'Invalid payload', data=f'{request.data.decode()}')

    def run(self):
        self._app.run()

    def add_namespace(self, namespace: Namespace):
        self._api.add_namespace(namespace)

    @property
    def app(self) -> Flask:
        return self._app
    
    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            raise ValueError('Logger is not enabled')
        return self._logger
    
    @property
    def oidc(self) -> OpenIDConnect:
        if self._oidc is None:
            raise ValueError('OpenID Connect is not enabled')
        return self._oidc


class GunEaasy(BaseApplication): # pragma: no cover
    def __init__(self, app: Flask, options: dict | None = None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value for key, value in self.options.items()
            if self.cfg is not None and key in self.cfg.settings and value is not None}
        if self.cfg is not None:
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
