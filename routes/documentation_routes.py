from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

documentation_bp = Blueprint("documentation_bp", __name__)

@documentation_bp.route("/documentation")
def documentation():
    documentation_query = """
    SELECT
        d.documentation_id,
        d.title,
        d.camera_id,
        c.camera_name,
        d.variant_id,
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

    documentation = fetch_all(documentation_query)
    cameras = fetch_all(cameras_query)
    variants = fetch_all(variants_query)

    mode = request.args.get("mode")

    return render_template(
        "documentation.html",
        documentation=documentation,
        cameras=cameras,
        variants=variants,
        doc_to_edit=None,
        mode=mode
    )


@documentation_bp.route("/documentation/edit/<int:documentation_id>")
def edit_documentation(documentation_id):
    documentation_query = """
    SELECT
        d.documentation_id,
        d.title,
        d.camera_id,
        c.camera_name,
        d.variant_id,
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

    documentation = fetch_all(documentation_query)
    cameras = fetch_all(cameras_query)
    variants = fetch_all(variants_query)
    doc_to_edit = fetch_one(
        "SELECT * FROM documentation WHERE documentation_id = %s;",
        (documentation_id,)
    )

    return render_template(
        "documentation.html",
        documentation=documentation,
        cameras=cameras,
        variants=variants,
        doc_to_edit=doc_to_edit,
        mode=None
    )


@documentation_bp.route("/documentation/add", methods=["POST"])
def add_documentation():
    title = request.form["title"]
    camera_id = request.form["camera_id"]
    variant_id = request.form["variant_id"] or None
    document_type = request.form["document_type"] or None
    source = request.form["source"] or None
    publication_year = request.form["publication_year"] or None
    url = request.form["url"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO documentation
    (title, camera_id, variant_id, document_type, source, publication_year, url, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        title,
        camera_id,
        variant_id,
        document_type,
        source,
        publication_year,
        url,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("documentation_bp.documentation"))


@documentation_bp.route("/documentation/update/<int:documentation_id>", methods=["POST"])
def update_documentation(documentation_id):
    title = request.form["title"]
    camera_id = request.form["camera_id"]
    variant_id = request.form["variant_id"] or None
    document_type = request.form["document_type"] or None
    source = request.form["source"] or None
    publication_year = request.form["publication_year"] or None
    url = request.form["url"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE documentation
    SET title = %s,
        camera_id = %s,
        variant_id = %s,
        document_type = %s,
        source = %s,
        publication_year = %s,
        url = %s,
        notes = %s
    WHERE documentation_id = %s
    """

    values = (
        title,
        camera_id,
        variant_id,
        document_type,
        source,
        publication_year,
        url,
        notes,
        documentation_id
    )

    execute_query(update_query, values)
    return redirect(url_for("documentation_bp.documentation"))


@documentation_bp.route("/documentation/delete/<int:documentation_id>", methods=["POST"])
def delete_documentation(documentation_id):
    execute_query("DELETE FROM documentation WHERE documentation_id = %s;", (documentation_id,))
    return redirect(url_for("documentation_bp.documentation"))