// Second, independent check (runs only for gate candidates, after verifyGrounding).
// The verifier did not write the draft; it re-searches SupportKB and must confirm
// every claim and every customer question. Both lists must be reported and empty,
// and both booleans strictly true, or the ticket goes to human review.
const v = $vars.verifyGrounding.output || {};

const text = x => (typeof x === 'string' ? x.trim() : '');
const strictTrue = x => x === true || text(x).toLowerCase() === 'true';
const toList = x => (Array.isArray(x) ? x.map(i => text(i)).filter(i => i.length > 0) : null);

const unsupported = toList(v.unsupportedClaims);
const unanswered = toList(v.unansweredQuestions);
const failures = [];
if (!strictTrue(v.draftGrounded)) failures.push('verifier did not confirm the draft is grounded (draftGrounded=' + JSON.stringify(v.draftGrounded) + ')');
if (!strictTrue(v.answersEveryQuestion)) failures.push('verifier did not confirm every question is answered (answersEveryQuestion=' + JSON.stringify(v.answersEveryQuestion) + ')');
if (unsupported === null) failures.push('verifier did not report unsupportedClaims');
else if (unsupported.length) failures.push('claims not found in SupportKB: ' + unsupported.join('; '));
if (unanswered === null) failures.push('verifier did not report unansweredQuestions');
else if (unanswered.length) failures.push('questions the draft does not answer: ' + unanswered.join('; '));

return {
  verified: failures.length === 0,
  verificationFailures: failures,
  verificationSummary: failures.length === 0
    ? 'Auto-resolved: deterministic gate passed and independent verifier confirmed every claim against SupportKB. ' + text(v.verdictNotes)
    : 'Grounding check failed: ' + failures.join(' | ') + (text(v.verdictNotes) ? ' | Verifier notes: ' + text(v.verdictNotes) : '')
};
