from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

documentation_bp = Blueprint("documentation_bp", __name__)


@documentation_bp.route("/documentation")
def documentation():
    search = request.args.get("search", type=str)
    camera_id = request.args.get("camera_id", type=int)
    variant_id = request.args.get("variant_id", type=int)
    lens_id = request.args.get("lens_id", type=int)
    document_type = request.args.get("document_type", type=str)
    source = request.args.get("source", type=str)
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    selected_documentation_id = request.args.get("selected_documentation_id", type=int)

    mode = request.args.get("mode")

    documentation_query = """
    SELECT
        d.documentation_id,
        d.title,
        d.camera_id,
        c.camera_name,
        d.variant_id,
        cv.variant_name,
        d.lens_id,
        l.lens_name,
        d.document_type,
        d.source,
        d.publication_year,
        d.url,
        d.notes
    FROM documentation d
    LEFT JOIN cameras c ON d.camera_id = c.camera_id
    LEFT JOIN camera_variants cv ON d.variant_id = cv.variant_id
    LEFT JOIN lenses l ON d.lens_id = l.lens_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        documentation_query += """
        AND (
            d.title LIKE %s
            OR COALESCE(c.camera_name, '') LIKE %s
            OR COALESCE(cv.variant_name, '') LIKE %s
            OR COALESCE(l.lens_name, '') LIKE %s
            OR COALESCE(d.document_type, '') LIKE %s
            OR COALESCE(d.source, '') LIKE %s
            OR COALESCE(d.notes, '') LIKE %s
        )
        """
        values.extend([
            search_term, search_term, search_term,
            search_term, search_term, search_term, search_term
        ])

    if camera_id:
        documentation_query += " AND d.camera_id = %s"
        values.append(camera_id)

    if variant_id:
        documentation_query += " AND d.variant_id = %s"
        values.append(variant_id)

    if lens_id:
        documentation_query += " AND d.lens_id = %s"
        values.append(lens_id)

    if document_type:
        documentation_query += " AND d.document_type = %s"
        values.append(document_type)

    if source and source.strip():
        documentation_query += " AND COALESCE(d.source, '') LIKE %s"
        values.append(f"%{source.strip()}%")

    if year_min:
        documentation_query += " AND d.publication_year >= %s"
        values.append(year_min)

    if year_max:
        documentation_query += " AND d.publication_year <= %s"
        values.append(year_max)

    if selected_documentation_id:
        documentation_query += " AND d.documentation_id = %s"
        values.append(selected_documentation_id)

    documentation_query += " ORDER BY d.title;"

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

    lenses_query = """
    SELECT lens_id, lens_name
    FROM lenses
    ORDER BY lens_name;
    """

    document_types_query = """
    SELECT DISTINCT document_type
    FROM documentation
    WHERE document_type IS NOT NULL
      AND TRIM(document_type) <> ''
    ORDER BY document_type;
    """

    documentation = fetch_all(documentation_query, tuple(values))
    cameras = fetch_all(cameras_query)
    variants = fetch_all(variants_query)
    lenses = fetch_all(lenses_query)
    document_types = fetch_all(document_types_query)

    selected_document = None
    linked_camera = None
    linked_variant = None
    linked_lens = None

    if selected_documentation_id:
        selected_document = fetch_one("""
            SELECT
                d.documentation_id,
                d.title,
                d.camera_id,
                c.camera_name,
                d.variant_id,
                cv.variant_name,
                d.lens_id,
                l.lens_name,
                d.document_type,
                d.source,
                d.publication_year,
                d.url,
                d.notes
            FROM documentation d
            LEFT JOIN cameras c ON d.camera_id = c.camera_id
            LEFT JOIN camera_variants cv ON d.variant_id = cv.variant_id
            LEFT JOIN lenses l ON d.lens_id = l.lens_id
            WHERE d.documentation_id = %s;
        """, (selected_documentation_id,))

        if selected_document:
            if selected_document["camera_id"]:
                linked_camera = fetch_one("""
                    SELECT camera_id, camera_name, camera_type, release_year, notes
                    FROM cameras
                    WHERE camera_id = %s;
                """, (selected_document["camera_id"],))

            if selected_document["variant_id"]:
                linked_variant = fetch_one("""
                    SELECT cv.variant_id, cv.variant_name, cv.release_year, cv.frame_format, cv.production_end_year
                    FROM camera_variants cv
                    WHERE cv.variant_id = %s;
                """, (selected_document["variant_id"],))

            if selected_document["lens_id"]:
                linked_lens = fetch_one("""
                    SELECT l.lens_id, l.lens_name, l.focal_length, l.max_aperture, l.lens_type, l.release_year
                    FROM lenses l
                    WHERE l.lens_id = %s;
                """, (selected_document["lens_id"],))

    browse_params = {
        "search": search,
        "camera_id": camera_id,
        "variant_id": variant_id,
        "lens_id": lens_id,
        "document_type": document_type,
        "source": source,
        "year_min": year_min,
        "year_max": year_max
    }

    return render_template(
        "documentation.html",
        documentation=documentation,
        cameras=cameras,
        variants=variants,
        lenses=lenses,
        document_types=document_types,
        doc_to_edit=None,
        mode=mode,
        selected_document=selected_document,
        linked_camera=linked_camera,
        linked_variant=linked_variant,
        linked_lens=linked_lens,
        selected_search=search,
        selected_camera_id=camera_id,
        selected_variant_id=variant_id,
        selected_lens_id=lens_id,
        selected_document_type=document_type,
        selected_source=source,
        selected_year_min=year_min,
        selected_year_max=year_max,
        browse_params=browse_params
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
        d.lens_id,
        l.lens_name,
        d.document_type,
        d.source,
        d.publication_year,
        d.url,
        d.notes
    FROM documentation d
    LEFT JOIN cameras c ON d.camera_id = c.camera_id
    LEFT JOIN camera_variants cv ON d.variant_id = cv.variant_id
    LEFT JOIN lenses l ON d.lens_id = l.lens_id
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

    lenses_query = """
    SELECT lens_id, lens_name
    FROM lenses
    ORDER BY lens_name;
    """

    document_types_query = """
    SELECT DISTINCT document_type
    FROM documentation
    WHERE document_type IS NOT NULL
      AND TRIM(document_type) <> ''
    ORDER BY document_type;
    """

    documentation = fetch_all(documentation_query)
    cameras = fetch_all(cameras_query)
    variants = fetch_all(variants_query)
    lenses = fetch_all(lenses_query)
    document_types = fetch_all(document_types_query)

    doc_to_edit = fetch_one(
        "SELECT * FROM documentation WHERE documentation_id = %s;",
        (documentation_id,)
    )

    return render_template(
        "documentation.html",
        documentation=documentation,
        cameras=cameras,
        variants=variants,
        lenses=lenses,
        document_types=document_types,
        doc_to_edit=doc_to_edit,
        mode=None,
        selected_document=None,
        linked_camera=None,
        linked_variant=None,
        linked_lens=None,
        selected_search=None,
        selected_camera_id=None,
        selected_variant_id=None,
        selected_lens_id=None,
        selected_document_type=None,
        selected_source=None,
        selected_year_min=None,
        selected_year_max=None,
        browse_params={}
    )


@documentation_bp.route("/documentation/add", methods=["POST"])
def add_documentation():
    title = request.form["title"]
    camera_id = request.form["camera_id"] or None
    variant_id = request.form["variant_id"] or None
    lens_id = request.form["lens_id"] or None
    document_type = request.form["document_type"] or None
    source = request.form["source"] or None
    publication_year = request.form["publication_year"] or None
    url = request.form["url"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO documentation
    (title, camera_id, variant_id, lens_id, document_type, source, publication_year, url, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        title,
        camera_id,
        variant_id,
        lens_id,
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
    camera_id = request.form["camera_id"] or None
    variant_id = request.form["variant_id"] or None
    lens_id = request.form["lens_id"] or None
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
        lens_id = %s,
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
        lens_id,
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