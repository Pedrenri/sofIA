import os
import subprocess
import time
import traceback
import pyautogui
from pyautogui import ImageNotFoundException

def run_os_command(command: str) -> str:
    """
    Execute an OS system command and return its output.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
    except Exception as e:
        return str(e)

def print_message(message: str) -> str:
    """
    Print a message in the terminal and return an acknowledgement.
    """
    print(f"Jarvis Print: {message}")
    return f"Printed: {message}"

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
    Find and open an application by name.
    """
    try:
        if os.name == 'nt':  # Windows
            program_files = [
                os.environ.get('ProgramFiles', 'C:\\Program Files'),
                os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'),
                os.environ.get('LOCALAPPDATA', 'C:\\Users\\conta\\AppData\\Local')
            ]
            
            common_apps = {
                'chrome': 'start chrome',
                'firefox': 'start firefox',
                'edge': 'start msedge',
                'word': 'start winword',
                'excel': 'start excel',
                'powerpoint': 'start powerpnt',
                'notepad': 'start notepad',
                'cmd': 'start cmd',
                'explorer': 'start explorer',
                'calculator': 'start calc'
            }
            
            app_lower = app_name.lower()
            if app_lower in common_apps:
                subprocess.Popen(common_apps[app_lower], shell=True)
                return f"Abrindo {app_name}"
            
            # Try to find the .exe file
            for folder in program_files:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if file.lower() == f"{app_lower}.exe" or app_lower in file.lower():
                            path = os.path.join(root, file)
                            subprocess.Popen(f'start "" "{path}"', shell=True)
                            return f"Abrindo {file}"
            
            # If not found, try to run it directly
            subprocess.Popen(f'start {app_name}', shell=True)
            return f"Tentando abrir {app_name}"
        else:
            # For non-Windows systems
            subprocess.Popen(app_name, shell=True)
            return f"Abrindo {app_name}"
    except Exception as e:
        return f"Erro: {str(e)}"
    
def github_operations(operation, repo_name=None, description=None, local_path=None):
    """
    Perform GitHub operations like creating, cloning or deleting repositories.
    """
    try:
        # You'll need to install PyGithub: pip install PyGithub
        from github import Github
        import os
        
        # Get GitHub token from environment variable
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            return "Erro: Token do GitHub não encontrado. Configure a variável GITHUB_TOKEN."
        
        g = Github(github_token)
        user = g.get_user()
        
        if operation == "create":
            if not repo_name:
                return "Erro: Nome do repositório não fornecido."
            
            # Create the repository
            repo = user.create_repo(
                name=repo_name,
                description=description or "",
                private=True
            )
            
            # If local_path is provided, initialize the repo locally
            if local_path:
                os.makedirs(local_path, exist_ok=True)
                os.chdir(local_path)
                
                # Initialize git repo
                commands = [
                    f'git init',
                    f'echo "# {repo_name}" > README.md',
                    f'git add README.md',
                    f'git commit -m "Initial commit"',
                    f'git branch -M main',
                    f'git remote add origin {repo.clone_url}',
                    f'git push -u origin main'
                ]
                
                for cmd in commands:
                    subprocess.run(cmd, shell=True, check=True)
                
                return f"Repositório {repo_name} criado e inicializado em {local_path}"
            
            return f"Repositório {repo_name} criado com sucesso."
            
        elif operation == "clone":
            if not repo_name:
                return "Erro: Nome do repositório não fornecido."
            
            # Find the repository
            repo = None
            for r in user.get_repos():
                if r.name == repo_name:
                    repo = r
                    break
            
            if not repo:
                return f"Erro: Repositório {repo_name} não encontrado."
            
            # Clone the repository
            clone_path = local_path or os.path.join(os.getcwd(), repo_name)
            subprocess.run(f'git clone {repo.clone_url} "{clone_path}"', shell=True, check=True)
            
            return f"Repositório {repo_name} clonado para {clone_path}"
            
        elif operation == "delete":
            if not repo_name:
                return "Erro: Nome do repositório não fornecido."
            
            # Find and delete the repository
            for repo in user.get_repos():
                if repo.name == repo_name:
                    repo.delete()
                    return f"Repositório {repo_name} excluído com sucesso."
            
            return f"Erro: Repositório {repo_name} não encontrado."
            
        else:
            return f"Operação desconhecida: {operation}"
            
    except Exception as e:
        return f"Erro na operação do GitHub: {str(e)}"