import subprocess

def get_id_janela(pedaco_titulo):
    """
    Obtém o ID de uma janela com base em uma parte de seu título, usando wmctrl.

    Args:
        pedaco_titulo (str): Uma parte do título da janela.

    Returns:
        str: O ID da janela (ex: "0x0180000a") ou None se a janela não for encontrada.
    """
    try:
        # Comando para listar as janelas usando wmctrl
        # -l: lista as janelas
        # -p: mostra o PID
        # -G: mostra a geometria
        cmd = ["wmctrl", "-l", "-p", "-G"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # O resultado do comando será algo como:
        # "0x0180000a -1 3192 0 0 1024 768 nome da janela"
        
        lines = result.stdout.splitlines()
        for line in lines:
            if pedaco_titulo.lower() in line.lower():
                # O ID da janela é o primeiro item da linha
                window_id = line.split()[0]
                return window_id

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando wmctrl: {e}")
        return None
    except IndexError:
        # Não encontrou a janela na linha
        return None
        
    return None