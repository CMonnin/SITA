(() => {
  'use strict';

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

  function wireForm({ prefix, url, responseKey, variant, capLabel, extraFields = [] }) {
    const form = document.getElementById(`form-${prefix}`);
    const errorEl = document.getElementById(`${prefix}-error`);
    const submitBtn = form.querySelector('button[type="submit"]');
    const result = document.getElementById(`${prefix}-result`);
    const tableContainer = document.getElementById(`${prefix}-table`);
    const capTitle = document.getElementById(`${prefix}-cap`);
    const capTime = document.getElementById(`${prefix}-time`);
    const copyBtn = result.querySelector('.copy');

    let lastCsv = '';
    attachCopy(copyBtn, () => lastCsv);

    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      errorEl.textContent = '';
      submitBtn.dataset.pending = 'true';
      setStatus('computing…', 'var(--yellow)');

      const backboneRaw = form.elements.backbone_c.value;
      const payload = {
        formula: form.elements.formula.value.trim(),
        backbone_c: backboneRaw === '' ? null : Number(backboneRaw),
      };
      for (const field of extraFields) {
        payload[field] = form.elements[field].value.trim();
      }

      const { ok, elapsed, data } = await submitJson(url, payload);
      submitBtn.dataset.pending = 'false';

      if (!ok || data.error) {
        errorEl.textContent = `error: ${data.error || 'request failed'}`;
        result.hidden = true;
        setStatus('error', 'var(--red)');
        return;
      }

      const rows = data[responseKey];
      renderTable(tableContainer, rows, variant);
      capTitle.textContent = capLabel(rows.length);
      capTime.textContent = `ready · ${elapsed.toFixed(0)}ms`;
      lastCsv = data.csv;
      result.hidden = false;
      setStatus('ready', 'var(--green)');
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    wireForm({
      prefix: 'matrix',
      url: '/api/matrix',
      responseKey: 'matrix',
      variant: 'matrix',
      capLabel: (n) => `${n} × ${n} correction matrix`,
    });
    wireForm({
      prefix: 'mdv',
      url: '/api/mdv-star',
      responseKey: 'mdv_star',
      variant: 'vector',
      capLabel: (n) => `${n} × 1 corrected mdv`,
      extraFields: ['mdv'],
    });
  });
})();
