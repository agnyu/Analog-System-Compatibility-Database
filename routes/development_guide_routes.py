from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

development_guide_bp = Blueprint("development_guide_bp", __name__)

@development_guide_bp.route("/development-guide")
def development_guide():
    guides_query = """
    SELECT
        fdg.development_id,
        fdg.film_id,
        fs.film_name,
        fdg.developer_id,
        fd.developer_name,
        fdg.temperature_celsius,
        fdg.dilution,
        fdg.shot_iso,
        fdg.development_time_minutes,
        fdg.agitation_notes,
        fdg.notes
    FROM film_development_guide fdg
    JOIN film_stocks fs ON fdg.film_id = fs.film_id
    JOIN film_developers fd ON fdg.developer_id = fd.developer_id
    ORDER BY fs.film_name, fd.developer_name;
    """

    films_query = """
    SELECT film_id, film_name
    FROM film_stocks
    ORDER BY film_name;
    """

    developers_query = """
    SELECT developer_id, developer_name
    FROM film_developers
    ORDER BY developer_name;
    """

    guides = fetch_all(guides_query)
    films = fetch_all(films_query)
    developers = fetch_all(developers_query)

    mode = request.args.get("mode")

    return render_template(
        "development_guide.html",
        guides=guides,
        films=films,
        developers=developers,
        guide_to_edit=None,
        mode=mode
    )


@development_guide_bp.route("/development-guide/edit/<int:development_id>")
def edit_development_guide(development_id):
    guides_query = """
    SELECT
        fdg.development_id,
        fdg.film_id,
        fs.film_name,
        fdg.developer_id,
        fd.developer_name,
        fdg.temperature_celsius,
        fdg.dilution,
        fdg.shot_iso,
        fdg.development_time_minutes,
        fdg.agitation_notes,
        fdg.notes
    FROM film_development_guide fdg
    JOIN film_stocks fs ON fdg.film_id = fs.film_id
    JOIN film_developers fd ON fdg.developer_id = fd.developer_id
    ORDER BY fs.film_name, fd.developer_name;
    """

    films_query = """
    SELECT film_id, film_name
    FROM film_stocks
    ORDER BY film_name;
    """

    developers_query = """
    SELECT developer_id, developer_name
    FROM film_developers
    ORDER BY developer_name;
    """

    guides = fetch_all(guides_query)
    films = fetch_all(films_query)
    developers = fetch_all(developers_query)
    guide_to_edit = fetch_one(
        "SELECT * FROM film_development_guide WHERE development_id = %s;",
        (development_id,)
    )

    return render_template(
        "development_guide.html",
        guides=guides,
        films=films,
        developers=developers,
        guide_to_edit=guide_to_edit,
        mode=None
    )


@development_guide_bp.route("/development-guide/add", methods=["POST"])
def add_development_guide():
    film_id = request.form["film_id"]
    developer_id = request.form["developer_id"]
    temperature_celsius = request.form["temperature_celsius"] or None
    dilution = request.form["dilution"] or None
    shot_iso = request.form["shot_iso"] or None
    development_time_minutes = request.form["development_time_minutes"] or None
    agitation_notes = request.form["agitation_notes"] or None
    notes = request.form["notes"] or None

    insert_query = """
    INSERT INTO film_development_guide
    (film_id, developer_id, temperature_celsius, dilution, shot_iso, development_time_minutes, agitation_notes, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        film_id,
        developer_id,
        temperature_celsius,
        dilution,
        shot_iso,
        development_time_minutes,
        agitation_notes,
        notes
    )

    execute_query(insert_query, values)
    return redirect(url_for("development_guide_bp.development_guide"))


@development_guide_bp.route("/development-guide/update/<int:development_id>", methods=["POST"])
def update_development_guide(development_id):
    film_id = request.form["film_id"]
    developer_id = request.form["developer_id"]
    temperature_celsius = request.form["temperature_celsius"] or None
    dilution = request.form["dilution"] or None
    shot_iso = request.form["shot_iso"] or None
    development_time_minutes = request.form["development_time_minutes"] or None
    agitation_notes = request.form["agitation_notes"] or None
    notes = request.form["notes"] or None

    update_query = """
    UPDATE film_development_guide
    SET film_id = %s,
        developer_id = %s,
        temperature_celsius = %s,
        dilution = %s,
        shot_iso = %s,
        development_time_minutes = %s,
        agitation_notes = %s,
        notes = %s
    WHERE development_id = %s
    """

    values = (
        film_id,
        developer_id,
        temperature_celsius,
        dilution,
        shot_iso,
        development_time_minutes,
        agitation_notes,
        notes,
        development_id
    )

    execute_query(update_query, values)
    return redirect(url_for("development_guide_bp.development_guide"))


@development_guide_bp.route("/development-guide/delete/<int:development_id>", methods=["POST"])
def delete_development_guide(development_id):
    execute_query(
        "DELETE FROM film_development_guide WHERE development_id = %s;",
        (development_id,)
    )
    return redirect(url_for("development_guide_bp.development_guide"))