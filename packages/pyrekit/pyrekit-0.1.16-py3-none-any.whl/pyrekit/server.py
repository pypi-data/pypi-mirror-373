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
    Metaclass to automatically discover and register Flask routes from class methods.

    This metaclass inspects the methods of a class it's applied to. If a method
    name follows a specific naming convention (e.g., starts with 'GET_', 'POST_'),
    it's automatically converted into a Flask URL rule.

    Features:
    - Naming Convention: Method names like `GET_user_profile` are mapped to a
      `GET` request at the URL `/user/profile`.
    - Automatic Parameter Handling: Method arguments are converted into URL
      parameters. For example, `def GET_user(self, user_id):` becomes a route
      at `/user/<user_id>`.
    - Typed Parameters: Python type hints are used to create typed URL converters.
      For example, `def GET_user(self, user_id: int):` becomes `/user/<int:user_id>`.
    - Special 'index' method: A method named `index` is automatically mapped to
      the root URL '/' for GET and POST requests.
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        # A mapping of method prefixes to their corresponding HTTP verbs.
        HTTP_PREFIX_MAP = {
            'GET_': 'GET',
            'POST_': 'POST',
            'PUT_': 'PUT',
            'DELETE_': 'DELETE',
        }
        
        # A mapping of Python types to Flask's URL converters.
        TYPE_CONVERTER_MAP = {
            int: 'int',
            float: 'float',
            str: 'string',
        }

        routes_to_register = []

        # Iterate over all attributes of the class to find methods that look like routes.
        for item_name, item_value in attrs.items():
            if not callable(item_value) or item_name.startswith('_'):
                continue

            # Handle index page
            if item_name == 'index':
                rule = '/'
                http_methods = ['GET', 'POST']
                view_name = 'index'
                routes_to_register.append((rule, view_name, {'methods': http_methods}))
                print(f"Discovered special route: {rule} ({http_methods}) -> {name}.{view_name}")
                continue

            # Handle all other routes based on prefixes
            found_method = None
            path_prefix = None
            
            for prefix, method in HTTP_PREFIX_MAP.items():
                if item_name.startswith(prefix):
                    found_method = method
                    path_prefix = prefix
                    break # Stop after finding the first matching prefix

            if not found_method:
                continue # Skip methods that don't match naming convention

            # Construct the base URL rule from the method name.
            # 'GET_user_profile' becomes '/user/profile'
            path_name = item_name[len(path_prefix):]
            rule = f"/{path_name.replace('_', '/')}"

            # Inspect the method's signature to find its parameters.
            sig = inspect.signature(item_value)
            
            # Add parameters to the URL rule.
            for param in sig.parameters.values():
                if param.name == 'self':
                    continue
                
                # Check for type hints and map them to Flask converters.
                converter = TYPE_CONVERTER_MAP.get(param.annotation, 'string')
                
                # For default string type, we don't need to specify it.
                if converter == 'string':
                    rule += f"/<{param.name}>"
                else:
                    rule += f"/<{converter}:{param.name}>"

            # Prepare the options for Flask's add_url_rule.
            options = {'methods': [found_method]}
            routes_to_register.append((rule, item_name, options))
            # print(f"Discovered route: {rule} ({options['methods']}) -> {name}.{item_name}")

        # If no routes were found, there's nothing more to do.
        if not routes_to_register:
            return

        # --- Wrap the class's __init__ to register the routes after initialization ---
        original_init = cls.__init__

        def wrapped_init(self, *args, **kwargs):
            # Call the original __init__ first to ensure the object is set up.
            # In the case of Flask, this sets up the app instance.
            original_init(self, *args, **kwargs)
            
            # Now, add all the discovered URL rules to the instance.
            for rule, view_name, options in routes_to_register:
                # Get the actual method from the instance (self).
                view_func = getattr(self, view_name)
                
                # Use the method name as the endpoint name by default.
                endpoint = options.pop('endpoint', view_name)
                
                # Add the rule to the Flask app instance.
                self.add_url_rule(rule, endpoint=endpoint, view_func=view_func, **options)
                # print(f"Registered route: {rule} -> {self.__class__.__name__}.{view_name}")

        # Replace the class's original __init__ with wrapped version.
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
    
    def GET_dev_reload(self):
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
