# Contractor Auto-Booker — Claude Code Agent Prompt

This is the Claude Code prompt that runs the entire 4-step pipeline. Copy-paste into Claude Code and run with your contractor's zip codes + trade.

```python
# Paste this into Claude Code (claude.ai/code or your terminal)
# Replace the placeholders below with your actual values

AGENT_CONFIG = {
    "trades": ["roofing", "remodeling", "bathroom", "kitchen", "deck"],
    "zip_codes": ["80202", "80203", "80204", "80205", "80206", "80211", "80212"],
    "city": "Denver",
    "state": "CO",
    "your_company": "Mannis Home Enhancement",
    "your_phone": "+1-XXX-XXX-XXXX",
    "calendar_id": "your-google-calendar-id",
    "elevenlabs_voice_id": "your-elevenlabs-voice-id",
    "elevenlabs_api_key": "YOUR_KEY",
    "twilio_account_sid": "YOUR_SID",
    "twilio_auth_token": "YOUR_TOKEN",
    "twilio_from_number": "+1-XXX-XXX-XXXX",
}

PROMPT = """
You are an autonomous AI agent for {your_company}, a {trades} contractor in {city}, {state}.

Your job: find homeowners about to remodel, call them with a human-sounding AI voice, and book free in-home estimates on the calendar.

## Step 1: Scrape building permits
Use the local government building permits API (or scrape the public portal) for {zip_codes}.
Filter for permits filed in the last 30 days that match: {trades}.
Extract: homeowner name, address, project type, permit value, filing date.

## Step 2: Enrich contact info
For each permit, look up the homeowner's phone number using:
- Skip tracing services (BatchLeads, REISkip) — free trial works for ~50/mo
- Public records (property tax records, voter registration)
- Google search for "[homeowner name] [address]"

Output a CSV with: name, phone, address, project_type, project_value, permit_date.

## Step 3: Call with ElevenLabs voice
For each row in the CSV, use ElevenLabs to place an outbound call with this script:

"Hey, this is {your_name} from {your_company}. Am I speaking with [homeowner_name]?

Great. I'm reaching out because we saw you just pulled a permit for [project_type] at [address].

Did that project just start, or are you still in the planning phase?

[Listen to response]

Perfect. We do [project_type] all over {city} and we're booking estimates for [next two weeks]. I can have one of our project managers stop by for a free 30-minute walkthrough — no obligation, just ballpark numbers and ideas.

What works better for you — [day] afternoon or [day] morning?

[Book the appointment on Google Calendar]

Awesome. I'll text you a confirmation right now with [project_manager]'s contact info. Looking forward to it.

Have a great day."

## Step 4: Book on Google Calendar + send confirmation
Create a Google Calendar event titled "{your_company} - Estimate - [homeowner_name]"
Location: [address]
Duration: 30 minutes
Description: Project type: [project_type]. Permit value: $[value]. Lead source: building permits.

Then send a Twilio SMS:
"Hi [homeowner_name], this is {your_name} from {your_company}. Confirming your free estimate on [date] at [time]. Your project manager is [name], [phone]. Reply STOP to opt out."

## Output
For each completed call, log:
- Homeowner name
- Phone number called
- Call duration
- Outcome (booked / not interested / no answer / wrong number / voicemail)
- Booked date/time if applicable
- Project details

Save to a Google Sheet titled "{your_company} - AI Lead Pipeline"

## Rules
- Only call between 9am-7pm in the homeowner's local time zone
- Always identify yourself and your company at the start of the call
- Never make false claims or guarantees
- If the homeowner asks to be removed, mark them as DNC and never call again
- Stop calling if the homeowner says they're not interested (one objection = end call politely)
- TCPA compliance: only call numbers listed in the permit registry, never auto-dial random numbers
"""

print("Agent ready. Replace placeholder values in AGENT_CONFIG.")
print("Then paste this into Claude Code and run:")
print("  > Run the contractor auto-booker with config above")
print()
print("Expected output:")
print("  - CSV of scraped permits")
print("  - CSV of enriched contacts")
print("  - Call log with outcomes")
print("  - Booked estimates on Google Calendar")
print("  - Confirmation SMS sent via Twilio")
```

## What this does

1. **Finds 50-200 homeowners/month** who just pulled permits for the trades you serve
2. **Auto-enriches their phone numbers** (skip tracing + public records)
3. **Calls them with a human voice** (ElevenLabs) using a proven script
4. **Books the estimate on your calendar** + sends a confirmation text
5. **Logs everything** to a Google Sheet for review

## Cost per booked lead

| Service | Cost per lead |
|---|---|
| ElevenLabs voice (~$0.30/min × 2 min avg) | $0.60 |
| Twilio outbound (~$0.08/min × 2 min) | $0.16 |
| Claude API (~$0.15 per call script + enrichment) | $0.30 |
| Skip tracing (~$0.50/lead, batch pricing) | $0.50 |
| Twilio SMS confirmation | $0.01 |
| **Total per lead** | **~$1.57** |
| **Book rate: 20%** | **$7.85 per booked estimate** |

For a $28K average project x 35% close rate = $9,800 expected revenue per booked estimate. **ROI: 1,248x.**

## What you need to set this up

1. **ElevenLabs account** — $5/mo starter, get a voice clone
2. **Twilio account** — pay-as-you-go, ~$20/mo for 200 calls + SMS
3. **Skip tracing account** — BatchLeads or REISkip, $50/mo for 100 lookups
4. **Claude API key** — $20/mo for ~1000 calls
5. **Google Calendar API** — free
6. **Local building permits portal access** — usually free public API

## Total cost

~$100/mo for 200 leads/mo. Book 40 estimates. Close 14 at $28K = **$392K/mo revenue** at $100/mo cost.

## What's NOT included in this free version

This is a working starter. The full Master Systems version includes:
- **Meta Ads integration** (also feed leads from your paid ads into the same calendar)
- **Chloe AI inbound caller** (catch missed calls with the same AI voice)
- **GoHighLevel pipeline sync** (every estimate auto-routes through your CRM)
- **Multi-trade specialization** (separate voice prompts for roofing vs remodeling)
- **Lead scoring** (AI ranks leads by likely-to-close based on permit value + project type)
- **Retargeting** (drop the homeowner's email into a Meta retargeting audience)

That version is part of the Master Systems $5K/mo install.
