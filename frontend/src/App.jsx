import { useMemo, useState } from 'react';
import { analyzeCase, getJudgment, retrieveJudgments } from './api.js';

const EXAMPLES = [
  {
    label: 'Employment',
    text: 'My client was terminated from his employment without receiving any notice or opportunity to explain his position.',
  },
  {
    label: 'Contract',
    text: 'A supplier failed to deliver equipment by the agreed date, and our client incurred documented losses after repeated written requests for performance.',
  },
  {
    label: 'Property',
    text: 'My client has occupied inherited land for many years, but a relative is now disputing the title and has started construction on part of the property.',
  },
];

function Icon({ name, size = 18, strokeWidth = 1.8 }) {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true };
  const paths = {
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    back: <><path d="M19 12H5"/><path d="m11 18-6-6 6-6"/></>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 1 4 17.5z"/><path d="M4 17.5A2.5 2.5 0 0 1 6.5 15H20M8 7h8M8 10h7"/></>,
    check: <><path d="m5 12 4 4L19 6"/></>,
    chevron: <><path d="m9 18 6-6-6-6"/></>,
    close: <><path d="m18 6-12 12M6 6l12 12"/></>,
    compare: <><path d="M8 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h3M16 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M8 12h8M8 8h8M8 16h5"/></>,
    document: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h8"/></>,
    external: <><path d="M14 3h7v7M10 14 21 3"/><path d="M19 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h6"/></>,
    filter: <><path d="M4 7h16M7 12h10m-7 5h4"/><circle cx="8" cy="7" r="1.5" fill="currentColor"/><circle cx="15" cy="12" r="1.5" fill="currentColor"/></>,
    gavel: <><path d="m14 5 5 5M12 7l5 5M3 21l7-7M7 11l6 6M5 9l4-4 6 6-4 4zM14 18h7"/></>,
    info: <><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4.5 4.5"/></>,
    spark: <><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-2-5.8L4 11l6-2.2zM19 15l1 2.5 2 1-2 1-1 2.5-1-2.5-2-1 2-1z"/></>,
    scales: <><path d="M12 3v18M5 7h14M7 7l-4 7h8L7 7zm10 0-4 7h8l-4-7zM8 21h8"/></>,
    shield: <><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/><path d="m9 12 2 2 4-4"/></>,
    sliders: <><path d="M4 7h9M17 7h3M4 17h3m4 0h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/></>,
    sparkles: <><path d="m12 3 1.4 5.6L19 10l-5.6 1.4L12 17l-1.4-5.6L5 10l5.6-1.4zM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></>,
    x: <><path d="m18 6-12 12M6 6l12 12"/></>,
  };
  return <svg {...common}>{paths[name] || paths.spark}</svg>;
}

function Brand() {
  return (
    <a className="brand" href="#top" aria-label="NyayaAI home">
      <span className="brand-mark"><Icon name="scales" size={20} strokeWidth={1.7} /></span>
      <span className="brand-name">nyaya<span>ai</span><small>LEGAL RESEARCH</small></span>
    </a>
  );
}

function StepHeader({ stage, onReset }) {
  const steps = ['Describe', 'Review', 'Research'];
  return (
    <header className="topbar" id="top">
      <Brand />
      <nav className="step-nav" aria-label="Research progress">
        {steps.map((step, index) => {
          const activeIndex = stage === 'home' ? 0 : stage === 'analysis' ? 1 : 2;
          const isDone = index < activeIndex;
          return <div className={`step-item ${index === activeIndex ? 'active' : ''} ${isDone ? 'done' : ''}`} key={step}>
            <span className="step-number">{isDone ? <Icon name="check" size={13} /> : `0${index + 1}`}</span>{step}
          </div>;
        })}
      </nav>
      <button className="top-action" onClick={onReset}><Icon name="plus" size={16} /> New research</button>
    </header>
  );
}

function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;
  return <div className="error-banner" role="alert"><Icon name="info" size={17} /><span>{message}</span><button aria-label="Dismiss error" onClick={onDismiss}><Icon name="close" size={16} /></button></div>;
}

function Home({ description, setDescription, onAnalyze, loading, error, dismissError }) {
  return (
    <main className="page-shell home-page page-enter">
      <div className="hero-grid">
        <section className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-line" /> PRECEDENT RESEARCH, WITH PURPOSE</div>
          <h1>Find the law<br />behind <em>your facts.</em></h1>
          <p className="hero-description">Turn a case narrative into a focused search across Indian judgments—with the source material always in view.</p>
          <div className="hero-trust">
            <div className="trust-icon"><Icon name="shield" size={18} /></div>
            <span><strong>Built for careful research</strong><small>Sources stay attached. You stay in control.</small></span>
          </div>
        </section>
        <section className="input-card" aria-labelledby="describe-title">
          <div className="card-topline"><span className="card-step">01</span><span>START WITH THE FACTS</span><span className="private-note"><Icon name="sparkles" size={13} /> AI-assisted</span></div>
          <h2 id="describe-title">Describe the matter</h2>
          <p className="card-subtitle">Share the key events, what happened, and what is in dispute.</p>
          <ErrorBanner message={error} onDismiss={dismissError} />
          <label className="sr-only" htmlFor="case-description">Case description</label>
          <textarea id="case-description" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="For example: My client was dismissed without notice or an opportunity to respond..." maxLength={20000} />
          <div className="input-footer"><span>{description.length.toLocaleString()} / 20,000</span><span><Icon name="info" size={13} /> Avoid names or identifying details</span></div>
          <button className="primary-button analyze-button" onClick={onAnalyze} disabled={loading || description.trim().length < 20}>
            {loading ? <><span className="spinner" /> Understanding your case</> : <>Understand this case <Icon name="arrow" size={17} /></>}
          </button>
          <div className="disclaimer"><Icon name="info" size={14} /><span>Your description is sent to the configured AI provider for analysis and is not stored by NyayaAI. Research support only; no legal advice or outcome predictions.</span></div>
        </section>
      </div>
      <section className="examples-section">
        <div className="examples-heading"><span>NEED A STARTING POINT?</span><span>Choose an example to fill the description</span></div>
        <div className="example-row">{EXAMPLES.map((example, index) => <button key={example.label} className="example-card" onClick={() => setDescription(example.text)}>
          <span className="example-index">0{index + 1}</span><span><strong>{example.label}</strong><small>{example.text}</small></span><Icon name="chevron" size={17} />
        </button>)}</div>
      </section>
      <div className="home-footnote"><span>INDIAN CASE LAW</span><span className="footnote-dot" /><span>HUMAN-LED REVIEW</span><span className="footnote-dot" /><span>SOURCE-GROUNDED</span></div>
    </main>
  );
}

function EditableList({ title, hint, items, setItems, icon }) {
  const [draft, setDraft] = useState('');
  function addItem(event) {
    event.preventDefault();
    const value = draft.trim();
    if (value && !items.includes(value)) setItems([...items, value]);
    setDraft('');
  }
  return <section className="edit-section">
    <div className="edit-section-heading"><span className="edit-icon"><Icon name={icon} size={16} /></span><span><strong>{title}</strong><small>{hint}</small></span><span className="edit-count">{items.length}</span></div>
    <div className="editable-items">{items.map((item, index) => <div className="editable-item" key={`${item}-${index}`}>
      <span className="item-bullet" />
      <input aria-label={`${title} item ${index + 1}`} value={item} onChange={(event) => setItems(items.map((entry, itemIndex) => itemIndex === index ? event.target.value : entry))} />
      <button aria-label={`Remove ${item}`} onClick={() => setItems(items.filter((_, itemIndex) => itemIndex !== index))}><Icon name="close" size={14} /></button>
    </div>)}</div>
    <form className="add-item-form" onSubmit={addItem}><Icon name="plus" size={15} /><input aria-label={`Add ${title}`} value={draft} onChange={(event) => setDraft(event.target.value)} placeholder={`Add a ${title.toLowerCase().replace(/s$/, '')}...`} /><button type="submit" disabled={!draft.trim()}>Add</button></form>
  </section>;
}

function Analysis({ source, analysis, setAnalysis, onBack, onSearch, loading, error, dismissError }) {
  const update = (key, value) => setAnalysis({ ...analysis, [key]: value });
  return (
    <main className="page-shell workflow-page page-enter">
      <button className="back-link" onClick={onBack}><Icon name="back" size={16} /> Edit case description</button>
      <div className="workflow-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> CASE UNDERSTANDING</div><h1>Review the research brief.</h1><p>Check the extracted information and adjust it before searching. Your edits shape the queries.</p></div><div className="review-badge"><Icon name="spark" size={16} /> Draft for your review</div></div>
      <div className="source-strip"><span className="source-label">CASE DESCRIPTION</span><p>“{source}”</p></div>
      <ErrorBanner message={error} onDismiss={dismissError} />
      <div className="analysis-grid">
        <div className="analysis-main">
          <div className="category-card"><div className="category-icon"><Icon name="gavel" size={20} /></div><div><span>INDICATIVE CASE AREA</span><strong>{analysis.case_category}</strong></div><span className="ai-note"><Icon name="sparkles" size={14} /> AI extracted</span></div>
          <EditableList title="Key facts" hint="Events stated in your description" icon="document" items={analysis.facts} setItems={(items) => update('facts', items)} />
          <EditableList title="Potential legal issues" hint="Questions to investigate in the judgments" icon="scales" items={analysis.legal_issues} setItems={(items) => update('legal_issues', items)} />
        </div>
        <aside className="analysis-aside">
          <EditableList title="Search queries" hint="Terms sent to Indian Kanoon" icon="search" items={analysis.search_queries} setItems={(items) => update('search_queries', items)} />
          <div className="terminology-card"><div className="terminology-title"><span className="edit-icon"><Icon name="sparkles" size={15} /></span><span><strong>Legal terminology</strong><small>Suggested search language</small></span></div><div className="term-chips">{analysis.legal_terminology.map((term, index) => <span key={`${term}-${index}`}>{term}</span>)}</div></div>
          <div className="review-note"><Icon name="info" size={16} /><p>These are research prompts, not conclusions about the law. Confirm or edit them before continuing.</p></div>
        </aside>
      </div>
      <div className="workflow-footer"><span className="footer-hint"><Icon name="shield" size={15} /> Search uses your edited brief; it isn’t stored by NyayaAI.</span><button className="primary-button" onClick={onSearch} disabled={loading || !analysis.search_queries.length || !analysis.facts.length}>
        {loading ? <><span className="spinner" /> Searching judgments</> : <>Search Indian judgments <Icon name="arrow" size={17} /></>}
      </button></div>
    </main>
  );
}

function FilterPanel({ court, setCourt, fromdate, setFromdate, todate, setTodate, onApply, disabled }) {
  return <aside className="filter-panel">
    <div className="filter-title"><span className="filter-icon"><Icon name="sliders" size={17} /></span><strong>Refine search</strong></div>
    <label>Court</label><select value={court} onChange={(event) => setCourt(event.target.value)}><option value="">All indexed courts</option><option>Supreme Court</option><option>Delhi High Court</option><option>Bombay High Court</option><option>Madras High Court</option><option>Calcutta High Court</option><option>Kerala High Court</option><option>All High Courts</option></select>
    <label>Judgment date</label><div className="date-fields"><input aria-label="From date" placeholder="DD-MM-YYYY" value={fromdate} onChange={(event) => setFromdate(event.target.value)} /><span>to</span><input aria-label="To date" placeholder="DD-MM-YYYY" value={todate} onChange={(event) => setTodate(event.target.value)} /></div>
    <button className="secondary-button filter-apply" onClick={onApply} disabled={disabled}><Icon name="filter" size={15} /> Apply filters</button>
    <div className="filter-divider" />
    <div className="source-note"><Icon name="info" size={16} /><p>Results come from Indian Kanoon. Check the original judgment before relying on a passage.</p></div>
    <a className="ik-attribution" href="https://indiankanoon.org/" target="_blank" rel="noreferrer">Powered by <strong>IKanoon</strong><Icon name="external" size={12} /></a>
  </aside>;
}

function JudgmentCard({ judgment, index, selected, onSelect, onOpen }) {
  return <article className="judgment-card" style={{ '--card-index': index }}>
    <div className="judgment-card-top"><span className="result-number">{String(index + 1).padStart(2, '0')}</span><span className="relevance-label"><span className="relevance-dot" /> {Math.round(judgment.keyword_score * 100)}% keyword overlap</span><label className="compare-check"><input type="checkbox" checked={selected} onChange={onSelect} /><span>Compare</span></label></div>
    <button className="judgment-title-button" onClick={onOpen}><h3>{judgment.case_name}</h3><Icon name="external" size={15} /></button>
    <div className="case-meta"><span>{judgment.court || 'Court unavailable'}</span><i /> <span>{judgment.judgment_date || 'Date unavailable'}</span>{judgment.case_number && <><i /><span>{judgment.case_number}</span></>}</div>
    {judgment.matched_terms?.length > 0 && <div className="match-row"><span>Matched terms</span>{judgment.matched_terms.slice(0, 5).map((term) => <span className="match-chip" key={term}>{term}</span>)}</div>}
    <div className="passage-list">{judgment.passages?.slice(0, 2).map((passage, passageIndex) => <blockquote key={`${judgment.document_id}-${passageIndex}`}><span className="quote-mark">“</span><p>{passage.text}</p><span className="passage-score">{Math.round(passage.keyword_score * 100)}% overlap</span></blockquote>)}</div>
    <div className="judgment-card-footer"><a href={judgment.source_url} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>Original source <Icon name="external" size={13} /></a><button onClick={onOpen}>View judgment <Icon name="arrow" size={14} /></button></div>
  </article>;
}

function Results({ result, error, dismissError, court, setCourt, fromdate, setFromdate, todate, setTodate, onApply, onBack, onOpen, selected, onSelect, onCompare, loading }) {
  const [sort, setSort] = useState('relevance');
  const judgments = useMemo(() => [...result.judgments].sort((a, b) => sort === 'relevance' ? b.keyword_score - a.keyword_score : (a.case_name || '').localeCompare(b.case_name || '')), [result.judgments, sort]);
  return <main className="page-shell results-page page-enter">
    <button className="back-link" onClick={onBack}><Icon name="back" size={16} /> Back to research brief</button>
    <div className="results-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> PRECEDENT SEARCH</div><h1>Judgments for your brief.</h1><p>Search phrases are based on your reviewed facts and issues.</p></div><div className="results-count"><strong>{result.judgments.length}</strong><span>judgments retrieved</span></div></div>
    <div className="attribution-banner"><span className="attribution-mark"><Icon name="book" size={15} /></span><span>Search results powered by <strong>IKanoon</strong></span><a href="https://indiankanoon.org/" target="_blank" rel="noreferrer">Visit source <Icon name="external" size={12} /></a></div>
    <div className="query-summary"><Icon name="search" size={16} /><span>SEARCHED</span><div>{result.searched_queries.map((query) => <span className="query-pill" key={query}>{query}</span>)}</div></div>
    <ErrorBanner message={error} onDismiss={dismissError} />
    {result.warnings?.length > 0 && <div className="warning-note"><Icon name="info" size={16} /><span>{result.warnings.join(' ')}</span></div>}
    <div className="results-layout">
      <div className="results-main">
        <div className="results-toolbar"><div><strong>Retrieved judgments</strong><span>Ranked by lexical match against your brief</span></div><label className="sort-control"><span>Sort</span><select value={sort} onChange={(event) => setSort(event.target.value)}><option value="relevance">Keyword overlap</option><option value="title">Case name</option></select></label></div>
        {judgments.length ? <div className="judgment-list">{judgments.map((judgment, index) => <JudgmentCard key={judgment.document_id} judgment={judgment} index={index} selected={selected.includes(judgment.document_id)} onSelect={() => onSelect(judgment.document_id)} onOpen={() => onOpen(judgment)} />)}</div> : <div className="empty-results"><div className="empty-icon"><Icon name="book" size={22} /></div><h2>No judgments returned</h2><p>Try broadening your search phrases or removing a court or date filter from the brief.</p><button className="secondary-button" onClick={onBack}>Review search phrases</button></div>}
        <div className="results-disclaimer"><Icon name="info" size={15} /><span>Keyword overlap helps surface text. It does not establish legal similarity, binding status, or whether a decision remains good law.</span></div>
      </div>
      <FilterPanel court={court} setCourt={setCourt} fromdate={fromdate} setFromdate={setFromdate} todate={todate} setTodate={setTodate} onApply={onApply} disabled={loading} />
    </div>
    {selected.length >= 2 && <div className="compare-bar"><span><Icon name="compare" size={17} /> <strong>{selected.length} judgments selected</strong> for comparison</span><button className="primary-button" onClick={onCompare}>Compare selected <Icon name="arrow" size={15} /></button></div>}
    {selected.length === 1 && <div className="selection-hint">Select one more judgment to compare their matched passages.</div>}
  </main>;
}

function DetailDrawer({ judgment, detail, loading, error, onClose, onDismissError }) {
  if (!judgment) return null;
  return <div className="drawer-backdrop" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
    <section className="detail-drawer" role="dialog" aria-modal="true" aria-labelledby="detail-title">
      <div className="drawer-header"><span className="drawer-kicker"><Icon name="document" size={15} /> JUDGMENT DETAIL</span><button className="icon-button" aria-label="Close detail" onClick={onClose}><Icon name="close" /></button></div>
      <h2 id="detail-title">{judgment.case_name}</h2><div className="case-meta drawer-meta"><span>{judgment.court || 'Court unavailable'}</span><i /><span>{judgment.judgment_date || 'Date unavailable'}</span></div>
      <a className="source-button" href={judgment.source_url} target="_blank" rel="noreferrer">Open original Indian Kanoon page <Icon name="external" size={15} /></a>
      {error && <ErrorBanner message={error} onDismiss={onDismissError} />}
      {loading ? <div className="drawer-loading"><span className="spinner dark" /> Retrieving judgment text from source…</div> : detail && <>
        <div className="evidence-heading"><span>FULL TEXT</span><span>{detail.full_text.length.toLocaleString()} characters</span></div>
        <div className="full-text">{detail.full_text}</div>
      </>}
      <div className="drawer-footnote"><Icon name="shield" size={15} /> Verify the source text and context before citing.</div>
    </section>
  </div>;
}

function Comparison({ selectedJudgments, onBack, onOpen }) {
  const commonTerms = useMemo(() => {
    if (selectedJudgments.length < 2) return [];
    const all = selectedJudgments.map((judgment) => new Set(judgment.matched_terms || []));
    return [...all[0]].filter((term) => all.every((set) => set.has(term)));
  }, [selectedJudgments]);
  return <main className="page-shell compare-page page-enter">
    <button className="back-link" onClick={onBack}><Icon name="back" size={16} /> Back to results</button>
    <div className="workflow-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> SIDE-BY-SIDE REVIEW</div><h1>Compare retrieved judgments.</h1><p>Review source details and overlapping evidence across your selected cases.</p></div><div className="review-badge"><Icon name="info" size={15} /> Research aid</div></div>
    {commonTerms.length > 0 && <div className="common-terms"><span>TERMS FOUND IN ALL SELECTED CASES</span><div>{commonTerms.map((term) => <span className="match-chip" key={term}>{term}</span>)}</div></div>}
    <div className="comparison-grid">{selectedJudgments.map((judgment, index) => <article className="comparison-column" key={judgment.document_id} style={{ '--card-index': index }}>
      <div className="comparison-number">CASE 0{index + 1}</div><button className="comparison-title" onClick={() => onOpen(judgment)}>{judgment.case_name}<Icon name="external" size={14} /></button>
      <div className="case-meta"><span>{judgment.court || 'Court unavailable'}</span><i /><span>{judgment.judgment_date || 'Date unavailable'}</span></div>
      <div className="compare-score"><span>Keyword overlap</span><strong>{Math.round(judgment.keyword_score * 100)}%</strong></div>
      <div className="comparison-section"><span>MATCHED TERMS</span><div className="term-chips">{judgment.matched_terms?.length ? judgment.matched_terms.map((term) => <span className={commonTerms.includes(term) ? 'shared-term' : ''} key={term}>{term}</span>) : <small>No matching terms identified</small>}</div></div>
      <div className="comparison-section"><span>RETRIEVED PASSAGES</span>{judgment.passages?.length ? judgment.passages.map((passage, passageIndex) => <blockquote className="comparison-quote" key={passageIndex}><p>{passage.text}</p><small>{Math.round(passage.keyword_score * 100)}% keyword overlap</small></blockquote>) : <small>No matching passages returned.</small>}</div>
      <a className="comparison-source" href={judgment.source_url} target="_blank" rel="noreferrer">Open source <Icon name="external" size={13} /></a>
    </article>)}</div>
    <div className="comparison-disclaimer"><Icon name="info" size={17} /><p>Shared words are not proof that the courts addressed the same legal question. Read each full judgment and verify its legal status independently.</p></div>
  </main>;
}

export default function App() {
  const [stage, setStage] = useState('home');
  const [description, setDescription] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [court, setCourt] = useState('');
  const [fromdate, setFromdate] = useState('');
  const [todate, setTodate] = useState('');
  const [selected, setSelected] = useState([]);
  const [comparing, setComparing] = useState(false);
  const [detailJudgment, setDetailJudgment] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');

  function reset() {
    setStage('home'); setDescription(''); setAnalysis(null); setResults(null); setError(''); setSelected([]); setComparing(false); setCourt(''); setFromdate(''); setTodate(''); setDetailJudgment(null); setDetail(null); setDetailError('');
  }

  async function handleAnalyze() {
    setLoading(true); setError(''); setComparing(false);
    try {
      const response = await analyzeCase(description.trim());
      setAnalysis(response); setResults(null); setSelected([]); setStage('analysis');
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  async function handleSearch() {
    setLoading(true); setError('');
    try {
      const response = await retrieveJudgments({
        facts: analysis.facts.filter(Boolean),
        legal_issues: analysis.legal_issues.filter(Boolean),
        search_queries: analysis.search_queries.filter(Boolean),
        court: court || null,
        fromdate: fromdate || null,
        todate: todate || null,
        max_judgments: 5,
        passages_per_judgment: 3,
      });
      setResults(response); setSelected([]); setComparing(false); setStage('results');
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }

  async function openJudgment(judgment) {
    setDetailJudgment(judgment); setDetail(null); setDetailError(''); setDetailLoading(true);
    try { setDetail(await getJudgment(judgment.document_id)); }
    catch (requestError) { setDetailError(requestError.message); }
    finally { setDetailLoading(false); }
  }

  function toggleSelected(documentId) {
    if (selected.includes(documentId)) setSelected(selected.filter((id) => id !== documentId));
    else if (selected.length >= 3) setError('Compare up to three judgments at a time.');
    else setSelected([...selected, documentId]);
  }

  const selectedJudgments = useMemo(() => (results?.judgments || []).filter((judgment) => selected.includes(judgment.document_id)), [results, selected]);

  return <div className="app-frame">
    <StepHeader stage={stage} onReset={reset} />
    {stage === 'home' && <Home description={description} setDescription={setDescription} onAnalyze={handleAnalyze} loading={loading} error={error} dismissError={() => setError('')} />}
    {stage === 'analysis' && analysis && <Analysis source={description} analysis={analysis} setAnalysis={setAnalysis} onBack={() => setStage('home')} onSearch={handleSearch} loading={loading} error={error} dismissError={() => setError('')} />}
    {stage === 'results' && results && !comparing && <Results result={results} error={error} dismissError={() => setError('')} court={court} setCourt={setCourt} fromdate={fromdate} setFromdate={setFromdate} todate={todate} setTodate={setTodate} onApply={handleSearch} onBack={() => setStage('analysis')} onOpen={openJudgment} selected={selected} onSelect={toggleSelected} onCompare={() => setComparing(true)} loading={loading} />}
    {stage === 'results' && results && comparing && <Comparison selectedJudgments={selectedJudgments} onBack={() => setComparing(false)} onOpen={openJudgment} />}
    <footer className="app-footer"><Brand /><span>Legal research support, designed for human judgment.</span><span className="footer-version">NYAYAAI · PRECEDENT RESEARCH</span></footer>
    <DetailDrawer judgment={detailJudgment} detail={detail} loading={detailLoading} error={detailError} onDismissError={() => setDetailError('')} onClose={() => { setDetailJudgment(null); setDetail(null); }} />
  </div>;
}
