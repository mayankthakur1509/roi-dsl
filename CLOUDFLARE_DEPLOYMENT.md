# 🚀 Cloudflare Pages + Workers Deployment Guide

## Overview

The ROI-DSL Compiler now generates **complete Cloudflare Pages sites** with:
- ✅ Static HTML (Tailwind CSS)
- ✅ Cloudflare Workers API (vROI calculations)
- ✅ Edge-deployed globally
- ✅ Custom domains ready
- ✅ Analytics integration

---

## 🎯 Quick Deploy

### Step 1: Compile ROI-DSL to Cloudflare Site

```bash
# Compile Rose Maloney's site
python3 roi_compile.py compile examples/rose_maloney_cro.roi --output cloudflare

# Output structure:
outputs/cloudflare/
├── index.html          # Main page
├── config.json         # Site configuration
├── _headers            # Security headers
├── _redirects          # URL redirects
└── functions/
    └── api.js          # Worker API endpoints
```

### Step 2: Deploy to Cloudflare Pages

```bash
cd outputs/cloudflare

# Option A: Use Wrangler CLI
npx wrangler pages deploy . --project-name=rose-maloney-cro

# Option B: Connect GitHub repo
# 1. Push to GitHub
# 2. Connect in Cloudflare Dashboard
# 3. Auto-deploys on push

# Option C: Drag & Drop
# 1. Go to dash.cloudflare.com
# 2. Pages → Create Project → Upload
# 3. Drag the outputs/cloudflare folder
```

---

## 📋 Prerequisites

### 1. Cloudflare Account
```bash
# Free tier includes:
- Unlimited requests
- Unlimited bandwidth
- 500 builds/month
- Custom domains
- SSL certificates
```

### 2. Wrangler CLI (Optional but Recommended)
```bash
npm install -g wrangler

# Login
wrangler login

# Verify
wrangler whoami
```

---

## 🏗️ Project Structure

### Generated Files

```
outputs/cloudflare/
│
├── index.html              # Main landing page
│   • Hero section
│   • Value propositions
│   • Case studies
│   • vROI calculator form
│   • Contact CTA
│
├── config.json             # Site configuration
│   • Persona data
│   • Goals & metrics
│   • Case studies
│   • SEO metadata
│
├── _headers                # Cloudflare headers config
│   • Security headers
│   • CORS settings
│   • Cache rules
│
├── _redirects              # URL redirects
│   • /home → /
│   • /roi → /#vroi-calculator
│
└── functions/
    └── api.js              # Cloudflare Worker
        • POST /api/calculate-vroi
        • POST /api/contact
```

---

## ⚙️ Configuration

### wrangler.toml

Create this file in `outputs/cloudflare/`:

```toml
name = "rose-maloney-cro"
compatibility_date = "2024-01-01"

pages_build_output_dir = "."

[site]
bucket = "."

# Environment variables
[vars]
SITE_NAME = "Rose Maloney - Clinical Operations"
CONTACT_EMAIL = "MaloneyRosemary@gmail.com"

# KV Namespaces (for storing leads)
# [[kv_namespaces]]
# binding = "LEADS"
# id = "your-kv-namespace-id"

# Analytics Engine (for tracking)
# [[analytics_engine_datasets]]
# binding = "ANALYTICS"
```

### Custom Domain Setup

```bash
# After deployment, add custom domain
wrangler pages project create rose-maloney-cro

# Add custom domain in dashboard:
# Pages → rose-maloney-cro → Custom domains → Add
# Example: rose.trial-rescue.com
```

---

## 🔧 API Endpoints

### POST /api/calculate-vroi

Calculate ROI based on trial parameters.

**Request:**
```json
{
  "StudyPhase": "III",
  "SiteCount": "40",
  "MonthlyBurn": "2000000",
  "VendorCount": "3",
  "ExpectedDBLock": "52",
  "ActualDelay": "8",
  "CRORework": "15",
  "SubmissionCritical": "Yes"
}
```

**Response:**
```json
{
  "Monthly Burn Rate": "$2,000,000",
  "Cost of Delay": "$3,694,000",
  "Rework Cost Impact": "$300,000",
  "Total Financial Exposure": "$3,994,000",
  "Recommended Action": "Immediate Intervention Required"
}
```

### POST /api/contact

Submit contact form.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@pharma.com",
  "company": "PharmaCo",
  "message": "Interested in CRO oversight"
}
```

---

## 📱 Phone App Integration

### Option 1: Direct Links

```kotlin
// In phone app - open MintSite
fun openExpertProfile(expertId: String) {
    val urls = mapOf(
        "rose_maloney" to "https://rose.trial-rescue.com",
        "john_smith" to "https://john.trial-rescue.com"
    )
    
    val url = urls[expertId] ?: return
    openBrowser(url)
}
```

### Option 2: Deep Links

```kotlin
// Custom URL scheme: mintsite://rose_maloney
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="mintsite" />
</intent-filter>
```

### Option 3: API Integration

```kotlin
// Fetch vROI calculation from Worker
suspend fun calculateVROI(params: VROIParams): VROIResult {
    val response = httpClient.post("https://rose.trial-rescue.com/api/calculate-vroi") {
        contentType(ContentType.Application.Json)
        setBody(params)
    }
    return response.body()
}
```

---

## 🎨 Customization

### Update Tailwind Config

Add `tailwind.config.js` to customize colors:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#1e40af',    // Blue-700
        secondary: '#64748b',  // Slate-500
        accent: '#f59e0b'      // Amber-500
      }
    }
  }
}
```

### Add Custom Fonts

```html
<!-- In index.html <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">

<style>
  body {
    font-family: 'Inter', sans-serif;
  }
</style>
```

---

## 📊 Analytics Integration

### Cloudflare Web Analytics

Already included in generated HTML:

```html
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' 
        data-cf-beacon='{"token": "YOUR_TOKEN"}'></script>
```

Get your token:
1. Cloudflare Dashboard → Web Analytics
2. Add Site → Get beacon token
3. Replace `YOUR_TOKEN` in index.html

### Custom Event Tracking

```javascript
// Track vROI calculations
fetch('/api/calculate-vroi', { ... })
  .then(result => {
    // Send to analytics
    if (window.cloudflareAnalytics) {
      cloudflareAnalytics.track('vroi_calculation', {
        phase: data.StudyPhase,
        impact: result['Total Financial Exposure']
      });
    }
  });
```

---

## 🔐 Security Features

### Included Headers

```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### Rate Limiting (Add to Worker)

```javascript
// In functions/api.js
const RATE_LIMIT = 100; // requests per hour

async function checkRateLimit(request, env) {
  const ip = request.headers.get('CF-Connecting-IP');
  const key = `rate_limit_${ip}`;
  
  const current = await env.KV.get(key) || 0;
  if (current >= RATE_LIMIT) {
    return new Response('Rate limit exceeded', { status: 429 });
  }
  
  await env.KV.put(key, current + 1, { expirationTtl: 3600 });
  return null;
}
```

---

## 🚀 Deployment Workflow

### Option A: CLI Deployment

```bash
# 1. Compile
python3 roi_compile.py compile examples/rose_maloney_cro.roi --output cloudflare

# 2. Deploy
cd outputs/cloudflare
wrangler pages deploy . --project-name=rose-maloney-cro

# 3. Get URL
# https://rose-maloney-cro.pages.dev
```

### Option B: GitHub Actions (CI/CD)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Compile ROI-DSL
        run: |
          python3 roi_compile.py compile examples/rose_maloney_cro.roi --output cloudflare
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: pages deploy outputs/cloudflare --project-name=rose-maloney-cro
```

---

## 📖 Examples

### Deploy Rose Maloney Site

```bash
# Compile
python3 roi_compile.py compile examples/rose_maloney_cro.roi --output cloudflare

# Deploy
cd outputs/cloudflare
wrangler pages deploy . --project-name=rose-maloney

# Result
# ✅ https://rose-maloney.pages.dev
# ✅ Custom domain: https://rose.trial-rescue.com
```

### Deploy Multiple Experts

```bash
# Compile each expert
python3 roi_compile.py compile examples/rose_maloney.roi --output cloudflare
mv outputs/cloudflare outputs/rose-maloney

python3 roi_compile.py compile examples/john_smith.roi --output cloudflare
mv outputs/cloudflare outputs/john-smith

# Deploy each
cd outputs/rose-maloney && wrangler pages deploy . --project-name=rose-maloney
cd ../john-smith && wrangler pages deploy . --project-name=john-smith
```

---

## 🎯 Next Steps

1. ✅ Compile your .roi file
2. ✅ Deploy to Cloudflare Pages
3. ✅ Add custom domain
4. ✅ Configure analytics
5. ✅ Integrate with phone app

---

## 🆘 Troubleshooting

### Build Fails
```bash
# Check wrangler version
wrangler --version

# Update wrangler
npm install -g wrangler@latest

# Check logs
wrangler pages deployment tail
```

### Worker Errors
```bash
# View logs
wrangler pages deployment logs

# Test locally
wrangler pages dev outputs/cloudflare
```

### CORS Issues
```javascript
// Add to functions/api.js
headers: {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
}
```

---

**Ready to deploy!** 🚀

Your ROI-DSL files now compile directly to production-ready Cloudflare Pages sites.
