# 🏷️ Job Metadata Generator

A Streamlit demo app that uses AI to automatically generate structured metadata for job listings. Built for the AI Tinkerers Meetup (December 2025).

## 🎯 What it does

This app demonstrates how to use LLMs (via OpenRouter) to categorize job listings into structured metadata fields like:
- Arbeitsbereich (Work area)
- Berufserfahrung (Work experience)
- Arbeitszeit (Working hours)
- Ortsbindung (Location requirements)
- Sprachkenntnisse (Language skills)
- And more...

## 🚀 Quick Start

### Option 1: Use the batch file (Windows)
```bash
run.bat
```
This will automatically:
- Create a virtual environment if needed
- Install all dependencies
- Start the Streamlit app

### Option 2: Manual setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**
   ```bash
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openrouter_api_key_here
   ```
   
   Get your API key from [OpenRouter](https://openrouter.ai/)

5. **Run the app**
   ```bash
   streamlit run main.py
   ```

## 📁 Project Structure

```
├── main.py                 # Streamlit app
├── run.bat                 # Windows startup script
├── requirements.txt        # Python dependencies
├── .env                    # API key (create this!)
├── data/
│   ├── jobs_dataset_mock.json   # Sample job data
│   └── schema.json              # JSON Schema for metadata
├── logos/                  # Company logos
└── helperscripts/
    ├── concat_jobs.py              # Merge CSV files
    └── concat_jobs_freshdataset.py # Create clean dataset
```

## 🔧 Configuration

### Supported Models (via OpenRouter)
-    "openai/gpt-4o-mini",
-    "mistralai/ministral-3b-2512",
-    "anthropic/claude-3.5-sonnet"

Add any model signifier on openrouter

### Schema Fields
The metadata schema includes:
- **Arbeitsbereich**: Work area categories
- **Berufserfahrung**: Required experience level
- **Schulabschluss**: Education requirements
- **Arbeitszeit**: Full-time/Part-time
- **Ortsbindung**: Remote/On-site options
- **Tätigkeitsprofil**: Job description summary
- **Sprachkenntnisse**: Language requirements
- **relevante_skills**: Key skills
- **Befristung**: Contract type

## 📝 Features

- ✅ View job listings with filtering
- ✅ Generate metadata for individual jobs
- ✅ Batch process multiple jobs
- ✅ Export jobs with metadata
- ✅ Detailed console logging for demo purposes

## 🛠️ Helper Scripts

### concat_jobs.py
Concatenates CSV exports into a unified JSON dataset:
```bash
python helperscripts/concat_jobs.py --output data/jobs_dataset.json
```

### concat_jobs_freshdataset.py
Creates a clean dataset without existing metadata:
```bash
python helperscripts/concat_jobs_freshdataset.py --output data/jobs_dataset.json
```

## 📜 License

MIT

---

Built with ❤️ by Pluracon, Jay Rathjen for AI Tinkerers Meetup
