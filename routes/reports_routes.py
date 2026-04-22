from flask import Blueprint, render_template
from db import fetch_all

reports_bp = Blueprint("reports_bp", __name__)


@reports_bp.route("/reports")
def reports():
    camera_system_report = fetch_all("""
        SELECT
            camera_id,
            camera_name,
            manufacturer_name,
            mount_name,
            camera_type,
            release_year,
            variant_count,
            compatible_lens_count,
            documentation_count,
            accessory_compatibility_count
        FROM vw_camera_system_summary
        ORDER BY manufacturer_name, camera_name;
    """)

    film_workflow_report = fetch_all("""
        SELECT
            film_id,
            film_name,
            manufacturer_name,
            format_name,
            box_iso,
            color_type,
            release_year,
            discontinued,
            workflow_count,
            developer_count,
            avg_development_time_minutes,
            min_development_time_minutes,
            max_development_time_minutes
        FROM vw_film_workflow_coverage
        ORDER BY manufacturer_name, film_name;
    """)

    accessory_compatibility_report = fetch_all("""
        SELECT
            accessory_id,
            accessory_name,
            manufacturer_name,
            accessory_type,
            mount_name,
            format_name,
            release_year,
            compatible_variant_count,
            parent_camera_count,
            compatibility_type_count
        FROM vw_accessory_compatibility_summary
        ORDER BY manufacturer_name, accessory_name;
    """)

    developer_usage_report = fetch_all("""
        SELECT
            fd.developer_id,
            fd.developer_name,
            m.manufacturer_name,
            fd.developer_type,
            COUNT(DISTINCT fdg.development_id) AS workflow_entry_count,
            COUNT(DISTINCT fdg.film_id) AS distinct_film_count,
            ROUND(AVG(fdg.development_time_minutes), 2) AS avg_development_time_minutes,
            MIN(fdg.development_time_minutes) AS min_development_time_minutes,
            MAX(fdg.development_time_minutes) AS max_development_time_minutes
        FROM film_developers fd
        JOIN manufacturers m
            ON fd.manufacturer_id = m.manufacturer_id
        LEFT JOIN film_development_guide fdg
            ON fd.developer_id = fdg.developer_id
        GROUP BY
            fd.developer_id,
            fd.developer_name,
            m.manufacturer_name,
            fd.developer_type
        ORDER BY m.manufacturer_name, fd.developer_name;
    """)

    return render_template(
        "reports.html",
        camera_system_report=camera_system_report,
        film_workflow_report=film_workflow_report,
        accessory_compatibility_report=accessory_compatibility_report,
        developer_usage_report=developer_usage_report
    )