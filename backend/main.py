"""
FastAPI application - thin API layer.

Exposes backend functionality via HTTP endpoints.
No business logic here - just routing.
"""

from pathlib import Path
from typing import List
import tempfile
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .services import process_syllabus
from .schemas import AcademicEvent
from .calendar_service import add_events_to_calendar


# FastAPI app instance
app = FastAPI(
    title="Syllabus to Calendar API",
    description="Extract academic events from syllabi",
    version="0.1.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class EventResponse(BaseModel):
    """Response model for a single event."""
    title: str
    event_type: str
    start_date: str
    start_time: str | None
    end_date: str | None
    end_time: str | None
    description: str | None
    location: str | None
    is_all_day: bool


class ExtractEventsResponse(BaseModel):
    """Response model for extract-events endpoint."""
    success: bool
    total_events: int
    events: List[EventResponse]

class AddToCalendarRequest(BaseModel):
    """Request model for adding events to calendar."""
    events: List[EventResponse]


class CalendarEventResult(BaseModel):
    """Result for a single calendar event creation."""
    title: str
    date: str
    calendar_id: str | None = None
    link: str | None = None
    error: str | None = None


class AddToCalendarResponse(BaseModel):
    """Response model for add-to-calendar endpoint."""
    success: bool
    total: int
    created: List[CalendarEventResult]
    failed: List[CalendarEventResult]


def convert_event_to_response(event: AcademicEvent) -> EventResponse:
    """Convert AcademicEvent to API response model."""
    return EventResponse(
        title=event.title,
        event_type=event.event_type.value,
        start_date=event.start_date.isoformat(),
        start_time=event.start_time.isoformat() if event.start_time else None,
        end_date=event.end_date.isoformat() if event.end_date else None,
        end_time=event.end_time.isoformat() if event.end_time else None,
        description=event.description,
        location=event.location,
        is_all_day=event.is_all_day
    )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Syllabus to Calendar API", "status": "running"}


@app.post("/extract-events", response_model=ExtractEventsResponse)
async def extract_events_endpoint(file: UploadFile = File(...)):
    """
    Extract events from an uploaded syllabus file.
    
    Accepts PDF or text files, processes them, and returns normalized events.
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.text', '.md'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        try:
            # Write uploaded content to temp file
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = Path(tmp_file.name)
            
            # Process the syllabus
            events = process_syllabus(tmp_file_path)
            
            # Convert to response models
            event_responses = [convert_event_to_response(event) for event in events]
            
            return ExtractEventsResponse(
                success=True,
                total_events=len(event_responses),
                events=event_responses
            )
            
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        finally:
            # Clean up temp file
            if tmp_file_path.exists():
                os.unlink(tmp_file_path)

@app.post("/add-to-calendar", response_model=AddToCalendarResponse)
async def add_to_calendar_endpoint(request: AddToCalendarRequest):
    """
    Add events to Google Calendar.
    
    Accepts a list of events and adds them to the user's primary Google Calendar.
    Returns information about successfully created events and any failures.
    """
    try:
        # Convert EventResponse back to AcademicEvent for calendar service
        from datetime import date, time
        from .schemas import EventType
        
        academic_events = []
        for event_response in request.events:
            academic_event = AcademicEvent(
                title=event_response.title,
                event_type=EventType(event_response.event_type),
                start_date=date.fromisoformat(event_response.start_date),
                start_time=time.fromisoformat(event_response.start_time) if event_response.start_time else None,
                end_date=date.fromisoformat(event_response.end_date) if event_response.end_date else None,
                end_time=time.fromisoformat(event_response.end_time) if event_response.end_time else None,
                description=event_response.description,
                location=event_response.location,
                is_all_day=event_response.is_all_day
            )
            academic_events.append(academic_event)
        
        # Add to calendar
        result = add_events_to_calendar(academic_events)
        
        # Convert to response format
        created_results = [
            CalendarEventResult(
                title=item['title'],
                date=item['date'],
                calendar_id=item.get('calendar_id'),
                link=item.get('link')
            )
            for item in result.get('created', [])
        ]
        
        failed_results = [
            CalendarEventResult(
                title=item['title'],
                date='',
                error=item.get('error')
            )
            for item in result.get('failed', [])
        ]
        
        return AddToCalendarResponse(
            success=result.get('success', False),
            total=result.get('total', len(request.events)),
            created=created_results,
            failed=failed_results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add events to calendar: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}