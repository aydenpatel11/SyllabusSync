"""
Test script for Google Calendar integration.

This script tests the calendar_service module by:
1. Extracting events from a sample syllabus
2. Adding them to Google Calendar
"""

from pathlib import Path
from backend.extract_text import extract_text
from backend.extract_events import extract_events
from backend.normalize_events import normalize_events
from backend.calendar_service import add_events_to_calendar

def test_calendar_integration():
    """Test the full pipeline: extract -> normalize -> add to calendar."""
    
    # Step 1: Use a sample syllabus
    sample_file = Path("sample_syllabi/test_syllabus.txt")
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return
    
    print(f"📄 Processing: {sample_file}")
    print("-" * 60)
    
    # Step 2: Extract and normalize events
    text = extract_text(sample_file)
    raw_events = extract_events(text)
    normalized_events = normalize_events(raw_events)
    
    print(f"\n✅ Found {len(normalized_events)} events")
    print("\nEvents to be added to calendar:")
    print("-" * 60)
    
    for i, event in enumerate(normalized_events, 1):
        print(f"\n{i}. {event.title}")
        print(f"   Type: {event.event_type.value}")
        print(f"   Date: {event.start_date}")
        if event.start_time:
            print(f"   Time: {event.start_time}")
    
    # Step 3: Confirm before adding to calendar
    print("\n" + "=" * 60)
    response = input("\n🔔 Add these events to Google Calendar? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Cancelled. Events were not added to calendar.")
        return
    
    # Step 4: Add to Google Calendar
    print("\n📅 Adding events to Google Calendar...")
    print("-" * 60)
    
    result = add_events_to_calendar(normalized_events)
    
    # Step 5: Display results
    print("\n" + "=" * 60)
    if result['success']:
        print(f"✅ SUCCESS! Added {len(result['created'])} events to calendar")
    else:
        print(f"⚠️  Partial success: {len(result['created'])} added, {len(result['failed'])} failed")
    
    if result['created']:
        print("\n✅ Created Events:")
        for event in result['created']:
            print(f"   • {event['title']} ({event['date']})")
            print(f"     Link: {event['link']}")
    
    if result['failed']:
        print("\n❌ Failed Events:")
        for event in result['failed']:
            print(f"   • {event['title']}: {event['error']}")

if __name__ == "__main__":
    try:
        test_calendar_integration()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
