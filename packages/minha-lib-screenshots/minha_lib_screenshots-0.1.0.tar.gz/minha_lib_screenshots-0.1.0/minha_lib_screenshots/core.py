import mss
from PIL import Image
from .utils import get_id_janela  # Importa a nova função
import subprocess


def get_window_geometry_from_id(window_id):
    """
    Obtém a geometria (x, y, largura, altura) de uma janela
    a partir de seu ID usando wmctrl.
    """
    try:
        # Comando para listar as janelas e encontrar a geometria
        cmd = ["wmctrl", "-l", "-G"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        for line in result.stdout.splitlines():
            if window_id in line:
                # Exemplo da linha: "0x01e00004 0 115 115 1100 800  Desktop - VS Code"
                parts = line.split()
                # A geometria começa no 3º elemento (índice 2)
                x, y, width, height = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                return x, y, width, height
    except subprocess.CalledProcessError as e:
        print(f"Erro ao obter geometria da janela: {e}")
    except (IndexError, ValueError):
        print("Erro ao parsear a geometria da janela.")
    
    return None


def capture_entire_screen():
    """
    Captura a tela inteira.

    Returns:
        Image: Objeto de imagem PIL.
    """
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[0]) # Captura o primeiro monitor
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")


def capture_screen_area(x, y, width, height):
    """
    Captura uma área específica da tela.

    Args:
        x (int): Coordenada X do canto superior esquerdo.
        y (int): Coordenada Y do canto superior esquerdo.
        width (int): Largura da área a ser capturada.
        height (int): Altura da área a ser capturada.

    Returns:
        Image: Objeto de imagem PIL.
    """
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")


def capture_window(pedaco_titulo):
    """
    Captura uma janela com base em uma parte do seu título.

    Args:
        pedaco_titulo (str): Uma parte do título da janela.

    Returns:
        Image: Objeto de imagem PIL ou None se a janela não for encontrada.
    """
    window_id = get_id_janela(pedaco_titulo)
    
    if window_id is None:
        print(f"Erro: Nenhuma janela encontrada com '{pedaco_titulo}' no título.")
        return None
        
    # Opcional: Focar na janela para garantir que ela esteja visível
    try:
        subprocess.run(["wmctrl", "-i", "-a", window_id], check=True)
    except subprocess.CalledProcessError:
        print(f"Aviso: Não foi possível focar na janela com ID {window_id}.")
        
    geometry = get_window_geometry_from_id(window_id)
    if geometry:
        x, y, width, height = geometry
        return capture_screen_area(x, y, width, height)
        
    return None