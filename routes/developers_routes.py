from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

developers_bp = Blueprint("developers_bp", __name__)


@developers_bp.route("/developers")
def developers():
    search = request.args.get("search", type=str)
    manufacturer_id = request.args.get("manufacturer_id", type=int)
    developer_type = request.args.get("developer_type", type=str)
    selected_developer_id = request.args.get("selected_developer_id", type=int)

    mode = request.args.get("mode")

    manufacturers_query = """
    SELECT manufacturer_id, manufacturer_name
    FROM manufacturers
    ORDER BY manufacturer_name;
    """

    developer_types_query = """
    SELECT DISTINCT developer_type
    FROM film_developers
    WHERE developer_type IS NOT NULL
      AND TRIM(developer_type) <> ''
    ORDER BY developer_type;
    """

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
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        developers_query += """
        AND (
            d.developer_name LIKE %s
            OR m.manufacturer_name LIKE %s
            OR COALESCE(d.developer_type, '') LIKE %s
            OR COALESCE(d.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term, search_term])

    if manufacturer_id:
        developers_query += " AND d.manufacturer_id = %s"
        values.append(manufacturer_id)

    if developer_type:
        developers_query += " AND d.developer_type = %s"
        values.append(developer_type)

    if selected_developer_id:
        developers_query += " AND d.developer_id = %s"
        values.append(selected_developer_id)

    developers_query += " ORDER BY d.developer_name;"

    developers = fetch_all(developers_query, tuple(values))
    manufacturers = fetch_all(manufacturers_query)
    developer_types = fetch_all(developer_types_query)

    selected_developer = None
    guide_entries = []
    linked_films = []

    if selected_developer_id:
        selected_developer = fetch_one("""
            SELECT
                d.developer_id,
                d.developer_name,
                d.manufacturer_id,
                m.manufacturer_name,
                d.developer_type,
                d.notes
            FROM film_developers d
            JOIN manufacturers m ON d.manufacturer_id = m.manufacturer_id
            WHERE d.developer_id = %s;
        """, (selected_developer_id,))

        if selected_developer:
            linked_films = fetch_all("""
                SELECT DISTINCT
                    fs.film_id,
                    fs.film_name,
                    m.manufacturer_name,
                    ff.format_name,
                    fs.iso,
                    fs.color_type
                FROM film_development_guide fdg
                JOIN film_stocks fs ON fdg.film_id = fs.film_id
                JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
                JOIN film_formats ff ON fs.format_id = ff.format_id
                WHERE fdg.developer_id = %s
                ORDER BY fs.film_name;
            """, (selected_developer_id,))

            guide_entries = fetch_all("""
                SELECT DISTINCT
                    fs.film_name
                FROM film_development_guide fdg
                JOIN film_stocks fs ON fdg.film_id = fs.film_id
                WHERE fdg.developer_id = %s
                ORDER BY fs.film_name;
            """, (selected_developer_id,))

    browse_params = {
        "search": search,
        "manufacturer_id": manufacturer_id,
        "developer_type": developer_type
    }

    return render_template(
        "developers.html",
        developers=developers,
        manufacturers=manufacturers,
        developer_types=developer_types,
        developer_to_edit=None,
        mode=mode,
        selected_developer=selected_developer,
        guide_entries=guide_entries,
        linked_films=linked_films,
        selected_search=search,
        selected_manufacturer_id=manufacturer_id,
        selected_developer_type=developer_type,
        browse_params=browse_params
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
    ORDER BY d.developer_name;
    """

    manufacturers_query = """
    SELECT * FROM manufacturers
    ORDER BY manufacturer_name;
    """

    developer_types_query = """
    SELECT DISTINCT developer_type
    FROM film_developers
    WHERE developer_type IS NOT NULL
      AND TRIM(developer_type) <> ''
    ORDER BY developer_type;
    """

    developers = fetch_all(developers_query)
    manufacturers = fetch_all(manufacturers_query)
    developer_types = fetch_all(developer_types_query)

    developer_to_edit = fetch_one(
        "SELECT * FROM film_developers WHERE developer_id = %s;",
        (developer_id,)
    )

    return render_template(
        "developers.html",
        developers=developers,
        manufacturers=manufacturers,
        developer_types=developer_types,
        developer_to_edit=developer_to_edit,
        mode=None,
        selected_developer=None,
        guide_entries=[],
        linked_films=[],
        selected_search=None,
        selected_manufacturer_id=None,
        selected_developer_type=None,
        browse_params={}
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