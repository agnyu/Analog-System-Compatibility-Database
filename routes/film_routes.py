from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

film_bp = Blueprint("film_bp", __name__)


@film_bp.route("/film")
def film():
    search = request.args.get("search", type=str)
    manufacturer_id = request.args.get("manufacturer_id", type=int)
    format_id = request.args.get("format_id", type=int)
    color_type = request.args.get("color_type", type=str)
    iso_min = request.args.get("iso_min", type=int)
    iso_max = request.args.get("iso_max", type=int)
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    discontinued = request.args.get("discontinued", type=str)
    selected_film_id = request.args.get("selected_film_id", type=int)

    mode = request.args.get("mode")

    manufacturers_query = """
    SELECT manufacturer_id, manufacturer_name
    FROM manufacturers
    ORDER BY manufacturer_name;
    """

    formats_query = """
    SELECT format_id, format_name
    FROM film_formats
    ORDER BY format_name;
    """

    color_types_query = """
    SELECT DISTINCT color_type
    FROM film_stocks
    WHERE color_type IS NOT NULL
      AND TRIM(color_type) <> ''
    ORDER BY color_type;
    """

    films_query = """
    SELECT 
        fs.film_id,
        fs.film_name,
        fs.manufacturer_id,
        m.manufacturer_name,
        fs.iso,
        fs.format_id,
        ff.format_name,
        fs.color_type,
        fs.release_year,
        fs.discontinued,
        fs.notes
    FROM film_stocks fs
    JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
    JOIN film_formats ff ON fs.format_id = ff.format_id
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        films_query += """
        AND (
            fs.film_name LIKE %s
            OR m.manufacturer_name LIKE %s
            OR ff.format_name LIKE %s
            OR COALESCE(fs.color_type, '') LIKE %s
            OR COALESCE(fs.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term, search_term, search_term])

    if manufacturer_id:
        films_query += " AND fs.manufacturer_id = %s"
        values.append(manufacturer_id)

    if format_id:
        films_query += " AND fs.format_id = %s"
        values.append(format_id)

    if color_type:
        films_query += " AND fs.color_type = %s"
        values.append(color_type)

    if iso_min:
        films_query += " AND fs.iso >= %s"
        values.append(iso_min)

    if iso_max:
        films_query += " AND fs.iso <= %s"
        values.append(iso_max)

    if year_min:
        films_query += " AND fs.release_year >= %s"
        values.append(year_min)

    if year_max:
        films_query += " AND fs.release_year <= %s"
        values.append(year_max)

    if discontinued == "active":
        films_query += " AND fs.discontinued = 0"
    elif discontinued == "discontinued":
        films_query += " AND fs.discontinued = 1"

    if selected_film_id:
        films_query += " AND fs.film_id = %s"
        values.append(selected_film_id)

    films_query += " ORDER BY fs.film_name;"

    films = fetch_all(films_query, tuple(values))
    manufacturers = fetch_all(manufacturers_query)
    formats = fetch_all(formats_query)
    color_types = fetch_all(color_types_query)

    selected_film = None
    development_entries = []

    if selected_film_id:
        selected_film = fetch_one("""
            SELECT 
                fs.film_id,
                fs.film_name,
                fs.manufacturer_id,
                m.manufacturer_name,
                fs.iso,
                fs.format_id,
                ff.format_name,
                fs.color_type,
                fs.release_year,
                fs.discontinued,
                fs.notes
            FROM film_stocks fs
            JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
            JOIN film_formats ff ON fs.format_id = ff.format_id
            WHERE fs.film_id = %s;
        """, (selected_film_id,))

        if selected_film:
            development_entries = fetch_all("""
                SELECT
                    d.developer_name,
                    fdg.dilution,
                    fdg.temperature_celsius,
                    fdg.development_time_minutes,
                    fdg.notes
                FROM film_development_guide fdg
                JOIN film_developers d ON fdg.developer_id = d.developer_id
                WHERE fdg.film_id = %s
                ORDER BY d.developer_name, fdg.dilution;
            """, (selected_film_id,))

    browse_params = {
        "search": search,
        "manufacturer_id": manufacturer_id,
        "format_id": format_id,
        "color_type": color_type,
        "iso_min": iso_min,
        "iso_max": iso_max,
        "year_min": year_min,
        "year_max": year_max,
        "discontinued": discontinued
    }

    return render_template(
        "film.html",
        films=films,
        manufacturers=manufacturers,
        formats=formats,
        color_types=color_types,
        film_to_edit=None,
        mode=mode,
        selected_film=selected_film,
        development_entries=development_entries,
        selected_search=search,
        selected_manufacturer_id=manufacturer_id,
        selected_format_id=format_id,
        selected_color_type=color_type,
        selected_iso_min=iso_min,
        selected_iso_max=iso_max,
        selected_year_min=year_min,
        selected_year_max=year_max,
        selected_discontinued=discontinued,
        browse_params=browse_params
    )


@film_bp.route("/film/edit/<int:film_id>")
def edit_film(film_id):
    films_query = """
    SELECT 
        fs.film_id,
        fs.film_name,
        fs.manufacturer_id,
        m.manufacturer_name,
        fs.iso,
        fs.format_id,
        ff.format_name,
        fs.color_type,
        fs.release_year,
        fs.discontinued,
        fs.notes
    FROM film_stocks fs
    JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
    JOIN film_formats ff ON fs.format_id = ff.format_id
    ORDER BY fs.film_name;
    """

    manufacturers_query = """
    SELECT * FROM manufacturers
    ORDER BY manufacturer_name;
    """

    formats_query = """
    SELECT * FROM film_formats
    ORDER BY format_name;
    """

    color_types_query = """
    SELECT DISTINCT color_type
    FROM film_stocks
    WHERE color_type IS NOT NULL
      AND TRIM(color_type) <> ''
    ORDER BY color_type;
    """

    films = fetch_all(films_query)
    manufacturers = fetch_all(manufacturers_query)
    formats = fetch_all(formats_query)
    color_types = fetch_all(color_types_query)

    film_to_edit = fetch_one(
        "SELECT * FROM film_stocks WHERE film_id = %s;",
        (film_id,)
    )

    return render_template(
        "film.html",
        films=films,
        manufacturers=manufacturers,
        formats=formats,
        color_types=color_types,
        film_to_edit=film_to_edit,
        mode=None,
        selected_film=None,
        development_entries=[],
        selected_search=None,
        selected_manufacturer_id=None,
        selected_format_id=None,
        selected_color_type=None,
        selected_iso_min=None,
        selected_iso_max=None,
        selected_year_min=None,
        selected_year_max=None,
        selected_discontinued=None,
        browse_params={}
    )


@film_bp.route("/film/add", methods=["POST"])
def add_film():
    film_name = request.form["film_name"]
    manufacturer_id = request.form["manufacturer_id"]
    iso = request.form["iso"] or None
    format_id = request.form["format_id"]
    color_type = request.form["color_type"] or None
    release_year = request.form["release_year"] or None
    discontinued = 1 if request.form.get("discontinued") == "on" else 0
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO film_stocks
    (film_name, manufacturer_id, iso, format_id, color_type, release_year, discontinued, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        film_name, manufacturer_id, iso, format_id,
        color_type, release_year, discontinued, notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("film_bp.film"))


@film_bp.route("/film/update/<int:film_id>", methods=["POST"])
def update_film(film_id):
    film_name = request.form["film_name"]
    manufacturer_id = request.form["manufacturer_id"]
    iso = request.form["iso"] or None
    format_id = request.form["format_id"]
    color_type = request.form["color_type"] or None
    release_year = request.form["release_year"] or None
    discontinued = 1 if request.form.get("discontinued") == "on" else 0
    notes = request.form["notes"] or None

    update_query = """
    UPDATE film_stocks
    SET film_name = %s,
        manufacturer_id = %s,
        iso = %s,
        format_id = %s,
        color_type = %s,
        release_year = %s,
        discontinued = %s,
        notes = %s
    WHERE film_id = %s
    """

    values = (
        film_name, manufacturer_id, iso, format_id,
        color_type, release_year, discontinued, notes, film_id
    )

    execute_query(update_query, values)
    return redirect(url_for("film_bp.film"))


@film_bp.route("/film/delete/<int:film_id>", methods=["POST"])
def delete_film(film_id):
    execute_query("DELETE FROM film_stocks WHERE film_id = %s;", (film_id,))
    return redirect(url_for("film_bp.film"))