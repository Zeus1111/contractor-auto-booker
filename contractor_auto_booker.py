"""
Contractor Auto-Booker
=======================
A free Claude Code agent that books contractor estimates in under 60 seconds.

Pipeline:
  1. Scrape local building permits + Google reviews to find homeowners about to remodel
  2. Pull contact info + project type
  3. Dial them with ElevenLabs voice + custom script
  4. Book the estimate on Google Calendar + send confirmation text via Twilio

Built for: Tyler Bogart / Master Systems
License: MIT (free, fork it)
Repo: github.com/Zeus1111/contractor-auto-booker
"""

__version__ = "1.0.0"
__author__ = "Tyler Bogart <tyler@master-systems.com>"

# Pipeline stages
PIPELINE_STAGES = [
    "scrape_permits",
    "enrich_contacts",
    "generate_lead_list",
    "dial_with_voice",
    "book_calendar",
    "send_confirmation",
]

# Cost estimate per booked lead
COST_PER_BOOKED_ESTIMATE_USD = 2.40  # ElevenLabs voice + Twilio + Claude API

# Typical close rate
ESTIMATE_CLOSE_RATE = 0.35

# Average Denver contractor project
AVERAGE_PROJECT_USD = 28_000

# ROI math
def expected_revenue(leads_count: int) -> dict:
    """Calculate expected revenue from a batch of leads."""
    booked = int(leads_count * 0.20)  # 20% pick up + book
    closed = int(booked * ESTIMATE_CLOSE_RATE)
    revenue = closed * AVERAGE_PROJECT_USD
    cost = leads_count * COST_PER_BOOKED_ESTIMATE_USD
    return {
        "leads": leads_count,
        "booked_estimates": booked,
        "closed_deals": closed,
        "expected_revenue": revenue,
        "estimated_cost": cost,
        "roi_multiple": round(revenue / max(cost, 1), 1),
    }


if __name__ == "__main__":
    # Demo
    print("Contractor Auto-Booker v" + __version__)
    print("=" * 50)
    for batch in [50, 100, 500]:
        result = expected_revenue(batch)
        print(f"\n{batch} leads → {result['booked_estimates']} booked → {result['closed_deals']} closed → ${result['expected_revenue']:,} revenue")
        print(f"  Cost: ${result['estimated_cost']} | ROI: {result['roi_multiple']}x")
