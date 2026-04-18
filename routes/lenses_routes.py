from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

lenses_bp = Blueprint("lenses_bp", __name__)

@lenses_bp.route("/lenses")
def lenses():
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

    lenses = fetch_all(lens_query)
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)

    mode = request.args.get("mode")

    return render_template(
        "lenses.html",
        lenses=lenses,
        manufacturers=manufacturers,
        mounts=mounts,
        lens_to_edit=None,
        mode=mode
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

    lenses = fetch_all(lens_query)
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)
    lens_to_edit = fetch_one(
        "SELECT * FROM lenses WHERE lens_id = %s;",
        (lens_id,)
    )

    return render_template(
        "lenses.html",
        lenses=lenses,
        manufacturers=manufacturers,
        mounts=mounts,
        lens_to_edit=lens_to_edit,
        mode=None
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