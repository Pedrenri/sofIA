import os
import subprocess
import time
import traceback
import pyautogui
import requests
from dotenv import load_dotenv
from pyautogui import ImageNotFoundException

load_dotenv()

""" TODO:
    - 🆗 Implementar funções com a Amazon (controle de dispositivos Alexa); 🆗
    - Implementar funções para controle de navegadores e música no computador host;
    - Implementar controle e gerenciamento de agenda (foco no google calendar);
    - Implementar funções para melhor controle das impressoras 3D Bambu Lab (estudar conexão com Prusa no futuro)
    - Implementar melhorias de UI e UX:
        - 🆗 Adicionar wake-word para ativação por voz direta do programa; 🆗
        - 🆗 Adicionar capacidade de rodar e escutar em background; 🆗
        - Adicionar suporte de overlay (identifica wake-word -> exibe overlay no monitor -> ouve -> executa)
        - 🆗 Adicionar modo de desenvolvimento (com front como é atualmente.) 🆗
"""


alexa_device_states = {
    "quarto": False,
    "sala": False
}

_last_lights_control_time = 0
alexa_webhook = os.getenv("IFTTTUrl")

def lights_control(routine: str):
    """
    Control a light/device linked to alexa.
    """

    if not alexa_webhook:
        return "Erro: URL do webhook da Alexa não está configurada."

    global _last_lights_control_time
    now = time.time()
    if now - _last_lights_control_time < 2:
        return "Aguarde um pouco."

    _last_lights_control_time = now
    routine_mapping = {
        "LuzQuartoOn": ("quarto", True),
        "LuzQuartoOff": ("quarto", False),
        "LuzSalaOn": ("sala", True),
        "LuzSalaOff": ("sala", False),
    }

    if routine not in routine_mapping:
        return f"Error: Unknown routine '{routine}'."

    print("DEBUG: Running Alexa routine:", routine)

    if (routine == "LuzQuartoOn" and alexa_device_states["quarto"] is True):
        routine = "LuzQuartoOff"

    device, state = routine_mapping[routine]
    alexa_device_states[device] = state

    try:
        url = f"{alexa_webhook}/{routine}"
        response = requests.get(url)

        if "data" in response.json():
            event_id = response.json()["data"][0].get("id")
            if event_id.startswith("SUCCESS"):
                return "Sucesso"
            else:
                return f"Falha ao ativar a rotina '{routine}': {event_id}"

    except Exception as e:
        return str(e)
    
# Isso foi adicionado para evitar que a SofIA desligue a si mesma.

FORBIDDEN_COMMANDS = [
    "shutdown",
    "reboot",
    "poweroff",
    "desligar",
    "reiniciar",
    "shutdown.exe"
]

def run_os_command(command: str) -> str:
    """
    Execute an OS system command and return its output,
    but block dangerous commands like shutdown or reboot.
    """
    command_lower = command.lower()

    if any(word in command_lower for word in FORBIDDEN_COMMANDS):
        return "⚠️ Comando bloqueado por segurança."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
    except Exception as e:
        return str(e)

def print_stl(stl_file: str, pc_username: str = None) -> str:
    """
    Open an STL file with the default associated application using subprocess.run,
    then click through a series of images to initiate printing.
    
    The STL file path can use environment variables (e.g., %USERPROFILE%) or ~ for home.
    Additionally, if the file path contains "YourUsername", it is replaced with the
    provided pc_username (or the PC_USERNAME environment variable).
    
    Returns a success or error message.
    """
    try:
        # If a username is provided, use it; otherwise, get it from the environment.
        if pc_username is None:
            pc_username = os.getenv("PC_USERNAME", "YourUsername")
        
        # Replace "YourUsername" placeholder with the actual PC username.
        stl_file = stl_file.replace("YourUsername", pc_username)
        
        # Expand environment variables and user home directory in the provided path.
        stl_file_expanded = os.path.expandvars(stl_file)
        stl_file_expanded = os.path.expanduser(stl_file_expanded)
        print(f"Expanded STL file path: {stl_file_expanded}")
        
        # Check if the file exists
        if not os.path.exists(stl_file_expanded):
            return f"Error: File not found at {stl_file_expanded}"
        
        # Open the STL file using subprocess.run.
        command = f'start "" "{stl_file_expanded}"'
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stderr:
            print("Error opening STL file:", result.stderr)
            return f"Error opening STL file: {result.stderr}"
        
        # Wait for the application to open (adjust delay as needed)
        time.sleep(10)
        
        # Define image paths for the printing workflow
        images = [
            './bambu_print/slice.jpg',
            './bambu_print/print.jpg',
            './bambu_print/send.jpg'
        ]
        confidence_threshold = 0.99
        
        for image in images:
            print(f'Waiting for {image}...')
            while True:
                try:
                    location = pyautogui.locateOnScreen(image, confidence=confidence_threshold)
                    if location:
                        x, y = pyautogui.center(location)
                        print(f'Found {image}, clicking at ({x}, {y})')
                        pyautogui.click(x, y)
                        time.sleep(3)  # Pause briefly after each click
                        break
                except ImageNotFoundException:
                    time.sleep(0.5)
        return "STL file printed successfully."
    except Exception as e:
        return f"Error printing STL: {str(e)}"

def clean_code(code_string):
    """
    Remove escape characters, quotes and other formatting issues from generated code.
    """
    if not any(char in code_string for char in ['\n', '\t', '"', "\'"]):
        return code_string
    
    if (code_string.startswith('"') and code_string.endswith('"')) or \
       (code_string.startswith("'") and code_string.endswith("'")):
        code_string = code_string[1:-1]
    
    code_string = code_string.replace('\n', '\n')
    
    replacements = {
        '\\t': '\\t',
        '"': '"',
        "\\'": "'",
        '\\': '\\',
        '\\r': '\\r'
    }
    
    for old, new in replacements.items():
        code_string = code_string.replace(old, new)
    
    return code_string

def create_file(file_path, content):
    """
    Create a file with the given content, cleaning the code first.
    """
    try:
        print(f"DEBUG: Tentando criar arquivo em: {file_path}")
        print(f"DEBUG: Primeiros 100 caracteres do conteúdo: {content[:100]}")
        
        file_path = os.path.expandvars(file_path)
        file_path = os.path.expanduser(file_path)
        file_path = os.path.normpath(file_path)
        print(f"DEBUG: Caminho normalizado: {file_path}")
        
        # Garante que o diretório existe
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            print(f"DEBUG: Criando diretório: {directory}")
            os.makedirs(directory, exist_ok=True)
        
        # Limpa o conteúdo
        cleaned_content = clean_code(content)
        print(f"DEBUG: Conteúdo limpo. Primeiros 100 caracteres: {cleaned_content[:100]}")
        
        # Escreve no arquivo
        print(f"DEBUG: Escrevendo no arquivo: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        # Verifica se o arquivo foi criado
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"DEBUG: Arquivo criado com sucesso: {file_path} ({file_size} bytes)")
            return f"Arquivo criado: {file_path}"
        else:
            print(f"DEBUG: Arquivo não encontrado após criação: {file_path}")
            return f"Erro: Arquivo não foi criado em {file_path}"
    except Exception as e:
        print(f"DEBUG: Erro ao criar arquivo: {str(e)}")
        traceback.print_exc()
        return f"Erro ao criar arquivo: {str(e)}"
        
def open_application(app_name):
    """
    Finds and opens an application by name, using various strategies to
    locate applications in Windows
    """
    try:
        import os
        import subprocess
        import glob
        
        print(f"DEBUG: Tentando abrir aplicativo: {app_name}")

        if (app_name.lower() == "bamboo" or app_name.lower() == "bamboo studio"):
            app_name = app_name.replace("bamboo", "bambu")

        print(f"DEBUG: Nome do aplicativo normalizado: {app_name}")
        # Normaliza o nome do aplicativo
        app_name_lower = app_name.lower()
        
        # 1. Verifica aplicativos comuns com comandos diretos
        common_apps = {
            'chrome': 'start chrome',
            'google chrome': 'start chrome',
            'firefox': 'start firefox',
            'edge': 'start msedge',
            'microsoft edge': 'start msedge',
            'word': 'start winword',
            'excel': 'start excel',
            'powerpoint': 'start powerpnt',
            'notepad': 'start notepad',
            'bloco de notas': 'start notepad',
            'cmd': 'start cmd',
            'prompt de comando': 'start cmd',
            'terminal': 'start cmd',
            'explorer': 'start explorer',
            'explorador de arquivos': 'start explorer',
            'calculadora': 'start calc',
            'calculator': 'start calc',
            'paint': 'start mspaint',
            'spotify': 'start spotify',
            'discord': 'start discord',
            'steam': 'start steam',
            'visual studio code': 'start code',
            'vscode': 'start code',
            'vs code': 'start code',
            'outlook': 'start outlook',
            'teams': 'start teams',
            'microsoft teams': 'start teams'
        }
        
        # Verifica se é um app comum
        for key, command in common_apps.items():
            if app_name_lower == key or app_name_lower in key:
                print(f"DEBUG: Executando comando direto: {command}")
                subprocess.run(command, shell=True)
                return f"Abrindo {app_name}"
        
        # 2. Tenta encontrar no Menu Iniciar
        start_menu_paths = [
            os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
            os.path.join(os.environ.get('PROGRAMDATA', r'C:\ProgramData'), r'Microsoft\Windows\Start Menu\Programs')
        ]
        
        for start_menu in start_menu_paths:
            if os.path.exists(start_menu):
                print(f"DEBUG: Procurando em {start_menu}")
                # Procura por atalhos (.lnk) que contenham o nome do aplicativo
                for root, dirs, files in os.walk(start_menu):
                    for file in files:
                        if file.lower().endswith('.lnk'):
                            if app_name_lower in file.lower():
                                shortcut_path = os.path.join(root, file)
                                print(f"DEBUG: Encontrado atalho: {shortcut_path}")
                                os.startfile(shortcut_path)
                                return f"Abrindo {file}"
        
        # 3. Tenta procurar nos diretórios de programas
        program_dirs = [
            os.environ.get('ProgramFiles', r'C:\Program Files'),
            os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'),
            os.path.join(os.environ.get('LOCALAPPDATA', r'C:\Users'), os.environ.get("USERNAME", "conta"), r'AppData\Local')
        ]
        
        for program_dir in program_dirs:
            if os.path.exists(program_dir):
                print(f"DEBUG: Procurando em {program_dir}")
                # Procura por executáveis (.exe) que contenham o nome do aplicativo
                exe_paths = []
                for root, dirs, files in os.walk(program_dir):
                    for file in files:
                        if file.lower().endswith('.exe'):
                            if app_name_lower in file.lower():
                                exe_path = os.path.join(root, file)
                                exe_paths.append(exe_path)
                
                # Se encontrou algum executável, abre o primeiro
                if exe_paths:
                    print(f"DEBUG: Encontrados {len(exe_paths)} executáveis")
                    print(f"DEBUG: Abrindo {exe_paths[0]}")
                    os.startfile(exe_paths[0])
                    return f"Abrindo {os.path.basename(exe_paths[0])}"
        
        # 4. Tenta pesquisar no registro do Windows
        try:
            import winreg
            print("DEBUG: Pesquisando no registro do Windows")
            # Procura por aplicativos registrados
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        app_key = winreg.EnumKey(key, i)
                        if app_name_lower in app_key.lower():
                            with winreg.OpenKey(key, app_key) as app_key_handle:
                                app_path = winreg.QueryValue(app_key_handle, None)
                                print(f"DEBUG: Encontrado no registro: {app_path}")
                                os.startfile(app_path)
                                return f"Abrindo {app_key}"
                    except:
                        continue
        except Exception as reg_error:
            print(f"DEBUG: Erro ao pesquisar no registro: {reg_error}")
        
        # 5. Última tentativa: executa diretamente como comando
        print(f"DEBUG: Tentativa final: executar como comando")
        try:
            subprocess.run(f'start {app_name}', shell=True, check=True)
            return f"Tentando abrir {app_name}"
        except subprocess.CalledProcessError:
            # Se falhar, tenta com o comando "explorer"
            try:
                subprocess.run(f'explorer shell:AppsFolder{app_name}', shell=True, check=True)
                return f"Tentando abrir {app_name} via explorer"
            except:
                pass
        
        # Se chegou aqui, não conseguiu abrir o aplicativo
        return f"Não foi possível encontrar ou abrir {app_name}"
    
    except Exception as e:
        print(f"DEBUG: Erro ao abrir aplicativo: {str(e)}")
        return f"Erro ao abrir {app_name}: {str(e)}"
    