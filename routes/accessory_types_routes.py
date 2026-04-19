from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

accessory_types_bp = Blueprint("accessory_types_bp", __name__)

@accessory_types_bp.route("/accessory-types")
def accessory_types():
    accessory_types_query = """
    SELECT
        accessory_type_id,
        type_name
    FROM accessory_types
    ORDER BY type_name;
    """

    accessory_types = fetch_all(accessory_types_query)
    mode = request.args.get("mode")

    return render_template(
        "accessory_types.html",
        accessory_types=accessory_types,
        accessory_type_to_edit=None,
        mode=mode
    )


@accessory_types_bp.route("/accessory-types/edit/<int:accessory_type_id>")
def edit_accessory_type(accessory_type_id):
    accessory_types_query = """
    SELECT
        accessory_type_id,
        type_name
    FROM accessory_types
    ORDER BY type_name;
    """

    accessory_types = fetch_all(accessory_types_query)
    accessory_type_to_edit = fetch_one(
        "SELECT * FROM accessory_types WHERE accessory_type_id = %s;",
        (accessory_type_id,)
    )

    return render_template(
        "accessory_types.html",
        accessory_types=accessory_types,
        accessory_type_to_edit=accessory_type_to_edit,
        mode=None
    )


@accessory_types_bp.route("/accessory-types/add", methods=["POST"])
def add_accessory_type():
    type_name = request.form["type_name"]

    insert_query = """
    INSERT INTO accessory_types
    (type_name)
    VALUES (%s)
    """

    execute_query(insert_query, (type_name,))
    return redirect(url_for("accessory_types_bp.accessory_types"))


@accessory_types_bp.route("/accessory-types/update/<int:accessory_type_id>", methods=["POST"])
def update_accessory_type(accessory_type_id):
    type_name = request.form["type_name"]

    update_query = """
    UPDATE accessory_types
    SET type_name = %s
    WHERE accessory_type_id = %s
    """

    execute_query(update_query, (type_name, accessory_type_id))
    return redirect(url_for("accessory_types_bp.accessory_types"))


@accessory_types_bp.route("/accessory-types/delete/<int:accessory_type_id>", methods=["POST"])
def delete_accessory_type(accessory_type_id):
    execute_query(
        "DELETE FROM accessory_types WHERE accessory_type_id = %s;",
        (accessory_type_id,)
    )
    return redirect(url_for("accessory_types_bp.accessory_types"))