from flask import Flask
from src.routes.generation import generation_bp
from src.routes.user import user_bp
from src.routes.report import report_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(generation_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)