from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

accessory_compatibility_bp = Blueprint("accessory_compatibility_bp", __name__)

@accessory_compatibility_bp.route("/accessory-compatibility")
def accessory_compatibility():
    compat_query = """
    SELECT
        ac.accessory_compat_id,
        ac.accessory_id,
        a.accessory_name,
        ac.variant_id,
        cv.variant_name,
        ac.compatibility_type,
        ac.notes
    FROM accessory_compatibility ac
    JOIN accessories a ON ac.accessory_id = a.accessory_id
    JOIN camera_variants cv ON ac.variant_id = cv.variant_id
    ORDER BY a.accessory_name, cv.variant_name;
    """

    accessories_query = """
    SELECT accessory_id, accessory_name
    FROM accessories
    ORDER BY accessory_name;
    """

    variants_query = """
    SELECT variant_id, variant_name
    FROM camera_variants
    ORDER BY variant_name;
    """

    compatibilities = fetch_all(compat_query)
    accessories = fetch_all(accessories_query)
    variants = fetch_all(variants_query)

    mode = request.args.get("mode")

    return render_template(
        "accessory_compatibility.html",
        compatibilities=compatibilities,
        accessories=accessories,
        variants=variants,
        compat_to_edit=None,
        mode=mode
    )


@accessory_compatibility_bp.route("/accessory-compatibility/edit/<int:accessory_compat_id>")
def edit_accessory_compatibility(accessory_compat_id):
    compat_query = """
    SELECT
        ac.accessory_compat_id,
        ac.accessory_id,
        a.accessory_name,
        ac.variant_id,
        cv.variant_name,
        ac.compatibility_type,
        ac.notes
    FROM accessory_compatibility ac
    JOIN accessories a ON ac.accessory_id = a.accessory_id
    JOIN camera_variants cv ON ac.variant_id = cv.variant_id
    ORDER BY a.accessory_name, cv.variant_name;
    """

    accessories_query = """
    SELECT accessory_id, accessory_name
    FROM accessories
    ORDER BY accessory_name;
    """

    variants_query = """
    SELECT variant_id, variant_name
    FROM camera_variants
    ORDER BY variant_name;
    """

    compatibilities = fetch_all(compat_query)
    accessories = fetch_all(accessories_query)
    variants = fetch_all(variants_query)
    compat_to_edit = fetch_one(
        "SELECT * FROM accessory_compatibility WHERE accessory_compat_id = %s;",
        (accessory_compat_id,)
    )

    return render_template(
        "accessory_compatibility.html",
        compatibilities=compatibilities,
        accessories=accessories,
        variants=variants,
        compat_to_edit=compat_to_edit,
        mode=None
    )


@accessory_compatibility_bp.route("/accessory-compatibility/add", methods=["POST"])
def add_accessory_compatibility():
    accessory_id = request.form["accessory_id"]
    variant_id = request.form["variant_id"]
    compatibility_type = request.form["compatibility_type"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO accessory_compatibility
    (accessory_id, variant_id, compatibility_type, notes)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        accessory_id,
        variant_id,
        compatibility_type,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("accessory_compatibility_bp.accessory_compatibility"))


@accessory_compatibility_bp.route("/accessory-compatibility/update/<int:accessory_compat_id>", methods=["POST"])
def update_accessory_compatibility(accessory_compat_id):
    accessory_id = request.form["accessory_id"]
    variant_id = request.form["variant_id"]
    compatibility_type = request.form["compatibility_type"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE accessory_compatibility
    SET accessory_id = %s,
        variant_id = %s,
        compatibility_type = %s,
        notes = %s
    WHERE accessory_compat_id = %s
    """

    values = (
        accessory_id,
        variant_id,
        compatibility_type,
        notes,
        accessory_compat_id
    )

    execute_query(update_query, values)
    return redirect(url_for("accessory_compatibility_bp.accessory_compatibility"))


@accessory_compatibility_bp.route("/accessory-compatibility/delete/<int:accessory_compat_id>", methods=["POST"])
def delete_accessory_compatibility(accessory_compat_id):
    execute_query(
        "DELETE FROM accessory_compatibility WHERE accessory_compat_id = %s;",
        (accessory_compat_id,)
    )
    return redirect(url_for("accessory_compatibility_bp.accessory_compatibility"))