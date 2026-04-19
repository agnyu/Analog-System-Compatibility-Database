from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

camera_bp = Blueprint("camera_bp", __name__)


@camera_bp.route("/cameras")
def cameras():
    search = request.args.get("search", type=str)
    manufacturer_id = request.args.get("manufacturer_id", type=int)
    mount_id = request.args.get("mount_id", type=int)
    camera_type = request.args.get("camera_type", type=str)
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)

    mode = request.args.get("mode")
    selected_camera_id = request.args.get("selected_camera_id", type=int)

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

    camera_types_query = """
    SELECT DISTINCT camera_type
    FROM cameras
    WHERE camera_type IS NOT NULL
      AND TRIM(camera_type) <> ''
    ORDER BY camera_type;
    """

    query = """
    SELECT
        c.camera_id,
        c.camera_name,
        c.manufacturer_id,
        m.manufacturer_name,
        c.mount_id,
        mo.mount_name,
        c.camera_type,
        c.release_year,
        c.notes
    FROM cameras c
    JOIN manufacturers m ON c.manufacturer_id = m.manufacturer_id
    JOIN mounts mo ON c.mount_id = mo.mount_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query += """
        AND (
            c.camera_name LIKE %s
            OR m.manufacturer_name LIKE %s
            OR mo.mount_name LIKE %s
            OR COALESCE(c.camera_type, '') LIKE %s
            OR COALESCE(c.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term, search_term, search_term])

    if manufacturer_id:
        query += " AND c.manufacturer_id = %s"
        values.append(manufacturer_id)

    if mount_id:
        query += " AND c.mount_id = %s"
        values.append(mount_id)

    if camera_type:
        query += " AND c.camera_type = %s"
        values.append(camera_type)

    if year_min:
        query += " AND c.release_year >= %s"
        values.append(year_min)

    if year_max:
        query += " AND c.release_year <= %s"
        values.append(year_max)

    if selected_camera_id:
        query += " AND c.camera_id = %s"
        values.append(selected_camera_id)

    query += " ORDER BY c.camera_name;"

    cameras = fetch_all(query, tuple(values))
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)
    camera_types = fetch_all(camera_types_query)

    selected_camera = None
    variants = []
    compatible_lenses = []
    compatible_accessories = []
    documentation = []

    if selected_camera_id:
        selected_camera = fetch_one("""
            SELECT
                c.camera_id,
                c.camera_name,
                c.manufacturer_id,
                m.manufacturer_name,
                c.mount_id,
                mo.mount_name,
                c.camera_type,
                c.release_year,
                c.notes
            FROM cameras c
            JOIN manufacturers m ON c.manufacturer_id = m.manufacturer_id
            JOIN mounts mo ON c.mount_id = mo.mount_id
            WHERE c.camera_id = %s;
        """, (selected_camera_id,))

        if selected_camera:
            variants = fetch_all("""
                SELECT
                    cv.variant_id,
                    cv.variant_name
                FROM camera_variants cv
                WHERE cv.camera_id = %s
                ORDER BY cv.variant_name;
            """, (selected_camera_id,))

            compatible_lenses = fetch_all("""
                SELECT
                    l.lens_id,
                    l.lens_name
                FROM lenses l
                WHERE l.mount_id = %s
                ORDER BY l.lens_name;
            """, (selected_camera["mount_id"],))

            compatible_accessories = fetch_all("""
                SELECT
                    a.accessory_id,
                    a.accessory_name
                FROM accessories a
                WHERE a.mount_id = %s
                ORDER BY a.accessory_name;
            """, (selected_camera["mount_id"],))

            documentation = fetch_all("""
                SELECT
                    d.documentation_id,
                    d.title
                FROM documentation d
                WHERE d.camera_id = %s
                ORDER BY d.title;
            """, (selected_camera_id,))

    browse_params = {
        "search": search,
        "manufacturer_id": manufacturer_id,
        "mount_id": mount_id,
        "camera_type": camera_type,
        "year_min": year_min,
        "year_max": year_max
    }

    return render_template(
        "cameras.html",
        cameras=cameras,
        manufacturers=manufacturers,
        mounts=mounts,
        camera_types=camera_types,
        camera_to_edit=None,
        mode=mode,
        selected_camera=selected_camera,
        variants=variants,
        compatible_lenses=compatible_lenses,
        compatible_accessories=compatible_accessories,
        documentation=documentation,
        selected_search=search,
        selected_manufacturer_id=manufacturer_id,
        selected_mount_id=mount_id,
        selected_camera_type=camera_type,
        selected_year_min=year_min,
        selected_year_max=year_max,
        browse_params=browse_params
    )


@camera_bp.route("/cameras/edit/<int:camera_id>")
def edit_camera(camera_id):
    camera_query = """
    SELECT
        c.camera_id,
        c.camera_name,
        c.manufacturer_id,
        m.manufacturer_name,
        c.mount_id,
        mo.mount_name,
        c.camera_type,
        c.release_year,
        c.notes
    FROM cameras c
    JOIN manufacturers m ON c.manufacturer_id = m.manufacturer_id
    JOIN mounts mo ON c.mount_id = mo.mount_id
    ORDER BY c.camera_name;
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

    camera_types_query = """
    SELECT DISTINCT camera_type
    FROM cameras
    WHERE camera_type IS NOT NULL
      AND TRIM(camera_type) <> ''
    ORDER BY camera_type;
    """

    cameras = fetch_all(camera_query)
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)
    camera_types = fetch_all(camera_types_query)

    camera_to_edit = fetch_one(
        "SELECT * FROM cameras WHERE camera_id = %s;",
        (camera_id,)
    )

    return render_template(
        "cameras.html",
        cameras=cameras,
        manufacturers=manufacturers,
        mounts=mounts,
        camera_types=camera_types,
        camera_to_edit=camera_to_edit,
        mode=None,
        selected_camera=None,
        variants=[],
        compatible_lenses=[],
        compatible_accessories=[],
        documentation=[],
        selected_search=None,
        selected_manufacturer_id=None,
        selected_mount_id=None,
        selected_camera_type=None,
        selected_year_min=None,
        selected_year_max=None,
        browse_params={}
    )


@camera_bp.route("/cameras/add", methods=["POST"])
def add_camera():
    camera_name = request.form["camera_name"]
    manufacturer_id = request.form["manufacturer_id"]
    mount_id = request.form["mount_id"]
    camera_type = request.form["camera_type"] or None
    release_year = request.form["release_year"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO cameras
    (camera_name, manufacturer_id, mount_id, camera_type, release_year, notes)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        camera_name,
        manufacturer_id,
        mount_id,
        camera_type,
        release_year,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("camera_bp.cameras"))


@camera_bp.route("/cameras/update/<int:camera_id>", methods=["POST"])
def update_camera(camera_id):
    camera_name = request.form["camera_name"]
    manufacturer_id = request.form["manufacturer_id"]
    mount_id = request.form["mount_id"]
    camera_type = request.form["camera_type"] or None
    release_year = request.form["release_year"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE cameras
    SET camera_name = %s,
        manufacturer_id = %s,
        mount_id = %s,
        camera_type = %s,
        release_year = %s,
        notes = %s
    WHERE camera_id = %s
    """

    values = (
        camera_name,
        manufacturer_id,
        mount_id,
        camera_type,
        release_year,
        notes,
        camera_id
    )

    execute_query(update_query, values)
    return redirect(url_for("camera_bp.cameras"))


@camera_bp.route("/cameras/delete/<int:camera_id>", methods=["POST"])
def delete_camera(camera_id):
    execute_query("DELETE FROM cameras WHERE camera_id = %s;", (camera_id,))
    return redirect(url_for("camera_bp.cameras"))