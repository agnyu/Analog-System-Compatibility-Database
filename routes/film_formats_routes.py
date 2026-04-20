from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

film_formats_bp = Blueprint("film_formats_bp", __name__)


@film_formats_bp.route("/film-formats")
def film_formats():
    search = request.args.get("search", type=str)
    format_type = request.args.get("format_type", type=str)
    usage_scope = request.args.get("usage_scope", type=str)
    selected_format_id = request.args.get("selected_format_id", type=int)

    mode = request.args.get("mode")

    format_types_query = """
    SELECT DISTINCT format_type
    FROM film_formats
    WHERE format_type IS NOT NULL
      AND TRIM(format_type) <> ''
    ORDER BY format_type;
    """

    formats_query = """
    SELECT
        ff.format_id,
        ff.format_name,
        ff.format_type,
        ff.notes,
        COUNT(DISTINCT fs.film_id) AS film_count,
        COUNT(DISTINCT a.accessory_id) AS accessory_count
    FROM film_formats ff
    LEFT JOIN film_stocks fs ON ff.format_id = fs.format_id
    LEFT JOIN accessories a ON ff.format_id = a.format_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        formats_query += """
        AND (
            ff.format_name LIKE %s
            OR COALESCE(ff.format_type, '') LIKE %s
            OR COALESCE(ff.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term])

    if format_type:
        formats_query += " AND ff.format_type = %s"
        values.append(format_type)

    formats_query += """
    GROUP BY ff.format_id, ff.format_name, ff.format_type, ff.notes
    """

    if usage_scope == "film_only":
        formats_query += " HAVING COUNT(DISTINCT fs.film_id) > 0 AND COUNT(DISTINCT a.accessory_id) = 0"
    elif usage_scope == "accessory_only":
        formats_query += " HAVING COUNT(DISTINCT fs.film_id) = 0 AND COUNT(DISTINCT a.accessory_id) > 0"
    elif usage_scope == "both":
        formats_query += " HAVING COUNT(DISTINCT fs.film_id) > 0 AND COUNT(DISTINCT a.accessory_id) > 0"
    elif usage_scope == "unused":
        formats_query += " HAVING COUNT(DISTINCT fs.film_id) = 0 AND COUNT(DISTINCT a.accessory_id) = 0"

    if selected_format_id:
        if "HAVING" in formats_query:
            formats_query += " AND ff.format_id = %s"
        else:
            formats_query += " HAVING ff.format_id = %s"
        values.append(selected_format_id)

    formats_query += " ORDER BY ff.format_name;"

    formats = fetch_all(formats_query, tuple(values))
    format_types = fetch_all(format_types_query)

    selected_format = None
    linked_films = []
    linked_accessories = []

    if selected_format_id:
        selected_format = fetch_one("""
            SELECT
                format_id,
                format_name,
                format_type,
                notes
            FROM film_formats
            WHERE format_id = %s;
        """, (selected_format_id,))

        if selected_format:
            linked_films = fetch_all("""
                SELECT
                    fs.film_id,
                    fs.film_name,
                    m.manufacturer_name,
                    fs.iso,
                    fs.color_type,
                    fs.discontinued
                FROM film_stocks fs
                JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
                WHERE fs.format_id = %s
                ORDER BY fs.film_name;
            """, (selected_format_id,))

            linked_accessories = fetch_all("""
                SELECT
                    a.accessory_id,
                    a.accessory_name,
                    m.manufacturer_name,
                    at.type_name,
                    a.release_year
                FROM accessories a
                JOIN manufacturers m ON a.manufacturer_id = m.manufacturer_id
                JOIN accessory_types at ON a.accessory_type_id = at.accessory_type_id
                WHERE a.format_id = %s
                ORDER BY a.accessory_name;
            """, (selected_format_id,))

    browse_params = {
        "search": search,
        "format_type": format_type,
        "usage_scope": usage_scope
    }

    return render_template(
        "film_formats.html",
        formats=formats,
        format_types=format_types,
        format_to_edit=None,
        mode=mode,
        selected_format=selected_format,
        linked_films=linked_films,
        linked_accessories=linked_accessories,
        selected_search=search,
        selected_format_type=format_type,
        selected_usage_scope=usage_scope,
        browse_params=browse_params
    )


@film_formats_bp.route("/film-formats/edit/<int:format_id>")
def edit_film_format(format_id):
    formats_query = """
    SELECT
        ff.format_id,
        ff.format_name,
        ff.format_type,
        ff.notes,
        COUNT(DISTINCT fs.film_id) AS film_count,
        COUNT(DISTINCT a.accessory_id) AS accessory_count
    FROM film_formats ff
    LEFT JOIN film_stocks fs ON ff.format_id = fs.format_id
    LEFT JOIN accessories a ON ff.format_id = a.format_id
    GROUP BY ff.format_id, ff.format_name, ff.format_type, ff.notes
    ORDER BY ff.format_name;
    """

    format_types_query = """
    SELECT DISTINCT format_type
    FROM film_formats
    WHERE format_type IS NOT NULL
      AND TRIM(format_type) <> ''
    ORDER BY format_type;
    """

    formats = fetch_all(formats_query)
    format_types = fetch_all(format_types_query)

    format_to_edit = fetch_one(
        "SELECT * FROM film_formats WHERE format_id = %s;",
        (format_id,)
    )

    return render_template(
        "film_formats.html",
        formats=formats,
        format_types=format_types,
        format_to_edit=format_to_edit,
        mode=None,
        selected_format=None,
        linked_films=[],
        linked_accessories=[],
        selected_search=None,
        selected_format_type=None,
        selected_usage_scope=None,
        browse_params={}
    )


@film_formats_bp.route("/film-formats/add", methods=["POST"])
def add_film_format():
    format_name = request.form["format_name"]
    format_type = request.form["format_type"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO film_formats
    (format_name, format_type, notes)
    VALUES (%s, %s, %s)
    """

    execute_query(insert_query, (format_name, format_type, notes))
    return redirect(url_for("film_formats_bp.film_formats"))


@film_formats_bp.route("/film-formats/update/<int:format_id>", methods=["POST"])
def update_film_format(format_id):
    format_name = request.form["format_name"]
    format_type = request.form["format_type"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE film_formats
    SET format_name = %s,
        format_type = %s,
        notes = %s
    WHERE format_id = %s
    """

    execute_query(update_query, (format_name, format_type, notes, format_id))
    return redirect(url_for("film_formats_bp.film_formats"))


@film_formats_bp.route("/film-formats/delete/<int:format_id>", methods=["POST"])
def delete_film_format(format_id):
    execute_query("DELETE FROM film_formats WHERE format_id = %s;", (format_id,))
    return redirect(url_for("film_formats_bp.film_formats"))