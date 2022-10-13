import json

from flask import Flask, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Un valor que cambiaremos cuando vayamos a produccion "

DATETIME_STRING_FORMAT = "%d/%m/%Y %M:%H:%S"

@app.route("/dashboard")
def dashboard():
    now = datetime.now()

    # Le daremos unos valores default a las sesiones en lo que implementamos
    # los usuarios la proxima semana
    if not "user" in session:
        session["user"] = {
            "nombreUsuario": "Usuario anonimo",
            "id":  12345,
            "nivel":  7,
            "puntuacion":  70,
            "avatar":  "/static/img/to-be-determined.gif",
            "lastLogin":  now.strftime(DATETIME_STRING_FORMAT),
        }

    lastLogin = datetime.strptime(session["user"]["lastLogin"],
                                  DATETIME_STRING_FORMAT)
    
    timePast = now - lastLogin
    tenMinutes = 60 * 10

    if timePast.total_seconds() > tenMinutes:
        session["user"]["avatar"] = "/static/img/to-be-determined-sad.gif"
    

    # Pendiente de tener el template para rellenarlo
    return json.dumps(session["user"])


if __name__ == "__main__":
    app.run()