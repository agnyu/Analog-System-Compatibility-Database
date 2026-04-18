from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

mounts_bp = Blueprint("mounts_bp", __name__)

@mounts_bp.route("/mounts")
def mounts():
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

    mounts = fetch_all(mounts_query)
    manufacturers = fetch_all(manufacturers_query)

    mode = request.args.get("mode")

    return render_template(
        "mounts.html",
        mounts=mounts,
        manufacturers=manufacturers,
        mount_to_edit=None,
        mode=mode
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

    mounts = fetch_all(mounts_query)
    manufacturers = fetch_all(manufacturers_query)
    mount_to_edit = fetch_one(
        "SELECT * FROM mounts WHERE mount_id = %s;",
        (mount_id,)
    )

    return render_template(
        "mounts.html",
        mounts=mounts,
        manufacturers=manufacturers,
        mount_to_edit=mount_to_edit,
        mode=None
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