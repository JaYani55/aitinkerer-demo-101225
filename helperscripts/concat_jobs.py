"""
Concatenation script to unify employers, jobs, and jobsource data into a single JSON file.

This script:
1. Loads all CSV files (jobs_rows, jobs_archiviert_rows, employers_rows, jobsource_rows)
2. Normalizes job schemas between active and archived jobs
3. Parses the CategorizedData JSON column
4. Resolves foreign key relationships
5. Outputs a unified JSON structure to data/unified_jobs.json
"""

import json
import pandas as pd
from pathlib import Path
import argparse
from typing import Any


def parse_json_column(value: Any) -> dict | None:
    """Parse a JSON string column, returning None for invalid/empty values."""
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def load_csv_files(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load all CSV files from the data directory."""
    jobs_active = pd.read_csv(data_dir / "jobs_rows.csv")
    jobs_archived = pd.read_csv(data_dir / "jobs_archiviert_rows.csv")
    employers = pd.read_csv(data_dir / "employers_rows.csv")
    jobsources = pd.read_csv(data_dir / "jobsource_rows.csv")
    
    print(f"Loaded {len(jobs_active)} active jobs")
    print(f"Loaded {len(jobs_archived)} archived jobs")
    print(f"Loaded {len(employers)} employers")
    print(f"Loaded {len(jobsources)} job sources")
    
    return jobs_active, jobs_archived, employers, jobsources


def normalize_job_schemas(
    jobs_active: pd.DataFrame, 
    jobs_archived: pd.DataFrame
) -> pd.DataFrame:
    """
    Normalize job schemas between active and archived jobs.
    - Add original_id column to active jobs (set to None)
    - Add source_table column to distinguish origin
    """
    # Add original_id to active jobs if not present
    if "original_id" not in jobs_active.columns:
        jobs_active = jobs_active.copy()
        jobs_active["original_id"] = None
    
    # Add source table indicator
    jobs_active = jobs_active.copy()
    jobs_active["source_table"] = "active"
    
    jobs_archived = jobs_archived.copy()
    jobs_archived["source_table"] = "archived"
    
    # Concatenate both DataFrames
    all_jobs = pd.concat([jobs_active, jobs_archived], ignore_index=True)
    
    print(f"Combined {len(all_jobs)} total jobs")
    
    return all_jobs


def parse_categorized_data(jobs: pd.DataFrame) -> pd.DataFrame:
    """Parse the CategorizedData JSON column into a dict."""
    jobs = jobs.copy()
    jobs["CategorizedData"] = jobs["CategorizedData"].apply(parse_json_column)
    return jobs


def build_unified_structure(
    jobs: pd.DataFrame,
    employers: pd.DataFrame,
    jobsources: pd.DataFrame,
    include_embeddings: bool = False,
    include_descriptions: bool = True
) -> dict:
    """
    Build the unified JSON structure with resolved relationships.
    
    Structure:
    {
        "metadata": { ... },
        "employers": [ ... ],
        "jobsources": [ ... ],
        "jobs": [ ... ]  # With embedded employer/source names
    }
    """
    # Build employer lookup
    employer_lookup = {}
    for _, row in employers.iterrows():
        employer_id = row["id"]
        employer_lookup[employer_id] = {
            "id": employer_id,
            "name": row["name"] if pd.notna(row["name"]) else None,
            "alt_name": row["alt_name"] if pd.notna(row["alt_name"]) else None,
            "logo_url": row["logo_url"] if pd.notna(row["logo_url"]) else None,
            "fh": bool(row["fh"]) if pd.notna(row["fh"]) else False,
            "jobscount": int(row["jobscount"]) if pd.notna(row["jobscount"]) else 0,
            "jobscount_online": int(row["jobscount_online"]) if pd.notna(row["jobscount_online"]) else 0,
        }
    
    # Build jobsource lookup
    jobsource_lookup = {}
    for _, row in jobsources.iterrows():
        source_id = row["jobsource_id"]
        jobsource_lookup[source_id] = {
            "jobsource_id": source_id,
            "jobsource": row["jobsource"] if pd.notna(row["jobsource"]) else None,
            "description": row["description"] if pd.notna(row["description"]) else None,
        }
    
    # Build jobs list with embedded relationships
    jobs_list = []
    for _, row in jobs.iterrows():
        job_entry = {
            "id": int(row["id"]) if pd.notna(row["id"]) else None,
            "job_title": row["job_title"] if pd.notna(row["job_title"]) else None,
            "url": row["url"] if pd.notna(row["url"]) else None,
            "department": row["department"] if pd.notna(row["department"]) else None,
            "level": row["level"] if pd.notna(row["level"]) else None,
            "location": row["location"] if pd.notna(row["location"]) else None,
            "schedule": row["schedule"] if pd.notna(row["schedule"]) else None,
            "main": bool(row["main"]) if pd.notna(row["main"]) else False,
            "sync": bool(row["sync"]) if pd.notna(row["sync"]) else False,
            "ignore": bool(row["ignore"]) if pd.notna(row["ignore"]) else False,
            "removed": bool(row["removed"]) if pd.notna(row["removed"]) else False,
            "manual": bool(row["manual"]) if pd.notna(row["manual"]) else False,
            "Archived": bool(row["Archived"]) if pd.notna(row["Archived"]) else False,
            "ideal": bool(row["ideal"]) if pd.notna(row["ideal"]) else False,
            "created_at": row["created_at"] if pd.notna(row["created_at"]) else None,
            "updated_at": row["updated_at"] if pd.notna(row["updated_at"]) else None,
            "source_table": row["source_table"],
            "CategorizedData": row["CategorizedData"],
            "clicks": int(row["clicks"]) if pd.notna(row["clicks"]) else 0,
        }
        
        # Include description if requested
        if include_descriptions:
            job_entry["description"] = row["description"] if pd.notna(row["description"]) else None
        
        # Include embeddings if requested
        if include_embeddings:
            job_entry["job_embedding"] = row["job_embedding"] if pd.notna(row["job_embedding"]) else None
        
        # Add original_id for archived jobs
        if pd.notna(row.get("original_id")):
            job_entry["original_id"] = int(row["original_id"])
        
        # Resolve employer relationship
        employer_id = row["employer_id"]
        if pd.notna(employer_id) and employer_id in employer_lookup:
            employer = employer_lookup[employer_id]
            job_entry["employer"] = {
                "id": employer["id"],
                "name": employer["name"],
                "alt_name": employer["alt_name"],
                "logo_url": employer["logo_url"],
            }
        else:
            job_entry["employer"] = None
            job_entry["employer_id"] = employer_id if pd.notna(employer_id) else None
        
        # Resolve jobsource relationship
        jobsource_id = row["jobsource_id"]
        if pd.notna(jobsource_id) and jobsource_id in jobsource_lookup:
            source = jobsource_lookup[jobsource_id]
            job_entry["jobsource"] = {
                "jobsource_id": source["jobsource_id"],
                "jobsource": source["jobsource"],
            }
        else:
            job_entry["jobsource"] = None
            job_entry["jobsource_id"] = jobsource_id if pd.notna(jobsource_id) else None
        
        jobs_list.append(job_entry)
    
    # Build final structure
    unified = {
        "metadata": {
            "generated_at": pd.Timestamp.now().isoformat(),
            "total_jobs": len(jobs_list),
            "active_jobs": len([j for j in jobs_list if j["source_table"] == "active"]),
            "archived_jobs": len([j for j in jobs_list if j["source_table"] == "archived"]),
            "total_employers": len(employer_lookup),
            "total_jobsources": len(jobsource_lookup),
            "include_embeddings": include_embeddings,
            "include_descriptions": include_descriptions,
        },
        "employers": list(employer_lookup.values()),
        "jobsources": list(jobsource_lookup.values()),
        "jobs": jobs_list,
    }
    
    return unified


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate CSV files into a unified JSON structure"
    )
    parser.add_argument(
        "--include-embeddings",
        action="store_true",
        help="Include job_embedding field in output (increases file size significantly)"
    )
    parser.add_argument(
        "--exclude-descriptions",
        action="store_true",
        help="Exclude job descriptions from output to reduce file size"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: data/unified_jobs.json)"
    )
    
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    output_path = Path(args.output) if args.output else data_dir / "unified_jobs.json"
    
    print(f"Data directory: {data_dir}")
    print(f"Output path: {output_path}")
    print()
    
    # Load CSV files
    jobs_active, jobs_archived, employers, jobsources = load_csv_files(data_dir)
    
    # Normalize and combine job schemas
    all_jobs = normalize_job_schemas(jobs_active, jobs_archived)
    
    # Parse CategorizedData JSON column
    all_jobs = parse_categorized_data(all_jobs)
    
    # Build unified structure
    unified = build_unified_structure(
        all_jobs,
        employers,
        jobsources,
        include_embeddings=args.include_embeddings,
        include_descriptions=not args.exclude_descriptions,
    )
    
    # Write output JSON
    print()
    print(f"Writing unified JSON to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unified, f, ensure_ascii=False, indent=2)
    
    # Print summary
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Done! File size: {file_size_mb:.2f} MB")
    print()
    print("Summary:")
    print(f"  - Total jobs: {unified['metadata']['total_jobs']}")
    print(f"  - Active jobs: {unified['metadata']['active_jobs']}")
    print(f"  - Archived jobs: {unified['metadata']['archived_jobs']}")
    print(f"  - Employers: {unified['metadata']['total_employers']}")
    print(f"  - Job sources: {unified['metadata']['total_jobsources']}")


if __name__ == "__main__":
    main()
