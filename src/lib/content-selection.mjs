/** Stable rotation between Monday 00:00 UTC and Sunday 23:59 UTC. */
export function weeklySelection(items, now = new Date(), count = 4) {
  if (!items.length) return [];
  const week = Math.floor((now.getTime() - Date.UTC(1970, 0, 5)) / 604800000);
  const offset = ((week % items.length) + items.length) % items.length;
  return Array.from({ length: Math.min(count, items.length) }, (_, i) => items[(offset + i) % items.length]);
}

export function latestInspirations(items, count = items.length) {
  return [...items].sort((a, b) => (Date.parse(b.publishedAt || '') || 0) - (Date.parse(a.publishedAt || '') || 0)).slice(0, count);
}

export function quizSelections(rows, health = {}) {
  const unavailable = new Set(rows.filter(p => p.productStatus === 'unavailable').map(p => p.asin));
  const products = [...new Map(rows.filter(p => p.nom && /^[A-Z0-9]{10}$/.test(p.asin || '') && !unavailable.has(p.asin) && health[p.asin]?.status !== 'unavailable').map(p => [p.asin, p])).values()];
  const rank = (rules) => [...products].sort((a, b) => {
    const score = p => { const index = rules.findIndex(rule => rule.test(p.nom)); return index < 0 ? rules.length : index; };
    return score(a) - score(b);
  }).slice(0, 3);
  return {
    gaming: rank([/casque|headset|headphone/i, /clavier|keyboard|souris|mouse/i, /micro|mic\b/i]),
    chatting: rank([/webcam|camera|caméra|brio/i, /lumi[eè]re|light|led/i, /micro|mic\b/i]),
    podcast: rank([/micro|mic\b/i, /bras|arm|interface/i, /casque|headset|headphone/i]),
  };
}

/** Only selects real collection entries; never constructs an assumed seasonal URL. */
export function seasonalGuide(guides, now = new Date()) {
  const month = now.getUTCMonth();
  const pattern = month === 9 ? /halloween/i : month >= 10 ? /cadeau|no[eë]l|christmas/i : month >= 5 && month <= 7 ? /[eé]t[eé]|summer|chaleur/i : /cozy|pastel|minimal/i;
  return [...guides].filter(g => pattern.test(`${g.id} ${g.data.title}`)).sort((a, b) => b.data.publishDate.getTime() - a.data.publishDate.getTime())[0] || null;
}

/** A curated monthly palette; no generative dependency or recurring API cost. */
export function monthlyPanel(now = new Date()) {
  const palettes = [
    ['Winter Cloud','#dbeafe','#e0e7ff','#1e3a8a'], ['Rose Velvet','#ffe4e6','#fecdd3','#881337'],
    ['Spring Bloom','#fce7f3','#dcfce7','#365314'], ['Peach Garden','#ffedd5','#fef3c7','#7c2d12'],
    ['Lilac Dream','#ede9fe','#fae8ff','#581c87'], ['Summer Sky','#cffafe','#dbeafe','#164e63'],
    ['Coral Sunset','#ffe4e6','#ffedd5','#9a3412'], ['Mint Breeze','#ccfbf1','#ecfccb','#134e4a'],
    ['Autumn Latte','#fef3c7','#fed7aa','#78350f'], ['Spooky Pastel','#ffedd5','#e9d5ff','#581c87'],
    ['Cozy Cocoa','#f5e6d3','#e7d3c2','#57392d'], ['Frosted Berry','#fce7f3','#dbeafe','#831843'],
  ];
  const [label,c1,c2,fg] = palettes[now.getUTCMonth()];
  return {label,c1,c2,fg,bord:'#ffffff'};
}
