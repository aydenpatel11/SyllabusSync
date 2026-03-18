"""
Test script for event extraction.

Run this script to test the extract_events function with sample syllabi.
"""

from pathlib import Path
from backend.extract_text import extract_text
from backend.extract_events import extract_events


def test_with_file(file_path: Path):
    """Test event extraction with a syllabus file."""
    print(f"Testing with file: {file_path.name}")
    print("=" * 60)
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    # Extract text
    print("Extracting text...")
    text = extract_text(file_path)
    print(f"Extracted {len(text)} characters\n")
    
    # Extract events
    print("Extracting events...")
    events = extract_events(text)
    print(f"Found {len(events)} events:\n")
    
    # Display events
    for i, event in enumerate(events, 1):
        print(f"Event {i}:")
        print(f"  Title: {event.title}")
        print(f"  Type: {event.event_type.value}")
        print(f"  Date: {event.start_date.strftime('%B %d, %Y')}")
        if event.start_time:
            print(f"  Time: {event.start_time.strftime('%I:%M %p')}")
        else:
            print(f"  Time: All day")
        print(f"  Is All Day: {event.is_all_day}")
        if event.description:
            print(f"  Description: {event.description}")
        print()


def test_with_sample_text():
    """Test with inline sample text."""
    print("Testing with sample text...")
    print("=" * 60)
    
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
        print(f"  Date: {event.start_date.strftime('%B %d, %Y')}")
        if event.start_time:
            print(f"  Time: {event.start_time.strftime('%I:%M %p')}")
        else:
            print(f"  Time: All day")
        print()


if __name__ == "__main__":
    # Test with the sample syllabus file
    test_file = Path("sample_syllabi/test_syllabus.txt")
    
    if test_file.exists():
        test_with_file(test_file)
        print("\n" + "=" * 60 + "\n")
    else:
        print(f"Test file not found: {test_file}")
        print()
    
    # Test with sample text
    test_with_sample_text()
