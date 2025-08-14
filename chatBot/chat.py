from flask import Flask

# Cream aplicatia Flask
app = Flask(__name__)

# Ruta principala
@app.route('/')
def index():
    return "Hello, Flask is running!"


# Aceasta parte nu e necesara pe Passenger, dar e utila pentru test local
if __name__ == "__main__":
    app.run(debug=True)
