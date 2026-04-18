from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

lenses_bp = Blueprint("lenses_bp", __name__)

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
