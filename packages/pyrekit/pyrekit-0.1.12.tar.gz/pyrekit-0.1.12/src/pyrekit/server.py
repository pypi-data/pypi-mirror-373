from pyrekit.files import read_file, pack_app
import inspect
from flask import Flask, jsonify
from flask_cors import CORS
from multiprocessing import Process, Value
import logging


class Signal:
    """
        Signal class used to control hot_reload
    """
    def __init__(self):
        self.updated = Value('b', False)
        self.reload = Value('b', False)

    def flip_updated(self) -> None:
        with self.updated.get_lock():
            self.updated.value = not self.updated.value

    def flip_reload(self) -> None:
        with self.reload.get_lock():
            self.reload.value = not self.reload.value

    def get_reload(self) -> bool:
        with self.reload.get_lock():
            if self.reload.value == 0:
                return False
            else:
                return True
    
    def get_updated(self) -> bool:
        with self.updated.get_lock():
            if self.updated.value == 0:
                return False
            else:
                return True

class SuppressDevReloadFilter(logging.Filter):
    """A custom filter to suppress log messages for the /dev/reload route."""
    def filter(self, record):
        # The getMessage() method returns the final log string.
        # We return False to prevent this specific log record from being processed.
        message = record.getMessage()
        return "/dev/reload" not in message and "WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead." not in message

class AppMeta(type):
    """
    Metaclass to automatically discover and register routes from class methods.
    
    This metaclass uses a wrapping pattern. It waits for the class to be created,
    then wraps its __init__ method. The new __init__ first calls the original
    __init__ (ensuring the Flask app is properly set up) and then adds the
    discovered URL rules.
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        routes_to_register = []
        for item_name, item_value in attrs.items():
            if callable(item_value) and not item_name.startswith('_'):
                http_methods = []
                if item_name.lower().startswith('get_'):
                    http_methods.append('GET')
                elif item_name.lower().startswith('post_'):
                    http_methods.append('POST')
                elif item_name.lower().startswith('put_'):
                    http_methods.append('PUT')
                elif item_name.lower().startswith('delete_'):
                    http_methods.append('DELETE')

                # Makes sure all the methods that are not routes, are taken out                
                if not http_methods and item_name != 'index':
                    continue

                if item_name == 'index':
                    http_methods = ['GET', 'POST']

                sig = inspect.signature(item_value)
                params = [p for p in sig.parameters if p != 'self']
                
                if item_name == 'index':
                    rule = '/'
                else:
                    path_name = item_name
                    for prefix in ['GET_', 'POST_', 'PUT_', 'DELETE_']:
                        if path_name.startswith(prefix):
                            path_name = path_name[len(prefix):]
                    
                    rule = f"/{path_name.replace('_', '/')}"

                for param in params:
                    rule += f"/<{param}>"

                options = {'methods': http_methods}
                routes_to_register.append((rule, item_name, options))
                # print(f"Discovered route: {rule} ({options['methods']}) -> {name}.{item_name}")

        if not routes_to_register:
            return

        original_init = cls.__init__

        def wrapped_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            for rule, view_name, options in routes_to_register:
                view_func = getattr(self, view_name)
                current_options = options.copy()
                endpoint = current_options.pop('endpoint', view_name)
                self.add_url_rule(rule, endpoint=endpoint, view_func=view_func, **current_options)

        cls.__init__ = wrapped_init

class MetaclassServer(Flask, metaclass=AppMeta):
    """
    A base Flask application class that uses AppMeta to auto-register routes.
    Inherit from this class to create your application.
    """
    pass

class Server(MetaclassServer):
    """
    The backbone of the app, inherit from this one to make your server
    create any method with:
        index : special route, for the home "/"
        GET_ : will create a get route.
        POST_ : will create a post route.
        PUT_ : will create a put route.
        DELETE_ : will create a delete route.
    Any "_" will be interpreted as a "/"
    """
    def __init__(self, port=5000, host="0.0.0.0", DEV = False, **kwargs):
        super().__init__(import_name="pyreact internal server", **kwargs)
        CORS(self)
        log = logging.getLogger('werkzeug')
        log.addFilter(SuppressDevReloadFilter())
        self.port = port
        self.host = host
        self.signal: Signal = None
        self.DEV = DEV

    def set_Signal(self, signal: Signal):
        self.signal = signal

    def start(self):
        print(f"Server started at http://{self.host}/{self.port}")
        self.run(port=self.port, host=self.host)
    
    def get_dev_reload(self):
        if self.signal != None:
            ret = self.signal.get_reload()
            if self.signal.get_reload() is True:
                self.signal.flip_reload()
            return jsonify({"reload": ret})
        else:
            return {"reload": False, "message": "Route used for development"}, 404

class ServerProcess(Process):
    """
    Just serve as server manager, it manages the server
    """
    def __init__(self, server: Server, signal: Signal = None, DEV = False):
        self.server: Server = server
        super().__init__(target=self.server.start)
        self.DEV = DEV
        if self.DEV:
            self.signal = signal
            if self.server.signal is None:
                self.server.set_Signal(self.signal)


    def close(self):
        self.kill()
        self.join()
