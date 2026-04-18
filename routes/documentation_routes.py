from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

documentation_bp = Blueprint("documentation_bp", __name__)

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