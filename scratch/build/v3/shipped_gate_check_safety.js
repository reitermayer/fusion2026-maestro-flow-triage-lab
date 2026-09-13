// Deterministic safety gate for TriageTicketV3 (runs right after classifyAndDraft).
// The agent's kbCovered / kbSources / kbGaps are claims, not proof. A ticket only
// becomes an auto-resolve candidate when every check below passes; anything
// missing, malformed, or unexpected fails closed to human review. Candidates are
// then re-checked by the independent verifyGrounding agent before anything is sent.
const out = $vars.classifyAndDraft.output || {};

// The 14 SupportKB articles (bucket SupportKBDocs, Shared folder) as of 2026-09-13.
// A citation outside this list blocks auto-resolve, so adding an article only
// costs autonomy until this list is updated; it can never let a ticket through.
const KB_DOCS = [
  'kb-01-password-reset', 'kb-02-vpn-setup', 'kb-03-expense-reports', 'kb-04-mfa-enrollment',
  'kb-05-software-requests', 'kb-06-email-signature', 'kb-07-printers', 'kb-08-guest-wifi',
  'kb-09-laptop-hardware', 'kb-10-phishing', 'kb-11-onboarding', 'kb-12-meeting-rooms',
  'kb-13-hr-portal-access', 'kb-14-service-desk'
];
const AUTO_CATEGORIES = ['access', 'hardware', 'software', 'network', 'billing', 'other'];
const AUTO_PRIORITIES = ['low', 'medium'];
const URGENT_PRIORITIES = ['critical', 'high', 'urgent'];
const NOISE_MIN_CONFIDENCE = 0.8;
const AUTO_MIN_CONFIDENCE = 0.85;
// A reply that escalates, promises follow-up, or leaks internal tooling is not a
// resolution, whatever the flags say. Matched case-insensitively on the draft.
const BLOCKED_DRAFT_PHRASES = [
  'escalat', 'specialist', 'on-call', 'get back to you', 'follow up with you', 'look into',
  'supportkb', 'knowledge base', 'helpdesk article', 'runbook', 'published article',
  "i don't have", 'i do not have', "we don't have", 'we do not have',
  'unable to confirm', 'cannot confirm', "can't confirm",
  '[', ']', '{' + '{', '}' + '}', 'placeholder', 'tbd'  // braces split: the validator flags literal mustaches
];

const text = v => (typeof v === 'string' ? v.trim() : '');
const lower = v => text(v).toLowerCase();
const strictTrue = v => v === true || lower(v) === 'true';
const strictFalse = v => v === false || lower(v) === 'false';
const toNumber = v => {
  if (typeof v === 'number') return v;
  const s = text(v);
  return s !== '' && !isNaN(Number(s)) ? Number(s) : NaN;
};
const toList = v => (Array.isArray(v) ? v.map(x => text(x)).filter(x => x.length > 0) : null);
// Accepts "kb-01-password-reset", "kb-01-password-reset.txt", "kb-01" or a path;
// anything else (a title, a URL, an invented article) is not a citation.
const canonicalDoc = s => {
  const name = s.toLowerCase().split('/').pop().split('\\').pop().trim();
  const i = name.indexOf('kb-');
  if (i !== 0) return null;
  const prefix = name.substring(0, 5);
  const doc = KB_DOCS.find(d => d.startsWith(prefix)) || null;
  const rest = name.replace('.txt', '');
  return doc && (rest === prefix || rest === doc) ? doc : null;
};

const category = lower(out.category);
const priority = lower(out.priority);
const confidence = toNumber(out.confidence);
const kbSources = toList(out.kbSources);
const kbGaps = toList(out.kbGaps);
const draft = text(out.draftReply);
const draftForMatching = draft.toLowerCase().split('’').join("'");
const kbSourcesText = kbSources && kbSources.length ? kbSources.join(', ') : '(none)';
const kbGapsText = kbGaps === null ? '(not reported)' : (kbGaps.length ? kbGaps.join('; ') : '(none)');

let route;
const failures = [];
if (category === 'noise' && confidence >= NOISE_MIN_CONFIDENCE) {
  route = 'noise';
} else if (URGENT_PRIORITIES.includes(priority)) {
  route = 'urgent';
  failures.push('priority is ' + (text(out.priority) || '(missing)') + '; urgent tickets always get a human');
} else {
  if (!AUTO_CATEGORIES.includes(category)) failures.push('category "' + text(out.category) + '" is not auto-resolvable');
  if (!AUTO_PRIORITIES.includes(priority)) failures.push('priority "' + text(out.priority) + '" is not Low or Medium');
  if (!(confidence >= AUTO_MIN_CONFIDENCE && confidence <= 1)) failures.push('confidence ' + (isNaN(confidence) ? '(missing)' : confidence) + ' is below ' + AUTO_MIN_CONFIDENCE);
  if (!strictTrue(out.kbCovered)) failures.push('agent did not mark the ticket as fully covered by SupportKB (kbCovered=' + JSON.stringify(out.kbCovered) + ')');
  if (kbGaps === null) failures.push('agent did not report kbGaps');
  else if (kbGaps.length) failures.push('agent flagged KB gaps: ' + kbGapsText);
  if (!strictFalse(out.needsStaffAction)) failures.push('resolution needs staff action (needsStaffAction=' + JSON.stringify(out.needsStaffAction) + ')');
  if (kbSources === null || kbSources.length === 0) failures.push('no SupportKB sources cited');
  else {
    const unknown = kbSources.filter(s => canonicalDoc(s) === null);
    if (unknown.length) failures.push('cited sources that are not SupportKB articles: ' + unknown.join(', '));
  }
  if (!draft) failures.push('draft reply is empty');
  else {
    const hits = BLOCKED_DRAFT_PHRASES.filter(p => draftForMatching.includes(p));
    if (hits.length) failures.push('draft contains wording that is not a self-contained answer: ' + hits.map(h => '"' + h + '"').join(', '));
  }
  route = failures.length ? 'review' : 'verify';
}

const citedKbDocs = (kbSources || []).map(canonicalDoc).filter(d => d !== null)
  .filter((d, i, all) => all.indexOf(d) === i);

return {
  route: route,
  autoResolveCandidate: route === 'verify',
  gateFailures: failures,
  gateSummary: route === 'noise' ? 'Auto-skipped: automated noise (confidence ' + confidence + ')'
    : route === 'verify' ? 'Passed the deterministic gate; sent to the independent grounding check'
    : 'Not auto-resolved: ' + failures.join(' | '),
  kbCovered: strictTrue(out.kbCovered) && kbGaps !== null && kbGaps.length === 0,
  kbSourcesText: kbSourcesText,
  kbGapsText: kbGapsText,
  citedKbDocs: citedKbDocs.join(', ')
};
