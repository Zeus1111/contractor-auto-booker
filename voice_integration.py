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
We help homeowners around {city} get projects like that done right, on time and on budget.

So I can make this actually useful for you, mind if I ask a couple quick questions about the project?
Then if it makes sense, I can get you a free estimate. Cool?

[Wait for a yes. If they say no or not interested, thank them and end the call.]

-- DISCOVERY (from Jake's sales script) --
Ask questions to get the ANSWERS, not just because they're on the script.
If one answer covers the next few questions, skip those questions.

1. The problem
   "What's the biggest thing you're trying to fix or change with this {project_type}?"
   If the answer is vague: "What do you mean by that?" / "How so?" / "Could you expand on that?"

2. Context on the project
   "Did that project just start, or are you still in the planning phase?"
   "Do you have a contractor lined up yet, or are you still shopping around?"
   "Roughly what budget are you working with?"

3. Urgency
   "How long have you been dealing with that?"
   "What changed recently that made you pull the permit now?"

4. Prior solutions
   "Have you gotten any other estimates or worked with anyone on this so far?"
   If yes: "How did that go? What did you like about it, and what didn't you like?"

5. End goal
   "Picture it finished. What does the ideal result look like for you?"
   "When would you like it done by?"

6. Who decides
   "Is this a decision you'll make yourself, or is there a spouse or partner who should be at the walkthrough too?"

[Listen to every answer. Note it for the project manager.]

-- TRANSITION AND BOOKING --
Awesome. Based on what you told me, I think we can help with that.
I can have one of our project managers stop by for a free 30-minute walkthrough. No obligation, just ballpark numbers and ideas for {project_type}.

What works better for you, {day_a} afternoon or {day_b} morning?
[If a spouse or partner is part of the decision, pick a time when they can be there too.]

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
