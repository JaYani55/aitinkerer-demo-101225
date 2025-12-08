"""
Script to create a fresh dataset from unified_jobs.json without metadata.

This script reads the unified_jobs.json file and outputs a new JSON file
containing only the employers, jobsources, and jobs arrays without the metadata field.
"""

import json
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Create a fresh dataset from unified_jobs.json without metadata"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input file path (default: data/unified_jobs.json)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: data/jobs_dataset.json)"
    )
    
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    input_path = Path(args.input) if args.input else data_dir / "unified_jobs.json"
    output_path = Path(args.output) if args.output else data_dir / "jobs_dataset.json"
    
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")
    print()
    
    # Load unified JSON
    print("Loading unified_jobs.json...")
    with open(input_path, "r", encoding="utf-8") as f:
        unified_data = json.load(f)
    
    # Remove CategorizedData from each job
    jobs_cleaned = []
    for job in unified_data.get("jobs", []):
        job_copy = {k: v for k, v in job.items() if k != "CategorizedData"}
        jobs_cleaned.append(job_copy)
    
    # Create fresh dataset without metadata and CategorizedData
    fresh_dataset = {
        "employers": unified_data.get("employers", []),
        "jobsources": unified_data.get("jobsources", []),
        "jobs": jobs_cleaned,
    }
    
    # Write output JSON
    print(f"Writing fresh dataset to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fresh_dataset, f, ensure_ascii=False, indent=2)
    
    # Print summary
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Done! File size: {file_size_mb:.2f} MB")
    print()
    print("Summary:")
    print(f"  - Employers: {len(fresh_dataset['employers'])}")
    print(f"  - Job sources: {len(fresh_dataset['jobsources'])}")
    print(f"  - Jobs: {len(fresh_dataset['jobs'])}")


if __name__ == "__main__":
    main()
