"""Merge the blind AI-drafted random-audit records into artifacts/random_review.json.

The expected records were written from post text alone, before any prediction was seen, and are
recorded as AI reviews (ai_reviewed=True, human_reviewed=False) as the course permits. Error types
are derived mechanically by comparing each prediction with its expected record.
Usage: python merge_random_audit.py
"""
from datetime import datetime, timezone

from analysis_pipeline import Path, audit_sets, read_json, write_json

REVIEWER = 'Claude Opus 5.5 (AI reviewer, permitted by course policy); submitted by Matthew Walker'
FIELDS = {'brands': 'brand', 'relations': 'relation', 'links': 'attribute link', 'desires': 'desire',
          'directions': 'direction'}


def error_types(predicted, expected):
    pred, gold = audit_sets(predicted), audit_sets(expected)
    kinds = []
    for field, label in FIELDS.items():
        if pred[field] - gold[field]:
            kinds.append('extra ' + label)
        if gold[field] - pred[field]:
            kinds.append('missed ' + label)
    return kinds


def main():
    art = Path(__file__).resolve().parent / 'artifacts'
    reviews = read_json(art / 'random_review.json')
    drafts = read_json(art / 'random_audit_drafts.json')
    if reviews is None or drafts is None:
        raise SystemExit('Copy random_review.json from Drive into artifacts/ first.')
    now = datetime.now(timezone.utc).isoformat()
    for a in reviews:
        draft = drafts[str(a['post_id'])]
        a['expected'] = draft['expected']
        a['error_types'] = error_types(a['predicted'], a['expected']) if a.get('predicted') else ['missing prediction']
        a['notes'] = ('Blind AI review by Claude (Opus 5.5): expected record written from the post text before '
                      'the prediction was seen. ' + draft['note']).strip()
        a.update(reviewer=REVIEWER, reviewed_at=now, ai_reviewed=True, human_reviewed=False)
    write_json(art / 'random_review.json', reviews)
    print(f'merged {len(reviews)} random-audit reviews')


if __name__ == '__main__':
    main()
