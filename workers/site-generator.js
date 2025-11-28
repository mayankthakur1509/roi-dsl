// Cloudflare Worker: Automated Authority Site Generator
// Endpoint: /api/generate-site

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Route handlers
    if (url.pathname === '/api/generate-site' && request.method === 'POST') {
      return handleGenerateSite(request, env, corsHeaders);
    }
    
    if (url.pathname === '/api/check-status' && request.method === 'GET') {
      return handleCheckStatus(request, env, corsHeaders);
    }
    
    return new Response('Not Found', { status: 404 });
  }
};

async function handleGenerateSite(request, env, corsHeaders) {
  try {
    // Parse multipart form data
    const formData = await request.formData();
    const resumeFile = formData.get('resume');
    const specialty = formData.get('specialty');
    const yearsExperience = formData.get('yearsExperience');
    const majorAchievement = formData.get('majorAchievement');
    const photo = formData.get('credentialsPhoto'); // optional
    
    // Generate unique job ID
    const jobId = crypto.randomUUID();
    
    // Store job status
    await env.JOBS.put(jobId, JSON.stringify({
      status: 'processing',
      createdAt: Date.now()
    }), { expirationTtl: 3600 });
    
    // Process asynchronously (don't wait)
    env.waitUntil(processGeneration(jobId, resumeFile, {
      specialty,
      yearsExperience,
      majorAchievement,
      photo
    }, env));
    
    return new Response(JSON.stringify({
      jobId,
      status: 'processing',
      message: 'Site generation started. Check status in 30 seconds.'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Generate site error:', error);
    return new Response(JSON.stringify({
      error: error.message
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

async function processGeneration(jobId, resumeFile, userData, env) {
  try {
    // Step 1: Extract text from resume
    const resumeText = await extractTextFromResume(resumeFile);
    
    // Step 2: Call Claude API to generate .roi file
    const roiFile = await generateROIFromResume(resumeText, userData, env);
    
    // Step 3: Compile .roi to Cloudflare site
    const siteFiles = await compileROIToSite(roiFile);
    
    // Step 4: Deploy to Cloudflare Pages
    const siteUrl = await deployToPages(jobId, siteFiles, env);
    
    // Step 5: Update job status
    await env.JOBS.put(jobId, JSON.stringify({
      status: 'complete',
      siteUrl,
      completedAt: Date.now()
    }), { expirationTtl: 86400 }); // 24 hours
    
    // Step 6: Send notification (optional)
    // await sendPushNotification(jobId, siteUrl, env);
    
  } catch (error) {
    console.error('Processing error:', error);
    await env.JOBS.put(jobId, JSON.stringify({
      status: 'failed',
      error: error.message,
      failedAt: Date.now()
    }), { expirationTtl: 86400 });
  }
}

async function extractTextFromResume(file) {
  // Convert PDF/DOCX to text
  const arrayBuffer = await file.arrayBuffer();
  const uint8Array = new Uint8Array(arrayBuffer);
  
  // For PDF: use pdf.js or send to external service
  // For DOCX: use mammoth.js or send to external service
  // Simplified: assume text extraction service
  
  const response = await fetch('https://api.extracttext.com/v1/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/octet-stream' },
    body: uint8Array
  });
  
  const result = await response.json();
  return result.text;
}

async function generateROIFromResume(resumeText, userData, env) {
  // Call Claude API to generate .roi file
  const prompt = `You are an expert at creating ROI-DSL files for authority sites.

Given this resume and information, generate a complete .roi file in ROI-DSL format:

RESUME:
${resumeText}

USER INFO:
- Specialty: ${userData.specialty}
- Years Experience: ${userData.yearsExperience}
- Major Achievement: ${userData.majorAchievement}

Generate a complete .roi file following this structure:
- Extract PERSONA from their role/title
- Extract 4-6 GOALs from their achievements and value props
- Infer 4-6 METRICs based on their experience level
- Create 2-3 RMetrics (computed risk scores)
- Create 4-6 WHEN/THEN triggers for automation
- Add VARIANT Hero, Subhead, CTA, SecondaryCTA
- Extract 4-6 CREDENTIALs (years, projects, certifications, etc.)
- Create 3-6 CASE_STUDYs from their work history
- Define 4-6 SERVICEs based on their expertise
- Add 3-5 TRAINING modules they could offer
- Create 6-8 VROI_INPUT fields relevant to their industry
- Create 4-5 VROI_OUTPUT fields
- Add 6 STAT items for stats bar
- Extract contact info for CONTACT_NAME, CONTACT_EMAIL, CONTACT_LOCATION
- Add SEO_TITLE, SEO_DESCRIPTION, SEO_KEYWORDS
- Add 5-8 SK_TAGs for semantic search
- Set OUTPUT MintSite

CRITICAL: Output ONLY the .roi file content. No markdown, no explanations. Start with "# [Name] - Authority Site" and end with "OUTPUT MintSite".`;

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4000,
      messages: [{
        role: 'user',
        content: prompt
      }]
    })
  });
  
  const result = await response.json();
  return result.content[0].text;
}

async function compileROIToSite(roiContent) {
  // Call your ROI-DSL compiler service
  // Option 1: Python service endpoint
  const response = await fetch('https://your-compiler-service.com/compile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      roiContent,
      outputType: 'cloudflare'
    })
  });
  
  const files = await response.json();
  return files;
  
  // Option 2: Re-implement compiler in JavaScript (more complex)
  // Or use WASM-compiled Python
}

async function deployToPages(jobId, siteFiles, env) {
  // Deploy to Cloudflare Pages via API
  const projectName = `expert-${jobId.substring(0, 8)}`;
  
  // Upload files to Pages
  const response = await fetch(
    `https://api.cloudflare.com/client/v4/accounts/${env.CF_ACCOUNT_ID}/pages/projects/${projectName}/deployments`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.CF_API_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        files: siteFiles,
        production: true
      })
    }
  );
  
  const result = await response.json();
  const siteUrl = `https://${projectName}.pages.dev`;
  
  return siteUrl;
}

async function handleCheckStatus(request, env, corsHeaders) {
  const url = new URL(request.url);
  const jobId = url.searchParams.get('jobId');
  
  if (!jobId) {
    return new Response(JSON.stringify({ error: 'Missing jobId' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
  
  const jobData = await env.JOBS.get(jobId);
  
  if (!jobData) {
    return new Response(JSON.stringify({ error: 'Job not found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
  
  return new Response(jobData, {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}
