
(() => {
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];

  const escapeHtml = (value = '') =>
    String(value).replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[c]));

  const safeUrl = value => {
    try {
      const u = new URL(value);
      return ['https:', 'http:'].includes(u.protocol) ? u.href : '#';
    } catch {
      return '#';
    }
  };

  const form = $('#inspectForm');
  const repoInput = $('#repoInput');
  const caseResult = $('#caseResult');
  const caseEmpty = $('#caseEmpty');
  const formError = $('#formError');
  const caseStatus = $('#caseStatus');
  const toast = $('#toast');

  let lastResult = null;
  let toastTimer = null;

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.hidden = true;
    }, 3000);
  }

  function loading() {
    caseEmpty.hidden = true;
    caseResult.hidden = false;
    caseResult.innerHTML = `
      <div class="loading">
        <span class="loading-orbit">✳</span>
        FETCHING PUBLIC TRACES…
        <br>
        <small>THE ARCHIVIST IS CHECKING THE RECORDS</small>
      </div>
    `;
    caseStatus.textContent = 'INVESTIGATION RUNNING';
    $('#casefile').scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  }

  function metric(value, label) {
    return `
      <div class="metric">
        <strong>${escapeHtml(value ?? 'N/A')}</strong>
        <span>${escapeHtml(label)}</span>
      </div>
    `;
  }

  function renderResult(data, isSample = false, shouldPersist = true) {
    lastResult = data;

    if (shouldPersist && !isSample) {
      saveHistory(data);
    }

    const r = data.repository || {};
    const f = data.features || {};
    const a = data.assessment || {};
    const story = data.story || data.epitaph || {};
    const evidence = data.evidence || [];
    const reasons = a.reasons || [];
    const limitations = data.limitations || [];

    const age =
      f.days_since_last_commit == null ||
      f.days_since_last_commit >= 9999
        ? 'N/A'
        : `${f.days_since_last_commit}`;

    const releaseAge =
      f.days_since_last_release == null ||
      f.days_since_last_release >= 9999
        ? 'N/A'
        : `${f.days_since_last_release}`;

    const score = Math.max(
      0,
      Math.min(100, Number(a.score) || 0)
    );

    const storyText =
      story.text || 'No story was returned for this case.';

    const sampleBadge = isSample
      ? '<span class="sample-label">ILLUSTRATIVE SAMPLE · NOT LIVE GITHUB DATA</span>'
      : '';

    const evidenceHtml = evidence.length
      ? evidence.map(e => `
          <div class="evidence-item">
            <span class="evidence-id">${escapeHtml(e.id)}</span>
            <div>
              <b>${escapeHtml(e.claim)}</b>
              <a href="${safeUrl(e.url)}"
                 target="_blank"
                 rel="noopener noreferrer">
                Open supporting source ↗
              </a>
            </div>
          </div>
        `).join('')
      : '<p class="muted">No evidence records were returned.</p>';

    const reasonHtml = reasons.length
      ? reasons.map(x => `<li>${escapeHtml(x)}</li>`).join('')
      : '<li>No assessment reasons returned.</li>';

    const limits = limitations.length
      ? limitations
      : [
          a.disclaimer ||
          'This is a heuristic based on a limited public API snapshot, not proof of abandonment.'
        ];

    caseResult.innerHTML = `
      <article class="case-report" id="renderedReport">
        <header class="report-header">
          <div>
            ${sampleBadge}
            <div class="eyebrow">
              CASE FILE / ${
                escapeHtml(
                  data.generated_at
                    ? new Date(data.generated_at).toLocaleDateString()
                    : 'ARCHIVE SAMPLE'
                )
              }
            </div>
            <h3>${escapeHtml(r.full_name || 'Unknown repository')}</h3>
            <p class="repo-description">
              ${escapeHtml(r.description || 'No public description supplied.')}
              · ${escapeHtml(r.language || 'Unknown language')}
              · ${r.archived ? 'ARCHIVED' : 'NOT MARKED ARCHIVED'}
            </p>
          </div>

          <div class="report-actions">
            <button class="mini-button" id="copyReport">
              COPY SUMMARY ↗
            </button>

            ${
              !isSample && r.full_name
                ? `
                  <a class="mini-button"
                     href="/api/export/${encodeURIComponent(r.full_name.split('/')[0])}/${encodeURIComponent(r.full_name.split('/')[1] || '')}"
                     target="_blank"
                     rel="noopener">
                    EXPORT .MD ↗
                  </a>
                `
                : ''
            }

            <a class="mini-button"
               href="${safeUrl(r.url || '#')}"
               target="_blank"
               rel="noopener">
              OPEN REPO ↗
            </a>
          </div>
        </header>

        <div class="report-body">
          <div class="score-row">
            <div class="score-gauge" style="--score:${score}%">
              <strong>${score}</strong>
              <small>VITALITY / 100</small>
            </div>

            <div class="score-copy">
              <span class="status">
                ${escapeHtml(a.label || 'Unknown activity')}
              </span>
              <h4>Still breathing? Let's check the receipts.</h4>
              <p>
                ${escapeHtml(
                  a.disclaimer ||
                  'A transparent heuristic, not a prediction of maintainer intent. A quiet repository is not necessarily abandoned.'
                )}
              </p>
            </div>
          </div>

          <div class="metric-grid">
            ${metric(age, 'DAYS SINCE LAST COMMIT')}
            ${metric(
              f.stars ?? r.stars ?? 0,
              'STARS LEFT ON THE GRAVESTONE'
            )}
            ${metric(
              f.contributors_observed ?? 0,
              'CONTRIBUTORS OBSERVED'
            )}
            ${metric(releaseAge, 'DAYS SINCE RELEASE')}
          </div>

          <div class="report-columns">
            <section class="report-panel">
              <h4>✎ A TINY EULOGY, WITH RECEIPTS</h4>
              <div class="story-copy">
                ${escapeHtml(storyText)}
              </div>
              ${
                story.note
                  ? `<div class="story-note">${escapeHtml(story.note)}</div>`
                  : ''
              }
              <div class="story-note">
                TONE: LOVINGLY SARCASTIC · CLAIMS SHOULD BE CHECKED AGAINST THEIR CITATIONS
              </div>
            </section>

            <section class="report-panel">
              <h4>▥ WHAT THE RECORD SAYS</h4>
              <ul class="reason-list">${reasonHtml}</ul>

              <h4 style="margin-top:22px">! LIMITATIONS</h4>
              <ul class="limit-list">
                ${limits.map(x => `<li>${escapeHtml(x)}</li>`).join('')}
              </ul>
            </section>

            <section class="report-panel full">
              <h4>⌕ EVIDENCE LEDGER / CLICK TO VERIFY</h4>
              ${evidenceHtml}
            </section>
          </div>
        </div>
      </article>
    `;

    caseResult.hidden = false;
    caseEmpty.hidden = true;
    caseStatus.textContent = isSample
      ? 'SAMPLE CASE LOADED'
      : 'CASE FILE OPEN';

    $('#copyReport')?.addEventListener('click', async () => {
      const text = `
${r.full_name}
Vitality: ${score}/100 (${a.label})

${storyText}

Evidence:
${evidence.map(e =>
  `${e.id}: ${e.claim} — ${e.url}`
).join('\n')}
      `.trim();

      try {
        await navigator.clipboard.writeText(text);
        showToast('Case summary copied to clipboard.');
      } catch {
        showToast('Clipboard access was blocked by the browser.');
      }
    });
  }

  // --------------------------------------------------
  // LOCAL CASE HISTORY
  // --------------------------------------------------

  const HISTORY_KEY = 'software-cemetery.case-history.v1';

  function readHistory() {
    try {
      const value = JSON.parse(
        localStorage.getItem(HISTORY_KEY) || '[]'
      );
      return Array.isArray(value) ? value : [];
    } catch {
      return [];
    }
  }

  function saveHistory(data) {
    try {
      const repo = data.repository || {};

      if (!repo.full_name) return;

      const rows = readHistory().filter(
        x => x.repository?.full_name !== repo.full_name
      );

      rows.unshift({
        saved_at: new Date().toISOString(),
        repository: repo,
        features: data.features || {},
        assessment: data.assessment || {},
        story: data.story || {},
        evidence: data.evidence || [],
        limitations: data.limitations || [],
        generated_at: data.generated_at || new Date().toISOString(),
        citation_check: data.citation_check || null
      });

      localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(rows.slice(0, 12))
      );

      renderHistory();
    } catch {
      showToast(
        'Case opened, but this browser blocked local archive storage.'
      );
    }
  }

  function renderHistory() {
    const target = $('#historyList');
    if (!target) return;

    const query = (
      $('#historySearch')?.value || ''
    ).toLowerCase().trim();

    const rows = readHistory().filter(x =>
      (x.repository?.full_name || '').toLowerCase().includes(query) ||
      (x.repository?.description || '').toLowerCase().includes(query)
    );

    if (!rows.length) {
      target.innerHTML = `
        <div class="history-empty">
          <span>▤</span>
          <p>
            ${
              query
                ? 'No saved cases match that filter.'
                : 'No case files have been saved in this browser yet.'
            }
          </p>
          <a href="#investigate">Open a case ↗</a>
        </div>
      `;
      return;
    }

    target.innerHTML = rows.map((x, i) => `
      <article class="history-card">
        <div class="history-card-top">
          <span>${new Date(x.saved_at).toLocaleDateString()}</span>
          <span>${escapeHtml(x.assessment?.label || 'UNASSESSED')}</span>
        </div>

        <h4>${escapeHtml(x.repository?.full_name || 'Unknown repository')}</h4>
        <p>${escapeHtml(x.repository?.description || 'No description supplied.')}</p>

        <div class="history-card-actions">
          <span class="history-score">
            ${escapeHtml(x.assessment?.score ?? '—')}
            <small>/100</small>
          </span>
          <button type="button" data-history-open="${i}">
            OPEN CASE ↗
          </button>
        </div>
      </article>
    `).join('');

    $$('[data-history-open]', target).forEach(button => {
      button.addEventListener('click', () => {
        const found = rows[Number(button.dataset.historyOpen)];

        if (found) {
          renderResult(found, false, false);
          $('#casefile').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  $('#historySearch')?.addEventListener('input', renderHistory);

  $('#clearHistory')?.addEventListener('click', () => {
    try {
      localStorage.removeItem(HISTORY_KEY);
      renderHistory();
      showToast('Local case archive cleared.');
    } catch {
      showToast('The browser did not allow clearing local storage.');
    }
  });

  renderHistory();

  // --------------------------------------------------
  // REPOSITORY SUGGESTION PICKER
  // --------------------------------------------------

  // Repository picker expand/collapse
  const addRepositoryButton = $('#addRepositoryButton');
  const repositorySuggestions = $('#repositorySuggestions');

  if (addRepositoryButton && repositorySuggestions) {
    addRepositoryButton.addEventListener('click', () => {
      const isOpening = repositorySuggestions.hidden;

      repositorySuggestions.hidden = !isOpening;
      addRepositoryButton.setAttribute('aria-expanded', String(isOpening));

      addRepositoryButton.classList.toggle('is-open', isOpening);
    });
  }

  // Select a repository without automatically submitting the form
  $$('[data-repo]').forEach(btn => {
    btn.addEventListener('click', () => {
      repoInput.value = btn.dataset.repo;

      $$('.suggestion-item').forEach(item => {
        item.classList.toggle('selected-repository', item === btn);
      });

      if (repositorySuggestions && addRepositoryButton) {
        repositorySuggestions.hidden = true;
        addRepositoryButton.setAttribute('aria-expanded', 'false');
        addRepositoryButton.classList.remove('is-open');
      }

      showToast(`Repository selected: ${btn.dataset.repo}`);

      $('#investigate').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });

      repoInput.focus();
    });
  });

  // --------------------------------------------------
  // REPOSITORY INVESTIGATION
  // --------------------------------------------------

  function showError(target, message) {
    target.textContent = message;
    target.hidden = false;
  }

  async function inspectRepo(repo, useLlm = false) {
    formError.hidden = true;
    loading();

    try {
      const response = await fetch('/api/inspect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          repo,
          use_llm: useLlm
        })
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(
          payload.detail || 'The archive could not open this case.'
        );
      }

      renderResult(payload);
      showToast('Case file opened. Receipts included.');
    } catch (err) {
      caseResult.hidden = true;
      caseEmpty.hidden = false;
      caseStatus.textContent = 'CASE COULD NOT OPEN';

      showError(
        formError,
        `${err.message}\n\nCheck the repository spelling, internet connection, and GitHub API rate limit.`
      );

      $('#investigate').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }

  form.addEventListener('submit', e => {
    e.preventDefault();

    if (!repoInput.value.trim()) return;

    inspectRepo(
      repoInput.value.trim(),
      $('#useLlm').checked
    );
  });

  // --------------------------------------------------
  // ILLUSTRATIVE SAMPLE CASE
  // --------------------------------------------------

  $('#sampleButton').addEventListener('click', () => {
    const sample = {
      generated_at: new Date().toISOString(),

      repository: {
        full_name: 'archive-lantern/forgotten-widget',
        url: 'https://github.com',
        description: 'A fictional sample project for previewing the Software Cemetery interface. This is not a real repository.',
        language: 'JavaScript',
        archived: false,
        stars: 128,
        forks: 19
      },

      features: {
        days_since_last_commit: 847,
        stars: 128,
        forks: 19,
        contributors_observed: 4,
        days_since_last_release: 1024,
        archived: false
      },

      assessment: {
        score: 42,
        label: 'Very quiet',
        reasons: [
          'Illustrative sample: the last recorded push is shown as 847 days ago.',
          'The sample repository is not marked archived.',
          'Four contributors appear in the illustrative sample.',
          'No release has been published in the sample window for 1,024 days.'
        ],
        disclaimer: 'This is fictional preview data to demonstrate the interface. It is not a real GitHub investigation and must not be used as a factual repository assessment.'
      },

      story: {
        model: 'illustrative sample story',
        text: 'Here lies forgotten-widget, a fictional project that began with the energy of three coffees and a README that promised “just one more feature.” [E1] Its tiny star collection suggests that at least a few people once bookmarked the adventure. [E2] The last recorded push in this imaginary case was 847 days ago. [E3] Somewhere in the code, a TODO comment has likely achieved permanent residency. We cannot know why the project went quiet, and we will not invent a dramatic maintainer exit just to improve the plot. Perhaps it works perfectly. Perhaps it is waiting for a weekend that has not arrived. The respectful next step: inspect open issues, read the contribution guide, and ask whether help is welcome. May its dependencies remain resolvable and its tests occasionally green.',
        note: 'Sample citations are illustrative placeholders, not source-verified references.'
      },

      evidence: [
        {
          id: 'E1',
          claim: 'Fictional project description and identity (sample only).',
          url: 'https://github.com'
        },
        {
          id: 'E2',
          claim: 'Illustrative star and fork counts (sample only).',
          url: 'https://github.com'
        },
        {
          id: 'E3',
          claim: 'Illustrative activity interval (sample only).',
          url: 'https://github.com'
        }
      ],

      limitations: [
        'This is synthetic sample content and does not describe a real repository.'
      ]
    };

    renderResult(sample, true);

    $('#casefile').scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  });

  // --------------------------------------------------
  // REPOSITORY COMPARISON
  // --------------------------------------------------

  $('#compareForm').addEventListener('submit', async e => {
    e.preventDefault();

    const target = $('#compareResults');
    const error = $('#compareError');

    error.hidden = true;
    target.hidden = false;
    target.innerHTML = `
      <div class="loading">COMPARING PUBLIC RECORDS…</div>
    `;

    const repos = $('#compareRepos').value
      .split(/[\n,;]/)
      .map(s => s.trim())
      .filter(Boolean);

    if (repos.length < 2 || repos.length > 5) {
      target.hidden = true;
      showError(
        error,
        'Enter between 2 and 5 repositories, one per line.'
      );
      return;
    }

    try {
      const res = await fetch('/api/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ repos })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Comparison failed.');
      }

      target.innerHTML = data.results.map(x =>
        x.ok
          ? `
            <div class="compare-row">
              <a href="${safeUrl(x.url)}"
                 target="_blank"
                 rel="noopener">
                ${escapeHtml(x.repo)} ↗
              </a>
              <strong>${escapeHtml(x.score)}/100</strong>
              <span>
                ${escapeHtml(x.label)}
                · ${
                  x.days_since_last_commit == null
                    ? 'N/A'
                    : escapeHtml(x.days_since_last_commit) + 'd since commit'
                }
              </span>
            </div>
          `
          : `
            <div class="compare-row">
              <span>${escapeHtml(x.repo)}</span>
              <span class="error">Could not inspect</span>
              <span>${escapeHtml(x.error)}</span>
            </div>
          `
      ).join('');

    } catch (err) {
      target.hidden = true;
      showError(error, err.message);
    }
  });

  // --------------------------------------------------
  // FLOATING HELP ASSISTANT
  // --------------------------------------------------

  const helpOverlay = $('#helpOverlay');

  function openHelp() {
    helpOverlay.hidden = false;
    $('#helpQuestion').focus();
  }

  function closeHelp() {
    helpOverlay.hidden = true;
  }

  $('#helpFab').addEventListener('click', openHelp);
  $('#helpTop').addEventListener('click', openHelp);
  $('#closeHelp').addEventListener('click', closeHelp);

  helpOverlay.addEventListener('click', e => {
    if (e.target === helpOverlay) closeHelp();
  });

  const answers = {
    score: 'The vitality score runs from 0 to 100 and is a transparent heuristic based on observable signals such as commit recency, release recency, contributor concentration, and archive status. It is not a quality score and cannot reveal a maintainer’s intentions.',

    abandoned: 'We cannot know that from public activity alone. A repo can be stable, maintained privately, or intentionally quiet. The archive uses labels like “quiet” or “archived,” links to evidence, and tells you what it cannot establish.',

    privacy: 'The app requests public GitHub repository metadata for the repository you submit. It does not need your GitHub password. If you configure a personal access token, keep it in your local .env file and never commit it. Local API response caching may store public metadata on the server.',

    llm: 'Install Ollama, download the configured model (default: gemma3:4b), start Ollama, then enable the local AI checkbox before investigating. If Ollama is unavailable, the app falls back to its evidence-linked story template. AI prose should still be checked against citations.',

    compare: 'Open Compare repos in the sidebar, enter 2–5 public repositories one per line, and select Compare records. The results show their heuristic vitality scores side by side.',

    export: 'Open a live case file and choose EXPORT .MD. The report includes repository details, story, signals, evidence links, and caveats.'
  };

  function answerHelp(question) {
    const q = question.toLowerCase();

    if (q.includes('score') || q.includes('vital')) {
      return answers.score;
    }

    if (
      q.includes('abandon') ||
      q.includes('dead') ||
      q.includes('quiet')
    ) {
      return answers.abandoned;
    }

    if (
      q.includes('data') ||
      q.includes('privacy') ||
      q.includes('token')
    ) {
      return answers.privacy;
    }

    if (
      q.includes('ollama') ||
      q.includes('gemma') ||
      q.includes('ai')
    ) {
      return answers.llm;
    }

    if (q.includes('compare')) {
      return answers.compare;
    }

    if (
      q.includes('export') ||
      q.includes('download')
    ) {
      return answers.export;
    }

    if (
      q.includes('investigat') ||
      q.includes('start') ||
      q.includes('repo')
    ) {
      return 'Use the Investigate section. Enter owner/repository or paste a public GitHub URL, optionally enable local Ollama, then press the arrow. The case file will show the score, story, reasons, and evidence links.';
    }

    return 'I can help with repository investigations, vitality scores, evidence, comparisons, exports, and local AI. Try one of the quick questions above, or ask me about one of those topics.';
  }

  $$('.help-prompts button').forEach(button => {
    button.addEventListener('click', () => {
      const answer = $('#helpAnswer');
      answer.textContent =
        answers[button.dataset.help] || 'Ask me about the archive.';
      answer.hidden = false;
    });
  });

  $('#helpForm').addEventListener('submit', e => {
    e.preventDefault();

    const question = $('#helpQuestion').value.trim();
    if (!question) return;

    const answer = $('#helpAnswer');
    answer.textContent = answerHelp(question);
    answer.hidden = false;
    $('#helpQuestion').value = '';
  });

  // --------------------------------------------------
  // SIDEBAR NAVIGATION
  // --------------------------------------------------

  const navLinks = $$('.nav-link');

  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navLinks.forEach(x => x.classList.remove('active'));
      link.classList.add('active');

      $('#crumbCurrent').textContent = link.textContent
        .replace(/[⌂⌕▤⇄◉✳]/g, '')
        .replace(/\d+/g, '')
        .trim()
        .toUpperCase();

      $('#sidebar').classList.remove('open');
    });
  });

  $('#mobileMenu').addEventListener('click', () => {
    $('#sidebar').classList.toggle('open');
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeHelp();
      $('#sidebar').classList.remove('open');
    }
  });
})();
