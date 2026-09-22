"""
Working voice + SMS integration for Contractor Auto-Booker.

Setup:
  pip install elevenlabs twilio python-dotenv requests
  export ELEVENLABS_API_KEY=***
  export ELEVENLABS_VOICE_ID=your_voice_id
  export TWILIO_ACCOUNT_SID=your_sid
  export TWILIO_AUTH_TOKEN=***
  export TWILIO_FROM_NUMBER=+1XXXXXXXXXX
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path

try:
    from elevenlabs import generate, set_api_key
    from twilio.rest import Client as TwilioClient
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("ElevenLabs/Twilio not installed. Run: pip install elevenlabs twilio")


CALL_SCRIPT = """
Hey, this is {caller_name} from {company_name}. Am I speaking with {homeowner_name}?

Great. I'm reaching out because we saw you just pulled a permit for {project_type} at {address}.

Did that project just start, or are you still in the planning phase?

[Listen — pause 3 seconds]

Perfect. We do {project_type} all over {city} and we're booking estimates for the next two weeks. I can have one of our project managers stop by for a free 30-minute walkthrough — no obligation, just ballpark numbers and ideas.

What works better for you — {day_a} afternoon or {day_b} morning?

[Book the appointment]

Awesome. I'll text you a confirmation right now with your project manager's contact info. Looking forward to it.

Have a great day.
"""


def make_call_script(lead: dict, config: dict) -> str:
    return CALL_SCRIPT.format(
        caller_name=config.get("caller_name", "Tyler"),
        company_name=config.get("company_name", "Mannis Home Enhancement"),
        homeowner_name=lead["name"],
        project_type=lead["project_type"],
        address=lead["address"],
        city=config.get("city", "Denver"),
        day_a="this Wednesday",
        day_b="Thursday",
    )


def place_call_with_elevenlabs(lead: dict, config: dict) -> dict:
    if not DEPS_AVAILABLE:
        return {"status": "deps_missing", "message": "Run: pip install elevenlabs twilio"}

    set_api_key(os.environ["ELEVENLABS_API_KEY"])

    script_text = make_call_script(lead, config)

    audio = generate(
        text=script_text,
        voice=os.environ["ELEVENLABS_VOICE_ID"],
        model="eleven_turbo_v2_5",
    )

    output_path = Path(f"calls/{lead['name'].replace(' ', '_')}_{datetime.now().isoformat()}.mp3")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio)

    return {
        "status": "voicemail_ready",
        "lead": lead["name"],
        "audio_path": str(output_path),
        "note": "Use ElevenLabs Agents Platform or Vapi/Bland.ai to actually place the call",
    }


def send_confirmation_sms(lead: dict, appointment: dict, config: dict) -> dict:
    if not DEPS_AVAILABLE:
        return {"status": "deps_missing"}

    client = TwilioClient(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

    body = (
        f"Hi {lead['name']}, this is {config.get('caller_name', 'Tyler')} from "
        f"{config.get('company_name', 'Mannis Home Enhancement')}. "
        f"Confirming your free estimate on {appointment['date']} at {appointment['time']}. "
        f"Your project manager is {appointment['pm_name']}, {appointment['pm_phone']}. "
        f"Reply STOP to opt out."
    )

    message = client.messages.create(
        body=body,
        from_=os.environ["TWILIO_FROM_NUMBER"],
        to=lead["phone"],
    )

    return {
        "status": "sent",
        "message_sid": message.sid,
        "to": lead["phone"],
    }


def log_outcome(lead: dict, outcome: dict, log_file: str = "call_log.csv"):
    file_exists = Path(log_file).exists()
    with open(log_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "name", "phone", "address", "project_type",
            "call_status", "booked", "appointment_date", "appointment_time",
            "sms_sent", "notes"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "name": lead["name"],
            "phone": lead["phone"],
            "address": lead["address"],
            "project_type": lead["project_type"],
            "call_status": outcome.get("call_status", "unknown"),
            "booked": outcome.get("booked", False),
            "appointment_date": outcome.get("appointment_date", ""),
            "appointment_time": outcome.get("appointment_time", ""),
            "sms_sent": outcome.get("sms_sent", False),
            "notes": outcome.get("notes", ""),
        })


if __name__ == "__main__":
    sample_lead = {
        "name": "Sarah Johnson",
        "phone": "+13035551234",
        "address": "1234 Larimer St, Denver, CO 80202",
        "project_type": "kitchen remodel",
        "permit_value": 45000,
    }

    sample_config = {
        "caller_name": "Tyler",
        "company_name": "Mannis Home Enhancement",
        "city": "Denver",
    }

    script = make_call_script(sample_lead, sample_config)
    print("=" * 60)
    print("CALL SCRIPT:")
    print("=" * 60)
    print(script)
    print("=" * 60)
    print("\nTo actually place the call:")
    print("  1. Set up ElevenLabs + Twilio (see README.md)")
    print("  2. Use ElevenLabs Agents Platform or Vapi.ai to bridge them")
    print("  3. Run: place_call_with_elevenlabs(sample_lead, sample_config)")
