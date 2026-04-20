from flask import Flask, render_template
from db import fetch_one

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
    featured_camera = fetch_one("""
        SELECT
            c.camera_id,
            c.camera_name,
            m.manufacturer_name,
            c.release_year,
            c.camera_type,
            mo.mount_name,
            c.notes
        FROM cameras c
        JOIN manufacturers m ON c.manufacturer_id = m.manufacturer_id
        LEFT JOIN mounts mo ON c.mount_id = mo.mount_id
        ORDER BY RAND()
        LIMIT 1;
    """)

    featured_film = fetch_one("""
        SELECT
            fs.film_id,
            fs.film_name,
            m.manufacturer_name,
            fs.iso,
            ff.format_name,
            fs.color_type,
            fs.release_year,
            fs.discontinued,
            fs.notes
        FROM film_stocks fs
        JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
        JOIN film_formats ff ON fs.format_id = ff.format_id
        ORDER BY RAND()
        LIMIT 1;
    """)

    featured_lens = fetch_one("""
        SELECT
            l.lens_id,
            l.lens_name,
            m.manufacturer_name,
            mo.mount_name,
            l.focal_length,
            l.max_aperture,
            l.lens_type,
            l.release_year,
            l.notes
        FROM lenses l
        JOIN manufacturers m ON l.manufacturer_id = m.manufacturer_id
        JOIN mounts mo ON l.mount_id = mo.mount_id
        ORDER BY RAND()
        LIMIT 1;
    """)

    featured_documentation = fetch_one("""
        SELECT
            documentation_id,
            title,
            document_type,
            source,
            publication_year,
            url
        FROM documentation
        ORDER BY RAND()
        LIMIT 1;
    """)

    return render_template(
        "index.html",
        featured_camera=featured_camera,
        featured_film=featured_film,
        featured_lens=featured_lens,
        featured_documentation=featured_documentation
    )


if __name__ == "__main__":
    app.run(debug=True)