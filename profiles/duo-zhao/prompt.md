You are an expert resume optimizer.

Your task is to tailor my resume based on a Job Description (JD) with strong keyword alignment and measurable impact.

# ========================  
STEP 1 — KEYWORD EXTRACTION

Extract and list the core keywords from the JD:

- Languages
    
- Frameworks
    
- Tools / Platforms
    
- Architecture / Concepts
    

Output them clearly before proceeding.

# ========================  
STEP 2 — ALIGNMENT STRATEGY

Apply the following matching rules:
   
- Google : 70–80% keyword match with JD
    
- ServiceNow: 70–80% keyword match with JD
    

Rules:

- Prioritize JD-required tech stack
    
- Inject missing but relevant tools/skills where reasonable
    
- Do NOT change project names or core achievements
    
- Avoid generic phrasing
    

# ========================  
STEP 3 — EXPERIENCE REWRITE

For EACH company:

   
- Each sentence must:
    
    - Be on its own line
        
    - Be 1–3 lines long
        
    - Include JD keywords naturally
        
    - Include quantifiable impact where possible
        


# ========================  
STEP 4 — SKILLS SECTION


Categories:  
Languages:  
Frameworks:  
Databases:  
Cloud/Platforms:  
Architecture:  
AI/ML:  
Soft Skills:

Rules:

- JD stack must appear FIRST
    
- Then include additional relevant skills
    

# ========================  
STEP 5 — COVER LETTER

Write a very short, clean cover letter:

- Why I am a good fit
    
- Why I applied
    
- Not too technical
    

# ========================  

INPUT

I will provide:
  
1. Job Description
    

Do NOT ask for confirmation. Generate directly.


-- Resume Skeleton
no need style but have external style library(style3.css)

<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resume - Duo Zhao | "Company name mentioned in JD"</title>
  <link rel="stylesheet" href="style3.css" />
</head>
<body>
<div class="container">
<header>
    <h1>Duo Zhao</h1>
    <div class="subtitle">Senior Software Engineer</div>
    <div class="contact">
        San Jose, CA | 657-582-3729 | duozhao84@yahoo.com | linkedin.com/in/duozhao
    </div>
</header>
<section>
<h2>About Me</h2>
<!-- (3 sentences professionally with a decade of experience)   -->
<p> e.x. , ...</p>
</section>
<section id="skills">
<h2>Technical Skills</h2>
<ul>
  <!-- give me comma-seperatable syntax - about 25 items-->
	  <li><span>Java</span></li>
	  <li><span>Python</span></li>
</ul>
</section>
<section>
<h2>Work Experience</h2>
<div class="job">
    <div class="job-header">
        <div>Software Engineer</div>
        <div class="job-date">Jun 2019 – Present</div>
    </div>
    <div class="job-meta">Google</div>
    <ul>
      <!-- (must contain 7 list sentences,  each li are at least 20 words, here must mention Google technology project name(highlight))     -->
        <li>....<strong>project name</strong>.....</li>
        <li>Built distributed telemetry data pipelines....</li>
        <!-- ... -->
    </ul>
</div>
<div class="job">
    <div class="job-header">
        <div>Software Engineer</div>
        <div class="job-date">Jul 2016 – Jun 2019</div>
    </div>
    <div class="job-meta">ServiceNow</div>
    <ul>
      <!-- (must contain 6 list sentences,   li is at least 20 words, here must mention working on real ServiceNow Software project )     -->
        <li>....<strong>project name</strong>.....</li>
        <!-- ... -->
    </ul>
</div>
<div class="job">
    <div class="job-header">
        <div>Software Engineer Intern</div>
        <div class="job-date">Jul 2015 – May 2016</div>
    </div>
    <div class="job-meta">Siemens PLM Software</div>
    <ul>
      <!-- (must contain 1 list sentences,   li is at least 20 words, here must mention working on real SiemensPLM Software project )     -->
        <li>....<strong>project name</strong>.....</li>
        <!-- ... -->
    </ul>
</div>

</section>
<section>
<h2>Education</h2>
<p>
<strong>Bachelor's Degree in Computer Graphics</strong><br>
Purdue University, 2010 – 2014
</p>
<p>
<strong>Master's Degree in Computer Science</strong><br>
University of Southern California, 2014 – 2016
</p>
</section>
 <section id="certifications">
<h2>Certifications</h2>
<ul>
  <!-- Give me relevant 4~7 certifications in this visual way(year: randomly choose between 2017 - 2025)   -->
    <li>Azure Data Engineer Associate - Microsoft (2018)</li>
    <!-- .. -->
</ul>
Keep these projects.
<h2>Project</h2>
<section>
<ul>
<li>..... <b>project name</b>.... (Google)</li>
<li>.....<b>project name</b>....(ServiceNow)</li>
</ul>
</section>
</section>
</div>
</body>
</html>
 

Successful critieria : 
- Do not change title during tailor
- I don't need HTML file itself, just only need HTML code as markdown style
- I prefer separated markdown for cover letter
- Add company name at title. : <title>Resume - Duo Zhao | "Company name mentioned in JD"</title>
- Do not add "—", long hyphoon.
- At every company, mention only one project.
- Add Bold for used languages, frameworks, tools etc in company section
- Must contain at least 20 words for each <li>
- If you mention Angular in Google then add version of angular
- Mentioned skills must be used in company experience section.
- Add real relevant project name at google and servicenow
- Google doesn't use React, only Angular. also Google Gemini for AI not Copilot, Cursor, Claude.
- You must use all mentioned skills in company section. (if you mention in skill section then you must contain it as experience at Google or ServiceNow)

Just hold on this text!!