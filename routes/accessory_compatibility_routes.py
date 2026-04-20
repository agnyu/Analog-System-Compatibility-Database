from flask import Blueprint, render_template, request, redirect, url_for
from db import fetch_all, fetch_one, execute_query

accessory_compatibility_bp = Blueprint("accessory_compatibility_bp", __name__)


@accessory_compatibility_bp.route("/accessory-compatibility")
def accessory_compatibility():
    search = request.args.get("search", type=str)
    accessory_id = request.args.get("accessory_id", type=int)
    variant_id = request.args.get("variant_id", type=int)
    compatibility_type = request.args.get("compatibility_type", type=str)
    selected_accessory_compat_id = request.args.get("selected_accessory_compat_id", type=int)

    mode = request.args.get("mode")

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
    WHERE 1=1
    """

    values = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        compat_query += """
        AND (
            a.accessory_name LIKE %s
            OR cv.variant_name LIKE %s
            OR COALESCE(ac.compatibility_type, '') LIKE %s
            OR COALESCE(ac.notes, '') LIKE %s
        )
        """
        values.extend([search_term, search_term, search_term, search_term])

    if accessory_id:
        compat_query += " AND ac.accessory_id = %s"
        values.append(accessory_id)

    if variant_id:
        compat_query += " AND ac.variant_id = %s"
        values.append(variant_id)

    if compatibility_type:
        compat_query += " AND ac.compatibility_type = %s"
        values.append(compatibility_type)

    if selected_accessory_compat_id:
        compat_query += " AND ac.accessory_compat_id = %s"
        values.append(selected_accessory_compat_id)

    compat_query += " ORDER BY a.accessory_name, cv.variant_name;"

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

    compatibility_types_query = """
    SELECT DISTINCT compatibility_type
    FROM accessory_compatibility
    WHERE compatibility_type IS NOT NULL
      AND TRIM(compatibility_type) <> ''
    ORDER BY compatibility_type;
    """

    compatibilities = fetch_all(compat_query, tuple(values))
    accessories = fetch_all(accessories_query)
    variants = fetch_all(variants_query)
    compatibility_types = fetch_all(compatibility_types_query)

    selected_compatibility = None
    linked_accessory = None
    linked_variant = None

    if selected_accessory_compat_id:
        selected_compatibility = fetch_one("""
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
            WHERE ac.accessory_compat_id = %s;
        """, (selected_accessory_compat_id,))

        if selected_compatibility:
            linked_accessory = fetch_one("""
                SELECT
                    a.accessory_id,
                    a.accessory_name,
                    m.manufacturer_name,
                    at.type_name,
                    mo.mount_name,
                    ff.format_name,
                    a.release_year,
                    a.description,
                    a.compatibility_notes
                FROM accessories a
                JOIN manufacturers m ON a.manufacturer_id = m.manufacturer_id
                JOIN accessory_types at ON a.accessory_type_id = at.accessory_type_id
                LEFT JOIN mounts mo ON a.mount_id = mo.mount_id
                LEFT JOIN film_formats ff ON a.format_id = ff.format_id
                WHERE a.accessory_id = %s;
            """, (selected_compatibility["accessory_id"],))

            linked_variant = fetch_one("""
                SELECT
                    cv.variant_id,
                    cv.variant_name,
                    cv.release_year,
                    cv.frame_format,
                    cv.production_end_year,
                    c.camera_id,
                    c.camera_name
                FROM camera_variants cv
                JOIN cameras c ON cv.camera_id = c.camera_id
                WHERE cv.variant_id = %s;
            """, (selected_compatibility["variant_id"],))

    browse_params = {
        "search": search,
        "accessory_id": accessory_id,
        "variant_id": variant_id,
        "compatibility_type": compatibility_type
    }

    return render_template(
        "accessory_compatibility.html",
        compatibilities=compatibilities,
        accessories=accessories,
        variants=variants,
        compatibility_types=compatibility_types,
        compat_to_edit=None,
        mode=mode,
        selected_compatibility=selected_compatibility,
        linked_accessory=linked_accessory,
        linked_variant=linked_variant,
        selected_search=search,
        selected_accessory_id=accessory_id,
        selected_variant_id=variant_id,
        selected_compatibility_type=compatibility_type,
        browse_params=browse_params
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

    compatibility_types_query = """
    SELECT DISTINCT compatibility_type
    FROM accessory_compatibility
    WHERE compatibility_type IS NOT NULL
      AND TRIM(compatibility_type) <> ''
    ORDER BY compatibility_type;
    """

    compatibilities = fetch_all(compat_query)
    accessories = fetch_all(accessories_query)
    variants = fetch_all(variants_query)
    compatibility_types = fetch_all(compatibility_types_query)
    compat_to_edit = fetch_one(
        "SELECT * FROM accessory_compatibility WHERE accessory_compat_id = %s;",
        (accessory_compat_id,)
    )

    return render_template(
        "accessory_compatibility.html",
        compatibilities=compatibilities,
        accessories=accessories,
        variants=variants,
        compatibility_types=compatibility_types,
        compat_to_edit=compat_to_edit,
        mode=None,
        selected_compatibility=None,
        linked_accessory=None,
        linked_variant=None,
        selected_search=None,
        selected_accessory_id=None,
        selected_variant_id=None,
        selected_compatibility_type=None,
        browse_params={}
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