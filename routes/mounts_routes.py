from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

mounts_bp = Blueprint("mounts_bp", __name__)


@mounts_bp.route("/mounts")
def mounts():
    search = request.args.get("search", type=str)
    manufacturer_id = request.args.get("manufacturer_id", type=int)
    mount_type = request.args.get("mount_type", type=str)
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    selected_mount_id = request.args.get("selected_mount_id", type=int)

    mode = request.args.get("mode")

    manufacturers_query = """
    SELECT manufacturer_id, manufacturer_name
    FROM manufacturers
    ORDER BY manufacturer_name;
    """

    mount_types_query = """
    SELECT DISTINCT mount_type
    FROM mounts
    WHERE mount_type IS NOT NULL
      AND TRIM(mount_type) <> ''
    ORDER BY mount_type;
    """

    mounts_query = """
    SELECT
        mo.mount_id,
        mo.mount_name,
        mo.manufacturer_id,
        m.manufacturer_name,
        mo.mount_type,
        mo.year_introduced,
        mo.notes
    FROM mounts mo
    JOIN manufacturers m ON mo.manufacturer_id = m.manufacturer_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        mounts_query += """
        AND (
            mo.mount_name LIKE %s
            OR m.manufacturer_name LIKE %s
            OR COALESCE(mo.mount_type, '') LIKE %s
            OR COALESCE(mo.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term, search_term])

    if manufacturer_id:
        mounts_query += " AND mo.manufacturer_id = %s"
        values.append(manufacturer_id)

    if mount_type:
        mounts_query += " AND mo.mount_type = %s"
        values.append(mount_type)

    if year_min:
        mounts_query += " AND mo.year_introduced >= %s"
        values.append(year_min)

    if year_max:
        mounts_query += " AND mo.year_introduced <= %s"
        values.append(year_max)

    if selected_mount_id:
        mounts_query += " AND mo.mount_id = %s"
        values.append(selected_mount_id)

    mounts_query += " ORDER BY mo.mount_name;"

    mounts = fetch_all(mounts_query, tuple(values))
    manufacturers = fetch_all(manufacturers_query)
    mount_types = fetch_all(mount_types_query)

    selected_mount = None
    linked_cameras = []
    linked_variants = []
    linked_lenses = []

    if selected_mount_id:
        selected_mount = fetch_one("""
            SELECT
                mo.mount_id,
                mo.mount_name,
                mo.manufacturer_id,
                m.manufacturer_name,
                mo.mount_type,
                mo.year_introduced,
                mo.notes
            FROM mounts mo
            JOIN manufacturers m ON mo.manufacturer_id = m.manufacturer_id
            WHERE mo.mount_id = %s;
        """, (selected_mount_id,))

        if selected_mount:
            linked_cameras = fetch_all("""
                SELECT
                    c.camera_id,
                    c.camera_name,
                    c.camera_type,
                    c.release_year
                FROM cameras c
                WHERE c.mount_id = %s
                ORDER BY c.camera_name;
            """, (selected_mount_id,))

            linked_variants = fetch_all("""
                SELECT
                    cv.variant_id,
                    cv.variant_name,
                    cv.camera_id,
                    c.camera_name
                FROM camera_variants cv
                JOIN cameras c ON cv.camera_id = c.camera_id
                WHERE c.mount_id = %s
                ORDER BY cv.variant_name;
            """, (selected_mount_id,))

            linked_lenses = fetch_all("""
                SELECT
                    l.lens_id,
                    l.lens_name,
                    l.lens_type,
                    l.release_year
                FROM lenses l
                WHERE l.mount_id = %s
                ORDER BY l.lens_name;
            """, (selected_mount_id,))

    browse_params = {
        "search": search,
        "manufacturer_id": manufacturer_id,
        "mount_type": mount_type,
        "year_min": year_min,
        "year_max": year_max
    }

    return render_template(
        "mounts.html",
        mounts=mounts,
        manufacturers=manufacturers,
        mount_types=mount_types,
        mount_to_edit=None,
        mode=mode,
        selected_mount=selected_mount,
        linked_cameras=linked_cameras,
        linked_variants=linked_variants,
        linked_lenses=linked_lenses,
        selected_search=search,
        selected_manufacturer_id=manufacturer_id,
        selected_mount_type=mount_type,
        selected_year_min=year_min,
        selected_year_max=year_max,
        browse_params=browse_params
    )


@mounts_bp.route("/mounts/edit/<int:mount_id>")
def edit_mount(mount_id):
    mounts_query = """
    SELECT
        mo.mount_id,
        mo.mount_name,
        mo.manufacturer_id,
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

    mount_types_query = """
    SELECT DISTINCT mount_type
    FROM mounts
    WHERE mount_type IS NOT NULL
      AND TRIM(mount_type) <> ''
    ORDER BY mount_type;
    """

    mounts = fetch_all(mounts_query)
    manufacturers = fetch_all(manufacturers_query)
    mount_types = fetch_all(mount_types_query)
    mount_to_edit = fetch_one(
        "SELECT * FROM mounts WHERE mount_id = %s;",
        (mount_id,)
    )

    return render_template(
        "mounts.html",
        mounts=mounts,
        manufacturers=manufacturers,
        mount_types=mount_types,
        mount_to_edit=mount_to_edit,
        mode=None,
        selected_mount=None,
        linked_cameras=[],
        linked_variants=[],
        linked_lenses=[],
        selected_search=None,
        selected_manufacturer_id=None,
        selected_mount_type=None,
        selected_year_min=None,
        selected_year_max=None,
        browse_params={}
    )


@mounts_bp.route("/mounts/add", methods=["POST"])
def add_mount():
    mount_name = request.form["mount_name"]
    manufacturer_id = request.form["manufacturer_id"]
    mount_type = request.form["mount_type"] or None
    year_introduced = request.form["year_introduced"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO mounts
    (mount_name, manufacturer_id, mount_type, year_introduced, notes)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        mount_name,
        manufacturer_id,
        mount_type,
        year_introduced,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("mounts_bp.mounts"))


@mounts_bp.route("/mounts/update/<int:mount_id>", methods=["POST"])
def update_mount(mount_id):
    mount_name = request.form["mount_name"]
    manufacturer_id = request.form["manufacturer_id"]
    mount_type = request.form["mount_type"] or None
    year_introduced = request.form["year_introduced"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE mounts
    SET mount_name = %s,
        manufacturer_id = %s,
        mount_type = %s,
        year_introduced = %s,
        notes = %s
    WHERE mount_id = %s
    """

    values = (
        mount_name,
        manufacturer_id,
        mount_type,
        year_introduced,
        notes,
        mount_id
    )

    execute_query(update_query, values)
    return redirect(url_for("mounts_bp.mounts"))


@mounts_bp.route("/mounts/delete/<int:mount_id>", methods=["POST"])
def delete_mount(mount_id):
    execute_query("DELETE FROM mounts WHERE mount_id = %s;", (mount_id,))
    return redirect(url_for("mounts_bp.mounts"))