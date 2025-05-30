import os


def load_stylesheet(name):

    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "layouts")
    file_path = os.path.join(base_path, f"layout_{name}.qss")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Estilo {name} no encontrado en la ruta: {file_path}")
        return ""
