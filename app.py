from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Aplicación de Prueba DevSecOps</h1><p>Visita <a href='/hello?name=Mundo'>/hello?name=Mundo</a></p>"

@app.route("/hello")
def hello():
    # VULNERABILIDAD INTENCIONAL: Cross-Site Scripting (XSS) Reflejado
    # La entrada del usuario se concatena directamente en la plantilla sin escapar ni sanitizar
    name = request.args.get("name", "Invitado")
    template = f"""
    <!DOCTYPE html>
    <html>
    <head><title>DevSecOps Demo</title></head>
    <body>
        <h2>Bienvenido al sistema</h2>
        <p>Hola, {name}!</p>
    </body>
    </html>
    """
    return render_template_string(template)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
