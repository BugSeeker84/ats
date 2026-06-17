---
# ── Structured fields (the MATCHER reads these) ──────────────────────────────
name: Full Name
current_company: Walmart            # current / most recent employer
location: Bentonville, AR (Remote)  # used for location matching
years_experience: 12
# The matcher weights INDUSTRY MATCH highest — list the real domains this dev has shipped in:
target_industries: [Retail, E-commerce, Supply Chain]
# Headline skills used for skill matching:
primary_skills: [Java, Spring Boot, Kafka, Microservices, AWS, Kubernetes]
# One line the matcher can use for quick context:
summary: Senior backend engineer specializing in high-throughput retail commerce platforms.
contact:
  email: name@example.com
  phone: "+1 555 000 0000"
  location: Bentonville, AR
  linkedin: https://linkedin.com/in/...
  github: https://github.com/...
---

<!--
Everything BELOW the frontmatter is the full source of truth the GENERATOR uses to
build the resume. Put the real, complete, truthful experience here. The generator
selects and emphasizes from this — it must not invent anything not written here.
-->

## Summary
2–3 sentences describing the developer.

## Experience

### Senior Software Engineer — Walmart  (2019 – Present)
- Bullet describing a real accomplishment, with metrics where possible.
- Another accomplishment.
- Tech used: ...

### Software Engineer — Previous Company  (2015 – 2019)
- ...

## Skills
- **Languages:** ...
- **Frameworks:** ...
- **Cloud / Infra:** ...
- **Data:** ...

## Education
- B.S. in Computer Science — University (Year)

## Certifications
- ...
