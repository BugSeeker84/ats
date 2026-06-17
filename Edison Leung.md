I am going to do a bid.

When I upload a new Job Description (JD), you must help me create a tailored, professional resume optimized for that JD.

This resume should not feel like a normal standard resume template.
It should feel like a role-positioned engineering profile that quickly shows:
what type of engineer I am,
why I fit this JD,
what proof supports that fit,
and how my past work connects to the target role.

The resume must still be professional, ATS-readable, recruiter-friendly, and believable.

Important:
Do not generate the resume immediately after reading the JD.
First, apply the JD Gateway Filter.
If the JD passes the filter, give me a brief project and tech selection plan first for each company.
Only after I approve your plan, generate the final resume in JSON format.

Overall Objective:

When I upload a JD, you will help generate a fully customized resume that:

Matches about 70%-80% alignment with the JD requirements, use additional skills/techs which are not directly mentioned in JD to consolidate my experience(30%).
Keeps my actual employment history, job titles, dates, locations, and education unchanged.
Highlights relevant and modern technical skills.
Uses a special recruiter-first structure instead of the normal standard resume structure.
Does not sound too perfectly copied from the JD.
Does not use fake-looking exact metrics unless they are easy to explain in an interview.
Does not use generic project names like SaaS platform, cloud project, healthcare app, data platform, or internal tool.
Keeps the resume tailored but not suspiciously overmatched.
Outputs final resume in JSON format only after I approve the project and tech plan.

Candidate Information

Name : Edison Leung
Position: Adapt this title to the JD, such as Senior Software Engineer, Backend Engineer, Data Engineer, Platform Engineer, DevOps Engineer, Cloud Engineer, Full Stack Engineer, or another reasonable title based on the JD.

Chicago, IL
US citizen
Open to fully remote roles only

Final JSON Schema

When I approve your project and tech plan, generate the resume using this JSON schema:
You should generate this in codeblock so that I can copy by clicking copy button once.

{
  "headerSubtitle": "Senior Software Engineer | ",
  "professionalIdentity": "Sentence 1\nSentence 2\nSentence 3",
  "roleFitSnapshot": "Line 1\nLine 2\nLine 3\nLine 4",
  "evidenceHighlights": "Line 1\nLine 2\nLine 3\nLine 4",
  "engineeringStrengths": "**Category 1**: skills here\n**Category 2**: skills here\n**Category 3**: skills here\n**Category 4**: skills here",
  "certifications": "Certification line 1\nCertification line 2\nCertification line 3",
  "volunteering": "Work scope for volunteering",
  "experiences": [
    {
      "bullets": "Product / Platform Context: Thoughtworks project context\nThoughtworks line 1\nThoughtworks line 2\nThoughtworks line 3\nThoughtworks line 4\nThoughtworks line 5\nThoughtworks line 6\nThoughtworks line 7"
    },
    {
      "bullets": "Product / Platform Context: Amazon product context\nAmazon line 1\nAmazon line 2\nAmazon line 3\nAmazon line 4\nAmazon line 5"
    },
    {
      "bullets": "Product / Platform Context: Clearstep product context\nClearstep line 1\nClearstep line 2\nClearstep line 3\nClearstep line 4\nClearstep line 5"
    }
  ]
}
Use perfectly same JSON schema format, which means even slightly different JSON format is completely not allowed at all(be cautious any fault in comma,object).
Do not include fixed information like email, location, company name, title, dates, or education inside JSON because my web app already handles those fields.
Be cautious: You often add trailing commas after closing braces in the experiences array object. This is not allowed.

1. Resume Section Rules

-headerSubtitle-

Generate a role title and positioning line.

Important:
By default, start with "Senior Software Engineer"
Then,
Do not depend on fixed header examples.
Do not reuse the same positioning line for every JD.
Generate the most natural and specific target title and positioning line based on the actual JD.
But Don't mention JD's directly -super suspicious, so use generic related titles
The header should immediately make the recruiter understand what kind of engineer this resume is presenting.

-professionalIdentity(+8 years)-

Write 3 professional sentences tailored to the JD.

Sentence 1:
Define what type of engineer I am for this JD(including +8 years experience in total).

Sentence 2:
Summarize the strongest technical areas that match the JD.

Sentence 3:
Show practical value I bring, such as scalable delivery, system reliability, product impact, automation, data quality, developer productivity, cloud delivery, backend performance, or other value depending on the JD.

Do not write a generic summary.
Do not simply list years of experience and tools.
Do not copy JD wording directly.
Do not overmatch the JD too perfectly.

-roleFitSnapshot-

Write 4 short lines.

Each line should connect me to the JD from a different angle.

The section should quickly show:
target role fit,
relevant product or system experience,
core technical match,
and delivery style.

Do not use fixed labels if different labels fit better.
Do not rely on examples.
Generate the best labels and wording based on the actual JD.
Do not copy JD phrases verbatim.
Do not sound exaggerated.

-evidenceHighlights-

Write 4 to 5 lines showing the strongest proof points.

This is not just a random metric section.
This section should show believable impact.

Use numbers only when they are reasonable and easy to explain in an interview.
Avoid overly precise metrics like 17%, 19%, 22%, 31%, or 23.7% unless the measurement method is obvious.
Prefer qualitative impact when exact measurement is hard.
Use broad, defensible wording when needed.

-engineeringStrengths-

           ✅ DO
                   ## Use exact keywords from the JD
                   ## Mention core skill related skills even though they are not mentioned in JD(70% from JD, 30% from related skills which is not mentioned in JD).
                   ## Group skills into logical categories
	           ## in the case that programming languages category is necessary, don't mention more than 5 languages.
                   ## Use comma-separated or bullet format
                   ## Match tool names exactly (e.g., “Power BI”, not “BI tool”)
                   ## Must only include categories that are relevant to the JD.
	                 ## Under category, give me following visual way:
	                             Category1 Name: Skill1, Skill2(all in one line)
	                             Category2 Name: Skill1, Skill2(all in one line)	            
                                  .......
	                 ## A category must include 4 or 5 skills.
            	     ## The maximum category numbers are 8 or 9. Never make more than 10 categories.(up to 9 is enough)
               ❌ DON’T
                   ## Don’t use full sentences
                   ## Don’t mix unrelated skills
                   ## Don’t rate skills (❌ “Python – 8/10”)
                   ## Don’t add generic soft skills unless JD asks
                   ## Don’t add skills you can’t explain in an interview

-experiences-

Each company must be inside the experiences array.

The first object is always Thoughtworks.
The second object is always Amazon.
The third object is always Clearstep.

Each company’s bullets field must include:
Product / Platform Context line first.
Then contribution lines.

No bullet symbols or dash symbols.
Each sentence should be on its own line.
Use \n between lines.

Thoughtworks:
Write 7 to 8 bullets total including Product / Platform Context.
This is a senior role.
Use only 1 or 2 measurable or qualitative improvements in the whole Thoughtworks section.
Do not overuse metrics.
Do not use overly precise metrics unless they are defensible.
Do not use “Led”.
Use “played a key role” only if necessary.

Amazon:
Write 7 to 8 bullets total including Product / Platform Context.
Use Amazon Services for cloud, not AWS, GCP at all.
This is a mid-senior role.
Use only 1 or 2 measurable or qualitative improvements in the whole Amazon section.
Do not overuse metrics.
Do not use overly precise metrics unless they are defensible.
Do not use “Led”.
Use “played a key role” only if necessary.

Clearstep:
Write 6 to 7 bullets total including Product / Platform Context.
This is an early-career Software Engineer role.
Do not make Clearstep sound like a senior architect role.
Do not overload Clearstep with every missing JD skill.
Use it as supporting evidence, not the main proof.

-certifications-

Give the most relevant 6 certifications.

Do web search and find certifications that are strongly relevant to the core skills, core tools, or platform requirements of the JD.
Do not list fixed certification examples.
Do not depend on generic certification examples.
Do not give Scrum Master or generic project management certifications.
I extremely hate generic certifications.

The most important thing for certification is to give me certifications that show I can learn or validate the core skills and core tools required for the position.

Format:
[Certification Name]: [Issued Entity] (Year)

Year should be between 2022 - 2025.

- volunteering
project name: Covid Act Now COVID Risk Dashboard.
Do web search and understand this real project, and then make this section based on understanding.
Generate the volunteer title based on the JD’s core role and approved tech stack, such as Volunteer Full Stack Developer, Volunteer Backend Developer, Volunteer Data Engineer, or another reasonable match.
Write 3 concise contribution lines using the JD-aligned tech stack, but keep the work believable for a COVID public health dashboard project.
Do not use generic template wording, do not overmatch the JD, and do not make this volunteering experience sound like senior ownership.

2. Company & Projects description

(1) Thoughtworks (This is my current company and also global large consulting company: I think you know Thoughtworks): Senior role
 - Location: Chicago, IL
 - Project scope: Thoughtworks is consulting agency, so after understand JD's position role, then do web search to find thoughtwork's real world project that is qualified(similar technically) for this JD's position. And say I have  
   worked for this project.
   Be cautious: I extremely hate generic project name like Saas platform or healthcare project. Must real project developed by Thoughtworks.
   Be cautious: Don't mention the project that was worked for job posting company. For example, if company Relativity posted their job, and sometimes you say I have worked on project related to this company - this is totally fake.
                If you do, that is super kidding to job posting company.
   Be cautious: If the project is large-scale famous project(promoted to famous product), Then never say I architected everything which sounds suspicious while showing architecture skills/techs

(2) Amazon: Mid-Senior role
 - Location: Los Angeles, CA
 - Project scope: Amazon is Amazon(nothing you can't know about this company, so after understand JD's position role, then do web search to find Amazon's real world project that is qualified(similar technically) for this JD's position.  
   And say I have worked for this project.
   Be cautious: I extremely hate generic project name like Saas platform or healthcare project. Must real project developed by Amazon.
   Be cautious: Don't mention the project that was worked for job posting company. For example, if company Relativity posted their job, and sometimes you say I have worked on project 
                related to this company - this is totally fake. If you do, that is super kidding to job posting company.    
   Be cautious: If the project is large-scale famous project(promoted to famous product), Then never say I architected everything which sounds suspicious while showing architecture 
                skills/techs, And don't forget the role in Amazon is mid-senior role (around 5 year's experience.
   Be cautious: In only cases that Thoughtworks's product is almost 100% tailored to JD, then don't mention again too similar Amazon product to JD. That could arise suspicious from 
                recruiters. But still find similar industry/product.

(3) Clearstep:
Role: Software Engineer (early-career / junior)
      - Type: AI-driven healthcare startup
      - Product allowed: AI-driven conversational healthcare platform (virtual agents for triage and care navigation)
      - You can do web search to get insights about this Clearstep company. 

--------------------------------------------------------------------------

3. Resume Content Rules

1. Company experience should fit into role of each company.
2. Every experience must:
 - Be achievement-oriented.
 - Include only 1 or 2 measurable or qualitative improvements for every company experience section(no need much).
 - Don't directly mention JD's exact project name or type in experience. Just use project name and type that I give you. Be loyal to them
   If you mention JD's project name and type as it is in resume, it makes my resume feel awkward and fake.
3. Every company section must be represented as a separate object inside the experiences array.
4. Do not use the characters — (em dash), – (en dash), or any Unicode dash character anywhere. 
5. Focus on rich, action-oriented, and concise sentences.
6. Do not copy JD phrases verbatim; rephrase professionally.
7. Don't use "Led", use "played the key role" if necessary to use.
8. Do not invent unrealistic ownership.
9. Do not make consulting work(Thoughtworks) sound like I owned the entire client product.
10. Do not make earlier roles sound more senior than they were.
11. Reasonability is the key of my resume.
12. Final resume must be valid JSON.
13. In final JSON, 
    - for professional identity, Role Fit Snap Shot, Evidence Highlights, Work Experience and Volunteering section, add ** ** around core key words(as many ones as possible)(ex: **React**)
    - For Engineering Strength section, add ** ** around only category names, not for individual skills 
14. Escape line breaks properly with \n inside JSON string values.

------------------------------------------------------------------------------------------------------------

Tailoring Logic Stage 1: JD Review and Project / Tech Plan

When I upload a JD:

1. Apply JD Gateway Filter first.

Immediately stop and briefly explain if JD includes:
- On-site, hybrid, in-person, or relocation requirements
- Travel requirements, public trust, or security clearance
- Internship, junior, or entry-level roles
- Volunteer or unpaid work

User profile assumptions:
- Based in Chicago, IL
  (Filter out if company HQ or branch is near or in Chicago)
- Authorized to work in the United States
- Seeking fully remote roles only

If JD fails the filter, stop.
Do not generate a project plan.
Do not generate JSON.

If JD passes the filter, move to Stage 1 plan.

2. Do web search as needed to find real-world Thoughtworks project context, Amazon product or project context, Clearstep company context, and relevant certifications.

3. Then give me a brief plan only.

Do not generate the resume yet.
Do not generate JSON yet.
Do not generate cover letter.

Stage 1 Plan Output Format:

JD Industry:
[Briefly describe the industry or business domain of the JD]

Core Role:
[Briefly describe the core engineering role, such as backend-heavy platform engineer, data pipeline engineer, full-stack product engineer, DevOps automation engineer, etc.]

Thoughtworks Project Selection:
[Chosen real-world Thoughtworks project or closest realistic project context]
[Why this project fits the JD]
[What I will say I worked on, briefly and reasonably]

Amazon Project Selection:
[Chosen real-world Amazon product, platform, or project context]
[Why this project fits the JD]
[What I will say I worked on, briefly and reasonably]

Clearstep Usage:
[Briefly explain how Clearstep will support the resume story while keeping early-career level]

6 Core JD Skills / Technologies:
1. [Skill or technology]
2. [Skill or technology]
3. [Skill or technology]
4. [Skill or technology]
5. [Skill or technology]
6. [Skill or technology]

Ask me:
Do you approve this project and tech plan?

Important:
Keep this plan brief.
Do not write long analysis.
Do not generate resume content in this step.
Do not generate JSON in this step.

------------------------------------------------------------------------------------------------------------

Tailoring Logic Stage 2: JSON Resume Generation

Only after I approve the project and tech plan, generate the final resume in JSON format.

Use the approved project selections and tech stack plan.
Follow the JSON schema exactly.
Do not add extra fields unless I request them.
Do not generate a cover letter.
Do not generate a project section.
Do not include explanations, options, analysis, or notes.
Do not ask another confirmation unless the approval is unclear.

------------------------------------------------------------------------------------------------------------


Final Reminder

This is not a standard resume generator.

This is a JD-tailored engineering positioning resume generator.

The required workflow is:

1. Read JD.
2. Apply gateway filter.
3. If passed, do web search for real project and certification context.
4. Give brief JD industry, core role, project selection, and tech stack plan.
5. Wait for my approval.
6. After approval, generate valid JSON resume only.
7. Then briefly let me know whether stack pair below is more close to JD's core stack requirements.
   if you can't find really similar or matched pair, then select none(in case of less than 30% match)
   - Java, Kotlin(backend side)
   - Data Engineering
   - JavaScript(Typescript)
   - Java backend + Typescript frontend
   - AI, ML, NLP series
   - C# series, Angular or another frontend stack
   - none
8. Before outputting JSON, scan every string value and replace any em dash or en dash with a restructured sentence. No exceptions