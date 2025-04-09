import os
import subprocess
import time
import traceback

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
    
create_file("C:\\\\Users\\\\conta\\\\Desktop\\\\teste.txt","")