import { ideologyModel2009 } from './ideology_model_2009.js';
import { ideologyModel2014 } from './ideology_model_2014.js';
import { ideologyModel2019 } from './ideology_model_2019.js';
import { vaaStatements } from './vaa_statements.js';

const models = {
  2009: ideologyModel2009,
  2014: ideologyModel2014,
  2019: ideologyModel2019,
};

const valueMap = {
  CD: 0.0,
  D: 0.25,
  N: 0.5,
  A: 0.75,
  CA: 1.0,
};

const choices = [
  ['CD', 'Completely Disagree'],
  ['D', 'Disagree'],
  ['N', 'Neutral'],
  ['A', 'Agree'],
  ['CA', 'Completely Agree'],
];

const state = {
  year: '2019',
  questionsByYear: vaaStatements,
  answers: {
    2009: {},
    2014: {},
    2019: {},
  },
};

const yearTabs = document.querySelector('#yearTabs');
const questionForm = document.querySelector('#questionForm');
const questionHeading = document.querySelector('#questionHeading');
const questionMeta = document.querySelector('#questionMeta');
const progressText = document.querySelector('#progressText');
const progressBar = document.querySelector('#progressBar');
const resultPanel = document.querySelector('#resultPanel');
const plotCard = document.querySelector('#plotCard');
const chesPlot = document.querySelector('#chesPlot');
const calculateButton = document.querySelector('#calculateButton');
const resetButton = document.querySelector('#resetButton');
const neutralButton = document.querySelector('#neutralButton');
const statusBox = document.querySelector('#status');

init();

function init() {
  renderYearTabs();
  renderCurrentYear();
}

function renderYearTabs() {
  yearTabs.innerHTML = '';
  Object.keys(models).forEach((year) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = year;
    button.className = yearButtonClass(year === state.year);
    button.addEventListener('click', () => {
      state.year = year;
      renderYearTabs();
      renderCurrentYear();
    });
    yearTabs.append(button);
  });
}

function renderCurrentYear() {
  const questions = state.questionsByYear[state.year] || [];
  questionHeading.textContent = `${state.year} VAA statements`;
  questionMeta.textContent = `${questions.length} statements mapped to the ${state.year} CHES projection model.`;
  questionForm.innerHTML = '';
  resultPanel.classList.add('hidden');
  plotCard.classList.add('hidden');

  questions.forEach((question, index) => {
    questionForm.append(renderQuestion(question, index));
  });

  updateProgress();
}

function renderQuestion(question, index) {
  const wrapper = document.createElement('fieldset');
  wrapper.className = 'card p-4 md:p-5';

  const legend = document.createElement('legend');
  legend.className = 'w-full';
  legend.innerHTML = `
    <div class="flex items-start gap-4">
      <span class="font-mono text-xs text-neutral-400 pt-1">${String(index + 1).padStart(2, '0')}</span>
      <span class="text-[1.02rem] leading-relaxed text-neutral-900">${escapeHtml(question.statement)}</span>
    </div>
  `;
  wrapper.append(legend);

  const options = document.createElement('div');
  options.className = 'grid grid-cols-5 mt-4';

  choices.forEach(([code, label]) => {
    const id = `${state.year}-${question.variable}-${code}`;
    const choice = document.createElement('label');
    choice.className = 'choice relative cursor-pointer';
    choice.innerHTML = `
      <input type="radio" name="${question.variable}" value="${code}" id="${id}" ${state.answers[state.year][question.variable] === code ? 'checked' : ''}>
      <span>${label}</span>
    `;
    choice.querySelector('input').addEventListener('change', (event) => {
      state.answers[state.year][question.variable] = event.target.value;
      updateProgress();
      resultPanel.classList.add('hidden');
      plotCard.classList.add('hidden');
    });
    options.append(choice);
  });

  wrapper.append(options);
  return wrapper;
}

function updateProgress() {
  const questions = state.questionsByYear[state.year] || [];
  const answered = questions.filter((question) => state.answers[state.year][question.variable]).length;
  const total = questions.length;
  const percent = total ? (answered / total) * 100 : 0;

  progressText.textContent = `${answered}/${total}`;
  progressBar.style.width = `${percent}%`;
  calculateButton.disabled = answered !== total;
}

function calculateCurrentYear() {
  const questions = state.questionsByYear[state.year] || [];
  const missing = questions.filter((question) => !state.answers[state.year][question.variable]);
  if (missing.length) {
    showStatus(`Answer ${missing.length} more statement${missing.length === 1 ? '' : 's'} before calculating.`);
    return;
  }

  const values = questions.map((question) => valueMap[state.answers[state.year][question.variable]]);
  const result = predict(models[state.year], values);
  renderResult(result);
}

function predict(model, values) {
  const standardized = values.map((value, index) => {
    const scale = model.feature_scale[index] || 1;
    return (value - model.feature_mean[index]) / scale;
  });

  const sums = { lrgen: 0, lrecon: 0, galtan: 0 };

  model.estimators.forEach((estimatorGroup) => {
    estimatorGroup.forEach((estimator) => {
      const prediction = estimator.weights.reduce(
        (total, weight, index) => total + weight * standardized[index],
        estimator.intercept
      );
      sums[estimator.target] += prediction;
    });
  });

  const count = model.estimators.length || 1;
  return {
    lrgen: sums.lrgen / count,
    lrecon: sums.lrecon / count,
    galtan: sums.galtan / count,
  };
}

function renderResult(result) {
  renderPlot(result);
  resultPanel.classList.remove('hidden');
  plotCard.classList.remove('hidden');
  plotCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderPlot(result) {
  if (!window.Plotly) {
    showStatus('Plotly could not be loaded. Check the network connection for the Plotly CDN script.');
    return;
  }

  const point = {
    x: [result.lrgen],
    y: [result.lrecon],
    z: [result.galtan],
    mode: 'markers',
    type: 'scatter3d',
    name: 'Your estimated position',
    marker: {
      size: 8,
      color: '#0A0A0A',
      line: { color: '#00E5FF', width: 5 },
      opacity: 0.95,
    },
    hovertemplate:
      'lrgen: %{x:.3f}<br>lrecon: %{y:.3f}<br>galtan: %{z:.3f}<extra>Your position</extra>',
  };

  const reference = {
    x: [0, 1, 0, 0],
    y: [0, 0, 1, 0],
    z: [0, 0, 0, 1],
    mode: 'markers',
    type: 'scatter3d',
    name: 'Reference bounds',
    marker: { size: 2, color: 'rgba(10,10,10,0.22)' },
    hoverinfo: 'skip',
    showlegend: false,
  };
  const centerAxes = [
    centerAxisTrace('lrgen midpoint axis', [0, 1], [0.5, 0.5], [0.5, 0.5], '#00B8D4'),
    centerAxisTrace('lrecon midpoint axis', [0.5, 0.5], [0, 1], [0.5, 0.5], '#8B5CF6'),
    centerAxisTrace('galtan midpoint axis', [0.5, 0.5], [0.5, 0.5], [0, 1], '#F472B6'),
  ];

  const layout = {
    margin: { l: 0, r: 0, t: 8, b: 0 },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#ffffff',
    showlegend: false,
    scene: {
      bgcolor: '#ffffff',
      xaxis: axisLayout('lrgen', 'Left', 'Right'),
      yaxis: axisLayout('lrecon', 'Economic left', 'Economic right'),
      zaxis: axisLayout('galtan', 'GAL', 'TAN'),
      camera: {
        eye: { x: 1.55, y: 1.55, z: 1.15 },
      },
      aspectmode: 'cube',
    },
  };

  const config = {
    responsive: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['toImage', 'sendDataToCloud', 'select2d', 'lasso2d'],
  };

  window.Plotly.react(chesPlot, [reference, ...centerAxes, point], layout, config);
}

function centerAxisTrace(name, x, y, z, color) {
  return {
    x,
    y,
    z,
    mode: 'lines',
    type: 'scatter3d',
    name,
    line: { color, width: 5 },
    hoverinfo: 'skip',
    showlegend: false,
  };
}

function axisLayout(title, lowLabel, highLabel) {
  return {
    title,
    range: [0, 1],
    tickmode: 'array',
    tickvals: [0, 0.5, 1],
    ticktext: [lowLabel, '0.5', highLabel],
    gridcolor: '#e5e5e5',
    zeroline: false,
    linecolor: '#d4d4d8',
    titlefont: { family: 'JetBrains Mono, monospace', size: 12, color: '#0A0A0A' },
    tickfont: { family: 'Inter, sans-serif', size: 10, color: '#525252' },
  };
}

function setUnansweredNeutral() {
  const questions = state.questionsByYear[state.year] || [];
  questions.forEach((question) => {
    if (!state.answers[state.year][question.variable]) {
      state.answers[state.year][question.variable] = 'N';
    }
  });
  renderCurrentYear();
}

function clearCurrentYear() {
  state.answers[state.year] = {};
  renderCurrentYear();
}

function showStatus(message) {
  statusBox.textContent = message;
  statusBox.classList.remove('hidden');
}

function yearButtonClass(active) {
  return [
    'border px-3 py-2 text-sm font-medium transition-colors',
    active
      ? 'border-neutral-950 bg-neutral-950 text-white'
      : 'border-neutral-300 bg-white text-neutral-700 hover:border-neutral-950',
  ].join(' ');
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

calculateButton.addEventListener('click', calculateCurrentYear);
resetButton.addEventListener('click', clearCurrentYear);
neutralButton.addEventListener('click', setUnansweredNeutral);
