from app import create_app

app = create_app()

@app.route('/ping')
def ping():
    return "Pong from run.py!"
