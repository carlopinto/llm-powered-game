import os
from llmgame import create_app

app = create_app()

app.secret_key = os.getenv("APP_SECRET_KEY")

if __name__ == '__main__':
    app.run()