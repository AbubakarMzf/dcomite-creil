"""
Point d'entree web pour DComite
Separe du main.py (Tkinter)
Lancer: python web_app.py
"""
from web import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
