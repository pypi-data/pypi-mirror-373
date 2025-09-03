import uuid
from datetime import datetime, timedelta
from ..core import tool

@tool
def create_calendar_event(title: str, start_time_str: str, duration_minutes: int, attendees: list[str] = None):
    """
    Creates a calendar event in the standard iCalendar (.ics) format from event details.
    Use this to schedule meetings, appointments, or events.

    Args:
        title: The title or summary of the event.
        start_time_str: The starting time of the event in ISO 8601 format (e.g., '2025-08-25T14:30:00').
        duration_minutes: The duration of the event in minutes.
        attendees: A list of email addresses of people to invite.
    """
    try:
        # Parse the start time and calculate the end time
        start_time = datetime.fromisoformat(start_time_str)
        end_time = start_time + timedelta(minutes=duration_minutes)

        # Get current time for timestamping
        now = datetime.utcnow()

        # Format times for the iCalendar spec (YYYYMMDDTHHMMSSZ)
        start_format = start_time.strftime("%Y%m%dT%H%M%SZ")
        end_format = end_time.strftime("%Y%m%dT%H%M%SZ")
        now_format = now.strftime("%Y%m%dT%H%M%SZ")

        # Build the .ics file content as a string
        ics_parts = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Toolchain//EN",
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}",
            f"DTSTAMP:{now_format}",
            f"DTSTART:{start_format}",
            f"DTEND:{end_format}",
            f"SUMMARY:{title}",
        ]

        if attendees:
            for email in attendees:
                ics_parts.append(f"ATTENDEE;CN={email}:mailto:{email}")
        
        ics_parts.append("END:VEVENT")
        ics_parts.append("END:VCALENDAR")

        return {"ics_data": "\n".join(ics_parts)}

    except ValueError:
        return {"error": "Invalid start_time_str format. Please use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

