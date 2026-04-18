from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

developers_bp = Blueprint("developers_bp", __name__)

@developers_bp.route("/developers")
def developers():
    developers_query = """
    SELECT
        d.developer_id,
        d.developer_name,
        d.manufacturer_id,
        m.manufacturer_name,
        d.developer_type,
        d.notes
    FROM film_developers d
    JOIN manufacturers m ON d.manufacturer_id = m.manufacturer_id
    ORDER BY d.developer_id;
    """

    developers = fetch_all(developers_query)
    manufacturers = fetch_all("SELECT * FROM manufacturers ORDER BY manufacturer_name;")

    mode = request.args.get("mode")

    return render_template(
        "developers.html",
        developers=developers,
        manufacturers=manufacturers,
        developer_to_edit=None,
        mode=mode
    )


@developers_bp.route("/developers/edit/<int:developer_id>")
def edit_developer(developer_id):
    developers_query = """
    SELECT
        d.developer_id,
        d.developer_name,
        d.manufacturer_id,
        m.manufacturer_name,
        d.developer_type,
        d.notes
    FROM film_developers d
    JOIN manufacturers m ON d.manufacturer_id = m.manufacturer_id
    ORDER BY d.developer_id;
    """

    developers = fetch_all(developers_query)
    manufacturers = fetch_all("SELECT * FROM manufacturers ORDER BY manufacturer_name;")
    developer_to_edit = fetch_one(
        "SELECT * FROM film_developers WHERE developer_id = %s;",
        (developer_id,)
    )

    return render_template(
        "developers.html",
        developers=developers,
        manufacturers=manufacturers,
        developer_to_edit=developer_to_edit,
        mode=None
    )


@developers_bp.route("/developers/add", methods=["POST"])
def add_developer():
    developer_name = request.form["developer_name"]
    manufacturer_id = request.form["manufacturer_id"]
    developer_type = request.form["developer_type"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO film_developers
    (developer_name, manufacturer_id, developer_type, notes)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        developer_name,
        manufacturer_id,
        developer_type,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("developers_bp.developers"))


@developers_bp.route("/developers/update/<int:developer_id>", methods=["POST"])
def update_developer(developer_id):
    developer_name = request.form["developer_name"]
    manufacturer_id = request.form["manufacturer_id"]
    developer_type = request.form["developer_type"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE film_developers
    SET developer_name = %s,
        manufacturer_id = %s,
        developer_type = %s,
        notes = %s
    WHERE developer_id = %s
    """

    values = (
        developer_name,
        manufacturer_id,
        developer_type,
        notes,
        developer_id
    )

    execute_query(update_query, values)
    return redirect(url_for("developers_bp.developers"))


@developers_bp.route("/developers/delete/<int:developer_id>", methods=["POST"])
def delete_developer(developer_id):
    execute_query("DELETE FROM film_developers WHERE developer_id = %s;", (developer_id,))
    return redirect(url_for("developers_bp.developers"))