from flask import Blueprint, render_template, request
from db import fetch_all, fetch_one, execute_query

database_features_bp = Blueprint("database_features_bp", __name__)


def load_database_features_context(
    procedure_message=None,
    procedure_error=None,
    variant_workflow_results=None,
    function_result=None,
    function_error=None
):
    accessories = fetch_all("""
        SELECT accessory_id, accessory_name
        FROM accessories
        ORDER BY accessory_name;
    """)

    variants = fetch_all("""
        SELECT variant_id, variant_name
        FROM camera_variants
        ORDER BY variant_name;
    """)

    cameras = fetch_all("""
        SELECT camera_id, camera_name
        FROM cameras
        ORDER BY camera_name;
    """)

    lenses = fetch_all("""
        SELECT lens_id, lens_name
        FROM lenses
        ORDER BY lens_name;
    """)

    camera_audit_rows = fetch_all("""
        SELECT
            audit_id,
            camera_id,
            old_camera_name,
            new_camera_name,
            old_mount_id,
            new_mount_id,
            old_manufacturer_id,
            new_manufacturer_id,
            old_camera_type,
            new_camera_type,
            changed_at
        FROM camera_audit
        ORDER BY changed_at DESC
        LIMIT 15;
    """)

    film_development_guide_audit_rows = fetch_all("""
        SELECT
            audit_id,
            development_id,
            old_film_id,
            new_film_id,
            old_developer_id,
            new_developer_id,
            old_temperature_celsius,
            new_temperature_celsius,
            old_dilution,
            new_dilution,
            changed_at
        FROM film_development_guide_audit
        ORDER BY changed_at DESC
        LIMIT 15;
    """)

    return {
        "accessories": accessories,
        "variants": variants,
        "cameras": cameras,
        "lenses": lenses,
        "camera_audit_rows": camera_audit_rows,
        "film_development_guide_audit_rows": film_development_guide_audit_rows,
        "procedure_message": procedure_message,
        "procedure_error": procedure_error,
        "variant_workflow_results": variant_workflow_results or [],
        "function_result": function_result,
        "function_error": function_error
    }


@database_features_bp.route("/database-features")
def database_features():
    context = load_database_features_context()
    return render_template("database_features.html", **context)


@database_features_bp.route("/database-features/run-add-accessory-compatibility", methods=["POST"])
def run_add_accessory_compatibility():
    accessory_id = request.form.get("accessory_id", type=int)
    variant_id = request.form.get("variant_id", type=int)
    compatibility_type = request.form.get("compatibility_type", type=str)
    notes = request.form.get("notes", type=str)

    procedure_message = None
    procedure_error = None

    try:
        execute_query(
            "CALL sp_add_accessory_compatibility(%s, %s, %s, %s);",
            (
                accessory_id,
                variant_id,
                compatibility_type if compatibility_type else None,
                notes if notes else None
            )
        )
        procedure_message = "Accessory compatibility procedure executed successfully."
    except Exception as e:
        procedure_error = str(e)

    context = load_database_features_context(
        procedure_message=procedure_message,
        procedure_error=procedure_error
    )
    return render_template("database_features.html", **context)


@database_features_bp.route("/database-features/run-variant-film-workflow", methods=["POST"])
def run_variant_film_workflow():
    variant_id = request.form.get("variant_id", type=int)

    procedure_message = None
    procedure_error = None
    variant_workflow_results = []

    try:
        variant_workflow_results = fetch_all("""
            SELECT
                c.camera_name AS parent_camera,
                cv.variant_name,
                cv.frame_format,
                fs.film_name,
                fs.iso AS box_iso,
                fs.color_type,
                fd.developer_name,
                fdg.shot_iso,
                fdg.temperature_celsius,
                fdg.dilution,
                fdg.development_time_minutes
            FROM camera_variants cv
            JOIN cameras c
                ON cv.camera_id = c.camera_id
            JOIN film_formats ff
                ON ff.format_name = cv.frame_format
            JOIN film_stocks fs
                ON fs.format_id = ff.format_id
            LEFT JOIN film_development_guide fdg
                ON fs.film_id = fdg.film_id
            LEFT JOIN film_developers fd
                ON fdg.developer_id = fd.developer_id
            WHERE cv.variant_id = %s
            ORDER BY fs.film_name, fd.developer_name, fdg.shot_iso;
        """, (variant_id,))
        procedure_message = "Variant film workflow procedure executed successfully."
    except Exception as e:
        procedure_error = str(e)

    context = load_database_features_context(
        procedure_message=procedure_message,
        procedure_error=procedure_error,
        variant_workflow_results=variant_workflow_results
    )
    return render_template("database_features.html", **context)


@database_features_bp.route("/database-features/run-lens-camera-function", methods=["POST"])
def run_lens_camera_function():
    camera_id = request.form.get("camera_id", type=int)
    lens_id = request.form.get("lens_id", type=int)

    function_result = None
    function_error = None

    try:
        result_row = fetch_one(
            "SELECT fn_is_lens_compatible_with_camera(%s, %s) AS compatibility_result;",
            (camera_id, lens_id)
        )

        if result_row is not None:
            function_result = result_row.get("compatibility_result")
        else:
            function_result = "No result returned."
    except Exception as e:
        function_error = str(e)

    context = load_database_features_context(
        function_result=function_result,
        function_error=function_error
    )
    return render_template("database_features.html", **context)