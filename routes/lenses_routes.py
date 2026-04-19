from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

lenses_bp = Blueprint("lenses_bp", __name__)


@lenses_bp.route("/lenses")
def lenses():
    search = request.args.get("search", type=str)
    manufacturer_id = request.args.get("manufacturer_id", type=int)
    mount_id = request.args.get("mount_id", type=int)
    lens_type = request.args.get("lens_type", type=str)
    focal_min = request.args.get("focal_min", type=int)
    focal_max = request.args.get("focal_max", type=int)
    year = request.args.get("year", type=int)

    mode = request.args.get("mode")
    selected_lens_id = request.args.get("selected_lens_id", type=int)

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

    lens_types_query = """
    SELECT DISTINCT lens_type
    FROM lenses
    WHERE lens_type IS NOT NULL
      AND TRIM(lens_type) <> ''
    ORDER BY lens_type;
    """

    lens_query = """
    SELECT
        l.lens_id,
        l.lens_name,
        l.manufacturer_id,
        m.manufacturer_name,
        l.mount_id,
        mo.mount_name,
        l.focal_length,
        l.max_aperture,
        l.lens_type,
        l.release_year,
        l.notes
    FROM lenses l
    JOIN manufacturers m ON l.manufacturer_id = m.manufacturer_id
    JOIN mounts mo ON l.mount_id = mo.mount_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        lens_query += """
        AND (
            l.lens_name LIKE %s
            OR m.manufacturer_name LIKE %s
            OR mo.mount_name LIKE %s
            OR COALESCE(l.focal_length, '') LIKE %s
            OR COALESCE(l.max_aperture, '') LIKE %s
            OR COALESCE(l.lens_type, '') LIKE %s
            OR COALESCE(l.notes, '') LIKE %s
        )
        """
        values.extend([
            search_term, search_term, search_term,
            search_term, search_term, search_term, search_term
        ])

    if manufacturer_id:
        lens_query += " AND l.manufacturer_id = %s"
        values.append(manufacturer_id)

    if mount_id:
        lens_query += " AND l.mount_id = %s"
        values.append(mount_id)

    if lens_type:
        lens_query += " AND l.lens_type = %s"
        values.append(lens_type)

    if focal_min:
        lens_query += " AND CAST(l.focal_length AS UNSIGNED) >= %s"
        values.append(focal_min)

    if focal_max:
        lens_query += " AND CAST(l.focal_length AS UNSIGNED) <= %s"
        values.append(focal_max)

    if year:
        lens_query += " AND l.release_year = %s"
        values.append(year)

    if selected_lens_id:
        lens_query += " AND l.lens_id = %s"
        values.append(selected_lens_id)

    lens_query += " ORDER BY l.lens_name;"

    lenses = fetch_all(lens_query, tuple(values))
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)
    lens_types = fetch_all(lens_types_query)

    selected_lens = None
    compatible_cameras = []
    compatible_variants = []
    related_documentation = []

    if selected_lens_id:
        selected_lens = fetch_one("""
            SELECT
                l.lens_id,
                l.lens_name,
                l.manufacturer_id,
                m.manufacturer_name,
                l.mount_id,
                mo.mount_name,
                l.focal_length,
                l.max_aperture,
                l.lens_type,
                l.release_year,
                l.notes
            FROM lenses l
            JOIN manufacturers m ON l.manufacturer_id = m.manufacturer_id
            JOIN mounts mo ON l.mount_id = mo.mount_id
            WHERE l.lens_id = %s;
        """, (selected_lens_id,))

        if selected_lens:
            compatible_cameras = fetch_all("""
                SELECT
                    c.camera_id,
                    c.camera_name,
                    c.camera_type,
                    c.release_year
                FROM cameras c
                WHERE c.mount_id = %s
                ORDER BY c.camera_name;
            """, (selected_lens["mount_id"],))

            compatible_variants = fetch_all("""
                SELECT
                    cv.variant_id,
                    cv.variant_name,
                    cv.camera_id,
                    c.camera_name
                FROM camera_variants cv
                JOIN cameras c ON cv.camera_id = c.camera_id
                WHERE c.mount_id = %s
                ORDER BY cv.variant_name;
            """, (selected_lens["mount_id"],))

            related_documentation = fetch_all("""
                SELECT
                    d.documentation_id,
                    d.title,
                    d.document_type,
                    d.source,
                    d.publication_year,
                    d.url,
                    d.notes
                FROM documentation d
                WHERE d.lens_id = %s
                ORDER BY d.title;
            """, (selected_lens_id,))

    browse_params = {
        "search": search,
        "manufacturer_id": manufacturer_id,
        "mount_id": mount_id,
        "lens_type": lens_type,
        "focal_min": focal_min,
        "focal_max": focal_max,
        "year": year
    }

    return render_template(
        "lenses.html",
        lenses=lenses,
        manufacturers=manufacturers,
        mounts=mounts,
        lens_types=lens_types,
        lens_to_edit=None,
        mode=mode,
        selected_lens=selected_lens,
        compatible_cameras=compatible_cameras,
        compatible_variants=compatible_variants,
        related_documentation=related_documentation,
        selected_search=search,
        selected_manufacturer_id=manufacturer_id,
        selected_mount_id=mount_id,
        selected_lens_type=lens_type,
        selected_focal_min=focal_min,
        selected_focal_max=focal_max,
        selected_year=year,
        browse_params=browse_params
    )


@lenses_bp.route("/lenses/edit/<int:lens_id>")
def edit_lens(lens_id):
    lens_query = """
    SELECT
        l.lens_id,
        l.lens_name,
        l.manufacturer_id,
        m.manufacturer_name,
        l.mount_id,
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

    lens_types_query = """
    SELECT DISTINCT lens_type
    FROM lenses
    WHERE lens_type IS NOT NULL
      AND TRIM(lens_type) <> ''
    ORDER BY lens_type;
    """

    lenses = fetch_all(lens_query)
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)
    lens_types = fetch_all(lens_types_query)

    lens_to_edit = fetch_one(
        "SELECT * FROM lenses WHERE lens_id = %s;",
        (lens_id,)
    )

    return render_template(
        "lenses.html",
        lenses=lenses,
        manufacturers=manufacturers,
        mounts=mounts,
        lens_types=lens_types,
        lens_to_edit=lens_to_edit,
        mode=None,
        selected_lens=None,
        compatible_cameras=[],
        compatible_variants=[],
        related_documentation=[],
        selected_search=None,
        selected_manufacturer_id=None,
        selected_mount_id=None,
        selected_lens_type=None,
        selected_focal_min=None,
        selected_focal_max=None,
        selected_year=None,
        browse_params={}
    )


@lenses_bp.route("/lenses/add", methods=["POST"])
def add_lens():
    lens_name = request.form["lens_name"]
    manufacturer_id = request.form["manufacturer_id"]
    mount_id = request.form["mount_id"]
    focal_length = request.form["focal_length"] or None
    max_aperture = request.form["max_aperture"] or None
    lens_type = request.form["lens_type"] or None
    release_year = request.form["release_year"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO lenses
    (lens_name, manufacturer_id, mount_id, focal_length, max_aperture, lens_type, release_year, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        lens_name,
        manufacturer_id,
        mount_id,
        focal_length,
        max_aperture,
        lens_type,
        release_year,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("lenses_bp.lenses"))


@lenses_bp.route("/lenses/update/<int:lens_id>", methods=["POST"])
def update_lens(lens_id):
    lens_name = request.form["lens_name"]
    manufacturer_id = request.form["manufacturer_id"]
    mount_id = request.form["mount_id"]
    focal_length = request.form["focal_length"] or None
    max_aperture = request.form["max_aperture"] or None
    lens_type = request.form["lens_type"] or None
    release_year = request.form["release_year"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE lenses
    SET lens_name = %s,
        manufacturer_id = %s,
        mount_id = %s,
        focal_length = %s,
        max_aperture = %s,
        lens_type = %s,
        release_year = %s,
        notes = %s
    WHERE lens_id = %s
    """

    values = (
        lens_name,
        manufacturer_id,
        mount_id,
        focal_length,
        max_aperture,
        lens_type,
        release_year,
        notes,
        lens_id
    )

    execute_query(update_query, values)
    return redirect(url_for("lenses_bp.lenses"))


@lenses_bp.route("/lenses/delete/<int:lens_id>", methods=["POST"])
def delete_lens(lens_id):
    execute_query("DELETE FROM lenses WHERE lens_id = %s;", (lens_id,))
    return redirect(url_for("lenses_bp.lenses"))