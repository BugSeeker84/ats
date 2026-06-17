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

- PayPal: 70–80% keyword match with JD
    
- Slate Technology Inc: 70–80% keyword match with JD
    
- Intuit: 50–60% keyword match with JD
    

Rules:

- Prioritize JD-required tech stack
    
- Inject missing but relevant tools/skills where reasonable
    
- Do NOT change project names or core achievements
    
- Avoid generic phrasing
    

# ========================  
STEP 3 — EXPERIENCE REWRITE

For EACH company:

- Write 4–5 detailed sentences
    
- Each sentence must:
    
    - Be on its own line
        
    - Be 1–3 lines long
        
    - Include JD keywords naturally
        
    - Include quantifiable impact where possible

    - Add bold for keywords
        


# ========================  
STEP 4 — SKILLS SECTION



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

1. My LinkedIn profile / base resume
    
2. Job Description
    

Do NOT ask for confirmation. Generate directly.


-- Resume Skeleton
no need style but have external style library(style3.css)

<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resume - Weijing Lin | "Company name mentioned in JD"</title>
  <link rel="stylesheet" href="style3.css" />
</head>
<body>
<div class="container">
<header>
    <h1>Weijing Lin</h1>
    <div class="subtitle">Senior Software Engineer</div>
    <div class="contact">
        Los Angeles, CA | 657-582-3729 | jaylin.weijing@gmail.com | linkedin.com/in/weijingjaylin | github.com/dotku
    </div>
</header>
<section>
<h2>About Me</h2>
<!-- (3 sentences professionally with 9+ years experience)   -->
<p> e.x. , ...</p>
</section>
<section id="skills">
<h2>Technical Skills</h2>
<ul>
  <!-- give me comma-seperatable syntax - about 25 items-->
	  <li><span>Java</span></li>
	  <li><span>Python</span></li>
      <li><span>SQL</span></li>
      <li><span>AWS</span></li>
      <li><span>GCP</span></li>
  <!-- do not merge skills in <span></span>, only one skill must be in span-->

</ul>
</section>
<section>
<h2>Work Experience</h2>
<div class="job">
    <div class="job-header">
        <div>Senior Software Engineer</div>
        <div class="job-date">Nov 2024 – Present</div>
    </div>
    <div class="job-meta">PayPal</div>
    <ul>
      <!-- (must contain 7 list sentences, each li are at least 25 words, here must mention PayPal company project name(highlight))   -->
        <li>Led backend architecture for <strong>project name</strong>....</li>
        <li>Designed distributed Golang microservices on .....</li>
        <!-- .... -->
    </ul>
</div>
<div class="job">
    <div class="job-header">
        <div>Senior AI Engineer</div>
        <div class="job-date">Jan 2023 - Oct 2024</div>
    </div>
    <div class="job-meta">Intuit</div>
    <ul>
      <!-- (must contain 6 list sentences,  each li are at least 15 words, here must mention Sunscrapers technology project name(highlight))     -->
        <li>Developed cloud backend services <strong>project name</strong>.....</li>
        <li>Built distributed telemetry data pipelines....</li>
        <!-- ... -->
    </ul>
</div>
<div class="job">
    <div class="job-header">
        <div>Senior Software Engineer</div>
        <div class="job-date">Jan 2021 – Jan 2023</div>
    </div>
    <div class="job-meta">Slate Technologies Inc.</div>
    <ul>
      <!-- (must contain 4 list sentences,  each li are at least 15 words, here must mention Fujitsu technology project name(highlight))     -->
        <li>....<strong>project name</strong>.....</li>
        <li>Built distributed telemetry data pipelines....</li>
        <!-- ... -->
    </ul>
</div>
<div class="job">
    <div class="job-header">
        <div>Software Engineer</div>
        <div class="job-date">Jan 2019 – Jan 2021</div>
    </div>
    <div class="job-meta">Facebook / Meta</div>
    <ul>
      <!-- (must contain 4 list sentences,  each li are at least 15 words, here must mention Fujitsu technology project name(highlight))     -->
        <li>....<strong>project name</strong>.....</li>
        <li>Built distributed telemetry data pipelines....</li>
        <!-- ... -->
    </ul>
</div>
<div class="job">
    <div class="job-header">
        <div>Senior Software Engineer</div>
        <div class="job-date">Jan 2018 – Jan 2019</div>
    </div>
    <div class="job-meta">Huawei</div>
    <ul>
      <!-- (must contain 4 list sentences,  each li are at least 15 words, here must mention Fujitsu technology project name(highlight))     -->
        <li>....<strong>project name</strong>.....</li>
        <li>Built distributed telemetry data pipelines....</li>
        <!-- ... -->
    </ul>
</div>
<div class="job">
    <div class="job-header">
        <div>Frontend Developer</div>
        <div class="job-date">Jun 2013 – Jan 2018</div>
    </div>
    <div class="job-meta">BlueJay Mobile Health</div>
    <ul>
      <!-- (must contain 4 list sentences,  each li are at least 15 words, here must mention Fujitsu technology project name(highlight))     -->
        <li>....<strong>project name</strong>.....</li>
        <li>......</li>
        <!-- ... -->
    </ul>
</div>
</section>
<section>
<h2>Education</h2>
<p>
<strong>Bachelor's Degree in Computer Science</strong><br>
San Jose State University, 2007 – 2011
</p>
</section>
 <section id="certifications">
<h2>Certifications</h2>
<ul>
  <!-- Give me relevant 4~7 certifications in this visual way(year: randomly choose between 2020 - 2025)   -->
    <li>Azure Data Engineer Associate — Microsoft (2022)</li>
    <!-- .. -->
</ul>
Keep these projects.
<h2>Project</h2>
<section>
<ul>
<li>Adapted cutting-edge AI technologies including <b>MCP</b> and <b>A2A</b> from POC (Proof of Concept) to product, empowering 33,000 employees globally to adopt AI technologies and address their daily work across Engineering, HR, Marketing, Finance, Legal, Security, and other departments with a billions-dollar budget. (2024–2025)</li>
<li><b>Intuit GenStudio</b>: Led the development of an AI-powered platform as part of Intuit’s $10 billion AI transformation initiative, integrating GenAI/LLM technologies like OpenAI GPT, Meta LLAMA, Google Gemini, and Anthropic Claude. The platform supports 7,000+ employees with 50% activation and 20% daily usage. (2023–2024)</li>
<li><b>Meta AIM Data Integrity</b>: Led a team managing data integrity across multiple AI projects, collaborating with 300+ third-party labelers on command detection, hate speech detection, music copyrights, and voice transcription. Contributed to the prototyping of Facebook Portal (Meta Portal), which generated $280M in revenue. (2020)</li>
</ul>
</section>
</section>
</div>
</body>
</html>
 

Successful critieria : 
- Fix subtitle as Senior Full Stack / AI Engineer
- I am in Los Angeles, CA right now
- Do not change title during tailor
- I don't need HTML file itself, just only need HTML code as markdown style
- I prefer separated markdown for cover letter
- Add only San Jose State University as my study.
- Add bold for used languages, frameworks, tools in company section
- Add company name at title. : <title>Resume - Weijing Lin | "Company name mentioned in JD"</title>
- Do not add "—", long hyphoon.
- BlueJay Mobile should focus on frontend and junior-mid level.
- Do nothing until I share the job description


 I can input some question. give me concise answer.  
Just hold on this text!!