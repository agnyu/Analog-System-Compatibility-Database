from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

camera_variants_bp = Blueprint("camera_variants_bp", __name__)


@camera_variants_bp.route("/camera-variants")
def camera_variants():
    search = request.args.get("search", type=str)
    camera_id = request.args.get("camera_id", type=int)
    frame_format = request.args.get("frame_format", type=str)
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    production_end_min = request.args.get("production_end_min", type=int)
    production_end_max = request.args.get("production_end_max", type=int)

    mode = request.args.get("mode")
    selected_variant_id = request.args.get("selected_variant_id", type=int)

    variants_query = """
    SELECT
        cv.variant_id,
        cv.variant_name,
        cv.camera_id,
        c.camera_name,
        cv.release_year,
        cv.frame_format,
        cv.production_end_year,
        cv.notes
    FROM camera_variants cv
    JOIN cameras c ON cv.camera_id = c.camera_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        variants_query += """
        AND (
            cv.variant_name LIKE %s
            OR c.camera_name LIKE %s
            OR COALESCE(cv.frame_format, '') LIKE %s
            OR COALESCE(cv.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term, search_term])

    if camera_id:
        variants_query += " AND cv.camera_id = %s"
        values.append(camera_id)

    if frame_format:
        variants_query += " AND cv.frame_format = %s"
        values.append(frame_format)

    if year_min:
        variants_query += " AND cv.release_year >= %s"
        values.append(year_min)

    if year_max:
        variants_query += " AND cv.release_year <= %s"
        values.append(year_max)

    if production_end_min:
        variants_query += " AND cv.production_end_year >= %s"
        values.append(production_end_min)

    if production_end_max:
        variants_query += " AND cv.production_end_year <= %s"
        values.append(production_end_max)

    if selected_variant_id:
        variants_query += " AND cv.variant_id = %s"
        values.append(selected_variant_id)

    variants_query += " ORDER BY cv.variant_name;"

    cameras_query = """
    SELECT camera_id, camera_name
    FROM cameras
    ORDER BY camera_name;
    """

    frame_formats_query = """
    SELECT DISTINCT frame_format
    FROM camera_variants
    WHERE frame_format IS NOT NULL
      AND TRIM(frame_format) <> ''
    ORDER BY frame_format;
    """

    variants = fetch_all(variants_query, tuple(values))
    cameras = fetch_all(cameras_query)
    frame_formats = fetch_all(frame_formats_query)

    selected_variant = None
    parent_camera = None
    related_documentation = []
    related_accessories = []

    if selected_variant_id:
        selected_variant = fetch_one("""
            SELECT
                cv.variant_id,
                cv.variant_name,
                cv.camera_id,
                c.camera_name,
                c.mount_id,
                cv.release_year,
                cv.frame_format,
                cv.production_end_year,
                cv.notes
            FROM camera_variants cv
            JOIN cameras c ON cv.camera_id = c.camera_id
            WHERE cv.variant_id = %s;
        """, (selected_variant_id,))

        if selected_variant:
            parent_camera = fetch_one("""
                SELECT
                    c.camera_id,
                    c.camera_name,
                    c.camera_type,
                    c.release_year,
                    c.notes
                FROM cameras c
                WHERE c.camera_id = %s;
            """, (selected_variant["camera_id"],))

            related_accessories = fetch_all("""
                SELECT
                    a.accessory_id,
                    a.accessory_name
                FROM accessories a
                WHERE a.mount_id = %s
                ORDER BY a.accessory_name;
            """, (selected_variant["mount_id"],))

            related_documentation = fetch_all("""
                SELECT
                    d.documentation_id,
                    d.title
                FROM documentation d
                WHERE d.camera_id = %s
                ORDER BY d.title;
            """, (selected_variant["camera_id"],))

    return render_template(
        "camera_variants.html",
        variants=variants,
        cameras=cameras,
        frame_formats=frame_formats,
        variant_to_edit=None,
        mode=mode,
        selected_variant=selected_variant,
        parent_camera=parent_camera,
        related_documentation=related_documentation,
        related_accessories=related_accessories,
        selected_search=search,
        selected_camera_id=camera_id,
        selected_frame_format=frame_format,
        selected_year_min=year_min,
        selected_year_max=year_max,
        selected_production_end_min=production_end_min,
        selected_production_end_max=production_end_max
    )


@camera_variants_bp.route("/camera-variants/edit/<int:variant_id>")
def edit_camera_variant(variant_id):
    variants_query = """
    SELECT
        cv.variant_id,
        cv.variant_name,
        cv.camera_id,
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

    frame_formats_query = """
    SELECT DISTINCT frame_format
    FROM camera_variants
    WHERE frame_format IS NOT NULL
      AND TRIM(frame_format) <> ''
    ORDER BY frame_format;
    """

    variants = fetch_all(variants_query)
    cameras = fetch_all(cameras_query)
    frame_formats = fetch_all(frame_formats_query)

    variant_to_edit = fetch_one(
        "SELECT * FROM camera_variants WHERE variant_id = %s;",
        (variant_id,)
    )

    return render_template(
        "camera_variants.html",
        variants=variants,
        cameras=cameras,
        frame_formats=frame_formats,
        variant_to_edit=variant_to_edit,
        mode=None,
        selected_variant=None,
        parent_camera=None,
        related_documentation=[],
        related_accessories=[],
        selected_search=None,
        selected_camera_id=None,
        selected_frame_format=None,
        selected_year_min=None,
        selected_year_max=None,
        selected_production_end_min=None,
        selected_production_end_max=None
    )


@camera_variants_bp.route("/camera-variants/add", methods=["POST"])
def add_camera_variant():
    variant_name = request.form["variant_name"]
    camera_id = request.form["camera_id"]
    release_year = request.form["release_year"] or None
    frame_format = request.form["frame_format"] or None
    production_end_year = request.form["production_end_year"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO camera_variants
    (variant_name, camera_id, release_year, frame_format, production_end_year, notes)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        variant_name,
        camera_id,
        release_year,
        frame_format,
        production_end_year,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("camera_variants_bp.camera_variants"))


@camera_variants_bp.route("/camera-variants/update/<int:variant_id>", methods=["POST"])
def update_camera_variant(variant_id):
    variant_name = request.form["variant_name"]
    camera_id = request.form["camera_id"]
    release_year = request.form["release_year"] or None
    frame_format = request.form["frame_format"] or None
    production_end_year = request.form["production_end_year"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE camera_variants
    SET variant_name = %s,
        camera_id = %s,
        release_year = %s,
        frame_format = %s,
        production_end_year = %s,
        notes = %s
    WHERE variant_id = %s
    """

    values = (
        variant_name,
        camera_id,
        release_year,
        frame_format,
        production_end_year,
        notes,
        variant_id
    )

    execute_query(update_query, values)
    return redirect(url_for("camera_variants_bp.camera_variants"))


@camera_variants_bp.route("/camera-variants/delete/<int:variant_id>", methods=["POST"])
def delete_camera_variant(variant_id):
    execute_query("DELETE FROM camera_variants WHERE variant_id = %s;", (variant_id,))
    return redirect(url_for("camera_variants_bp.camera_variants"))