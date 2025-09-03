import ast
from typing import Dict, List
from bs4 import BeautifulSoup
import requests
import base64
from PIL import Image
from os import mkdir
import io
from json import loads, dumps


# File definitions

INDEX_TSX = """import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';

const container = document.getElementById('root');
const root = createRoot(container!);
root.render(<App />);
"""

SERVER_TS = """"""

APP_TSX = """import React from 'react';
import {} from './server'

export function App() {
    return <h1>Hello from PyReact 👋</h1>;
}
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>APP_NAME</title>
    <link href="./output.css" rel="stylesheet">
</head>
<body>
    <div onload="pollServerAndReload()" id="root"></div>
    <script id="bundle" src="bundle.js"></script>
    <script id="DEV_RELOAD">
        async function shouldReload() {
          const res = await fetch("/dev/reload");

          const data = await res.json();
          const reload = data.reload;

          if (reload) {
            window.location.reload()
          }
        }

        setInterval(shouldReload, 500)
    </script>
</body>
</html>"""

TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
export default {
   content: ["./src/**/*.{html,js}"],
   theme: {
     extend:{},
   },
   plugins: [],
}"""

INPUT_CSS = """@import "tailwindcss";"""

MAIN_PY = """from flask import jsonify
from pyrekit.server import Server, ServerProcess
from pyrekit.files import pack_app, project_name
import webview

# don't rename this class
class AppServer(Server):
    def index(self):
        return pack_app(self.DEV)

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 5000
    
    app_server = AppServer(host=HOST, port=PORT)
    server_proc = ServerProcess(server=app_server)
    server_proc.start()
    
    webview.create_window(project_name(), f"http://{HOST}:{PORT}/")
    webview.start()

    server_proc.close()"""

# Support functions
   
def convert_image(path: str, quality: int = 100):
    """
        Receives a image path and then converts it to a base64 uri
    """

    data = ""
    if path.startswith("http://") or path.startswith("https://"):
        response = requests.get(path)
        if response.status_code == 200:
            data = response.content
        else:
            raise FileNotFoundError(f"Failed to get image: {path}")
    else:
        try:
            with open(path, "rb") as fd:
                data = fd.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Failed to get image: {path}")


    with Image.open(data) as file:
        file = file.convert("RGB")
        with io.BytesIO() as buffer:
            file.save(buffer, format="webp", quality=quality)
            base64_image = base64.b64encode(buffer.getvalue())
            base64_string = base64_image.decode("utf-8")
            new_src = f"data:image/webp;base64,{base64_string}"
            return new_src

def parse(path: str) -> List[Dict[str, str]]:
    """
        Reads a file get the AppServer class and then get all routes -> List[{name: str, return: str, method: str}].
    """

    content = read_file(path)

    tree = ast.parse(content)
    methods = []

    for node in ast.walk(tree):
        # Check if its a class
        if isinstance(node, ast.ClassDef):

            if node.name == "AppServer":

                for item in node.body:
                    # Checks if its a method
                    if isinstance(item, ast.FunctionDef):
                        name = item.name
                        keywords = ("get_", "post_", "put_", "delete_")
                        actual_key = ""

                        # Check to see if its a route or a normal method
                        found = False
                        for key in keywords:
                            found = name.startswith(key.upper())

                            if found:
                                actual_key = key[:-1]
                                break
                        
                        if not found:
                            continue

                        returns = ""
                        if item.returns:
                            returns = ast.unparse(item.returns)

                        methods.append({
                            "name": name[len(actual_key)+1:],
                            "returns": returns,
                            "method": actual_key
                        })
                break
    
    return methods

def create_function(function_info: Dict[str, str]):
    """
        Creates a typescript function in server.ts for each route in the AppServer
    """

    route = "/"+function_info['name'].replace("_", "/")
    method = function_info['method']

    if method == "get":
        return f"""
export function {function_info['name']}() {{
  // Fetches data from the '{route}' endpoint.
  return fetch('{route}')
    .then(res => {{
      if (!res.ok) {{
        throw new Error(`HTTP error! Status: ${{res.status}}`);
      }}
      return res.json();
    }})
    .catch(err => {{
      console.error("Fetch error:", err);
      throw err; // Re-throw the error to be handled by the caller
    }});
}}
"""

    elif method in ["post", "put"]:
        # POST and PUT requests both send data in the request body.
        method_upper = method.upper()
        return f"""
export function {function_info['name']}(data: any) {{
  // Sends a {method_upper} request to the '{route}' endpoint.
  return fetch('{route}', {{
    method: '{method_upper}',
    headers: {{
      'Content-Type': 'application/json',
    }},
    body: JSON.stringify(data),
  }})
    .then(res => {{
      if (!res.ok) {{
        throw new Error(`HTTP error! Status: ${{res.status}}`);
      }}
      return res.json();
    }})
    .catch(err => {{
      console.error("Fetch error:", err);
      throw err; // Re-throw the error to be handled by the caller
    }});
}}
"""

    elif method == "delete":
        return f"""
export function {function_info['name']}(id: string | number) {{
  // Sends a DELETE request to the '{route}/{{id}}' endpoint.
  return fetch(`{route}/${{id}}`, {{
    method: 'DELETE',
  }})
    .then(res => {{
      if (!res.ok) {{
        throw new Error(`HTTP error! Status: ${{res.status}}`);
      }}
      return res.json();
    }})
    .catch(err => {{
      console.error("Fetch error:", err);
      throw err; // Re-throw the error to be handled by the caller
    }});
}}
"""
    
    # Return an empty string if the method is not supported
    return ""


def pack_server_functions():
    """
        Pack all the fetcher functions
    """
    functions_info = parse("main.py")
    functions = [create_function(item) for item in functions_info]
    
    for f in functions_info:
        print(f)

    server_ts = ""

    for item in functions:
        server_ts += item
    
    with open("src/server.ts", "w") as fd:
        fd.write(server_ts)


def pack_app(DEV = False) -> str:
    """
        Packs the application into a html bundle
    """

    html = read_file("build/index.html")
    bundle = read_file("build/bundle.js")
    css = read_file("build/output.css")
    soup = BeautifulSoup(html, 'html.parser')

    # Edit the script tag
    script_tag = soup.find("script", {"id": "bundle"})

    if script_tag:
        del script_tag["src"]
        script_tag.string = bundle

    # Removes link tag and add style tag
    link_tag = soup.find("link", rel="stylesheet")

    if link_tag:
        link_tag.decompose()

    head_tag = soup.head
    if head_tag:
        style_tag = soup.new_tag("style")
        style_tag.string = css
        head_tag.append(style_tag)

    # Build actions
    if not DEV:
        # Remove the dev reload
        reload_script = soup.find("script", {"id": "DEV_RELOAD"})
        reload_script.decompose()

        # Grab all images and put them in the page itself as a uri, if cant get image, print to the console which image is the problemn and continue
        images = soup.select("img")
        for img in images:
            src = img.get("src")
            
            try:
                img["src"] = convert_image(src)
            except FileNotFoundError as err:
                print(err)

    bare_string = soup.prettify()
    app_string = bare_string.replace('"""', '\\"\\"\\"')

    return app_string

def get_package() -> Dict[str, str]:
    """
        Gets package.json or close the entire programn if not found
    """
    json_str = read_file("package.json")
    if len(json_str) != 0:
        return loads(json_str)
    else:
        print("package.json not found, maybe you did not setup the project!")
        exit(0)

def project_name() -> str:
    package = get_package()
    return package['project-name']

def create_base_dirs() -> None:
    """
        Check if the base dirs exists if not create them
    """
    try:
        mkdir("src")
        mkdir("build")
    except FileExistsError:
        print("src and build Folders already exists!")

def create_files(AppName: str = "PyReact") -> None:
    """
    Creates base files for the app
    """

    with open("src/index.tsx", "w") as fd:
        fd.write(INDEX_TSX)

    with open("src/server.ts", "w") as fd:
        fd.write(SERVER_TS)

    with open("src/App.tsx", "w") as fd:
        fd.write(APP_TSX)

    with open("build/index.html", "w") as fd:
        fd.write(INDEX_HTML.replace("APP_NAME", AppName))

    with open("tailwind.config.js", "w") as fd:
        fd.write(TAILWIND_CONFIG)

    with open("src/input.css", "w") as fd:
        fd.write(INPUT_CSS)

    with open("main.py", "w") as fd:
        fd.write(MAIN_PY)

    with open("package.json", "w") as fd:
        fd.write(create_package(AppName))


def create_package(AppName: str) -> str:
    """
        Creates a base package.json string
    """

    package = {
        "project-name": AppName,
        "compilerOptions": {
            "target": "ES6",
            "module": "ESNext",
            "jsx": "react-jsx",
            "strict": True,
            "moduleResolution": "node",
            "esModuleInterop": True
        },
        "include": ["src"],
        "scripts": {
            "tailwindcss_dev": "npx @tailwindcss/cli -i ./src/input.css -o ./build/output.css",
            "tailwindcss": "npx @tailwindcss/cli -i ./src/input.css -o ./build/output.css -m",
            "esbuild_dev": "npx esbuild src/index.tsx --sourcemap --bundle --outfile=build/bundle.js --loader:.tsx=tsx",
            "esbuild": "npx esbuild src/index.tsx --minify --bundle --outfile=build/bundle.js --loader:.tsx=tsx",
            "build": "npm run tailwindcss && npm run esbuild",
            "run": "npm run tailwindcss_dev && npm run esbuild_dev"
        }
    }

    data = dumps(package, indent=4)
    return data


def read_file(path: str) -> str:
    """
        Read file and return content, if not exists, print error and returns empty string
    """

    try:
        with open(path, "r") as fd:
            return fd.read()
    except FileNotFoundError:
        print("File not Found! ", path)
        return ""
    
def list_scripts():
    """
    Lists the scripts available in package.json
    """
    package = get_package()
    scripts = package["scripts"].keys()
    print("Found", len(scripts), "scripts:")
    for s in scripts:
        print("\b - ", s)
