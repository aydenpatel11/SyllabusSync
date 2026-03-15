# Syllabus to Calendar

A Python-based application that automatically extracts important academic dates from course syllabi (PDF or text) and adds them to Google Calendar.

## Features

- **Multi-format Support**: Extract text from PDF, TXT, and Markdown files
- **Smart Event Extraction**: Automatically identifies:
  - Exams (midterms, finals)
  - Assignments and homework
  - Quizzes
  - Deadlines
  - Readings
  - Labs and discussions
- **Event Normalization**: Cleans and validates extracted events
- **REST API**: FastAPI-based backend for easy integration

## Project Structure

```
syllabus-to-calendar/
├── backend/
│   ├── __init__.py
│   ├── extract_text.py         # PDF/text extraction
│   ├── extract_events.py       # Event extraction logic
│   ├── normalize_events.py     # Event validation & cleaning
│   ├── schemas.py              # Data models
│   └── config.py               # Configuration
├── sample_syllabi/             # Sample files for testing
├── requirements.txt
└── README.md
```

## Technologies Used

- **Python 3.12+**
- **Pydantic**: Data validation and settings management
- **pdfplumber**: PDF text extraction
- **dateparser**: Flexible date parsing

## Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd syllabus-to-calendar
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Testing the Modules

You can test individual modules directly:

```bash
# Test text extraction
python backend/extract_text.py

# Test event extraction
python test_extract_events.py
```

### Using as a Library

```python
from pathlib import Path
from backend.extract_text import extract_text
from backend.extract_events import extract_events
from backend.normalize_events import normalize_events

# Extract text from syllabus
file_path = Path("sample_syllabi/test_syllabus.txt")
text = extract_text(file_path)

# Extract events
events = extract_events(text)

# Normalize and clean events
normalized_events = normalize_events(events)

# Use the events
for event in normalized_events:
    print(f"{event.title} - {event.start_date}")
```

## Development

### Project Architecture

```
Syllabus File (PDF/TXT)
         ↓
    extract_text.py
         ↓
    Raw Text String
         ↓
    extract_events.py
         ↓
    List[AcademicEvent]
         ↓
    normalize_events.py
         ↓
    Clean, Validated Events
```

### Code Organization

The codebase follows a modular pipeline design:
- **extract_text.py**: Handles file reading and text extraction
- **extract_events.py**: Parses text and identifies events
- **normalize_events.py**: Cleans, validates, and deduplicates events
- **schemas.py**: Defines data models (Pydantic)
- **config.py**: Centralized configuration

### Running Tests

```bash
# Test event extraction with sample file
python test_extract_events.py
```

## Event Types Supported

The system can identify and categorize:

- **Exams**: Midterms, finals, tests
- **Assignments**: Homework, projects, papers
- **Quizzes**: Short tests, pop quizzes
- **Deadlines**: Due dates, submission deadlines
- **Readings**: Required reading assignments
- **Lectures**: Class sessions
- **Discussions**: Discussion sections
- **Labs**: Laboratory sessions
- **Other**: Any other academic events

## Event Normalization

Extracted events are automatically:
1. **Cleaned**: Remove redundant words, fix formatting
2. **Validated**: Check for missing fields, invalid dates
3. **Deduplicated**: Remove duplicate events
4. **Sorted**: Ordered by date

## Roadmap

### Planned Features

- **REST API**: FastAPI-based backend for HTTP access
- **Google Calendar Integration**: OAuth 2.0 authentication and direct calendar sync
- **Web Interface**: User-friendly frontend for uploading and managing events
- **Event Review & Editing**: Review and modify events before adding to calendar
- **Batch Operations**: Add multiple events at once

## Configuration

Configuration settings are in `backend/config.py`:

```python
# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SAMPLE_SYLLABI_DIR = PROJECT_ROOT / "sample_syllabi"
```

## Troubleshooting

### Common Issues

**1. Import errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**2. PDF extraction fails**
- Ensure the PDF is text-based (not scanned images)
- Try converting scanned PDFs with OCR first

**3. No events found**
- Check if syllabus has clear date formats
- Supported formats: "January 20, 2024", "1/20/2024", etc.
- Events need recognizable keywords (exam, assignment, due, etc.)

## Author

[Ayden Patel]

## Acknowledgments

- PDF extraction powered by pdfplumber
- Date parsing by dateparser
- Data validation with Pydantic

---

**Note**: This is a personal project for educational purposes. Always review extracted events before adding to your calendar.
