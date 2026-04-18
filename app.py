from flask import Flask, render_template
from routes.film_routes import film_bp
from routes.camera_routes import camera_bp
from routes.lenses_routes import lenses_bp
from routes.mounts_routes import mounts_bp
from routes.documentation_routes import documentation_bp
from routes.accessories_routes import accessories_bp

app = Flask(__name__)

app.register_blueprint(film_bp)
app.register_blueprint(camera_bp)
app.register_blueprint(lenses_bp)
app.register_blueprint(mounts_bp)
app.register_blueprint(documentation_bp)
app.register_blueprint(accessories_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


#Top Level Categories Here


#Sub Level Categories Here
@app.route("/camera-variants")
def camera_variants():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    variants_query = """
    SELECT
        cv.variant_id,
        cv.variant_name,
        c.camera_name,
        cv.release_year,
        cv.frame_format,
        cv.production_end_year,
        cv.notes
    FROM camera_variants cv
    JOIN cameras c ON cv.camera_id = c.camera_id
    ORDER BY cv.variant_name;
    """

    cameras_query = """
    SELECT camera_id, camera_name
    FROM cameras
    ORDER BY camera_name;
    """

    cursor.execute(variants_query)
    variants = cursor.fetchall()

    cursor.execute(cameras_query)
    cameras = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "camera_variants.html",
        variants=variants,
        cameras=cameras
    )



@app.route("/developers")
def developers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    developers_query = """
    SELECT
        d.developer_id,
        d.developer_name,
        m.manufacturer_name,
        d.developer_type,
        d.notes
    FROM film_developers d
    JOIN manufacturers m ON d.manufacturer_id = m.manufacturer_id
    ORDER BY d.developer_name;
    """

    manufacturers_query = """
    SELECT manufacturer_id, manufacturer_name
    FROM manufacturers
    ORDER BY manufacturer_name;
    """

    cursor.execute(developers_query)
    developers = cursor.fetchall()

    cursor.execute(manufacturers_query)
    manufacturers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "developers.html",
        developers=developers,
        manufacturers=manufacturers
    )

@app.route("/development-guide")
def development_guide():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    guides_query = """
    SELECT
        fdg.development_id,
        fs.film_name,
        fd.developer_name,
        fdg.temperature_celsius,
        fdg.dilution,
        fdg.shot_iso,
        fdg.development_time_minutes,
        fdg.agitation_notes,
        fdg.notes
    FROM film_development_guide fdg
    JOIN film_stocks fs ON fdg.film_id = fs.film_id
    JOIN film_developers fd ON fdg.developer_id = fd.developer_id
    ORDER BY fs.film_name, fd.developer_name;
    """

    films_query = """
    SELECT film_id, film_name
    FROM film_stocks
    ORDER BY film_name;
    """

    developers_query = """
    SELECT developer_id, developer_name
    FROM film_developers
    ORDER BY developer_name;
    """

    cursor.execute(guides_query)
    guides = cursor.fetchall()

    cursor.execute(films_query)
    films = cursor.fetchall()

    cursor.execute(developers_query)
    developers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "development_guide.html",
        guides=guides,
        films=films,
        developers=developers
    )

@app.route("/accessory-types")
def accessory_types():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    accessory_types_query = """
    SELECT
        accessory_type_id,
        type_name
    FROM accessory_types
    ORDER BY type_name;
    """

    cursor.execute(accessory_types_query)
    accessory_types = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "accessory_types.html",
        accessory_types=accessory_types
    )

@app.route("/accessory-compatibility")
def accessory_compatibility():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    compat_query = """
    SELECT
        ac.accessory_compat_id,
        a.accessory_name,
        cv.variant_name,
        ac.compatibility_type,
        ac.notes
    FROM accessory_compatibility ac
    JOIN accessories a ON ac.accessory_id = a.accessory_id
    JOIN camera_variants cv ON ac.variant_id = cv.variant_id
    ORDER BY a.accessory_name, cv.variant_name;
    """

    accessories_query = """
    SELECT accessory_id, accessory_name
    FROM accessories
    ORDER BY accessory_name;
    """

    variants_query = """
    SELECT variant_id, variant_name
    FROM camera_variants
    ORDER BY variant_name;
    """

    cursor.execute(compat_query)
    compatibilities = cursor.fetchall()

    cursor.execute(accessories_query)
    accessories = cursor.fetchall()

    cursor.execute(variants_query)
    variants = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "accessory_compatibility.html",
        compatibilities=compatibilities,
        accessories=accessories,
        variants=variants
    )

@app.route("/film-formats")
def film_formats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    formats_query = """
    SELECT
        format_id,
        format_name,
        format_type,
        notes
    FROM film_formats
    ORDER BY format_name;
    """

    cursor.execute(formats_query)
    formats = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "film_formats.html",
        formats=formats
    )

#Sub Level Categories Here

if __name__ == "__main__":
    app.run(debug=True)