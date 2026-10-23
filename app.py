from flask import Flask, render_template, request
from agent import ErroAgente, verificar

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    texto = request.form.get("entrada", "")
    resultado = None
    erro = None
    if request.method == "POST":
        if not texto.strip():
            erro = "Insira uma notícia, manchete ou afirmação."
        else:
            try:
                resultado = verificar(texto)
            except ErroAgente as exc:
                erro = str(exc)
            except Exception:
                erro = "Não foi possível concluir a verificação. Tente novamente."
    return render_template("index.html", texto=texto, resultado=resultado, erro=erro)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
