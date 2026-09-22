# Contractor Auto-Booker

> A free Claude Code agent that books contractor estimates in under 60 seconds.

**Built for:** Master Systems / The Trade Standard — Tyler Bogart
**License:** MIT (free, fork it)
**Status:** Working starter. Production deploy requires ElevenLabs + Twilio setup (~$100/mo).

---

## What this does

A 4-step AI pipeline that books contractor estimates on autopilot:

1. **Scrape local building permits** — finds homeowners who just pulled permits for your trades
2. **Enrich contacts** — looks up phone numbers via skip tracing + public records
3. **Call with human voice** — ElevenLabs voice + proven script
4. **Book on calendar** — Google Calendar event + Twilio SMS confirmation

**Time per lead:** ~58 seconds (scraping + call + book)
**Book rate:** 20% (industry standard for outbound)
**Close rate:** 35% (Denver contractor average)
**Avg project:** $28,000

### ROI math

For **100 leads/month**:
- Booked: 20
- Closed: 7
- Revenue: **$196,000**
- Cost: **$240**
- **ROI: 816x**

---

## Quick start

### 1. Install
```bash
git clone https://github.com/Zeus1111/contractor-auto-booker.git
cd contractor-auto-booker
pip install -r requirements.txt
```

### 2. Set up accounts
- **ElevenLabs** — $5/mo Starter, clone a voice (or use a stock voice)
- **Twilio** — pay-as-you-go, ~$20/mo for 200 calls + SMS
- **Skip tracing** — BatchLeads or REISkip, ~$50/mo
- **Claude API** — $20/mo for ~1000 calls

### 3. Set environment variables
```bash
export ELEVENLABS_API_KEY=***
export ELEVENLABS_VOICE_ID=your_voice_id
export TWILIO_ACCOUNT_SID=your_sid
export TWILIO_AUTH_TOKEN=***
export TWILIO_FROM_NUMBER=+1XXXXXXXXXX
```

### 4. Run the demo
```bash
python3 contractor_auto_booker.py
```

### 5. Run in Claude Code
Copy `prompt.md` into Claude Code, replace the placeholder values in `AGENT_CONFIG`, and run.

---

## File structure

```
contractor-auto-booker/
├── README.md                   # this file
├── prompt.md                   # Claude Code agent prompt (copy-paste)
├── contractor_auto_booker.py   # main pipeline + ROI calculator
├── voice_integration.py        # ElevenLabs + Twilio integration
├── requirements.txt            # Python deps
├── .gitignore
├── LICENSE                     # MIT
└── examples/
    └── sample_leads.csv        # example lead input
```

---

## How to make it actually call people

ElevenLabs doesn't natively place phone calls. To bridge it to a phone line, you need one of:

### Option A: ElevenLabs Agents Platform (easiest, paid add-on)
- Built-in Twilio integration
- Configure in ElevenLabs dashboard
- $0.10/min + Twilio cost

### Option B: Vapi.ai (recommended, $0.10/min)
- Native ElevenLabs + Twilio + function calling
- Webhook support for booking
- Great docs and reliability
- Used by 1,000+ AI agencies

### Option C: Bland.ai (enterprise, $0.09/min)
- Same as Vapi but more enterprise
- Better for high volume

### Option D: LiveKit + Twilio SIP trunk (DIY, free)
- Most flexible, most work
- See angus.sewell's Instagram reel for the pattern

**My recommendation:** Vapi.ai. 15 min to set up, $0.10/min, handles everything.

---

## Customization

### Change the call script
Edit `CALL_SCRIPT` in `voice_integration.py` to match your voice and offer.

### Add more trades
Add to `AGENT_CONFIG["trades"]` in `prompt.md`:
```python
"trades": ["roofing", "remodeling", "bathroom", "kitchen", "deck", "hvac", "plumbing"]
```

### Change the geographic area
Edit `AGENT_CONFIG["zip_codes"]` and `AGENT_CONFIG["city"]`.

### A/B test the script
Save variations to `scripts/v1.py`, `scripts/v2.py`, etc. and rotate them.

---

## What's NOT included in this free version

This is a working starter. The full **Master Systems** version adds:

- **Meta Ads integration** (feed leads from paid ads into same calendar)
- **Chloe AI inbound caller** (catch missed calls with same AI voice)
- **GoHighLevel pipeline sync** (every estimate auto-routes through your CRM)
- **Multi-trade specialization** (separate voice prompts for roofing vs remodeling)
- **Lead scoring** (AI ranks leads by likely-to-close based on permit value)
- **Retargeting** (drop homeowner email into Meta retargeting audience)
- **DNC compliance + opt-out handling**
- **TCPA-compliant calling hours + time zone detection**

That version is part of the **Master Systems $5K/mo install**.

---

## Questions?

DM me on IG: `@tytheaiguy`
Or email: tyler@master-systems.com

Built by Tyler Bogart / Master Systems
Denver, CO
