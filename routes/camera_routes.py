from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

camera_bp = Blueprint("camera_bp", __name__)

@camera_bp.route("/cameras")
def cameras():
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

    cameras = fetch_all(camera_query)
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)

    mode = request.args.get("mode")

    return render_template(
        "cameras.html",
        cameras=cameras,
        manufacturers=manufacturers,
        mounts=mounts,
        camera_to_edit=None,
        mode=mode
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

    cameras = fetch_all(camera_query)
    manufacturers = fetch_all(manufacturers_query)
    mounts = fetch_all(mounts_query)
    camera_to_edit = fetch_one(
        "SELECT * FROM cameras WHERE camera_id = %s;",
        (camera_id,)
    )

    return render_template(
        "cameras.html",
        cameras=cameras,
        manufacturers=manufacturers,
        mounts=mounts,
        camera_to_edit=camera_to_edit,
        mode=None
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