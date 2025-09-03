from pyrekit.files import get_package, create_files, create_base_dirs, pack_app, pack_server_functions, project_name
from pyrekit.server import Signal, ServerProcess
from typing import Type
import time
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
import importlib
import sys
from subprocess import run
from os import getcwd


class EventHandler(FileSystemEventHandler):
    """
        Used to find when a file is modified
    """

    def __init__(self, sig: Signal):
        super().__init__()
        self.sig: Signal = sig

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        if self.sig.get_updated() is False:
            self.sig.flip_updated()

def open_observer(sig: Signal, path: str, recursive=True):
    """
        Created to facilitate the creation of observers
    """

    event_handler = EventHandler(sig)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=recursive)
    observer.start()
    return observer


def check_modifications(sig: Signal, path: str = "src/"):
    """
        A quick way to open a observer and check for modifications
    """
    observer = open_observer(sig, path)

    print("Press CTRL + C to close.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing...")
    finally:
        observer.stop()
        observer.join()

def command(c: str, hide: bool = False):
    """
        Runs a command
    """
    run(c.split(" "), capture_output=hide)

def setup(AppName: str = "PyReact"):
    """
        Setups the project, creating a package.json and creating the src, build dirs, and all the files
    """
    # Check if the base dirs already exists or creates them
    create_base_dirs()

    # Creates all the needed files
    create_files(AppName)
    
    # Run the setup install
    command("npm install react react-dom esbuild tailwindcss @tailwindcss/cli")

def get_server_handle() -> Type:
    """
        Used to get AppServer class during hot_reload, make sure that the main.py file exists and that the AppServer class name is not changed
    """
    project_path = getcwd()

    if project_path not in sys.path:
        sys.path.insert(0, project_path)

    try:
        # rewrites the cached server module, so that hot-reload works
        if 'main' in sys.modules:
            importlib.reload(sys.modules['main'])

        from main import AppServer
        return AppServer

    except ImportError:
        raise ImportError("ERROR: You probably renamed the AppServer class in main.py, make sure it's still AppServer")
    except Exception as e:
        # Catch other potential errors
        print(f"An unexpected error occurred: {e}")
        raise
    finally:
        # Clean up by removing the path
        if project_path in sys.path:
            sys.path.remove(project_path)


def open_server(signal: Signal, DEV = False) -> ServerProcess:
    """
        Facilitate the opening server of the server, currently only used in development
    """
    AppServer = get_server_handle()
    app_server = AppServer(DEV=DEV)
    server = ServerProcess(app_server, DEV=DEV, signal=signal)
    return server

def bundler(script: str):
    pack_server_functions()
    command(f"npm run {script}", hide=True)

def handle_script(s: str):
    """
        Handle the scripts actions
    """

    package = get_package()
    scripts = package["scripts"]
    if s not in scripts:
        print("This command does not exists!")
        return
    
    command(f"npm run {s}", hide=True)

    if s == "build" or s == "run":
        bundler(s)

    if s == "build":
        app_string = pack_app()

        server = ""
        with open("main.py", "r") as fd:
            server = fd.read()
            server = server.replace('project_name()', f'"{project_name()}"')
            server = server.replace('pack_app(self.DEV)', f'r"""{app_string}"""')

        with open("app.py", "w", encoding="utf-8") as fd:
            fd.write(server)

    elif s == "run":
        server = None
        signal = Signal()
        server_signal = Signal()
        server_observer = open_observer(server_signal, "./main.py", recursive=False)

        try:
            server = open_server(signal=signal, DEV=True)
            bundler(s)
        except ImportError as error:
            print(error)
            print("Closing...")
            return
        
        observer = open_observer(sig=signal, path="src")
        server.start()
        
        try:
            while True:
                if signal.get_updated() or server_signal.get_updated():
                    bundler(s)

                if signal.get_updated():
                    print("Change detected in the frontend, recompiling...")
                    signal.flip_updated()

                    if signal.get_reload() is False:
                        signal.flip_reload()
                    print("Recompiled...")

                if server_signal.get_updated():
                    print("Change detected in the backed main.py, reloading server...")
                    server.close()
                    server = open_server(signal=signal, DEV=True)
                    server.start()
                    server_signal.flip_updated()
                    print("Server reloaded successfully.")

        except KeyboardInterrupt:
            print("Closing...")

        except ImportError as error:
            print(error)

        finally:
            server.close()
            observer.stop()
            observer.join()
            server_observer.stop()
            server_observer.join()
            print("Cleanup complete. Exiting...")
            



