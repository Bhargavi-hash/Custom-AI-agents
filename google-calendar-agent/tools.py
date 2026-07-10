from auth import get_calendar_service
from datetime import datetime

def list_events(start_date: str, end_date: str) -> list[dict]:
    """
    Lists calendar events within a date range.
    Args:
        start_date: Start of the range, in YYYY-MM-DD format
        end_date: End of the range, in YYYY-MM-DD format
    """
    service = get_calendar_service()

    start_date += 'T00:00:00Z'
    end_date += 'T23:59:59Z'

    # Hint: you need to convert start_date/end_date into RFC3339 datetime strings
    # for timeMin/timeMax — think about what time of day to use for each boundary
    # (midnight at the start of start_date, midnight at the START of the day 
    # AFTER end_date, so the whole end_date is included)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_date,   # fill this in
        timeMax=end_date,   # fill this in
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    raw_events = events_result.get('items', [])

    # Hint: build a simplified list of dicts here — just id, summary, start, end
    # Watch out: an all-day event has event['start']['date'], while a timed 
    # event has event['start']['dateTime'] — you'll need to handle both

    simplified = []
    for event in raw_events:
        event_id = event['id']
        summary = event.get('summary', '(no title)')
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        e = {
            'id': event_id,
            'summary': summary,
            'start': start,
            'end': end
        }

        simplified.append(e)

    return simplified

def create_event(summary: str, start_datetime: str, end_datetime: str, description: str = "") -> dict:
    """
    Creates a new calendar event.
    Args:
        summary: The title of the event
        start_datetime: Start time in RFC3339 format, e.g. '2026-07-15T14:00:00-07:00'
        end_datetime: End time in RFC3339 format, e.g. '2026-07-15T15:00:00-07:00'
        description: Optional extra detail about the event
    """
    service = get_calendar_service()

    event_body = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_datetime},
        'end': {'dateTime': end_datetime},
    }

    created_event = service.events().insert(calendarId='primary', body=event_body).execute()

    return {
        'id': created_event['id'],
        'summary': created_event.get('summary'),
        'start': created_event['start'].get('dateTime'),
        'end': created_event['end'].get('dateTime'),
        'link': created_event.get('htmlLink')
    }

def update_event(event_id: str, summary: str = None, start_datetime: str = None,
                  end_datetime: str = None, description: str = None) -> dict:
    """
    Updates specific fields of an existing calendar event. Only provided
    fields are changed; omitted fields stay as they were.
    Args:
        event_id: The id of the event to update
        summary: New title, if changing
        start_datetime: New start time in RFC3339 format, if changing
        end_datetime: New end time in RFC3339 format, if changing
        description: New description, if changing
    """
    service = get_calendar_service()

    body = {}
    if summary is not None:
        body['summary'] = summary
    if start_datetime is not None:
        body['start'] = {'dateTime': start_datetime}
    if end_datetime is not None:
        body['end'] = {'dateTime': end_datetime}
    if description is not None:
        body['description'] = description

    updated_event = service.events().patch(
        calendarId='primary', eventId=event_id, body=body
    ).execute()

    return {
        'id': updated_event['id'],
        'summary': updated_event.get('summary'),
        'start': updated_event['start'].get('dateTime'),
        'end': updated_event['end'].get('dateTime'),
    }

def delete_event(event_id: str) -> dict:
    """
    Deletes a calendar event by its id.
    Args:
        event_id: The id of the event to delete
    """
    service = get_calendar_service()
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return {"deleted": True, "event_id": event_id}


def get_meeting_stats(start_date: str, end_date: str) -> dict:
    """
    Computes meeting statistics for a date range: total meeting count,
    total scheduled hours, and average meeting length.
    Args:
        start_date: Start of the range, in YYYY-MM-DD format
        end_date: End of the range, in YYYY-MM-DD format
    """
    events = list_events(start_date, end_date)

    meeting_count = 0
    total_scheduled_hours = 0.0

    for e in events:
        start_dt = datetime.fromisoformat(e['start'])
        end_dt = datetime.fromisoformat(e['end'])
        duration = end_dt - start_dt
        duration_hours = duration.total_seconds() / 3600

        if duration_hours >= 24:
            continue  # skip all-day events entirely -- not counted at all

        meeting_count += 1
        total_scheduled_hours += duration_hours

    avg_meeting_minutes = (total_scheduled_hours / meeting_count * 60) if meeting_count > 0 else 0

    return {
        "meeting_count": meeting_count,
        "total_hours": round(total_scheduled_hours, 2),
        "avg_meeting_minutes": round(avg_meeting_minutes, 1)
    }


def compare_periods(period_1_start: str, period_1_end: str,
                     period_2_start: str, period_2_end: str) -> dict:
    """
    Compares meeting load between two date ranges — e.g., this week vs. last week.
    Args:
        period_1_start: Start of the first period, YYYY-MM-DD
        period_1_end: End of the first period, YYYY-MM-DD
        period_2_start: Start of the second period, YYYY-MM-DD
        period_2_end: End of the second period, YYYY-MM-DD
    """
    stats_1 = get_meeting_stats(period_1_start, period_1_end)
    stats_2 = get_meeting_stats(period_2_start, period_2_end)

    return {
        "period_1": stats_1,
        "period_2": stats_2,
        "meeting_count_diff": stats_1["meeting_count"] - stats_2["meeting_count"],
        "total_hours_diff": round(stats_1["total_hours"] - stats_2["total_hours"], 2)
    }


if __name__ == "__main__":
    # First, use the event_id printed from your create_event test
    
    stats = get_meeting_stats(start_date='2026-07-05', end_date='2026-07-12')
    print("Stats:", stats)

    