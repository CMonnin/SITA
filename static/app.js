(() => {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const fmt = (v) => {
    if (v === 0) return '0.0000';
    return Number(v).toFixed(4);
  };

  const isZero = (v) => Math.abs(Number(v)) < 1e-9;

  // Render a 2D matrix into the given container as a <table>.
  // `variant` is 'matrix' (square, coord both axes) or 'vector' (n×1 column, only row coords).
  function renderTable(container, data, variant) {
    const rows = data.length;
    const cols = rows > 0 ? data[0].length : 0;

    const table = document.createElement('table');
    table.className = 'matrix';

    // column header row (coord indices)
    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    const corner = document.createElement('th');
    corner.className = 'corner';
    corner.scope = 'col';
    corner.textContent = variant === 'vector' ? 'i' : '';
    headRow.appendChild(corner);
    for (let j = 0; j < cols; j++) {
      const th = document.createElement('th');
      th.scope = 'col';
      th.textContent = variant === 'vector' ? '·' : String(j);
      headRow.appendChild(th);
    }
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    for (let i = 0; i < rows; i++) {
      const tr = document.createElement('tr');
      tr.style.setProperty('--i', String(i));
      const rowHead = document.createElement('th');
      rowHead.scope = 'row';
      rowHead.textContent = String(i);
      tr.appendChild(rowHead);

      for (let j = 0; j < cols; j++) {
        const td = document.createElement('td');
        const v = data[i][j];
        if (variant === 'matrix' && j > i && isZero(v)) {
          td.textContent = '·';
          td.className = 'zero';
        } else if (variant === 'matrix' && i === j) {
          td.textContent = fmt(v);
          td.className = 'diag';
        } else {
          td.textContent = fmt(v);
        }
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);

    container.replaceChildren(table);
  }

  // Clipboard: handle button with data-target referencing the result figure's id
  function attachCopy(button, getCsv) {
    button.addEventListener('click', async () => {
      const targetId = button.dataset.target;
      const target = targetId ? document.getElementById(targetId) : null;
      const csv = getCsv();
      if (!csv) return;

      button.dataset.state = 'working';
      button.textContent = '[ .... ]';

      try {
        await navigator.clipboard.writeText(csv);
        button.dataset.state = 'success';
        button.textContent = '[ ✓ copied ]';
        if (target) {
          target.dataset.pulse = 'success';
          setTimeout(() => delete target.dataset.pulse, 700);
        }
      } catch (err) {
        button.dataset.state = 'error';
        button.textContent = '[ × failed ]';
        if (target) {
          target.dataset.pulse = 'error';
          setTimeout(() => delete target.dataset.pulse, 700);
        }
      }

      setTimeout(() => {
        button.dataset.state = 'idle';
        button.textContent = '[ copy ]';
      }, 1200);
    });
  }

  async function submitJson(url, body) {
    const started = performance.now();
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    });
    const elapsed = performance.now() - started;
    const data = await res.json().catch(() => ({ error: 'invalid server response' }));
    return { ok: res.ok, elapsed, data };
  }

  function setStatus(text, color) {
    const el = document.getElementById('modeline-status');
    if (!el) return;
    el.textContent = text;
    el.style.color = color || '';
  }

  function wireMatrixForm() {
    const form = document.getElementById('form-matrix');
    const errorEl = document.getElementById('matrix-error');
    const submitBtn = form.querySelector('button[type="submit"]');
    const result = document.getElementById('matrix-result');
    const tableContainer = document.getElementById('matrix-table');
    const capTitle = document.getElementById('matrix-cap');
    const capTime = document.getElementById('matrix-time');
    const copyBtn = result.querySelector('.copy');

    let lastCsv = '';
    attachCopy(copyBtn, () => lastCsv);

    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      errorEl.textContent = '';
      submitBtn.dataset.pending = 'true';
      setStatus('computing…', 'var(--yellow)');

      const formula = form.elements.formula.value.trim();
      const backboneRaw = form.elements.backbone_c.value;
      const backbone_c = backboneRaw === '' ? null : Number(backboneRaw);

      const { ok, elapsed, data } = await submitJson('/api/matrix', { formula, backbone_c });
      submitBtn.dataset.pending = 'false';

      if (!ok || data.error) {
        errorEl.textContent = `error: ${data.error || 'request failed'}`;
        result.hidden = true;
        setStatus('error', 'var(--red)');
        return;
      }

      const n = data.matrix.length;
      renderTable(tableContainer, data.matrix, 'matrix');
      capTitle.textContent = `${n} × ${n} correction matrix`;
      capTime.textContent = `ready · ${elapsed.toFixed(0)}ms`;
      lastCsv = data.csv;
      result.hidden = false;
      setStatus('ready', 'var(--green)');
    });
  }

  function wireMdvForm() {
    const form = document.getElementById('form-mdv');
    const errorEl = document.getElementById('mdv-error');
    const submitBtn = form.querySelector('button[type="submit"]');
    const result = document.getElementById('mdv-result');
    const tableContainer = document.getElementById('mdv-table');
    const capTitle = document.getElementById('mdv-cap');
    const capTime = document.getElementById('mdv-time');
    const copyBtn = result.querySelector('.copy');

    let lastCsv = '';
    attachCopy(copyBtn, () => lastCsv);

    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      errorEl.textContent = '';
      submitBtn.dataset.pending = 'true';
      setStatus('computing…', 'var(--yellow)');

      const formula = form.elements.formula.value.trim();
      const backboneRaw = form.elements.backbone_c.value;
      const backbone_c = backboneRaw === '' ? null : Number(backboneRaw);
      const mdv = form.elements.mdv.value.trim();

      const { ok, elapsed, data } = await submitJson('/api/mdv-star', { formula, backbone_c, mdv });
      submitBtn.dataset.pending = 'false';

      if (!ok || data.error) {
        errorEl.textContent = `error: ${data.error || 'request failed'}`;
        result.hidden = true;
        setStatus('error', 'var(--red)');
        return;
      }

      const n = data.mdv_star.length;
      renderTable(tableContainer, data.mdv_star, 'vector');
      capTitle.textContent = `${n} × 1 corrected mdv`;
      capTime.textContent = `ready · ${elapsed.toFixed(0)}ms`;
      lastCsv = data.csv;
      result.hidden = false;
      setStatus('ready', 'var(--green)');
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    wireMatrixForm();
    wireMdvForm();
  });
})();
