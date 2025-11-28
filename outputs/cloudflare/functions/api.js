// Cloudflare Worker API
// Handles vROI calculations and form submissions

export async function onRequestPost(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  
  // Route to appropriate handler
  if (url.pathname === '/api/calculate-vroi') {
    return handleVROI(request, env);
  }
  
  if (url.pathname === '/api/contact') {
    return handleContact(request, env);
  }
  
  return new Response('Not Found', { status: 404 });
}

async function handleVROI(request, env) {
  try {
    const data = await request.json();
    
    // Calculate vROI
    const result = calculateVROI(data);
    
    // Log to analytics (optional)
    // await env.ANALYTICS.writeDataPoint({
    //   blobs: ['vroi_calculation'],
    //   doubles: [result.delayCost],
    //   indexes: [data.StudyPhase]
    // });
    
    return new Response(JSON.stringify(result), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

function calculateVROI(data) {
  
  // Extract inputs
  const monthlyBurn = parseFloat(data.MonthlyBurn) || 2000000.0;
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
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });
  
  return {
    'Monthly Burn Rate': formatter.format(monthlyBurn),
    'Cost of Delay': formatter.format(delayCost),
    'Rework Cost Impact': formatter.format(reworkCost),
    'Total Financial Exposure': formatter.format(totalImpact),
    'Recommended Action': totalImpact > 1000000 ? 'Immediate Intervention Required' : 'Schedule Assessment'
  };

}

async function handleContact(request, env) {
  try {
    const data = await request.json();
    
    // Send to email service or CRM
    // await fetch('https://api.sendgrid.com/v3/mail/send', { ... });
    
    // Or store in KV
    // await env.LEADS.put(`lead_${Date.now()}`, JSON.stringify(data));
    
    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
