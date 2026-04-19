from flask import Flask, render_template
from routes.film_routes import film_bp
from routes.film_formats_routes import film_formats_bp
from routes.camera_routes import camera_bp
from routes.camera_variants_routes import camera_variants_bp
from routes.lenses_routes import lenses_bp
from routes.mounts_routes import mounts_bp
from routes.documentation_routes import documentation_bp
from routes.accessories_routes import accessories_bp
from routes.developers_routes import developers_bp
from routes.development_guide_routes import development_guide_bp
from routes.accessory_types_routes import accessory_types_bp
from routes.accessory_compatibility_routes import accessory_compatibility_bp

app = Flask(__name__)

app.register_blueprint(film_bp)
app.register_blueprint(film_formats_bp)
app.register_blueprint(camera_bp)
app.register_blueprint(camera_variants_bp)
app.register_blueprint(lenses_bp)
app.register_blueprint(mounts_bp)
app.register_blueprint(documentation_bp)
app.register_blueprint(accessories_bp)
app.register_blueprint(developers_bp)
app.register_blueprint(development_guide_bp)
app.register_blueprint(accessory_types_bp)
app.register_blueprint(accessory_compatibility_bp)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)