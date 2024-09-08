from app import create_app
from cli import cli

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)