from flask import Flask, render_template
from routes.film_routes import film_bp

app = Flask(__name__)

app.register_blueprint(film_bp)
app.register_blueprint(camera_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/lenses")
def lenses():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    lens_query = """
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
    ORDER BY l.lens_name;
    """

    manufacturers_query = """
    SELECT manufacturer_id, manufacturer_name
    FROM manufacturers
    ORDER BY manufacturer_name;
    """

    mounts_query = """
    SELECT mount_id, mount_name
    FROM mounts
    ORDER BY mount_name;
    """

    cursor.execute(lens_query)
    lenses = cursor.fetchall()

    cursor.execute(manufacturers_query)
    manufacturers = cursor.fetchall()

    cursor.execute(mounts_query)
    mounts = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "lenses.html",
        lenses=lenses,
        manufacturers=manufacturers,
        mounts=mounts
    )


@app.route("/accessories")
def accessories():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    accessory_query = """
    SELECT
        a.accessory_id,
        a.accessory_name,
        m.manufacturer_name,
        at.type_name,
        mo.mount_name,
        ff.format_name,
        a.release_year,
        a.description,
        a.compatibility_notes
    FROM accessories a
    JOIN manufacturers m ON a.manufacturer_id = m.manufacturer_id
    JOIN accessory_types at ON a.accessory_type_id = at.accessory_type_id
    LEFT JOIN mounts mo ON a.mount_id = mo.mount_id
    LEFT JOIN film_formats ff ON a.format_id = ff.format_id
    ORDER BY a.accessory_name;
    """

    manufacturers_query = """
    SELECT manufacturer_id, manufacturer_name
    FROM manufacturers
    ORDER BY manufacturer_name;
    """

    accessory_types_query = """
    SELECT accessory_type_id, type_name
    FROM accessory_types
    ORDER BY type_name;
    """

    mounts_query = """
    SELECT mount_id, mount_name
    FROM mounts
    ORDER BY mount_name;
    """

    formats_query = """
    SELECT format_id, format_name
    FROM film_formats
    ORDER BY format_name;
    """

    cursor.execute(accessory_query)
    accessories = cursor.fetchall()

    cursor.execute(manufacturers_query)
    manufacturers = cursor.fetchall()

    cursor.execute(accessory_types_query)
    accessory_types = cursor.fetchall()

    cursor.execute(mounts_query)
    mounts = cursor.fetchall()

    cursor.execute(formats_query)
    formats = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "accessories.html",
        accessories=accessories,
        manufacturers=manufacturers,
        accessory_types=accessory_types,
        mounts=mounts,
        formats=formats
    )


@app.route("/documentation")
def documentation():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    documentation_query = """
    SELECT
        d.documentation_id,
        d.title,
        c.camera_name,
        cv.variant_name,
        d.document_type,
        d.source,
        d.publication_year,
        d.url,
        d.notes
    FROM documentation d
    JOIN cameras c ON d.camera_id = c.camera_id
    LEFT JOIN camera_variants cv ON d.variant_id = cv.variant_id
    ORDER BY d.title;
    """

    cameras_query = """
    SELECT camera_id, camera_name
    FROM cameras
    ORDER BY camera_name;
    """

    variants_query = """
    SELECT variant_id, variant_name
    FROM camera_variants
    ORDER BY variant_name;
    """

    cursor.execute(documentation_query)
    documentation = cursor.fetchall()

    cursor.execute(cameras_query)
    cameras = cursor.fetchall()

    cursor.execute(variants_query)
    variants = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "documentation.html",
        documentation=documentation,
        cameras=cameras,
        variants=variants
    )

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

@app.route("/mounts")
def mounts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    mounts_query = """
    SELECT
        mo.mount_id,
        mo.mount_name,
        m.manufacturer_name,
        mo.mount_type,
        mo.year_introduced,
        mo.notes
    FROM mounts mo
    JOIN manufacturers m ON mo.manufacturer_id = m.manufacturer_id
    ORDER BY mo.mount_name;
    """

    manufacturers_query = """
    SELECT manufacturer_id, manufacturer_name
    FROM manufacturers
    ORDER BY manufacturer_name;
    """

    cursor.execute(mounts_query)
    mounts = cursor.fetchall()

    cursor.execute(manufacturers_query)
    manufacturers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "mounts.html",
        mounts=mounts,
        manufacturers=manufacturers
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