from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

accessory_types_bp = Blueprint("accessory_types_bp", __name__)


@accessory_types_bp.route("/accessory-types")
def accessory_types():
    search = request.args.get("search", type=str)
    has_accessories = request.args.get("has_accessories", type=str)
    selected_accessory_type_id = request.args.get("selected_accessory_type_id", type=int)

    mode = request.args.get("mode")

    accessory_types_query = """
    SELECT
        at.accessory_type_id,
        at.type_name,
        COUNT(a.accessory_id) AS accessory_count
    FROM accessory_types at
    LEFT JOIN accessories a ON at.accessory_type_id = a.accessory_type_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        accessory_types_query += """
        AND (
            at.type_name LIKE %s
        )
        """
        values.append(search_term)

    accessory_types_query += """
    GROUP BY at.accessory_type_id, at.type_name
    """

    if has_accessories == "yes":
        accessory_types_query += " HAVING COUNT(a.accessory_id) > 0"
    elif has_accessories == "no":
        accessory_types_query += " HAVING COUNT(a.accessory_id) = 0"

    if selected_accessory_type_id:
        if "HAVING" in accessory_types_query:
            accessory_types_query += " AND at.accessory_type_id = %s"
        else:
            accessory_types_query += " HAVING at.accessory_type_id = %s"
        values.append(selected_accessory_type_id)

    accessory_types_query += " ORDER BY at.type_name;"

    accessory_types = fetch_all(accessory_types_query, tuple(values))

    selected_accessory_type = None
    linked_accessories = []

    if selected_accessory_type_id:
        selected_accessory_type = fetch_one("""
            SELECT
                accessory_type_id,
                type_name
            FROM accessory_types
            WHERE accessory_type_id = %s;
        """, (selected_accessory_type_id,))

        if selected_accessory_type:
            linked_accessories = fetch_all("""
                SELECT
                    a.accessory_id,
                    a.accessory_name,
                    m.manufacturer_name,
                    mo.mount_name,
                    ff.format_name,
                    a.release_year
                FROM accessories a
                JOIN manufacturers m ON a.manufacturer_id = m.manufacturer_id
                LEFT JOIN mounts mo ON a.mount_id = mo.mount_id
                LEFT JOIN film_formats ff ON a.format_id = ff.format_id
                WHERE a.accessory_type_id = %s
                ORDER BY a.accessory_name;
            """, (selected_accessory_type_id,))

    browse_params = {
        "search": search,
        "has_accessories": has_accessories
    }

    return render_template(
        "accessory_types.html",
        accessory_types=accessory_types,
        accessory_type_to_edit=None,
        mode=mode,
        selected_accessory_type=selected_accessory_type,
        linked_accessories=linked_accessories,
        selected_search=search,
        selected_has_accessories=has_accessories,
        browse_params=browse_params
    )


@accessory_types_bp.route("/accessory-types/edit/<int:accessory_type_id>")
def edit_accessory_type(accessory_type_id):
    accessory_types_query = """
    SELECT
        at.accessory_type_id,
        at.type_name,
        COUNT(a.accessory_id) AS accessory_count
    FROM accessory_types at
    LEFT JOIN accessories a ON at.accessory_type_id = a.accessory_type_id
    GROUP BY at.accessory_type_id, at.type_name
    ORDER BY at.type_name;
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
        mode=None,
        selected_accessory_type=None,
        linked_accessories=[],
        selected_search=None,
        selected_has_accessories=None,
        browse_params={}
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