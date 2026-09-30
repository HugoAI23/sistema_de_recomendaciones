"""Módulo del Panel Web Interactivo (Dashboard) para Premier League Match Recommender (Fase 4).
Provee una interfaz moderna, reactiva y autónoma servida directamente por FastAPI.
"""

def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Premier League Match Recommender | Dashboard Fase 4</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            pl: {
              purple: '#37003c',
              dark: '#11071c',
              darker: '#0a0412',
              card: '#1b0e2d',
              cardborder: '#2f1a4d',
              green: '#00ff87',
              pink: '#ff2882',
              cyan: '#04f5ff',
              gold: '#ffb800'
            }
          }
        }
      }
    }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at top right, #240a38 0%, #0d0416 100%);
      min-height: 100vh;
    }
    .pl-gradient-text {
      background: linear-gradient(135deg, #00ff87 0%, #04f5ff 50%, #ff2882 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .badge-glow {
      box-shadow: 0 0 15px rgba(0, 255, 135, 0.35);
    }
    .card-hover {
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .card-hover:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(55, 0, 60, 0.6);
      border-color: rgba(0, 255, 135, 0.4);
    }
    input[type=range] {
      accent-color: #00ff87;
    }
  </style>
</head>
<body class="text-slate-100 antialiased selection:bg-pl-green selection:text-pl-dark">

  <!-- NAVBAR -->
  <header class="border-b border-pl-cardborder/80 bg-pl-dark/80 backdrop-blur-md sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-pl-pink via-pl-purple to-pl-green p-0.5 shadow-lg flex items-center justify-center">
          <div class="w-full h-full bg-pl-darker rounded-[10px] flex items-center justify-center text-2xl font-black text-pl-green">
            ⚽
          </div>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl sm:text-2xl font-black tracking-tight text-white">Premier League <span class="pl-gradient-text">Recommender</span></h1>
            <span class="text-[10px] font-bold uppercase tracking-wider bg-pl-green/10 text-pl-green border border-pl-green/30 px-2 py-0.5 rounded-full">Fase 4 REST</span>
          </div>
          <p class="text-xs text-slate-400">Motor Multimodal Híbrido: Analítica Numérica (xG, ICT) + PLN (VADER, TF-IDF)</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <span class="hidden md:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 text-emerald-400 border border-emerald-800">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Zero-Cost Mode Activo
        </span>
        <a href="/docs" target="_blank" class="px-3.5 py-1.5 text-xs font-medium bg-pl-card border border-pl-cardborder hover:border-pl-green/50 text-slate-200 rounded-lg transition-colors flex items-center gap-1.5">
          <span>Swagger UI</span>
          <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
        </a>
      </div>
    </div>
  </header>

  <!-- CONTENIDO PRINCIPAL -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

    <!-- PANEL DE CONTROL / FILTROS -->
    <section class="bg-pl-card/90 border border-pl-cardborder rounded-2xl p-6 shadow-2xl backdrop-blur-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 items-end">
        
        <!-- Jornada / Gameweek -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Jornada (Gameweek)</label>
          <div class="relative">
            <select id="gameweekSelect" class="w-full bg-pl-darker border border-pl-cardborder rounded-xl px-4 py-2.5 text-sm font-semibold text-white focus:outline-none focus:border-pl-green transition-colors appearance-none">
              <option value="8" selected>Jornada 8 (Temporada Actual 2026-2027)</option>
              <option value="6">Jornada 6 (Temporada Actual 2026-2027)</option>
              <option value="29">Jornada 29 (Jornada Histórica)</option>
              <option value="28">Jornada 28</option>
              <option value="30">Jornada 30</option>
              <option value="">Todas las jornadas</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
          </div>
        </div>

        <!-- Filtro por Fecha (Fase 4) -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Filtrar por Fecha</label>
          <div class="relative">
            <input type="date" id="dateInput" class="w-full bg-pl-darker border border-pl-cardborder rounded-xl px-4 py-2.5 text-sm font-medium text-white focus:outline-none focus:border-pl-green transition-colors" placeholder="YYYY-MM-DD">
          </div>
          <div class="flex flex-wrap gap-2 mt-2">
            <button type="button" onclick="setDateFilter('')" class="text-[11px] text-slate-400 hover:text-white underline">Todas</button>
            <button type="button" onclick="setDateFilter('2026-10-24')" class="text-[11px] text-pl-pink hover:underline font-bold">24 Oct (CHE vs TOT / AVL vs MCI)</button>
            <button type="button" onclick="setDateFilter('2026-10-25')" class="text-[11px] text-pl-green hover:underline font-bold">25 Oct (LIV vs BHA)</button>
            <button type="button" onclick="setDateFilter('2026-10-23')" class="text-[11px] text-pl-cyan hover:underline">23 Oct</button>
            <button type="button" onclick="setDateFilter('2026-10-11')" class="text-[11px] text-slate-400 hover:underline">J6: 11 Oct</button>
            <button type="button" onclick="setDateFilter('2026-03-31')" class="text-[11px] text-slate-400 hover:underline">31 Mar</button>
          </div>
        </div>

        <!-- Perfil de Scoring -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Perfil de Ponderación</label>
          <div class="relative">
            <select id="profileSelect" onchange="toggleCustomWeights()" class="w-full bg-pl-darker border border-pl-cardborder rounded-xl px-4 py-2.5 text-sm font-semibold text-white focus:outline-none focus:border-pl-green transition-colors appearance-none">
              <option value="cv_optimal" selected>⭐ Óptimo (k-Fold CV: Spearman 0.963)</option>
              <option value="balanced">Equilibrado Canónico (35% xG, 25% Paridad, 25% Fan, 15% Prensa)</option>
              <option value="goal_fest">Festival Goleador (60% xG Ofensivo)</option>
              <option value="tension">Tensión de Tabla & Drama (45% Paridad)</option>
              <option value="fan_hype">Hype Social & Foros (45% Sentimiento Afición)</option>
              <option value="custom">🛠️ Personalizado (Sliders Manuales)</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
          </div>
        </div>

        <!-- Selector de Motor ML vs Ponderado -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Motor de Inferencia</label>
          <div class="relative">
            <select id="engineSelect" class="w-full bg-pl-darker border border-pl-cardborder rounded-xl px-4 py-2.5 text-sm font-semibold text-white focus:outline-none focus:border-pl-green transition-colors appearance-none">
              <option value="ml_hybrid" selected>🤖 Machine Learning Híbrido (GBoost)</option>
              <option value="weighted">📐 Fórmula Ponderada Canónica</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
          </div>
        </div>

      </div>

      <!-- Sliders para pesos personalizados (ocultos por defecto) -->
      <div id="customWeightsPanel" class="hidden mt-6 pt-6 border-t border-pl-cardborder/60">
        <div class="flex items-center justify-between mb-4">
          <span class="text-xs font-bold text-pl-gold uppercase tracking-wider">Ajuste de Pesos Manual (Suma debe ser 1.0)</span>
          <span id="weightsSumLabel" class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">Suma: 1.00</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <div class="flex justify-between text-xs mb-1 text-slate-300">
              <span>w1: xG Combinado</span>
              <span id="val_w_xg" class="font-bold text-pl-green">0.35</span>
            </div>
            <input type="range" id="slider_w_xg" min="0" max="1" step="0.05" value="0.35" oninput="updateSliders()" class="w-full">
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1 text-slate-300">
              <span>w2: Paridad Tabla</span>
              <span id="val_w_parity" class="font-bold text-pl-cyan">0.25</span>
            </div>
            <input type="range" id="slider_w_parity" min="0" max="1" step="0.05" value="0.25" oninput="updateSliders()" class="w-full">
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1 text-slate-300">
              <span>w3: Sentimiento Afición</span>
              <span id="val_w_fan" class="font-bold text-pl-pink">0.25</span>
            </div>
            <input type="range" id="slider_w_fan" min="0" max="1" step="0.05" value="0.25" oninput="updateSliders()" class="w-full">
          </div>
          <div>
            <div class="flex justify-between text-xs mb-1 text-slate-300">
              <span>w4: Prensa / Medios</span>
              <span id="val_w_media" class="font-bold text-amber-400">0.15</span>
            </div>
            <input type="range" id="slider_w_media" min="0" max="1" step="0.05" value="0.15" oninput="updateSliders()" class="w-full">
          </div>
        </div>
      </div>

      <!-- BOTÓN DE ACCIÓN -->
      <div class="mt-6 flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-pl-cardborder/40">
        <div class="text-xs text-slate-400">
          <span id="evalCountLabel">Cargando partidos...</span>
        </div>
        <button id="calcBtn" onclick="fetchRecommendations()" class="px-6 py-3 rounded-xl bg-gradient-to-r from-pl-green to-pl-cyan hover:opacity-95 text-pl-dark font-black tracking-wide shadow-lg shadow-pl-green/20 flex items-center gap-2 transition-all transform active:scale-95">
          <svg id="calcSpinner" class="hidden animate-spin -ml-1 mr-2 h-4 w-4 text-pl-dark" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <span>RECOMENDAR PARTIDOS</span>
        </button>
      </div>

    </section>

    <!-- SECCIÓN TOP 3 RECOMENDADOS -->
    <section>
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            <span>🏆 Partidos Recomendados</span>
            <span id="badgeTop3Title" class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-pl-purple text-pl-green border border-pl-green/30">Top 3</span>
          </h2>
          <p class="text-sm text-slate-400">Clasificación optimizada por potencial de espectáculo y narrativa antes del pitazo inicial.</p>
        </div>
        <button onclick="toggleTelemetryModal()" class="text-xs text-pl-cyan hover:underline flex items-center gap-1 font-semibold">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          <span>Ver Métricas ML & CV</span>
        </button>
      </div>

      <!-- Tarjetas Top 3 -->
      <div id="topCardsContainer" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Generado dinámicamente -->
      </div>
    </section>

    <!-- EXPLORADOR DE TODOS LOS PARTIDOS DE LA JORNADA -->
    <section class="bg-pl-card/60 border border-pl-cardborder rounded-2xl p-6 shadow-xl">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-lg font-bold text-white tracking-tight">Todos los Partidos de la Fecha / Jornada</h3>
          <p class="text-xs text-slate-400">Haz clic en cualquier partido para ver su auditoría de variables y justificación completa.</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-pl-cardborder text-slate-400 text-xs uppercase tracking-wider">
              <th class="py-3 px-4">Local</th>
              <th class="py-3 px-4 text-center">Score Proyectado</th>
              <th class="py-3 px-4 text-right">Visitante</th>
              <th class="py-3 px-4 text-center">Fecha / Hora</th>
              <th class="py-3 px-4 text-center">Estilo Táctico</th>
              <th class="py-3 px-4 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody id="allMatchesTableBody" class="divide-y divide-pl-cardborder/40">
            <!-- Filas dinámicas -->
          </tbody>
        </table>
      </div>
    </section>

  </main>

  <!-- MODAL DE ANÁLISIS DETALLADO DE PARTIDO -->
  <div id="matchDetailModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-pl-card border border-pl-cardborder w-full max-w-3xl rounded-2xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto space-y-6">
      <div class="flex items-center justify-between border-b border-pl-cardborder pb-4">
        <div>
          <h3 id="modalMatchTitle" class="text-xl font-black text-white">Detalle de Partido</h3>
          <p id="modalMatchMeta" class="text-xs text-slate-400">Jornada y horario</p>
        </div>
        <button onclick="closeMatchModal()" class="w-8 h-8 rounded-lg bg-pl-darker text-slate-400 hover:text-white flex items-center justify-center font-bold">✕</button>
      </div>

      <div id="modalMatchBody" class="space-y-6">
        <!-- Contenido dinámico del modal -->
      </div>
    </div>
  </div>

  <!-- MODAL DE TELEMETRÍA Y VALIDACIÓN CRUZADA -->
  <div id="telemetryModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-pl-card border border-pl-cardborder w-full max-w-3xl rounded-2xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto space-y-6">
      <div class="flex items-center justify-between border-b border-pl-cardborder pb-4">
        <div>
          <h3 class="text-xl font-black text-white flex items-center gap-2">
            <span>🧪 Telemetría de Validación Cruzada k-Fold</span>
            <span class="text-xs bg-pl-green/10 text-pl-green border border-pl-green/30 px-2 py-0.5 rounded-full">Fase 3 & 4</span>
          </h3>
          <p class="text-xs text-slate-400">Calibración matemática de pesos e importancia del modelo Gradient Boosting.</p>
        </div>
        <button onclick="toggleTelemetryModal()" class="w-8 h-8 rounded-lg bg-pl-darker text-slate-400 hover:text-white flex items-center justify-center font-bold">✕</button>
      </div>

      <div id="telemetryModalBody" class="space-y-6">
        <!-- Contenido dinámico de telemetría -->
      </div>
    </div>
  </div>

  <!-- JAVASCRIPT DEL DASHBOARD -->
  <script>
    let currentRecommendations = null;
    let currentFixtures = [];

    function setDateFilter(dateStr) {
      document.getElementById('dateInput').value = dateStr;
      fetchRecommendations();
    }

    function toggleCustomWeights() {
      const profile = document.getElementById('profileSelect').value;
      const panel = document.getElementById('customWeightsPanel');
      if (profile === 'custom') {
        panel.classList.remove('hidden');
      } else {
        panel.classList.add('hidden');
      }
    }

    function updateSliders() {
      const w_xg = parseFloat(document.getElementById('slider_w_xg').value);
      const w_parity = parseFloat(document.getElementById('slider_w_parity').value);
      const w_fan = parseFloat(document.getElementById('slider_w_fan').value);
      const w_media = parseFloat(document.getElementById('slider_w_media').value);

      document.getElementById('val_w_xg').textContent = w_xg.toFixed(2);
      document.getElementById('val_w_parity').textContent = w_parity.toFixed(2);
      document.getElementById('val_w_fan').textContent = w_fan.toFixed(2);
      document.getElementById('val_w_media').textContent = w_media.toFixed(2);

      const sum = (w_xg + w_parity + w_fan + w_media).toFixed(2);
      const sumLabel = document.getElementById('weightsSumLabel');
      sumLabel.textContent = `Suma: ${sum}`;
      if (Math.abs(sum - 1.0) < 0.01) {
        sumLabel.className = 'text-xs font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800';
      } else {
        sumLabel.className = 'text-xs font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800';
      }
    }

    async function fetchRecommendations() {
      const btn = document.getElementById('calcBtn');
      const spinner = document.getElementById('calcSpinner');
      btn.disabled = true;
      spinner.classList.remove('hidden');

      const gwVal = document.getElementById('gameweekSelect').value;
      const dateVal = document.getElementById('dateInput').value;
      const profileVal = document.getElementById('profileSelect').value;
      const engineVal = document.getElementById('engineSelect').value;

      let payload = {
        profile: profileVal,
        model_type: engineVal,
        top_n: 10
      };
      if (gwVal) payload.gameweek = parseInt(gwVal);
      if (dateVal) payload.date = dateVal;

      if (profileVal === 'custom') {
        payload.custom_weights = {
          w_xg: parseFloat(document.getElementById('slider_w_xg').value),
          w_parity: parseFloat(document.getElementById('slider_w_parity').value),
          w_fan_excitement: parseFloat(document.getElementById('slider_w_fan').value),
          w_media_velocity: parseFloat(document.getElementById('slider_w_media').value)
        };
      }

      try {
        const res = await fetch('/api/v1/recommendations/top3', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Error al obtener recomendaciones');
        const data = await res.json();
        currentRecommendations = data;
        renderDashboard(data);
      } catch (err) {
        alert('No se pudieron obtener recomendaciones: ' + err.message);
      } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
      }
    }

    function renderDashboard(data) {
      document.getElementById('evalCountLabel').textContent = 
        `Evaluados ${data.total_evaluated_matches} partidos | Perfil: ${data.profile_used.toUpperCase()} | Motor: ${data.scoring_mode.toUpperCase()}` +
        (data.date_filter ? ` | Fecha: ${data.date_filter}` : '');

      const topMatches = data.top_matches.slice(0, 3);
      const container = document.getElementById('topCardsContainer');
      container.innerHTML = '';

      if (topMatches.length === 0) {
        container.innerHTML = `
          <div class="col-span-3 text-center py-12 bg-pl-card/50 rounded-2xl border border-pl-cardborder">
            <span class="text-4xl">🗓️</span>
            <p class="mt-2 text-base font-bold text-white">No hay partidos programados para el filtro seleccionado.</p>
            <p class="text-xs text-slate-400">Prueba quitando el filtro de fecha o seleccionando otra jornada.</p>
          </div>
        `;
        renderTableMatches(data.top_matches);
        return;
      }

      topMatches.forEach((m, idx) => {
        const home = m.fixture.home_team;
        const away = m.fixture.away_team;
        const num = m.numerical_features;
        const nlp = m.nlp_features;
        const att = m.feature_attributions || {};

        const rankMedal = idx === 0 ? '🥇 #1 RECOMENDADO' : (idx === 1 ? '🥈 #2 RECOMENDADO' : '🥉 #3 RECOMENDADO');
        const medalColor = idx === 0 ? 'border-pl-green/60 shadow-pl-green/10' : (idx === 1 ? 'border-pl-cyan/60 shadow-pl-cyan/10' : 'border-pl-pink/60 shadow-pl-pink/10');
        const scoreColor = m.excitement_score >= 80 ? 'text-pl-green' : (m.excitement_score >= 65 ? 'text-pl-cyan' : 'text-pl-gold');

        const kickoffFormatted = new Date(m.fixture.kickoff_time).toLocaleDateString('es-ES', {
          weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });

        const derbyBadge = m.fixture.is_derby ? `
          <span class="text-[10px] font-black uppercase tracking-wider bg-rose-950 text-rose-300 border border-rose-700 px-2 py-0.5 rounded">
            🔥 ${m.fixture.derby_name || 'DERBI'}
          </span>
        ` : '';

        const card = document.createElement('div');
        card.className = `bg-pl-card border rounded-2xl p-6 shadow-xl card-hover flex flex-col justify-between ${medalColor}`;
        card.innerHTML = `
          <div>
            <!-- Header Tarjeta -->
            <div class="flex items-center justify-between mb-4">
              <span class="text-xs font-black tracking-wider text-slate-300">${rankMedal}</span>
              <div class="flex items-center gap-1.5">
                ${derbyBadge}
                <span class="text-xs text-slate-400">${kickoffFormatted}</span>
              </div>
            </div>

            <!-- Enfrentamiento -->
            <div class="flex items-center justify-between py-2 border-y border-pl-cardborder/60 mb-4">
              <div class="text-left">
                <div class="text-lg font-black text-white">${home.name}</div>
                <div class="text-xs text-slate-400">Puesto #${home.position} · Forma: <span class="font-bold text-slate-200">${home.form}</span></div>
              </div>
              <div class="px-2 text-xs font-black text-slate-500">VS</div>
              <div class="text-right">
                <div class="text-lg font-black text-white">${away.name}</div>
                <div class="text-xs text-slate-400">Puesto #${away.position} · Forma: <span class="font-bold text-slate-200">${away.form}</span></div>
              </div>
            </div>

            <!-- Excitement Score Prominente -->
            <div class="bg-pl-darker/80 border border-pl-cardborder rounded-xl p-4 mb-4 flex items-center justify-between">
              <div>
                <span class="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">Excitement Score</span>
                <span class="text-3xl font-black ${scoreColor}">${m.excitement_score.toFixed(1)}</span>
                <span class="text-xs text-slate-500"> / 100</span>
              </div>
              <div class="text-right">
                <span class="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">Choque Táctico</span>
                <span class="text-xs font-bold text-pl-cyan">${num.tactical_style_label}</span>
                <div class="text-[11px] text-slate-400 font-semibold">${Math.round(num.tactical_clash_intensity * 100)}% intensidad</div>
              </div>
            </div>

            <!-- Desglose de Métricas Base -->
            <div class="space-y-2 mb-4 text-xs">
              <div>
                <div class="flex justify-between text-slate-300 mb-0.5">
                  <span>xG Combinado (${num.xg_combined.toFixed(2)})</span>
                  <span class="font-bold">${att.xg_offensive_potential ? att.xg_offensive_potential + '%' : ''}</span>
                </div>
                <div class="w-full bg-pl-darker rounded-full h-1.5 overflow-hidden">
                  <div class="bg-pl-green h-full rounded-full" style="width: ${Math.min(100, (num.xg_combined / 4.5) * 100)}%"></div>
                </div>
              </div>

              <div>
                <div class="flex justify-between text-slate-300 mb-0.5">
                  <span>Paridad en Tabla (${Math.round(num.table_parity * 100)}%)</span>
                  <span class="font-bold">${att.competitive_stakes_parity ? att.competitive_stakes_parity + '%' : ''}</span>
                </div>
                <div class="w-full bg-pl-darker rounded-full h-1.5 overflow-hidden">
                  <div class="bg-pl-cyan h-full rounded-full" style="width: ${num.table_parity * 100}%"></div>
                </div>
              </div>

              <div>
                <div class="flex justify-between text-slate-300 mb-0.5">
                  <span>Hype & Afición (${nlp.fan_excitement_index.toFixed(0)}/100)</span>
                  <span class="font-bold">${att.fan_hype_and_drama ? att.fan_hype_and_drama + '%' : ''}</span>
                </div>
                <div class="w-full bg-pl-darker rounded-full h-1.5 overflow-hidden">
                  <div class="bg-pl-pink h-full rounded-full" style="width: ${nlp.fan_excitement_index}%"></div>
                </div>
              </div>
            </div>

            <!-- Justificaciones Semánticas -->
            <div class="space-y-2 mb-4">
              <span class="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">Razones de Recomendación:</span>
              ${m.reasons.map(r => `
                <div class="bg-pl-darker/60 border border-pl-cardborder/50 rounded-lg p-2.5 text-xs">
                  <div class="font-bold text-pl-gold mb-0.5 flex items-center gap-1.5">
                    <span class="text-[9px] uppercase px-1.5 py-0.2 rounded bg-pl-purple border border-pl-cardborder text-slate-200">${r.category}</span>
                    <span>${r.title}</span>
                  </div>
                  <p class="text-slate-400 text-[11px] leading-relaxed">${r.description}</p>
                </div>
              `).join('')}
            </div>

          </div>

          <!-- Botón de Inspección -->
          <button onclick="openMatchModal(${m.fixture.id})" class="w-full mt-2 py-2 rounded-xl bg-pl-cardborder hover:bg-pl-purple text-xs font-bold text-slate-200 transition-colors flex items-center justify-center gap-1.5">
            <span>Ver Auditoría Completa</span>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </button>
        `;
        container.appendChild(card);
      });

      renderTableMatches(data.top_matches);
    }

    function renderTableMatches(matches) {
      const tbody = document.getElementById('allMatchesTableBody');
      tbody.innerHTML = '';

      matches.forEach(m => {
        const home = m.fixture.home_team;
        const away = m.fixture.away_team;
        const kickoff = new Date(m.fixture.kickoff_time).toLocaleDateString('es-ES', {
          month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-pl-darker/50 transition-colors cursor-pointer';
        tr.onclick = () => openMatchModal(m.fixture.id);
        tr.innerHTML = `
          <td class="py-3 px-4 font-bold text-white">${home.name} <span class="text-xs text-slate-400 font-normal">(#${home.position})</span></td>
          <td class="py-3 px-4 text-center">
            <span class="font-black text-sm text-pl-green px-2 py-0.5 rounded bg-pl-darker border border-pl-green/30">
              ${m.excitement_score.toFixed(1)}
            </span>
          </td>
          <td class="py-3 px-4 text-right font-bold text-white"><span class="text-xs text-slate-400 font-normal">(#${away.position})</span> ${away.name}</td>
          <td class="py-3 px-4 text-center text-xs text-slate-400">${kickoff}</td>
          <td class="py-3 px-4 text-center text-xs text-pl-cyan font-medium">${m.numerical_features.tactical_style_label}</td>
          <td class="py-3 px-4 text-center">
            <button onclick="event.stopPropagation(); openMatchModal(${m.fixture.id})" class="text-xs text-pl-green hover:underline font-bold">Detalle</button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function openMatchModal(fixtureId) {
      if (!currentRecommendations) return;
      const match = currentRecommendations.top_matches.find(m => m.fixture.id === fixtureId);
      if (!match) return;

      const f = match.fixture;
      const num = match.numerical_features;
      const nlp = match.nlp_features;
      const att = match.feature_attributions || {};

      document.getElementById('modalMatchTitle').textContent = `${f.home_team.name} vs ${f.away_team.name}`;
      document.getElementById('modalMatchMeta').textContent = `Jornada ${f.gameweek} · ${f.kickoff_time} · ${f.derby_name || 'Encuentro Regular'}`;

      const body = document.getElementById('modalMatchBody');
      body.innerHTML = `
        <!-- Métricas Rápidas -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
            <span class="text-[10px] text-slate-400 uppercase font-bold block">Excitement Score</span>
            <span class="text-2xl font-black text-pl-green">${match.excitement_score.toFixed(1)}</span>
          </div>
          <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
            <span class="text-[10px] text-slate-400 uppercase font-bold block">xG Proyectado</span>
            <span class="text-xl font-bold text-white">${num.xg_combined.toFixed(2)}</span>
          </div>
          <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
            <span class="text-[10px] text-slate-400 uppercase font-bold block">Paridad Tabla</span>
            <span class="text-xl font-bold text-pl-cyan">${Math.round(num.table_parity * 100)}%</span>
          </div>
          <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
            <span class="text-[10px] text-slate-400 uppercase font-bold block">Star Power ICT</span>
            <span class="text-xl font-bold text-pl-gold">${num.star_power.toFixed(0)}</span>
          </div>
        </div>

        <!-- Sección Táctica y PLN -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-pl-darker p-4 rounded-xl border border-pl-cardborder space-y-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-pl-cyan">Análisis Táctico Operativo</h4>
            <div class="text-xs space-y-2 text-slate-300">
              <div class="flex justify-between"><span>Arquetipo:</span> <span class="font-bold text-white">${num.tactical_style_label}</span></div>
              <div class="flex justify-between"><span>Intensidad de Choque:</span> <span class="font-bold text-white">${Math.round(num.tactical_clash_intensity * 100)}%</span></div>
              <div class="flex justify-between"><span>Pases Progresivos Proyectados:</span> <span class="font-bold text-white">${num.progressive_passes_combined.toFixed(0)}</span></div>
              <div class="flex justify-between"><span>Presiones Defensivas:</span> <span class="font-bold text-white">${num.defensive_pressures_combined.toFixed(0)}</span></div>
            </div>
          </div>

          <div class="bg-pl-darker p-4 rounded-xl border border-pl-cardborder space-y-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-pl-pink">Señales Cualitativas PLN</h4>
            <div class="text-xs space-y-2 text-slate-300">
              <div class="flex justify-between"><span>Hype Afición (Reddit):</span> <span class="font-bold text-white">${nlp.fan_excitement_index.toFixed(1)}/100</span></div>
              <div class="flex justify-between"><span>VADER Polarity:</span> <span class="font-bold text-white">${nlp.sentiment_compound.toFixed(2)}</span></div>
              <div class="flex justify-between"><span>Velocidad Prensa:</span> <span class="font-bold text-white">${nlp.media_velocity.toFixed(0)}/100</span></div>
              <div class="flex justify-between"><span>Dramatismo Histórico:</span> <span class="font-bold text-white">${Math.round(nlp.dramatic_intensity_score * 100)}%</span></div>
            </div>
          </div>
        </div>

        <!-- Atribución de Factores ML -->
        ${Object.keys(att).length > 0 ? `
          <div class="bg-pl-darker p-4 rounded-xl border border-pl-cardborder">
            <h4 class="text-xs font-bold uppercase tracking-wider text-pl-green mb-3">Atribución de Factores al Score</h4>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
              <div class="p-2 rounded bg-pl-card">
                <span class="text-slate-400 block text-[10px]">xG Ofensivo</span>
                <span class="font-bold text-pl-green">${att.xg_offensive_potential || 0}%</span>
              </div>
              <div class="p-2 rounded bg-pl-card">
                <span class="text-slate-400 block text-[10px]">Lo Que Está en Juego</span>
                <span class="font-bold text-pl-cyan">${att.competitive_stakes_parity || 0}%</span>
              </div>
              <div class="p-2 rounded bg-pl-card">
                <span class="text-slate-400 block text-[10px]">Hype & Drama</span>
                <span class="font-bold text-pl-pink">${att.fan_hype_and_drama || 0}%</span>
              </div>
              <div class="p-2 rounded bg-pl-card">
                <span class="text-slate-400 block text-[10px]">Medios & Estrellas</span>
                <span class="font-bold text-amber-400">${att.media_coverage_and_stars || 0}%</span>
              </div>
            </div>
          </div>
        ` : ''}

        <!-- Titulares y Menciones -->
        ${nlp.sample_headlines && nlp.sample_headlines.length > 0 ? `
          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Titulares y Discusión Social</h4>
            <ul class="space-y-1.5 text-xs text-slate-300">
              ${nlp.sample_headlines.map(h => `<li class="flex items-center gap-2"><span class="text-pl-cyan">📰</span> <span>${h}</span></li>`).join('')}
            </ul>
          </div>
        ` : ''}
      `;

      document.getElementById('matchDetailModal').classList.remove('hidden');
    }

    function closeMatchModal() {
      document.getElementById('matchDetailModal').classList.add('hidden');
    }

    async function toggleTelemetryModal() {
      const modal = document.getElementById('telemetryModal');
      if (!modal.classList.contains('hidden')) {
        modal.classList.add('hidden');
        return;
      }

      modal.classList.remove('hidden');
      const body = document.getElementById('telemetryModalBody');
      body.innerHTML = '<div class="text-center py-8 text-slate-400 text-sm">Cargando telemetría de validación cruzada...</div>';

      try {
        const res = await fetch('/api/v1/hybrid/cross-validation');
        const tel = await res.json();
        const cv = tel.cross_validation;
        const w = cv.optimal_weights;

        body.innerHTML = `
          <!-- Resumen Métricas -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
              <span class="text-[10px] text-slate-400 uppercase font-bold block">Spearman Rank Corr.</span>
              <span class="text-2xl font-black text-pl-green">${cv.spearman_rank_correlation.toFixed(3)}</span>
            </div>
            <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
              <span class="text-[10px] text-slate-400 uppercase font-bold block">NDCG@3 (Top 3 Quality)</span>
              <span class="text-2xl font-black text-pl-cyan">${cv.ndcg_at_3.toFixed(3)}</span>
            </div>
            <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
              <span class="text-[10px] text-slate-400 uppercase font-bold block">MSE Medio</span>
              <span class="text-2xl font-black text-pl-pink">${cv.mean_squared_error.toFixed(2)}</span>
            </div>
            <div class="bg-pl-darker p-3 rounded-xl border border-pl-cardborder text-center">
              <span class="text-[10px] text-slate-400 uppercase font-bold block">Coeficiente R²</span>
              <span class="text-2xl font-black text-pl-gold">${cv.r2_score.toFixed(3)}</span>
            </div>
          </div>

          <!-- Pesos Óptimos Obtenidos -->
          <div class="bg-pl-darker p-4 rounded-xl border border-pl-cardborder">
            <h4 class="text-xs font-bold uppercase tracking-wider text-white mb-2">Pesos Óptimos Calibrados (Preset 'cv_optimal')</h4>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
              <div class="p-2 rounded bg-pl-card border border-pl-cardborder">
                <span class="text-slate-400 block text-[10px]">w_xg</span>
                <span class="font-bold text-pl-green">${w.w_xg.toFixed(2)}</span>
              </div>
              <div class="p-2 rounded bg-pl-card border border-pl-cardborder">
                <span class="text-slate-400 block text-[10px]">w_parity</span>
                <span class="font-bold text-pl-cyan">${w.w_parity.toFixed(2)}</span>
              </div>
              <div class="p-2 rounded bg-pl-card border border-pl-cardborder">
                <span class="text-slate-400 block text-[10px]">w_fan_excitement</span>
                <span class="font-bold text-pl-pink">${w.w_fan_excitement.toFixed(2)}</span>
              </div>
              <div class="p-2 rounded bg-pl-card border border-pl-cardborder">
                <span class="text-slate-400 block text-[10px]">w_media_velocity</span>
                <span class="font-bold text-amber-400">${w.w_media_velocity.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <!-- Importancia de Variables en GradientBoostingRegressor -->
          <div class="bg-pl-darker p-4 rounded-xl border border-pl-cardborder">
            <h4 class="text-xs font-bold uppercase tracking-wider text-white mb-3">Importancia de Variables (Gradient Boosting)</h4>
            <div class="space-y-2">
              ${tel.feature_importances.map(item => `
                <div>
                  <div class="flex justify-between text-xs mb-1">
                    <span class="font-semibold text-slate-300">${item.feature} <span class="text-[10px] text-slate-500 font-normal">(${item.description})</span></span>
                    <span class="font-bold text-pl-green">${item.importance_percentage.toFixed(1)}%</span>
                  </div>
                  <div class="w-full bg-pl-card rounded-full h-1.5 overflow-hidden">
                    <div class="bg-pl-green h-full rounded-full" style="width: ${item.importance_percentage}%"></div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      } catch (err) {
        body.innerHTML = `<div class="text-rose-400 text-sm">Error cargando telemetría: ${err.message}</div>`;
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      fetchRecommendations();
    });
  </script>
</body>
</html>
"""
