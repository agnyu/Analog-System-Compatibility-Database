from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

accessories_bp = Blueprint("accessories_bp", __name__)

@accessories_bp.route("/accessories")
def accessories():
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

    mode = request.args.get("mode")

    return render_template(
        "accessories.html",
        accessories=accessories,
        manufacturers=manufacturers,
        accessory_types=accessory_types,
        mounts=mounts,
        formats=formats,
        accessory_to_edit=None,
        mode=mode
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
        mode=None
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