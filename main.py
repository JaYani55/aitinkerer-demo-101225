"""
Streamlit app for viewing jobs and generating metadata using OpenRouter API.
Demo version with detailed console logging.
"""

import streamlit as st
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Setup detailed logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

logger.info("="*60)
logger.info("🚀 JOB METADATA GENERATOR - Started")
logger.info("="*60)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("⚠️ No API key found in environment!")

# Initialize OpenRouter client
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Paths
DATA_DIR = Path(__file__).parent / "data"
LOGOS_DIR = Path(__file__).parent / "logos"
JOBS_FILE = DATA_DIR / "jobs_dataset_mock.json"
SCHEMA_FILE = DATA_DIR / "schema.json"


@st.cache_data
def load_jobs_data():
    """Load jobs data from JSON file."""
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Handle both list format (mock) and dict format (full dataset)
    if isinstance(data, list):
        logger.info(f"📊 Loaded {len(data)} jobs from {JOBS_FILE.name}")
        return data
    else:
        logger.info(f"📊 Loaded {len(data.get('jobs', []))} jobs from {JOBS_FILE.name}")
        return data


@st.cache_data
def load_schema():
    """Load schema from JSON file."""
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return schema


def save_jobs_data(data):
    """Save jobs data to JSON file."""
    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Data saved to {JOBS_FILE.name}")


def generate_metadata(job: dict, schema: dict, model: str = "openai/gpt-4o-mini") -> dict:
    """Generate metadata for a job using OpenRouter API."""
    job_id = job.get("id", "unknown")
    job_title = job.get("job_title", "Unknown")[:50]
    employer_name = job.get('employer', {}).get('name', 'Unknown') if job.get('employer') else 'Unknown'
    
    logger.info("")
    logger.info("="*70)
    logger.info(f"🤖 METADATA GENERATION - Job #{job_id}")
    logger.info("="*70)
    logger.info(f"📋 Title: {job_title}")
    logger.info(f"🏢 Employer: {employer_name}")
    logger.info(f"🎯 Model: {model}")
    logger.info("")
    
    # Show schema structure
    logger.info("-"*70)
    logger.info("📐 SCHEMA - Required Fields:")
    logger.info("-"*70)
    schema_fields = schema.get("properties", {})
    for field_name, field_def in schema_fields.items():
        field_type = field_def.get("type", "unknown")
        if "enum" in field_def:
            enum_values = field_def["enum"][:3]
            enum_preview = ", ".join(str(v) for v in enum_values)
            logger.info(f"   • {field_name}: [{enum_preview}...]")
        elif "items" in field_def and "enum" in field_def["items"]:
            enum_values = field_def["items"]["enum"][:3]
            enum_preview = ", ".join(str(v) for v in enum_values)
            logger.info(f"   • {field_name}: array of [{enum_preview}...]")
        else:
            logger.info(f"   • {field_name}: {field_type}")
    logger.info("")
    
    # Build system prompt
    system_prompt = (
        "Du bist ein hilfreicher Data Entry Assistent. Deine Aufgabe ist es, "
        "Stellenanzeigen zu kategorisieren. Antworte nur in validen JSON Objekten. "
        "Alle Kategorien müssen stets ausgefüllt werden. Halte dich strikt an das Schema und denke dir keine Kategorien aus. "
        "Mehrfachantworten sind möglich. Tätigkeitsprofil ist eine Kurzbeschreibung der "
        "Tätigkeit mit mindestens 3 Stichpunkten. Adresse ist der Ort der Tätigkeit, "
        "antworte so genau wie möglich. JSON Schema: " + json.dumps(schema)
    )
    
    logger.info("-"*70)
    logger.info("💬 SYSTEM PROMPT:")
    logger.info("-"*70)
    # Show prompt without schema (too long)
    prompt_display = system_prompt[:200] + "... [+ JSON Schema]"
    logger.info(f"   {prompt_display}")
    logger.info("")
    
    # Prepare job data
    job_for_prompt = {
        "job_title": job.get("job_title"),
        "description": job.get("description"),
        "location": job.get("location"),
        "department": job.get("department"),
        "level": job.get("level"),
        "schedule": job.get("schedule"),
        "employer": employer_name,
    }
    user_content = json.dumps(job_for_prompt, ensure_ascii=False)
    
    logger.info("-"*70)
    logger.info("📄 USER PROMPT (Job Data):")
    logger.info("-"*70)
    # Show truncated job data
    desc_preview = (job.get("description") or "")[:100] + "..." if len(job.get("description") or "") > 100 else job.get("description") or "N/A"
    logger.info(f"   Title: {job.get('job_title')}")
    logger.info(f"   Location: {job.get('location')}")
    logger.info(f"   Description: {desc_preview}")
    logger.info("")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    
    logger.info("-"*70)
    logger.info("🌐 SENDING REQUEST TO OPENROUTER...")
    logger.info("-"*70)
    logger.info(f"   Endpoint: openrouter.ai/api/v1/chat/completions")
    logger.info(f"   Model: {model}")
    logger.info(f"   Temperature: 0.2")
    logger.info(f"   Response format: JSON")
    logger.info("")
    
    start_time = datetime.now()
    chat_response = openrouter_client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://inklupreneur.de",
            "X-Title": "MetadataGen Demo",
        },
        model=model,
        messages=messages,
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"   ⏱️  Response received in {elapsed_time:.2f}s")
    
    content = chat_response.choices[0].message.content
    
    # Clean up response
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if "```" in content:
            content = content.rsplit("```", 1)[0]
    content = content.replace("\n", " ").replace("\r", " ").strip()
    
    result = json.loads(content)
    
    logger.info("")
    logger.info("-"*70)
    logger.info("✅ GENERATED METADATA:")
    logger.info("-"*70)
    for key, value in result.items():
        if isinstance(value, list):
            logger.info(f"   • {key}: {value}")
        else:
            value_str = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
            logger.info(f"   • {key}: {value_str}")
    logger.info("")
    logger.info("="*70)
    logger.info(f"✅ COMPLETE - Job #{job_id}")
    logger.info("="*70)
    logger.info("")
    
    return result


def get_logo_path(logo_url: str) -> str | None:
    """Get the full path for a local logo file."""
    if not logo_url:
        return None
    
    # Handle local file paths (e.g., "logos\\iiis.png")
    if logo_url.startswith("logos") or logo_url.startswith("logos/"):
        logo_path = Path(__file__).parent / logo_url.replace("\\", "/")
        if logo_path.exists():
            return str(logo_path)
        return None
    
    # Handle URLs
    if logo_url.startswith("http"):
        return logo_url
    
    return None


def main():
    st.set_page_config(
        page_title="Job Metadata Generator",
        page_icon="🏷️",
        layout="wide"
    )
    
    st.title("🏷️ Job Metadata Generator")
    st.markdown("View jobs and generate metadata using AI")
    st.markdown("*Demo version with detailed console logging*")
    
    # Load data
    try:
        data = load_jobs_data()
        schema = load_schema()
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.info("Please ensure jobs_dataset_mock.json exists in the data folder")
        return
    
    # Handle both list format (mock) and dict format (full dataset)
    if isinstance(data, list):
        jobs = data
    else:
        jobs = data.get("jobs", [])
    
    # Sidebar - Filters
    st.sidebar.header("Filters")
    
    # Filter by employer
    employer_names = sorted(set(
        j.get("employer", {}).get("name", "Unknown") 
        for j in jobs if j.get("employer")
    ))
    selected_employer = st.sidebar.selectbox(
        "Filter by Employer",
        ["All"] + employer_names
    )
    
    # Filter by has metadata
    metadata_filter = st.sidebar.selectbox(
        "Metadata Status",
        ["All", "Has Metadata", "No Metadata"]
    )
    
    # Model selection
    st.sidebar.header("Model Settings")
    model = st.sidebar.selectbox(
        "OpenRouter Model",
        [
            "openai/gpt-4o-mini",
            "mistralai/ministral-3b-2512",
            "anthropic/claude-3.5-sonnet"
        ]
    )
    
    # Apply filters
    filtered_jobs = jobs
    
    if selected_employer != "All":
        filtered_jobs = [
            j for j in filtered_jobs 
            if j.get("employer", {}).get("name") == selected_employer
        ]
    
    if metadata_filter == "Has Metadata":
        filtered_jobs = [j for j in filtered_jobs if j.get("CategorizedData")]
    elif metadata_filter == "No Metadata":
        filtered_jobs = [j for j in filtered_jobs if not j.get("CategorizedData")]
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(jobs))
    with col2:
        st.metric("Filtered Jobs", len(filtered_jobs))
    with col3:
        jobs_with_metadata = len([j for j in jobs if j.get("CategorizedData")])
        st.metric("With Metadata", jobs_with_metadata)
    with col4:
        st.metric("Without Metadata", len(jobs) - jobs_with_metadata)
    
    st.divider()
    
    # Jobs list
    st.subheader(f"Jobs ({len(filtered_jobs)})")
    
    for idx, job in enumerate(filtered_jobs[:50]):  # Limit to 50 for performance
        job_id = job.get("id")
        job_title = job.get("job_title", "Untitled")
        employer_info = job.get("employer", {})
        employer_name = employer_info.get("name", "Unknown Employer") if employer_info else "Unknown Employer"
        logo_url_raw = employer_info.get("logo_url") if employer_info else None
        logo_path = get_logo_path(logo_url_raw)
        has_metadata = bool(job.get("CategorizedData"))
        
        # Create expander with job title
        status_icon = "✅" if has_metadata else "⚪"
        with st.expander(f"{status_icon} {job_title} - {employer_name}", expanded=False):
            # Two columns: logo + info | actions
            col_main, col_actions = st.columns([4, 1])
            
            with col_main:
                # Header with logo
                header_cols = st.columns([1, 4])
                with header_cols[0]:
                    if logo_path:
                        st.image(logo_path, width=80)
                    else:
                        st.markdown("🏢")
                
                with header_cols[1]:
                    st.markdown(f"### {job_title}")
                    st.markdown(f"**Employer:** {employer_name}")
                    if job.get("location"):
                        st.markdown(f"📍 {job.get('location')}")
                    if job.get("schedule"):
                        st.markdown(f"⏰ {job.get('schedule')}")
                    if job.get("level"):
                        st.markdown(f"📊 {job.get('level')}")
                
                # Job details tabs
                tab_details, tab_description, tab_metadata = st.tabs(["Details", "Description", "Metadata"])
                
                with tab_details:
                    detail_cols = st.columns(2)
                    with detail_cols[0]:
                        st.markdown(f"**ID:** {job_id}")
                        st.markdown(f"**Department:** {job.get('department') or 'N/A'}")
                        st.markdown(f"**Source:** {job.get('source_table', 'N/A')}")
                        st.markdown(f"**Archived:** {'Yes' if job.get('Archived') else 'No'}")
                    with detail_cols[1]:
                        st.markdown(f"**Clicks:** {job.get('clicks', 0)}")
                        st.markdown(f"**Created:** {job.get('created_at', 'N/A')[:10] if job.get('created_at') else 'N/A'}")
                        st.markdown(f"**URL:** [Link]({job.get('url')})" if job.get('url') else "**URL:** N/A")
                        jobsource = job.get("jobsource", {})
                        st.markdown(f"**Job Source:** {jobsource.get('jobsource', 'N/A') if jobsource else 'N/A'}")
                
                with tab_description:
                    description = job.get("description", "No description available")
                    if description:
                        # Truncate long descriptions
                        if len(description) > 2000:
                            st.markdown(description[:2000] + "...")
                            with st.expander("Show full description"):
                                st.markdown(description)
                        else:
                            st.markdown(description)
                    else:
                        st.info("No description available")
                
                with tab_metadata:
                    if has_metadata:
                        st.json(job.get("CategorizedData"))
                    else:
                        st.info("No metadata generated yet. Click 'Generate Metadata' to create it.")
            
            with col_actions:
                st.markdown("### Actions")
                
                # Generate Metadata button
                if st.button("🏷️ Generate Metadata", key=f"gen_{job_id}"):
                    with st.spinner("Generating metadata..."):
                        try:
                            metadata = generate_metadata(job, schema, model)
                            
                            # Update job in data (handle both list and dict formats)
                            jobs_list = data if isinstance(data, list) else data.get("jobs", [])
                            for j in jobs_list:
                                if j["id"] == job_id:
                                    j["CategorizedData"] = metadata
                                    break
                            
                            save_jobs_data(data)
                            load_jobs_data.clear()
                            
                            st.success("Metadata generated!")
                            st.json(metadata)
                            st.rerun()
                            
                        except Exception as e:
                            logger.error(f"❌ Error: {str(e)}")
                            st.error(f"Error generating metadata: {str(e)}")
                
                # Clear metadata button
                if has_metadata:
                    if st.button("🗑️ Clear Metadata", key=f"clear_{job_id}"):
                        jobs_list = data if isinstance(data, list) else data.get("jobs", [])
                        for j in jobs_list:
                            if j["id"] == job_id:
                                j["CategorizedData"] = None
                                break
                        save_jobs_data(data)
                        load_jobs_data.clear()
                        st.success("Metadata cleared!")
                        st.rerun()
    
    if len(filtered_jobs) > 50:
        st.warning(f"Showing first 50 of {len(filtered_jobs)} jobs. Use filters to narrow down.")
    
    # Batch operations
    st.divider()
    st.subheader("Batch Operations")
    
    col_batch1, col_batch2 = st.columns(2)
    
    with col_batch1:
        jobs_without_metadata = [j for j in filtered_jobs if not j.get("CategorizedData")][:10]
        if jobs_without_metadata:
            if st.button(f"🏷️ Generate Metadata for Next {len(jobs_without_metadata)} Jobs (max 10)"):
                logger.info(f"🚀 BATCH: Processing {len(jobs_without_metadata)} jobs")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                jobs_list = data if isinstance(data, list) else data.get("jobs", [])
                
                for i, job in enumerate(jobs_without_metadata):
                    status_text.text(f"Processing {i+1}/{len(jobs_without_metadata)}: {job.get('job_title', 'Unknown')[:50]}...")
                    try:
                        metadata = generate_metadata(job, schema, model)
                        for j in jobs_list:
                            if j["id"] == job["id"]:
                                j["CategorizedData"] = metadata
                                break
                    except Exception as e:
                        logger.error(f"❌ Failed for job {job.get('id')}: {str(e)}")
                        st.warning(f"Failed for job {job.get('id')}: {str(e)}")
                    
                    progress_bar.progress((i + 1) / len(jobs_without_metadata))
                
                save_jobs_data(data)
                load_jobs_data.clear()
                status_text.text("Done!")
                logger.info(f"✅ BATCH COMPLETE: {len(jobs_without_metadata)} jobs processed")
                st.success(f"Generated metadata for {len(jobs_without_metadata)} jobs!")
                st.rerun()
        else:
            st.info("All filtered jobs have metadata.")
    
    with col_batch2:
        if st.button("📥 Export Data with Metadata"):
            jobs_list = data if isinstance(data, list) else data.get("jobs", [])
            jobs_with_meta = [j for j in jobs_list if j.get("CategorizedData")]
            
            export_data = {"jobs": jobs_with_meta}
            export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label="Download JSON",
                data=export_json,
                file_name="jobs_with_metadata.json",
                mime="application/json"
            )


if __name__ == "__main__":
    main()
