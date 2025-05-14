import httpx
from datetime import datetime


# TODO: implements and test robotframework listener to trace all logs from automations
class RobotLogListener:
    """
    this implementation isint working properly, the .robot file doesnt set the listener with
    the flag --listener

    Usefull docs:
        - https://docs.robotframework.org/docs/extending_robot_framework/listeners_prerun_api/listeners (main docs)
        - https://github.com/robotframework/robotframework/issues/3031
        - https://github.com/robotframework/robotframework/blob/master/doc/userguide/src/ExtendingRobotFramework/ListenerInterface.rst#id97
        - https://github.com/robotframework/robotframework/blob/master/doc/userguide/src/ExtendingRobotFramework/ListenerInterface.rst#listener-version-3
        - https://forum.robotframework.org/t/how-to-catch-suite-setup-failure-in-listener-interface-3/5664
    """
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LISTENER_API_VERSION = 3

    def log_message(self, message):
        print("[RobotLogListener] Mensagem recebida:", message.level, message.message)
        try:
            timestamp = datetime.strptime(message.timestamp, "%Y%m%d %H:%M:%S.%f").isoformat()
            data = {
                "level": message.level,
                "message": message.message,
                "timestamp": timestamp,
                "type": "robotframework"
            }

            with httpx.Client() as client:
                client.post("http://localhost:8000/logs/post", json=data)

        except Exception as e:
            print("[RobotLogListener] Erro ao enviar log:", e)
