const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SESSION_FILE = path.join(__dirname, 'session', 'apiradar_session.json');
const DATA_DIR = path.join(__dirname, 'data');
const APIRADAR_URL = 'https://apiradar.live';

// Asegurar directorios existen
[SESSION_FILE, DATA_DIR].forEach(p => {
  const dir = path.dirname(p);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

async function login(headless = false) {
  const hasSession = fs.existsSync(SESSION_FILE);
  
  const browser = await chromium.launch({ 
    headless: hasSession && headless 
  });
  
  let context;
  if (hasSession) {
    console.log('🔑 Usando sesión guardada...');
    context = await browser.newContext({ 
      storageState: SESSION_FILE 
    });
  } else {
    console.log('🌐 No hay sesión. Abriendo navegador para login...');
    context = await browser.newContext();
    const page = await context.newPage();
    
    await page.goto(APIRADAR_URL);
    
    console.log('\n👉 Por favor:');
    console.log('   1. Haz clic en "Sign in with Google"');
    console.log('   2. Completa el login');
    console.log('   3. Espera a que cargue el dashboard');
    console.log('   4. Presiona ENTER aquí cuando estés logueado\n');
    
    await new Promise(resolve => {
      process.stdin.once('data', resolve);
    });
    
    // Guardar sesión
    await context.storageState({ path: SESSION_FILE });
    console.log(`✅ Sesión guardada`);
  }
  
  return { browser, context };
}

async function scrapeLeaks(page, limit = null) {
  console.log('📄 Navegando a leaks...');
  await page.goto(`${APIRADAR_URL}/leaks`, { waitUntil: 'networkidle' });
  
  // Esperar a que cargue el contenido
  await page.waitForTimeout(2000);
  
  console.log('🔍 Analizando estructura de la página...');
  
  // Primero, inspeccionar qué hay en la página
  const title = await page.title();
  console.log(`   Título: ${title}`);
  
  // Guardar HTML para análisis
  const html = await page.content();
  const debugFile = path.join(DATA_DIR, 'debug_page.html');
  fs.writeFileSync(debugFile, html);
  console.log(`   HTML guardado en: ${debugFile}`);
  
  // Intentar extraer leaks (selectores genéricos)
  const leaks = await page.evaluate(() => {
    const results = [];
    
    // Buscar elementos que parezcan leaks
    // Estos selectores son placeholders - se ajustarán tras ver el HTML real
    const rows = document.querySelectorAll('tr, [class*="leak"], [class*="row"], article, .card');
    
    rows.forEach((row, i) => {
      const text = row.innerText || '';
      if (text.length > 10 && text.length < 2000) {
        results.push({
          index: i,
          text: text.substring(0, 500),
          html: row.outerHTML.substring(0, 500)
        });
      }
    });
    
    return results.slice(0, 20); // Limitar para debug
  });
  
  console.log(`   Encontrados ${leaks.length} elementos candidatos`);
  
  return leaks;
}

async function main() {
  console.log('🚀 APIRadar Scraper\n');
  
  const { browser, context } = await login(false); // Primera vez sin headless
  const page = await context.newPage();
  
  try {
    const leaks = await scrapeLeaks(page);
    
    // Guardar resultados
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = path.join(DATA_DIR, `debug_${timestamp}.json`);
    fs.writeFileSync(outputFile, JSON.stringify(leaks, null, 2));
    console.log(`\n💾 Debug guardado en: ${outputFile}`);
    
    console.log('\n📋 Preview de elementos encontrados:');
    leaks.slice(0, 5).forEach((leak, i) => {
      console.log(`\n[${i + 1}] ${leak.text.substring(0, 200)}...`);
    });
    
  } catch (err) {
    console.error('❌ Error:', err.message);
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
