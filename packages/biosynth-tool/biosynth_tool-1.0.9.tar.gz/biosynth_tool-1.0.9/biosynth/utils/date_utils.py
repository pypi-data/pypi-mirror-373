from datetime import datetime


def format_current_date():
    # Get the current date and time
    date = datetime.now()

    # Define the suffixes for the day
    suffixes = ['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th']

    # Format the date
    formatted_date = date.strftime("%B %d")  # Month and day
    day = int(date.strftime("%d"))
    suffix = suffixes[day % 10 if day < 30 else 0]  # Determine the appropriate suffix for the day
    formatted_date += f"{suffix}, {date.strftime('%H:%M')}"  # Add the time

    return formatted_date
