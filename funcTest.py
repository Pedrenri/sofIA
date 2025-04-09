import os
import subprocess
import time
import traceback
import pyautogui
from pyautogui import ImageNotFoundException

def github_operations(operation, repo_name=None, description=None, local_path=None):
    """
    Perform GitHub operations like creating, cloning or deleting repositories.
    """
    try:
        from github import Github
        import os
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            return "Erro: Token do GitHub não encontrado. Configure a variável GITHUB_TOKEN."
            print("Erro: Token do GitHub não encontrado. Configure a variável GITHUB_TOKEN.")
        g = Github(github_token)
        user = g.get_user()
        
        if operation == "create":
            if not repo_name:
                return "Erro: Nome do repositório não fornecido."
                print("Erro: Nome do repositório não fornecido.")
            repo = user.create_repo(
                name=repo_name,
                description=description or "",
                private=True
            )
            
            if local_path:
                os.makedirs(local_path, exist_ok=True)
                os.chdir(local_path)
                
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
                print("Erro: Nome do repositório não fornecido.")
            repo = None
            for r in user.get_repos():
                if r.name == repo_name:
                    repo = r
                    break
            
            if not repo:
                return f"Erro: Repositório {repo_name} não encontrado."
                print(f"Erro: Repositório {repo_name} não encontrado.")
            clone_path = local_path or os.path.join(os.getcwd(), repo_name)
            subprocess.run(f'git clone {repo.clone_url} "{clone_path}"', shell=True, check=True)
            
            return f"Repositório {repo_name} clonado para {clone_path}"
        elif operation == "delete":
            if not repo_name:
                return "Erro: Nome do repositório não fornecido."
                print("Erro: Nome do repositório não fornecido.")
            for repo in user.get_repos():
                if repo.name == repo_name:
                    repo.delete()
                    return f"Repositório {repo_name} excluído com sucesso."
            
            return f"Erro: Repositório {repo_name} não encontrado."
            print(f"Erro: Repositório {repo_name} não encontrado.")
        else:
            return f"Operação desconhecida: {operation}"
            print(f"Operação desconhecida: {operation}")
    except Exception as e:
        return f"Erro na operação do GitHub: {str(e)}"
        print(f"Erro na operação do GitHub: {str(e)}")
        
github_operations("create", repo_name="test-repo", description="Test repository", local_path="C:/Users/conta/Desktop/test-repo")