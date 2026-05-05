# AI Property Recommendation Platform Knowledge Base

## Enterprise Context

- Industry: real_estate
- Main business: The company helps users find suitable rental apartments and homes to buy in Tokyo and nearby areas. Staff members answer customer questions, compare neighborhoods, explain area characteristics, and recommend candidate areas and properties based on budget, commute, lifestyle, family structure, and preferences.
- AI objective: 
- Constraints: ['the system must not guarantee property price appreciation', 'the system must not make legal or financial decisions', 'final recommendation should be reviewed by a human real estate consultant', 'the system should explain reasoning and uncertainty clearly']

## Selected Opportunity

- Name: Neighborhood Scoring & Ranking Engine
- Target workflow: Area comparison and recommendation based on customer preferences (budget, commute, lifestyle, family structure).
- Capability: LLM-powered multi-criteria decision engine that scores and ranks neighborhoods using structured area profiles, commute data, school ratings, and safety metrics.
- Expected business value: Reduces consultant time per case by 40-50%, ensures consistent recommendations across staff, speeds up onboarding for new consultants.
- Key risk: Bias in scoring due to incomplete or outdated area data; overfitting to historical patterns.

## Operating Rules

- Always run deterministic local tools before DeepSeek drafting.
- Use actual area and property names from local tool results.
- Never use placeholder recommendations such as エリアA / エリアB / エリアC.
- Treat property suitability as decision support, not a final financial, legal, investment, or disaster-safety conclusion.
- Keep human_approval_required true and send_allowed false.

## Required Human Checks

- Hazard map and flood risk.
- Earthquake resilience and building management documents.
- School district, commute, station route, and listing freshness.
- Important matters explanation and licensed advisor review.
