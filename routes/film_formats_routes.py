from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

film_formats_bp = Blueprint("film_formats_bp", __name__)

@film_formats_bp.route("/film-formats")
def film_formats():
    formats_query = """
    SELECT
        format_id,
        format_name,
        format_type,
        notes
    FROM film_formats
    ORDER BY format_name;
    """

    formats = fetch_all(formats_query)
    mode = request.args.get("mode")

    return render_template(
        "film_formats.html",
        formats=formats,
        format_to_edit=None,
        mode=mode
    )


@film_formats_bp.route("/film-formats/edit/<int:format_id>")
def edit_film_format(format_id):
    formats_query = """
    SELECT
        format_id,
        format_name,
        format_type,
        notes
    FROM film_formats
    ORDER BY format_name;
    """

    formats = fetch_all(formats_query)
    format_to_edit = fetch_one(
        "SELECT * FROM film_formats WHERE format_id = %s;",
        (format_id,)
    )

    return render_template(
        "film_formats.html",
        formats=formats,
        format_to_edit=format_to_edit,
        mode=None
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