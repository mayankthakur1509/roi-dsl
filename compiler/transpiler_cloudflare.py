"""
Cloudflare Pages Transpiler
Generates static HTML/React sites deployable to Cloudflare Pages
"""

import json
from typing import Dict, Any


class CloudflarePagesTranspiler:
    """Transpiles ROI-DSL to Cloudflare Pages static site"""
    
    def compile(self, ast) -> Dict[str, str]:
        """
        Generate complete static site files
        Returns dict of {filename: content}
        """
        
        files = {}
        
        # 1. Generate index.html
        files['index.html'] = self._generate_html(ast)
        
        # 2. Generate _headers (Cloudflare config)
        files['_headers'] = self._generate_headers()
        
        # 3. Generate _redirects
        files['_redirects'] = self._generate_redirects()
        
        # 4. Generate site config JSON
        files['config.json'] = self._generate_config(ast)
        
        # 5. Generate functions/api.js (Worker)
        files['functions/api.js'] = self._generate_worker_api(ast)
        
        return files
    
    def _generate_html(self, ast) -> str:
        """Generate complete HTML page"""
        
        # Extract data
        persona = ast.persona.value if ast.persona else "Expert"
        hero_headline = next((v.value for v in ast.variants if v.type == "Hero"), "Transform Your Business")
        hero_subhead = next((v.value for v in ast.variants if v.type == "Subhead"), ast.goals[0].value if ast.goals else "")
        cta_primary = next((v.value for v in ast.variants if v.type == "CTA"), "Get Started")
        cta_secondary = next((v.value for v in ast.variants if v.type == "SecondaryCTA"), "Learn More")
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{ast.seo.get('TITLE', f'{persona} - Professional Services')}</title>
  <meta name="description" content="{ast.seo.get('DESCRIPTION', '')}"/>
  <meta name="keywords" content="{ast.seo.get('KEYWORDS', '')}"/>
  
  <!-- Cloudflare Web Analytics -->
  <script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "YOUR_TOKEN"}}'></script>
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    // Load site config
    let siteConfig = null;
    fetch('/config.json')
      .then(r => r.json())
      .then(config => {{
        siteConfig = config;
        console.log('Site config loaded:', config);
      }});
  </script>
</head>

<body class="bg-white text-gray-900">

<!-- HERO -->
<section id="hero" class="pt-20 pb-24 px-6 md:px-16 lg:px-32 bg-gradient-to-br from-blue-50 to-white">
  <div class="max-w-4xl mx-auto text-center">
    <h1 class="text-4xl md:text-6xl font-extrabold leading-tight">
      {hero_headline}
    </h1>
    
    <p class="mt-6 text-lg md:text-xl text-gray-700 leading-relaxed">
      {hero_subhead}
    </p>
    
    <div class="mt-8 flex flex-col md:flex-row gap-4 justify-center">
      <a href="#vroi-calculator"
         class="inline-block bg-blue-700 text-white px-8 py-4 rounded-md text-lg font-semibold hover:bg-blue-800 transition">
        {cta_primary} →
      </a>
      <a href="#services"
         class="inline-block bg-white text-blue-700 border-2 border-blue-700 px-8 py-4 rounded-md text-lg font-semibold hover:bg-blue-50 transition">
        {cta_secondary}
      </a>
    </div>
"""

        # Add credentials/stats
        if ast.credentials:
            html += f"""
    <div class="mt-12 grid grid-cols-2 md:grid-cols-{min(len(ast.credentials), 4)} gap-6 text-center">
"""
            for key, value in ast.credentials.items():
                html += f"""      <div class="text-gray-700">
        <div class="text-2xl font-bold text-blue-700">{value.split()[0]}</div>
        <div class="text-sm mt-1">{' '.join(value.split()[1:])}</div>
      </div>
"""
            html += "    </div>\n"
        
        html += """  </div>
</section>

"""

        # Stats Bar
        if ast.stats:
            html += """<!-- STATS BAR -->
<section id="stats" class="py-10 bg-gray-50 px-6 md:px-16 lg:px-32">
  <div class="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-6 gap-6 text-center text-gray-700">
"""
            for key, value in ast.stats.items():
                html += f"""    <div>
      <strong class="text-xl text-blue-700">{value.split()[0]}</strong><br>
      <span class="text-sm">{' '.join(value.split()[1:])}</span>
    </div>
"""
            html += """  </div>
</section>

"""

        # Value Propositions
        if ast.goals:
            html += """<!-- VALUE PROPOSITIONS -->
<section id="services" class="py-20 px-6 md:px-16 lg:px-32">
  <div class="max-w-5xl mx-auto">
    <h2 class="text-3xl md:text-4xl font-bold text-center mb-12">How We Help</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
"""
            for goal in ast.goals:
                # Extract dollar amounts for highlighting
                has_value = '$' in goal.value or '%' in goal.value
                icon = self._infer_icon(goal.value)
                
                html += f"""      <div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition">
        <div class="text-4xl mb-4">{icon}</div>
        <h3 class="text-xl font-semibold mb-3">{self._format_title(goal.name)}</h3>
        <p class="text-gray-700">{goal.value}</p>
        {'<p class="mt-3 text-blue-700 font-semibold">Quantified Value</p>' if has_value else ''}
      </div>
"""
            
            html += """    </div>
  </div>
</section>

"""

        # Case Studies
        if ast.case_studies:
            html += """<!-- CASE STUDIES -->
<section id="case-studies" class="py-20 bg-gray-50 px-6 md:px-16 lg:px-32">
  <div class="max-w-5xl mx-auto">
    <h2 class="text-3xl md:text-4xl font-bold text-center mb-12">Success Stories</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
"""
            for key, description in ast.case_studies.items():
                # Parse case study format
                parts = description.split('.')
                title = parts[0] if parts else description
                details = '. '.join(parts[1:]) if len(parts) > 1 else ""
                
                html += f"""      <div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition">
        <h3 class="text-lg font-semibold mb-3 text-blue-700">{self._format_title(key)}</h3>
        <p class="text-gray-700 mb-3">{title}</p>
        {f'<p class="text-sm text-gray-600">{details}</p>' if details else ''}
      </div>
"""
            
            html += """    </div>
  </div>
</section>

"""

        # vROI Calculator
        if ast.vroi_inputs:
            html += """<!-- vROI CALCULATOR -->
<section id="vroi-calculator" class="py-20 px-6 md:px-16 lg:px-32">
  <div class="max-w-4xl mx-auto">
    <h2 class="text-3xl md:text-4xl font-bold text-center mb-4">Calculate Your ROI</h2>
    <p class="text-center text-gray-600 mb-8">Get your personalized assessment in 60 seconds</p>
    
    <form id="vroi-form" class="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
"""
            
            for key, label in ast.vroi_inputs.items():
                html += f"""        <div>
          <label class="block text-sm font-semibold mb-2 text-gray-700">{label}</label>
          <input 
            type="text" 
            name="{key}"
            class="w-full border border-gray-300 rounded-md px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="{label}"
          />
        </div>
"""
            
            html += """      </div>
      
      <button 
        type="submit"
        class="mt-8 w-full bg-blue-700 text-white py-4 rounded-md text-lg font-bold hover:bg-blue-800 transition">
        Calculate My ROI →
      </button>
      
      <div id="vroi-result" class="mt-6 hidden">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 class="text-xl font-bold mb-4 text-blue-900">Your ROI Analysis</h3>
          <div id="vroi-output" class="space-y-3"></div>
        </div>
      </div>
    </form>
  </div>
</section>

<script>
// vROI Form Handler
document.getElementById('vroi-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);
  
  try {
    const response = await fetch('/api/calculate-vroi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    // Display results
    const outputDiv = document.getElementById('vroi-output');
    outputDiv.innerHTML = Object.entries(result)
      .map(([key, value]) => `
        <div class="flex justify-between items-center">
          <span class="font-semibold">${key}:</span>
          <span class="text-blue-700 font-bold">${value}</span>
        </div>
      `).join('');
    
    document.getElementById('vroi-result').classList.remove('hidden');
    document.getElementById('vroi-result').scrollIntoView({ behavior: 'smooth' });
  } catch (error) {
    alert('Error calculating ROI. Please try again.');
    console.error(error);
  }
});
</script>

"""

        # Contact CTA
        contact_email = ast.contact.get('EMAIL', 'contact@example.com')
        contact_name = ast.contact.get('NAME', 'Contact Us')
        
        html += f"""<!-- CONTACT CTA -->
<section id="contact" class="py-20 bg-gradient-to-br from-blue-700 to-blue-900 text-white px-6 md:px-16 lg:px-32">
  <div class="max-w-4xl mx-auto text-center">
    <h2 class="text-3xl md:text-4xl font-bold mb-6">Ready to Get Started?</h2>
    <p class="text-xl mb-8 text-blue-100">Let's discuss how we can help you achieve your goals.</p>
    
    <a href="mailto:{contact_email}" 
       class="inline-block bg-white text-blue-700 px-8 py-4 rounded-md text-lg font-semibold hover:bg-blue-50 transition">
      Contact {contact_name} →
    </a>
  </div>
</section>

<!-- FOOTER -->
<footer class="py-8 bg-gray-900 text-gray-400 text-center">
  <p>&copy; 2025 {contact_name}. All rights reserved.</p>
  <p class="mt-2 text-sm">Powered by HyperAI Marketing • Built with ROI-DSL</p>
</footer>

</body>
</html>"""
        
        return html
    
    def _generate_headers(self) -> str:
        """Generate Cloudflare Pages _headers file"""
        return """/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  
/config.json
  Cache-Control: public, max-age=300
  Content-Type: application/json

/functions/*
  Cache-Control: no-cache
"""
    
    def _generate_redirects(self) -> str:
        """Generate Cloudflare Pages _redirects file"""
        return """# Redirect rules
/home /
/contact /#contact
/services /#services
/roi /#vroi-calculator
"""
    
    def _generate_config(self, ast) -> str:
        """Generate site configuration JSON"""
        from compiler.transpiler_mintsite import MintSiteTranspiler
        transpiler = MintSiteTranspiler()
        return transpiler.compile(ast)
    
    def _generate_worker_api(self, ast) -> str:
        """Generate Cloudflare Worker for API endpoints"""
        
        # Build vROI calculation logic
        vroi_logic = self._generate_vroi_logic(ast)
        
        worker = f"""// Cloudflare Worker API
// Handles vROI calculations and form submissions

export async function onRequestPost(context) {{
  const {{ request, env }} = context;
  const url = new URL(request.url);
  
  // Route to appropriate handler
  if (url.pathname === '/api/calculate-vroi') {{
    return handleVROI(request, env);
  }}
  
  if (url.pathname === '/api/contact') {{
    return handleContact(request, env);
  }}
  
  return new Response('Not Found', {{ status: 404 }});
}}

async function handleVROI(request, env) {{
  try {{
    const data = await request.json();
    
    // Calculate vROI
    const result = calculateVROI(data);
    
    // Log to analytics (optional)
    // await env.ANALYTICS.writeDataPoint({{
    //   blobs: ['vroi_calculation'],
    //   doubles: [result.delayCost],
    //   indexes: [data.StudyPhase]
    // }});
    
    return new Response(JSON.stringify(result), {{
      headers: {{
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }}
    }});
  }} catch (error) {{
    return new Response(JSON.stringify({{ error: error.message }}), {{
      status: 400,
      headers: {{ 'Content-Type': 'application/json' }}
    }});
  }}
}}

function calculateVROI(data) {{
  {vroi_logic}
}}

async function handleContact(request, env) {{
  try {{
    const data = await request.json();
    
    // Send to email service or CRM
    // await fetch('https://api.sendgrid.com/v3/mail/send', {{ ... }});
    
    // Or store in KV
    // await env.LEADS.put(`lead_${{Date.now()}}`, JSON.stringify(data));
    
    return new Response(JSON.stringify({{ success: true }}), {{
      headers: {{ 'Content-Type': 'application/json' }}
    }});
  }} catch (error) {{
    return new Response(JSON.stringify({{ error: error.message }}), {{
      status: 400,
      headers: {{ 'Content-Type': 'application/json' }}
    }});
  }}
}}
"""
        return worker
    
    def _generate_vroi_logic(self, ast) -> str:
        """Generate vROI calculation JavaScript"""
        
        # Extract dollar values from goals
        monthly_burn = 2000000  # Default $2M
        for goal in ast.goals:
            if '$' in goal.value and 'M' in goal.value:
                # Extract value like "$2M"
                import re
                match = re.search(r'\$(\d+\.?\d*)M', goal.value)
                if match:
                    monthly_burn = float(match.group(1)) * 1000000
                    break
        
        return f"""
  // Extract inputs
  const monthlyBurn = parseFloat(data.MonthlyBurn) || {monthly_burn};
  const delayWeeks = parseFloat(data.ActualDelay) || 0;
  const reworkPercent = parseFloat(data.CRORework) || 0;
  
  // Calculate delay cost
  const weeksPerMonth = 4.33;
  const delayCost = (monthlyBurn / weeksPerMonth) * delayWeeks;
  
  // Calculate rework cost
  const reworkCost = monthlyBurn * (reworkPercent / 100);
  
  // Calculate total impact
  const totalImpact = delayCost + reworkCost;
  
  // Format currency
  const formatter = new Intl.NumberFormat('en-US', {{
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }});
  
  return {{
    'Monthly Burn Rate': formatter.format(monthlyBurn),
    'Cost of Delay': formatter.format(delayCost),
    'Rework Cost Impact': formatter.format(reworkCost),
    'Total Financial Exposure': formatter.format(totalImpact),
    'Recommended Action': totalImpact > 1000000 ? 'Immediate Intervention Required' : 'Schedule Assessment'
  }};
"""
    
    def _infer_icon(self, text: str) -> str:
        """Infer emoji icon from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['cost', 'save', 'burn', 'prevent']):
            return "💰"
        elif any(word in text_lower for word in ['time', 'timeline', 'delay', 'week']):
            return "⏱️"
        elif any(word in text_lower for word in ['risk', 'exposure', 'submission']):
            return "⚠️"
        elif any(word in text_lower for word in ['vendor', 'cro', 'alignment']):
            return "🤝"
        elif any(word in text_lower for word in ['deviation', 'reduce', 'quality']):
            return "📊"
        elif any(word in text_lower for word in ['control', 'governance', 'oversight']):
            return "🛡️"
        else:
            return "✓"
    
    def _format_title(self, name: str) -> str:
        """Format camelCase to Title Case"""
        import re
        spaced = re.sub(r'([A-Z])', r' \1', name)
        return spaced.strip()
