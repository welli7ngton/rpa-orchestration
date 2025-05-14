import json


def save_log_in_file(body: bytes):
    log_data = json.loads(body.decode("utf-8"))

    if log_data.get("type") == "python":
        log_path = './python_log.log'

    if log_data.get("type") == "robotframework":
        log_path = './robotframework_log.log'

    linha = f'{log_data["level"]}|{log_data["timestamp"]}|{log_data["type"]}|{log_data["message"]}\n'

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(linha)
    except Exception as e:
        print(f"[Erro ao salvar log no arquivo] {e}")
