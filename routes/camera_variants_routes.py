from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

camera_variants_bp = Blueprint("camera_variants_bp", __name__)

@camera_variants_bp.route("/camera-variants")
def camera_variants():
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

    variants = fetch_all(variants_query)
    cameras = fetch_all(cameras_query)

    mode = request.args.get("mode")

    return render_template(
        "camera_variants.html",
        variants=variants,
        cameras=cameras,
        variant_to_edit=None,
        mode=mode
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

    variants = fetch_all(variants_query)
    cameras = fetch_all(cameras_query)
    variant_to_edit = fetch_one(
        "SELECT * FROM camera_variants WHERE variant_id = %s;",
        (variant_id,)
    )

    return render_template(
        "camera_variants.html",
        variants=variants,
        cameras=cameras,
        variant_to_edit=variant_to_edit,
        mode=None
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