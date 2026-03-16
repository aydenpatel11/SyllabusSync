"""
Event extraction module for syllabi.

Extracts academic events (exams, assignments, deadlines) from extracted text.
"""

from typing import List
from datetime import date, time
from .schemas import AcademicEvent, EventType
import dateparser
import re


def extract_events(text: str) -> List[AcademicEvent]:
    """
    Extract academic events from syllabus text.
    
    Args:
        text: Raw text extracted from syllabus
        
    Returns:
        List of AcademicEvent objects
    """
    events = []
    
    # Split text into lines 
    lines = text.split('\n')
    
    # Build a map of character positions to line numbers
    char_to_line = {}
    char_pos = 0
    for line_num, line in enumerate(lines):
        # Map all positions in this line to this line number
        for i in range(len(line)):
            char_to_line[char_pos + i] = line_num
        char_pos += len(line) + 1 
    
    date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    matches = re.finditer(date_pattern, text)
    
    for match in matches:
        try:
            event_date = parse_date(match.group())
        except ValueError:
            continue
        
        # Find which line contains this date
        date_line_num = char_to_line.get(match.start(), 0)
        date_line = lines[date_line_num]
        
        # Find the date within this specific line (search again in the line)
        line_date_match = re.search(date_pattern, date_line)
        if not line_date_match:
            continue
        
        # Get line-aware context: current line + 1 line before and after
        context_lines = []
        for i in range(max(0, date_line_num - 1), min(len(lines), date_line_num + 2)):
            context_lines.append(lines[i])
        context = '\n'.join(context_lines)
        
        # Extract title: look backward from date position in the line
        date_in_line_pos = line_date_match.start()
        title_text = date_line[:date_in_line_pos].strip()
        
        # Clean up title: remove leading bullets, dashes, colons
        title = re.sub(r'^[-•:\s]+', '', title_text).strip()
        
        # If title is empty or too short, try looking at previous line
        if not title or len(title) < 3:
            if date_line_num > 0:
                prev_line = lines[date_line_num - 1].strip()
                # Only use previous line if it looks like a title (not a date range, etc.)
                if prev_line and not re.search(r'\d{1,2}[/-]\d{1,2}', prev_line):
                    title = re.sub(r'^[-•:\s]+', '', prev_line).strip()

        if not title:
            title = "Event"
        
        # Extract time: only search within 30 characters after the date
        time_obj = None
        date_end_in_line = line_date_match.end()
        time_search_text = date_line[date_end_in_line:date_end_in_line + 30]
        time_match = re.search(r'\b(?:at\s+)?(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)|\d{1,2}\s*(?:AM|PM|am|pm))\b', time_search_text)
        if time_match:
            try:
                time_obj = parse_time(time_match.group())
            except ValueError:
                pass
        
        # Detect event type from the immediate line context
        event_type = detect_event_type(date_line)
        
        event = AcademicEvent(
            title=title,
            event_type=event_type,
            start_date=event_date,
            start_time=time_obj,
            is_all_day=(time_obj is None)
        )
        events.append(event)
    
    return events


def parse_date(date_string: str) -> date:
    """
    Parse a date string into a date object.
    
    Args:
        date_string: String containing a date
        
    Returns:
        date object
        
    Raises:
        ValueError: If date cannot be parsed
    """
    parsed = dateparser.parse(date_string)
    if parsed is None:
        raise ValueError(f"Unable to parse date: {date_string}")
    return parsed.date()

def parse_time(time_string: str) -> time:
    """
    Parse a time string into a time object.

    Args:
        time_string: String containing a time
        
    Returns:
        time object
        
    Raises:
        ValueError: If time cannot be parsed
    """
    parsed = dateparser.parse(time_string)
    if parsed is None:
        raise ValueError(f"Unable to parse time: {time_string}")
    return parsed.time()


def detect_event_type(text: str) -> EventType:
    """
    Detect the type of event from text.
    
    Args:
        text: Text containing event description
        
    Returns:
        EventType enum value
    """
    text = text.lower()
    if "midterm" in text or "final" in text or "exam" in text:
        return EventType.EXAM
    elif "assignment" in text or "homework" in text:
        return EventType.ASSIGNMENT
    elif "quiz" in text:
        return EventType.QUIZ
    elif "due" in text:
        return EventType.DEADLINE
    elif "reading" in text:
        return EventType.READING
    elif "lecture" in text:
        return EventType.LECTURE
    elif "discussion" in text:
        return EventType.DISCUSSION
    elif "lab" in text:
        return EventType.LAB
    else:
        return EventType.OTHER


if __name__ == "__main__":
    # Quick test with sample text
    sample_text = """
    Assignment 1 Due: January 20, 2024
    Quiz 1: January 25, 2024
    Midterm Exam: February 15, 2024 at 2:00 PM
    Final Exam: May 10, 2024 at 3:00 PM
    """
    
    events = extract_events(sample_text)
    print(f"Found {len(events)} events:\n")
    
    for i, event in enumerate(events, 1):
        print(f"Event {i}:")
        print(f"  Title: {event.title}")
        print(f"  Type: {event.event_type.value}")
        print(f"  Date: {event.start_date}")
        if event.start_time:
            print(f"  Time: {event.start_time.strftime('%I:%M %p')}")
        print()