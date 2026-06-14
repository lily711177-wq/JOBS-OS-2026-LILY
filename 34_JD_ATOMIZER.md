# JD ATOMIZER — Core Logic Engine
## Autonomous Job Description Analysis → 4-Module JSON Output
## Command: `ATOMIZE [job_title]` or `ATOMIZE [paste JD text]`

---

### PURPOSE
Strip corporate jargon from any job posting → output a normalized JSON execution roadmap. Works for any role, any company, any industry. Company-agnostic by design.

---

### MODULE 1: INTAKE & COMPLIANCE

**NOC 2021 TEER Mapping (Common Ops/Strategy Roles):**

| Role Type | NOC Code | TEER | PR Eligible |
|-----------|----------|------|-------------|
| Senior Manager — Financial/Communications/Business | 00012 | 0 | true |
| Corporate Sales Manager (incl. BD, Partnerships) | 60010 | 0 | true |
| Computer/Info Systems Manager | 20012 | 0 | true |
| Business Management Consultant | 10022 | 1 | true |
| Other Administrative Services Manager | 10019 | 1 | true |
| Sales/Account Manager | 60010 | 0 | true |
| Program Manager | 10019 | 1 | true |
| Purchasing Agent/Officer | 10012 | 2 | true |
| Operations Manager (specific role dependent) | 10022 / 00012 | 0-1 | true |

**Unknown Role Fallback:** If role type isn't in the table above, scan the JD for:
- "Director", "VP", "Head of", "Chief" → TEER 0 → 00012
- "Manager", "Lead" → TEER 1 → 10022
- "Coordinator", "Officer", "Analyst" → TEER 2 → 10019
- Education + experience requirements determine TEER floor

---

### MODULE 2: REAL WORK DECODE

**Role Type Detection Heuristics:**
- **People Manager** if JD mentions: "lead a team", "direct reports", "manage a team of", "build and mentor", "hiring", "team leadership"
- **Individual Contributor** if JD mentions: "manage projects", "stakeholder management", "cross-functional collaboration" (without team lead), "individual contributor"

**Location Model Detection:**
- If "remote", "work from home", "virtual" → Remote
- If "hybrid", "flexible", "3 days", "2 days", "mix of" → Hybrid (extract days)
- If "in-office", "on-site" (without flexibility mention) → In-Office

---

### MODULE 3: AGENTIC OUTREACH PIPELINE

**Resume Keyword Extraction:**
- Pull top 8-12 keywords from JD that represent core competencies
- Cross-reference against candidate corpus for highest-density placement

**Message Generation Rules:**
- **Day 0 (LinkedIn):** <20 words. State applied role + 1 achievement metric + signal
- **Day 7 (Email follow-up):** Polite re-engagement. Reference role. Add 1 insight relevant to the company's current challenge (researched).
- **Day 14 (Persistence):** Value-add only. No ask. Share a relevant insight/observation about their industry/market. Keep them warm.

---

### MODULE 4: FINOPS & LIQUIDITY ENGINE

**Tax Calculation Constants (2026, BC/Vancouver):**

| Component | Rate | Max Insurable |
|-----------|------|---------------|
| Federal Tax | 15% → 20.5% → 26% → 29% → 33% (brackets) | Unlimited |
| BC Provincial Tax | 5.06% → 7.7% → 10.5% → 12.29% → 14.7% → 16.8% → 20.5% (brackets) | Unlimited |
| CPP | 5.95% | YMPE ~$73,200 (est 2026) — basic exemption $3,500 |
| EI | 1.64% | $65,700 (est 2026) |

**Federal Tax Brackets (2026 est):**
- $0 – $58,500: 15%
- $58,501 – $117,000: 20.5%
- $117,001 – $181,000: 26%
- $181,001 – $258,000: 29%
- $258,001+: 33%

**BC Provincial Tax Brackets (2026 est):**
- $0 – $48,900: 5.06%
- $48,901 – $97,800: 7.7%
- $97,801 – $112,200: 10.5%
- $112,201 – $136,200: 12.29%
- $136,201 – $184,800: 14.7%
- $184,801 – $257,800: 16.8%
- $257,801+: 20.5%

**Bi-weekly Calculation:**
- Gross Bi-weekly = Annual Salary / 26
- Federal per pay = Annual Federal Tax / 26
- Provincial per pay = Annual Provincial Tax / 26
- CPP per pay = min(annual CPP max, (Annual Salary - $3,500) × 5.95%) / 26
- EI per pay = min(Annual Salary × 1.64%, $65,700 × 1.64%) / 26
- Net Bi-weekly = Gross — (Fed + Prov + CPP + EI)

**Paycheck Bump Forecast:**
- CPP max hit week = CPP max / (CPP per pay × 26) × 52... simplified: when cumulative CPP paid reaches ~$4,034, CPP deductions stop for the year
- EI max hit week = EI max / (EI per pay × 26) × 52... when cumulative EI paid reaches ~$1,077
- Typically: EI caps ~August, CPP caps ~September
- Paycheck bump = CPP per pay + EI per pay (added back to net)

**Liquidity Timeline:**
| Stage | Days | Cumulative |
|-------|------|------------|
| Application to Screen | 5-10 | 5-10 |
| Screen to Interview | 7-14 | 12-24 |
| Interview to Offer | 5-14 | 17-38 |
| Offer to Accept | 3-7 | 20-45 |
| Background Check | 5-10 | 25-55 |
| Start Date Buffer | 14-28 | 39-83 |
| First Paycheck Lag | 14-21 | 53-104 |

Default estimate for corporate: **75 days** from application to first direct deposit.

---

### JSON OUTPUT SCHEMA

```json
{
  "compliance": {
    "noc_code": "string",
    "teer_level": 0,
    "pr_eligible": true
  },
  "work_decode": {
    "simplest_english_summary": "string",
    "role_type": "Individual Contributor" | "People Manager",
    "location_model": "string"
  },
  "outreach_assets": {
    "tailoring_keywords": ["string"],
    "linkedin_initial": "string",
    "follow_up_day7": "string",
    "follow_up_day14": "string"
  },
  "finops": {
    "gross_biweekly": 0,
    "estimated_net_biweekly": 0,
    "paycheck_bump_forecast": "string",
    "liquidity_timeline_days": 0
  }
}
```

---

### USAGE

To atomize any JD:
1. Copy the full job description text
2. Run `ATOMIZE [job_title]` and paste the JD
3. Or paste JD text directly after `ATOMIZE`
4. Output will be clean JSON only (no conversational text)

---

### DEMONSTRATION: Amazon BD Manager Consumer Electronics

See `34_JD_ATOMIZER_RUN.md` for the live output on this JD.
