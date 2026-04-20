from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

accessories_bp = Blueprint("accessories_bp", __name__)


@accessories_bp.route("/accessories")
def accessories():
    search = request.args.get("search", type=str)
    manufacturer_id = request.args.get("manufacturer_id", type=int)
    accessory_type_id = request.args.get("accessory_type_id", type=int)
    mount_id = request.args.get("mount_id", type=int)
    format_id = request.args.get("format_id", type=int)
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    selected_accessory_id = request.args.get("selected_accessory_id", type=int)

    mode = request.args.get("mode")

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

    accessory_query = """
    SELECT
        a.accessory_id,
        a.accessory_name,
        a.manufacturer_id,
        m.manufacturer_name,
        a.accessory_type_id,
        at.type_name,
        a.mount_id,
        mo.mount_name,
        a.format_id,
        ff.format_name,
        a.release_year,
        a.description,
        a.compatibility_notes
    FROM accessories a
    JOIN manufacturers m ON a.manufacturer_id = m.manufacturer_id
    JOIN accessory_types at ON a.accessory_type_id = at.accessory_type_id
    LEFT JOIN mounts mo ON a.mount_id = mo.mount_id
    LEFT JOIN film_formats ff ON a.format_id = ff.format_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        accessory_query += """
        AND (
            a.accessory_name LIKE %s
            OR m.manufacturer_name LIKE %s
            OR at.type_name LIKE %s
            OR COALESCE(mo.mount_name, '') LIKE %s
            OR COALESCE(ff.format_name, '') LIKE %s
            OR COALESCE(a.description, '') LIKE %s
            OR COALESCE(a.compatibility_notes, '') LIKE %s
        )
        """
        values.extend([
            search_term, search_term, search_term,
            search_term, search_term, search_term, search_term
        ])

    if manufacturer_id:
        accessory_query += " AND a.manufacturer_id = %s"
        values.append(manufacturer_id)

    if accessory_type_id:
        accessory_query += " AND a.accessory_type_id = %s"
        values.append(accessory_type_id)

    if mount_id:
        accessory_query += " AND a.mount_id = %s"
        values.append(mount_id)

    if format_id:
        accessory_query += " AND a.format_id = %s"
        values.append(format_id)

    if year_min:
        accessory_query += " AND a.release_year >= %s"
        values.append(year_min)

    if year_max:
        accessory_query += " AND a.release_year <= %s"
        values.append(year_max)

    if selected_accessory_id:
        accessory_query += " AND a.accessory_id = %s"
        values.append(selected_accessory_id)

    accessory_query += " ORDER BY a.accessory_name;"

    accessories = fetch_all(accessory_query, tuple(values))
    manufacturers = fetch_all(manufacturers_query)
    accessory_types = fetch_all(accessory_types_query)
    mounts = fetch_all(mounts_query)
    formats = fetch_all(formats_query)

    selected_accessory = None
    linked_cameras = []
    linked_variants = []
    related_documentation = []

    if selected_accessory_id:
        selected_accessory = fetch_one("""
            SELECT
                a.accessory_id,
                a.accessory_name,
                a.manufacturer_id,
                m.manufacturer_name,
                a.accessory_type_id,
                at.type_name,
                a.mount_id,
                mo.mount_name,
                a.format_id,
                ff.format_name,
                a.release_year,
                a.description,
                a.compatibility_notes
            FROM accessories a
            JOIN manufacturers m ON a.manufacturer_id = m.manufacturer_id
            JOIN accessory_types at ON a.accessory_type_id = at.accessory_type_id
            LEFT JOIN mounts mo ON a.mount_id = mo.mount_id
            LEFT JOIN film_formats ff ON a.format_id = ff.format_id
            WHERE a.accessory_id = %s;
        """, (selected_accessory_id,))

        if selected_accessory:
            if selected_accessory["mount_id"]:
                linked_cameras = fetch_all("""
                    SELECT
                        c.camera_id,
                        c.camera_name,
                        c.camera_type,
                        c.release_year
                    FROM cameras c
                    WHERE c.mount_id = %s
                    ORDER BY c.camera_name;
                """, (selected_accessory["mount_id"],))

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
                """, (selected_accessory["mount_id"],))

            related_documentation = fetch_all("""
                SELECT
                    d.documentation_id,
                    d.title,
                    d.document_type,
                    d.source,
                    d.publication_year,
                    d.url
                FROM documentation d
                WHERE d.camera_id IN (
                    SELECT c.camera_id
                    FROM cameras c
                    WHERE (%s IS NOT NULL AND c.mount_id = %s)
                )
                ORDER BY d.title;
            """, (
                selected_accessory["mount_id"],
                selected_accessory["mount_id"]
            ))

    browse_params = {
        "search": search,
        "manufacturer_id": manufacturer_id,
        "accessory_type_id": accessory_type_id,
        "mount_id": mount_id,
        "format_id": format_id,
        "year_min": year_min,
        "year_max": year_max
    }

    return render_template(
        "accessories.html",
        accessories=accessories,
        manufacturers=manufacturers,
        accessory_types=accessory_types,
        mounts=mounts,
        formats=formats,
        accessory_to_edit=None,
        mode=mode,
        selected_accessory=selected_accessory,
        linked_cameras=linked_cameras,
        linked_variants=linked_variants,
        related_documentation=related_documentation,
        selected_search=search,
        selected_manufacturer_id=manufacturer_id,
        selected_accessory_type_id=accessory_type_id,
        selected_mount_id=mount_id,
        selected_format_id=format_id,
        selected_year_min=year_min,
        selected_year_max=year_max,
        browse_params=browse_params
    )


@accessories_bp.route("/accessories/edit/<int:accessory_id>")
def edit_accessory(accessory_id):
    accessory_query = """
    SELECT
        a.accessory_id,
        a.accessory_name,
        a.manufacturer_id,
        m.manufacturer_name,
        a.accessory_type_id,
        at.type_name,
        a.mount_id,
        mo.mount_name,
        a.format_id,
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

    accessories = fetch_all(accessory_query)
    manufacturers = fetch_all(manufacturers_query)
    accessory_types = fetch_all(accessory_types_query)
    mounts = fetch_all(mounts_query)
    formats = fetch_all(formats_query)
    accessory_to_edit = fetch_one(
        "SELECT * FROM accessories WHERE accessory_id = %s;",
        (accessory_id,)
    )

    return render_template(
        "accessories.html",
        accessories=accessories,
        manufacturers=manufacturers,
        accessory_types=accessory_types,
        mounts=mounts,
        formats=formats,
        accessory_to_edit=accessory_to_edit,
        mode=None,
        selected_accessory=None,
        linked_cameras=[],
        linked_variants=[],
        related_documentation=[],
        selected_search=None,
        selected_manufacturer_id=None,
        selected_accessory_type_id=None,
        selected_mount_id=None,
        selected_format_id=None,
        selected_year_min=None,
        selected_year_max=None,
        browse_params={}
    )


@accessories_bp.route("/accessories/add", methods=["POST"])
def add_accessory():
    accessory_name = request.form["accessory_name"]
    manufacturer_id = request.form["manufacturer_id"]
    accessory_type_id = request.form["accessory_type_id"]
    mount_id = request.form["mount_id"] or None
    format_id = request.form["format_id"] or None
    release_year = request.form["release_year"] or None
    description = request.form["description"] or None
    compatibility_notes = request.form["compatibility_notes"] or None

    insert_query = """
    INSERT INTO accessories
    (accessory_name, manufacturer_id, accessory_type_id, mount_id, format_id, release_year, description, compatibility_notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        accessory_name,
        manufacturer_id,
        accessory_type_id,
        mount_id,
        format_id,
        release_year,
        description,
        compatibility_notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("accessories_bp.accessories"))


@accessories_bp.route("/accessories/update/<int:accessory_id>", methods=["POST"])
def update_accessory(accessory_id):
    accessory_name = request.form["accessory_name"]
    manufacturer_id = request.form["manufacturer_id"]
    accessory_type_id = request.form["accessory_type_id"]
    mount_id = request.form["mount_id"] or None
    format_id = request.form["format_id"] or None
    release_year = request.form["release_year"] or None
    description = request.form["description"] or None
    compatibility_notes = request.form["compatibility_notes"] or None

    update_query = """
    UPDATE accessories
    SET accessory_name = %s,
        manufacturer_id = %s,
        accessory_type_id = %s,
        mount_id = %s,
        format_id = %s,
        release_year = %s,
        description = %s,
        compatibility_notes = %s
    WHERE accessory_id = %s
    """

    values = (
        accessory_name,
        manufacturer_id,
        accessory_type_id,
        mount_id,
        format_id,
        release_year,
        description,
        compatibility_notes,
        accessory_id
    )

    execute_query(update_query, values)
    return redirect(url_for("accessories_bp.accessories"))


@accessories_bp.route("/accessories/delete/<int:accessory_id>", methods=["POST"])
def delete_accessory(accessory_id):
    execute_query("DELETE FROM accessories WHERE accessory_id = %s;", (accessory_id,))
    return redirect(url_for("accessories_bp.accessories"))