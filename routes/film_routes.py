from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

film_bp = Blueprint("film_bp", __name__)

@film_bp.route("/film")
def film():
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
    ORDER BY fs.film_id;
    """

    films = fetch_all(films_query)
    manufacturers = fetch_all("SELECT * FROM manufacturers ORDER BY manufacturer_name;")
    formats = fetch_all("SELECT * FROM film_formats ORDER BY format_name;")

    mode = request.args.get("mode")

    return render_template(
        "film.html",
        films=films,
        manufacturers=manufacturers,
        formats=formats,
        film_to_edit=None,
        mode=mode
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
    ORDER BY fs.film_id;
    """

    films = fetch_all(films_query)
    manufacturers = fetch_all("SELECT * FROM manufacturers ORDER BY manufacturer_name;")
    formats = fetch_all("SELECT * FROM film_formats ORDER BY format_name;")
    film_to_edit = fetch_one(
        "SELECT * FROM film_stocks WHERE film_id = %s;",
        (film_id,)
    )

    return render_template(
        "film.html",
        films=films,
        manufacturers=manufacturers,
        formats=formats,
        film_to_edit=film_to_edit,
        mode=None
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



# @app.route("/film")
# def film():
#     films_query = """
#     SELECT 
#         fs.film_id,
#         fs.film_name,
#         fs.manufacturer_id,
#         m.manufacturer_name,
#         fs.iso,
#         fs.format_id,
#         ff.format_name,
#         fs.color_type,
#         fs.release_year,
#         fs.discontinued,
#         fs.notes
#     FROM film_stocks fs
#     JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
#     JOIN film_formats ff ON fs.format_id = ff.format_id
#     ORDER BY fs.film_id;
#     """

#     films = fetch_all(films_query)
#     manufacturers = fetch_all("SELECT * FROM manufacturers ORDER BY manufacturer_name;")
#     formats = fetch_all("SELECT * FROM film_formats ORDER BY format_name;")

#     mode = request.args.get("mode")

#     return render_template(
#         "film.html",
#         films=films,
#         manufacturers=manufacturers,
#         formats=formats,
#         film_to_edit=None,
#         mode=mode
#     )


# @app.route("/film/edit/<int:film_id>")
# def edit_film(film_id):
#     films_query = """
#     SELECT 
#         fs.film_id,
#         fs.film_name,
#         fs.manufacturer_id,
#         m.manufacturer_name,
#         fs.iso,
#         fs.format_id,
#         ff.format_name,
#         fs.color_type,
#         fs.release_year,
#         fs.discontinued,
#         fs.notes
#     FROM film_stocks fs
#     JOIN manufacturers m ON fs.manufacturer_id = m.manufacturer_id
#     JOIN film_formats ff ON fs.format_id = ff.format_id
#     ORDER BY fs.film_id;
#     """

#     films = fetch_all(films_query)
#     manufacturers = fetch_all("SELECT * FROM manufacturers ORDER BY manufacturer_name;")
#     formats = fetch_all("SELECT * FROM film_formats ORDER BY format_name;")
#     film_to_edit = fetch_one(
#         "SELECT * FROM film_stocks WHERE film_id = %s;",
#         (film_id,)
#     )

#     return render_template(
#         "film.html",
#         films=films,
#         manufacturers=manufacturers,
#         formats=formats,
#         film_to_edit=film_to_edit,
#         mode=None
#     )


# @app.route("/film/add", methods=["POST"])
# def add_film():
#     film_name = request.form["film_name"]
#     manufacturer_id = request.form["manufacturer_id"]
#     iso = request.form["iso"] or None
#     format_id = request.form["format_id"]
#     color_type = request.form["color_type"] or None
#     release_year = request.form["release_year"] or None
#     discontinued = 1 if request.form.get("discontinued") == "on" else 0
#     notes = request.form["notes"] or None

#     insert_query = """
#     INSERT INTO film_stocks
#     (film_name, manufacturer_id, iso, format_id, color_type, release_year, discontinued, notes)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#     """

#     values = (
#         film_name, manufacturer_id, iso, format_id,
#         color_type, release_year, discontinued, notes
#     )

#     execute_query(insert_query, values)
#     return redirect(url_for("film"))


# @app.route("/film/update/<int:film_id>", methods=["POST"])
# def update_film(film_id):
#     film_name = request.form["film_name"]
#     manufacturer_id = request.form["manufacturer_id"]
#     iso = request.form["iso"] or None
#     format_id = request.form["format_id"]
#     color_type = request.form["color_type"] or None
#     release_year = request.form["release_year"] or None
#     discontinued = 1 if request.form.get("discontinued") == "on" else 0
#     notes = request.form["notes"] or None

#     update_query = """
#     UPDATE film_stocks
#     SET film_name = %s,
#         manufacturer_id = %s,
#         iso = %s,
#         format_id = %s,
#         color_type = %s,
#         release_year = %s,
#         discontinued = %s,
#         notes = %s
#     WHERE film_id = %s
#     """

#     values = (
#         film_name, manufacturer_id, iso, format_id,
#         color_type, release_year, discontinued, notes, film_id
#     )

#     execute_query(update_query, values)
#     return redirect(url_for("film"))


# @app.route("/film/delete/<int:film_id>", methods=["POST"])
# def delete_film(film_id):
#     execute_query("DELETE FROM film_stocks WHERE film_id = %s;", (film_id,))
#     return redirect(url_for("film"))