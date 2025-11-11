import pytest
import builtins
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from functions import lights_control, run_os_command, clean_code, create_file, open_application

def test_run_os_command_blocked():
    blocked = run_os_command("shutdown -h now")
    assert "bloqueado" in blocked or "⚠️" in blocked

def test_clean_code_quotes():
    s = "\"print('hello')\\n\""
    cleaned = clean_code(s)
    assert "print" in cleaned and '"' not in cleaned[0:1]

def test_create_file(tmp_path):
    test_file = tmp_path / "subdir" / "hello.txt"
    content = "'Olá mundo\\n'"
    res = create_file(str(test_file), content)
    assert "Arquivo criado" in res or test_file.exists()
    if test_file.exists():
        assert test_file.read_text(encoding='utf-8').strip().startswith("Olá")

def test_open_application_returns_string():
    res = open_application("app_que_nao_existe_12345")
    assert isinstance(res, str)
