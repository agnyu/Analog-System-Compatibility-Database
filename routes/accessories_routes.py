from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

accessories_bp = Blueprint("accessories_bp", __name__)

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