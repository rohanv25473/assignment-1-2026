"""Task A-G rendering, shared by the standalone notebook and build command."""
from pathlib import Path
import itertools
import json
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

from analysis_pipeline import *


def note(text):
    display(Markdown(text))


def table(df, limit=None):
    with pd.option_context('display.max_rows', 70, 'display.max_columns', 18, 'display.max_colwidth', 130):
        display(df.head(limit) if limit else df)


def heatmap(df, title, center=None):
    fig, ax = plt.subplots(figsize=(9, max(4, len(df) * .58)))
    values = df.to_numpy(dtype=float)
    image = ax.imshow(np.ma.masked_invalid(values), cmap='YlGnBu', aspect='auto')
    ax.set_xticks(range(len(df.columns)), labels=df.columns, rotation=45, ha='right')
    ax.set_yticks(range(len(df)), labels=df.index)
    for i in range(len(df)):
        for j in range(len(df.columns)):
            if np.isfinite(values[i, j]):
                ax.text(j, i, f'{values[i,j]:.2f}', ha='center', va='center', fontsize=8,
                        color='white' if values[i,j] > np.nanmax(values) * .6 else 'black')
    ax.set_title(title)
    fig.colorbar(image, ax=ax, label='Association lift')
    fig.tight_layout()
    plt.show()
    plt.close(fig)


def plot_map(mapping, title):
    points = mapping['points']
    fig, ax = plt.subplots(figsize=(9, 6))
    for cluster, data in points.groupby('cluster'):
        ax.scatter(data.x, data.y, s=110, label='Cluster ' + str(cluster + 1))
    for name, row in points.iterrows():
        ax.annotate(name, (row.x, row.y), xytext=(6, 5), textcoords='offset points')
    ax.set(xlabel='MDS dimension 1 (no intrinsic meaning)', ylabel='MDS dimension 2 (no intrinsic meaning)',
           title=title + f"\nStress={mapping['stress']:.3f}; k={mapping['k']}; silhouette={mapping['silhouette']:.3f}")
    ax.legend()
    fig.tight_layout()
    plt.show()
    plt.close(fig)


def collect_artifacts(root):
    root = Path(root)
    names = ['source_profile.json', 'sample_plan.json', 'discovery.json', 'taxonomy.json',
             'pilot.json', 'freeze.json', 'extractions.json', 'usage.json',
             'development_review.json', 'random_review.json', 'targeted_review.json']
    return {name: read_json(root / 'artifacts' / name) for name in names
            if (root / 'artifacts' / name).exists()}


class Report:
    def __init__(self, source, bundle, root=None):
        self.posts, self.all_rows, self.profile = prepare(source)
        self.bundle = bundle
        self.root = Path(root) if root else None
        self.taxonomy = bundle.get('taxonomy.json')
        self.found = bundle.get('discovery.json')
        self.plan = sample_plan(self.posts)
        self.records = []
        self.complete = False
        self.maps = {}
        self.selected_brands = []
        self.selected_themes = []
        self.primary = None
        self.audit = None
        self.target_ids = []
        self.review_complete = False
        self.status = []
        saved_profile = bundle.get('source_profile.json')
        if saved_profile and saved_profile != self.profile:
            raise ValueError('Saved source/preparation profile differs from current code/input.')
        if self.taxonomy:
            validate_taxonomy(self.taxonomy, self.posts)
            self.provenance = provenance_hash(self.taxonomy)
            extraction = bundle.get('extractions.json')
            if extraction:
                if extraction['provenance'] != self.provenance:
                    raise ValueError('Embedded extraction provenance mismatch; regenerate explicitly.')
                self.records = extraction['records']
                subset = self.posts[self.posts.post_id.isin([r['post_id'] for r in self.records])]
                validate_records(self.records, subset, self.taxonomy)
                self.complete = len(self.records) == len(self.posts)
                if self.complete:
                    if bundle.get('freeze.json', {}).get('provenance') != self.provenance:
                        raise ValueError('Full extraction lacks its matching frozen development record.')
                    self.semantic = semantic_labels(self.records)
                    self.lexical = lexical_labels(self.posts, self.taxonomy)
                    self.brand_freq = frequency(self.semantic, self.posts, 'brands')
                    self.theme_freq = frequency(self.semantic, self.posts, 'themes')
                    self.names = self.brand_freq.head(10).label.tolist()
                    if len(self.names) != 10:
                        raise ValueError('Fewer than ten supported brands; cannot satisfy B/C.')
                    self.audit = audit_metrics(bundle.get('random_review.json', []), self.records,
                                               self.plan['holdout'], self.posts, self.taxonomy, self.provenance)

    def pending(self, task):
        note(f'**{task}: awaiting full validated extraction.** Saved coverage: '
             f'{len(self.records):,}/{len(self.posts):,} retained posts. No missing response is counted as a negative label.')

    def overview(self):
        note('**Execution status:** ' + ('Full corpus extracted; inspect audit readiness below.' if self.complete else
                                        'Implementation and source/NLP outputs are available; semantic generation is pending.'))
        table(pd.DataFrame([self.profile]).T.rename(columns={0: 'value'}))
        note('This is the supplied historical corpus, not a representative current-market sample. Date labels are '
             'preserved without assuming day/month or claiming exact chronology. Usernames are observed author IDs.')
        exclusions = self.all_rows.exclusion.replace('', 'retained').value_counts().rename_axis('disposition').reset_index(name='rows')
        table(exclusions)
        affected = self.posts[self.posts.cleaning.map(bool)]
        rows = []
        for rule in ['quote_marker_kia_hyundai', 'recursive_benz', 'like_i_said', 'as_i_said']:
            matched = affected[affected.cleaning.map(lambda changes: any(x['rule'] == rule for x in changes))]
            if len(matched):
                r = matched.iloc[0]
                rows.append({'rule': rule, 'posts': len(matched), 'example_post_id': r.post_id,
                             'raw_excerpt': r.raw_text[:240], 'clean_excerpt': r.clean_text[:240]})
        table(pd.DataFrame(rows))
        author = self.posts.author.value_counts()
        table(pd.DataFrame({'group': ['largest author', 'top ten authors'],
                            'posts': [author.iloc[0], author.head(10).sum()],
                            'share': [author.iloc[0]/len(self.posts), author.head(10).sum()/len(self.posts)]}))

    def task_a(self):
        if self.found:
            note('**Executed dictionary-free discovery:** ' + self.found['method'] +
                 '. These phrase candidates and context groups are discovery evidence, not final brand rankings.')
            table(pd.DataFrame(self.found['candidates']).drop(columns='examples'), 35)
            table(pd.DataFrame([{'context_group': t['cluster'], 'leading_phrases': ', '.join(t['terms'][:15]),
                                 'example_post_ids': ', '.join(str(e['post_id']) for e in t['examples'])}
                                for t in self.found['topics']]))
        if self.taxonomy:
            note('Corpus-derived mapping (full table retained in embedded records):')
            table(pd.DataFrame(self.taxonomy['aliases']))
            table(pd.DataFrame([{'theme': t['theme'], 'subattributes': ', '.join(s['name'] for s in t['subattributes']),
                                 'rationale': t['rationale']} for t in self.taxonomy['themes']]))
            table(pd.DataFrame(self.taxonomy['unresolved']))
        if not self.complete:
            self.pending('Final Task A frequencies')
            return
        note('The top ten are fixed by **semantic substantive-post prevalence**, with alphabetic tie ordering '
             'for reproducible display. All marques are eligible; author coverage is a companion check.')
        table(self.brand_freq)
        table(self.theme_freq)
        table(frequency(self.semantic, self.posts, 'subattributes'))
        raw = frequency(lexical_labels(self.posts, self.taxonomy, raw=True), self.posts, 'brands')
        clean = frequency(self.lexical, self.posts, 'brands')
        impact = raw[['label', 'posts']].merge(clean[['label', 'posts']], on='label', how='outer', suffixes=('_raw', '_clean')).fillna(0)
        impact['delta_posts'] = impact.posts_clean - impact.posts_raw
        table(impact.sort_values('delta_posts'))
        no_gm = frequency(semantic_labels(self.records, expansion=False), self.posts, 'brands')
        table(no_gm.head(15))
        note('The table above disables inferred GM labels. Cleaning and GM expansion can change ranking; '
             'B/C sensitivities keep the primary top-ten set fixed to isolate the measurement effect.')

    def task_b(self):
        if not self.complete:
            self.pending('Task B')
            return
        self.b, self.bc, self.bm = lift_matrices(self.lexical, self.names)
        heatmap(self.b, 'Task B: lexical same-post lift')
        table(self.bc)
        table(self.bm.rename('lexical_brand_posts').to_frame())
        self.b_off = lift_matrices(lexical_labels(self.posts, self.taxonomy, expansion=False), self.names)[0]
        heatmap(self.b_off, 'Task B sensitivity: GM expansion disabled')
        self.b_off_counts = lift_matrices(lexical_labels(self.posts, self.taxonomy, expansion=False), self.names)[1]
        strongest = [(a,b,self.b.loc[a,b],int(self.bc.loc[a,b])) for a,b in itertools.combinations(self.names,2)]
        table(pd.DataFrame(strongest, columns=['a','b','lift','pair_posts']).sort_values('lift', ascending=False).head(10))
        note('Lift is unsmoothed N × pair_posts / (brand_A_posts × brand_B_posts). Zero pairs produce zero lift '
             'with positive marginals. Missing marginals are undefined, and the displayed diagonal is blank. '
             'Pair counts below five are flagged as weak descriptive support, not evidence of significance.')

    def task_c(self):
        if not self.complete:
            self.pending('Task C')
            return
        if not hasattr(self, 'b'):
            self.b, self.bc, self.bm = lift_matrices(self.lexical, self.names)
        self.cm, _, _ = lift_matrices(self.semantic, self.names)
        self.c, self.cc, self.cmar = lift_matrices(self.semantic, self.names, relations=True)
        self.c_off = lift_matrices(semantic_labels(self.records, expansion=False), self.names, True)[0]
        self.c_uncertain = lift_matrices(semantic_labels(self.records, uncertain=True), self.names, True)[0]
        heatmap(self.c, 'Task C: relationship-filtered semantic lift')
        table(self.cc)
        table(self.cmar.rename('semantic_brand_posts').to_frame())
        heatmap(self.cm, 'Recognition-only comparison: semantic same-post lift')
        self.comparison, self.agreement = compare_matrices(self.b, self.cm, self.c, self.bc, self.cc)
        table(self.comparison)
        table(pd.DataFrame([self.agreement]))
        heatmap(self.c_off, 'Task C sensitivity: inferred GM labels disabled')
        heatmap(self.c_uncertain, 'Task C sensitivity: uncertain labels included')
        counts = []
        for field in ['brands', 'relations', 'attributes', 'aspirations']:
            counts.append({'event': field, 'supported': sum(e['certainty']=='supported' for r in self.records for e in r[field]),
                           'uncertain': sum(e['certainty']=='uncertain' for r in self.records for e in r[field])})
        table(pd.DataFrame(counts))
        table(self.audit)
        note('Random-audit metrics are micro-averages on only 40 posts. Rare-event recall and population accuracy '
             'remain uncertain; targeted checks are not pooled into this estimate. No completed human annotation '
             'means no demonstrated semantic accuracy.')
        # Show real evidence behind the largest changes, rather than invented causal explanations.
        texts = self.posts.set_index('post_id').clean_text.to_dict()
        lex = {r['post_id']: r for r in self.lexical}
        examples = []
        for row in self.comparison.reindex(self.comparison.total_delta.abs().sort_values(ascending=False).index).head(5).itertuples():
            pair = tuple(sorted((row.a,row.b)))
            for sem in self.semantic:
                old = row.a in lex[sem['post_id']]['brands'] and row.b in lex[sem['post_id']]['brands']
                new_mentions = row.a in sem['brands'] and row.b in sem['brands']
                new_relation = pair in sem['relations']
                if old != new_relation:
                    examples.append({'pair': f'{row.a} / {row.b}', 'post_id': sem['post_id'],
                                     'lexical_pair': old, 'semantic_comention': new_mentions,
                                     'semantic_relation': new_relation, 'GM_inferred': bool(sem['inherited']),
                                     'text': texts[sem['post_id']]})
                    break
        table(pd.DataFrame(examples))
        note('Recognition_delta isolates changed brand attribution. Relation_filter_delta changes the event itself '
             'and is not an accuracy improvement. The displayed posts expose evidence for interpretation; they '
             'do not independently prove why every aggregate difference occurred.')

    def task_d(self):
        if not self.complete:
            self.pending('Task D')
            return
        if not hasattr(self, 'c'):
            raise RuntimeError('Execute B and C before D.')
        met = self.audit.set_index('field')
        reliable = bool((met.reviewed_posts == 40).all() and
                        met.loc['brands','f1'] >= GATES['brand_f1'] and
                        met.loc['relations','f1'] >= GATES['relation_f1'] and
                        met.loc['relations','gold_events'] >= GATES['min_relation_gold'])
        observed = int(sum(self.cc.loc[a,b] > 0 for a,b in itertools.combinations(self.names,2)))
        supported_brands = (self.cmar > 0).all()
        self.primary = 'semantic' if reliable and observed >= GATES['observed_pairs'] and supported_brands else 'lexical'
        for name, matrix in [('lexical', self.b), ('semantic', self.c)]:
            try:
                self.maps[name] = map_brands(matrix)
                plot_map(self.maps[name], f'Task D: {name} map' + (' (primary)' if name == self.primary else ' (sensitivity)'))
                table(self.maps[name]['solutions'])
            except ValueError as exc:
                note(f'{name} map unavailable: {exc}')
        note(f'**Primary: {self.primary}.** The predeclared gate requires 40 human-reviewed random posts, brand F1 '
             f'≥ {GATES["brand_f1"]}, relation F1 ≥ {GATES["relation_f1"]}, at least 10 gold relation events '
             f'and 15 observed brand pairs. Observed pairs: {observed}; audit gate passed: {reliable}. '
             'These pragmatic thresholds do not certify market validity.')
        self.cluster_stable = False
        if len(self.maps) == 2:
            lex = self.maps['lexical']['points']
            sem = self.maps['semantic']['points']
            self.ari = float(adjusted_rand_score(lex.cluster, sem.cluster))
            self.cluster_stable = self.ari >= GATES['cluster_ari']
            neighborhoods = []
            for b in self.names:
                ln = self.b.loc[b].idxmax() if self.b.loc[b].notna().any() else None
                sn = self.c.loc[b].idxmax() if self.c.loc[b].notna().any() else None
                neighborhoods.append({'brand': b, 'lexical_closest': ln, 'semantic_closest': sn,
                                      'neighbor_changed': ln != sn, 'lexical_cluster': lex.loc[b,'cluster'],
                                      'semantic_cluster': sem.loc[b,'cluster']})
            table(pd.DataFrame(neighborhoods))
            note(f'Cluster agreement across measurement choices (adjusted Rand index): **{self.ari:.3f}**. '
                 'Numeric cluster IDs are arbitrary; ARI compares shared membership without treating ID changes as changes.')
        if self.primary in self.maps:
            points = self.maps[self.primary]['points']
            table(points[['cluster']].reset_index(names='brand'))
            if self.cluster_stable:
                for group in sorted(points.cluster.unique()):
                    members = set(points.index[points.cluster.eq(group)])
                    self.selected_brands.append(next(b for b in self.names if b in members))
        self.selected_brands += [b for b in self.names if b not in self.selected_brands]
        self.selected_brands = self.selected_brands[:5]
        # Distinct hierarchy was reconciled before extraction; select on marginal support only.
        self.selected_themes = self.theme_freq.head(5).label.tolist()
        note('**E selection locked before association scores:** ' + ', '.join(self.selected_brands) +
             '. ' + ('Stable-cluster leaders, filled by prevalence.' if self.cluster_stable else
                      'Predeclared fallback: the five most prevalent brands because cross-method cluster stability was not established.'))
        note('Within each map, average linkage clusters the full distance matrix; silhouette chooses among k=2,3,4 '
             '(smaller k breaks ties). MDS is nonmetric with 12 seeded starts. Many tied distances and high stress '
             'can distort apparent separation. The axes do not mean luxury or performance.')

    def task_e(self):
        if not self.complete:
            self.pending('Task E')
            return
        if not self.selected_brands:
            raise RuntimeError('Execute D to lock the five-brand selection before E.')
        self.pos = positioning(self.semantic, self.selected_brands, self.selected_themes)
        heatmap(self.pos.pivot(index='brand', columns='theme', values='lift'), 'Task E: supported brand-attribute links')
        table(self.pos)
        lexical = []
        for r in self.lexical:
            lexical.append(dict(r, links=set(itertools.product(r['brands'], r['themes']))))
        lexical_pos = positioning(lexical, self.selected_brands, self.selected_themes)
        noinherit = positioning(semantic_labels(self.records, inherit_attributes=False), self.selected_brands, self.selected_themes)
        sensitivity = self.pos[['brand','theme','lift']].merge(
            lexical_pos[['brand','theme','lift']], on=['brand','theme'], suffixes=('_semantic','_lexical'))
        sensitivity = sensitivity.merge(noinherit[['brand','theme','lift']], on=['brand','theme']).rename(columns={'lift':'lift_no_inherited_links'})
        table(sensitivity)
        table(pd.DataFrame([{
            'supported_attribute_records_without_resolved_target': sum(
                e['certainty']=='supported' and not e['targets'] for r in self.records for e in r['attributes']),
            'posts_with_inherited_GM_feature_links': sum(bool(r['inherited_links']) for r in self.semantic),
            'distinct_inherited_post_brand_theme_links': sum(len(r['inherited_links']) for r in self.semantic),
        }]))
        note('The inherited-link-off check keeps brand and theme marginals fixed and removes GM-level feature links. '
             'It differs from removing GM-expanded brand labels entirely. Theme marginals include unassigned features. '
             'Positive/negative evidence counts can overlap within a post; frequent discussion is not a strength.')
        support = self.pos[self.pos.linked_posts >= GATES['min_pair_support']].sort_values('lift', ascending=False).head(5)
        self.strong_associations = support
        examples = []
        for row in support.itertuples():
            ids = [r['post_id'] for r in self.semantic if (row.brand,row.theme) in r['links']]
            # Reuse previous reviews where possible.
            reviewed = set(self.plan['development'] + self.plan['holdout'])
            ids.sort(key=lambda i: (i not in reviewed, i))
            for i in ids[:2]:
                self.target_ids.append(i)
                r = next(r for r in self.records if r['post_id']==i)
                spans = [e['evidence'] for e in r['attributes'] if e['theme']==row.theme]
                examples.append({'brand':row.brand,'theme':row.theme,'post_id':i,'evidence':spans})
        table(pd.DataFrame(examples))
        note('These are the strongest associations with at least five linked posts, selected for targeted review. '
             'Two supporting passages check the interpretation; they cannot validate an entire association.')

    def task_f(self):
        if not self.complete:
            self.pending('Task F')
            return
        self.asp = aspiration(self.semantic, self.posts)
        table(self.asp)
        for column, title in [('concrete_authors','Concrete purchase-intent ranking'),
                              ('conditional_authors','Conditional/dream ownership ranking')]:
            note('**' + title + '** (all equal counts are ties):')
            table(self.asp[['brand',column,'discussing_authors']].sort_values(
                [column,'brand'],ascending=[False,True]))
        upper = aspiration(semantic_labels(self.records, uncertain=True), self.posts)
        off = aspiration(semantic_labels(self.records, expansion=False), self.posts)
        sensitivity = self.asp[['brand','aspiring_authors','fraction']].merge(
            upper[['brand','aspiring_authors']], on='brand', how='outer', suffixes=('','_including_uncertain'))
        sensitivity = sensitivity.merge(off[['brand','fraction']], on='brand', how='left', suffixes=('','_no_GM_expansion'))
        table(sensitivity)
        maximum = self.asp.aspiring_authors.max()
        self.winners = self.asp.loc[self.asp.aspiring_authors.eq(maximum),'brand'].tolist() if maximum else []
        note(('**Observed leader(s): ' + ', '.join(self.winners) + f'**, with {maximum} distinct aspiring authors each.'
              if self.winners else '**No supported aspiration events were extracted.**') +
             ' The ranking is descriptive and period-level. A later rejection is flagged, not subtracted. '
             'Concrete and conditional counts overlap; their union is the primary count. Usernames are not verified people.')
        positive = [r for r in self.records if any(e['category'] in ['concrete','conditional'] and
                    e['certainty']=='supported' and e['brand']!='GM' for e in r['aspirations'])]
        already = set(self.plan['development'] + self.plan['holdout'] + self.target_ids)
        positive.sort(key=lambda r:(not any(e['brand'] in self.winners for e in r['aspirations']),
                                    r['post_id'] not in already, r['post_id']))
        selected = positive[:10]
        positive_ids = {r['post_id'] for r in positive}
        text_by_id = self.posts.set_index('post_id').clean_text.to_dict()
        difficult = [r for r in self.records if r['post_id'] not in positive_ids and
                     (r['aspirations'] or re.search(r'(?i)\b(wish|want|buy|own|afford|never|would)\b',
                       text_by_id[r['post_id']]))]
        difficult.sort(key=lambda r:(r['post_id'] not in already, r['post_id']))
        selected += difficult[:10]
        self.target_ids += [r['post_id'] for r in selected]
        table(pd.DataFrame([{'post_id':r['post_id'],'extracted_aspiration':r['aspirations']} for r in selected]))
        table(pd.DataFrame([{'GM_only_desire_events':sum(e['brand']=='GM' and e['category'] in ['concrete','conditional']
                                                       for r in self.records for e in r['aspirations']),
                             'unresolved_notes':sum(len(r['unresolved']) for r in self.records)}]))
        note('Targeted positive and difficult nonpositive cases diagnose errors and misses; they do not estimate '
             'unbiased recall. A fraction can look large for a tiny audience. GM-expanded mentions can increase '
             'a child-brand denominator without creating any child desire.')

    def reviews_and_cost(self):
        usage = self.bundle.get('usage.json', [])
        if usage:
            ledger = pd.DataFrame(usage)
            cols = ['step','model','input_tokens','output_tokens','total_tokens','charged_or_reserved_usd','status']
            table(ledger[cols].groupby(['step','model','status'], dropna=False).agg(
                calls=('status','size'), input_tokens=('input_tokens','sum'), output_tokens=('output_tokens','sum'),
                total_tokens=('total_tokens','sum'), cost_or_reserved_usd=('charged_or_reserved_usd','sum')).reset_index())
            note(f'Historical spend plus unresolved reservations: **${ledger.charged_or_reserved_usd.sum():.4f}** '
                 'of $15. Shared C/E/F calls are counted once. Reservations are conservative possible charges, '
                 'not confirmed billed usage. This cached report makes **zero new API calls**.')
        else:
            table(pd.DataFrame([{'step':'generation not run','model':MODEL,'calls':0,'input_tokens':0,
                                 'output_tokens':0,'total_tokens':0,'estimated_cost_usd':0.0}]))
            note('No notebook API generation usage exists. Chat assistance is separate and is not represented as free API extraction.')
        if not self.complete:
            return
        all_audits = self.bundle.get('development_review.json', []) + self.bundle.get('random_review.json', [])
        for a in self.bundle.get('targeted_review.json', []):
            if a['post_id'] not in {x['post_id'] for x in all_audits}:
                all_audits.append(a)
        required = set(self.plan['development'] + self.plan['holdout'] + self.target_ids)
        metrics = audit_metrics(all_audits, self.records, required, self.posts, self.taxonomy, self.provenance)
        self.review_complete = int(metrics.reviewed_posts.iloc[0]) == len(required)
        table(pd.DataFrame([{'review_set':'development','required':20}, {'review_set':'independent random','required':40},
                            {'review_set':'additional unique targeted','required':len(required)-60},
                            {'review_set':'total actually reviewed','required':int(metrics.reviewed_posts.iloc[0])}]))
        if self.root:
            extra = sorted(set(self.target_ids) - set(self.plan['development'] + self.plan['holdout']))
            save_template(self.root / 'artifacts' / 'targeted_review.json', review_template(
                self.posts, self.records, extra, self.provenance, 'positioning_or_aspiration'))
        errors = [{'post_id':a['post_id'],'sets':a['sets'],'error_types':a['error_types'],'notes':a['notes']}
                  for a in all_audits if a.get('human_reviewed')]
        table(pd.DataFrame(errors))

    def task_g(self):
        if not self.complete:
            self.pending('Task G recommendations and semantic value assessment')
            note('There is no defensible aspiration winner, competitive map, or positioning recommendation yet. '
                 'The implementation will populate these sections from saved full-corpus evidence.')
            return
        self.reviews_and_cost()
        met = self.audit.set_index('field')
        enough_review = self.review_complete and (met.reviewed_posts == 40).all()
        recommendations = []
        matrix = self.c if self.primary == 'semantic' else self.b
        counts = self.cc if self.primary == 'semantic' else self.bc
        pairs = [(a,b,float(matrix.loc[a,b]),int(counts.loc[a,b])) for a,b in itertools.combinations(self.names,2)
                 if counts.loc[a,b] >= GATES['min_pair_support'] and np.isfinite(matrix.loc[a,b])]
        pairs.sort(key=lambda x:-x[2])
        if pairs:
            a,b,lift,count = pairs[0]
            robust = enough_review and self.b.loc[a,b] > 1 and self.c.loc[a,b] > 1 and self.c_off.loc[a,b] > 1 and self.b_off.loc[a,b] > 1
            recommendations.append({'action':f'Include {a} and {b} together in a follow-up competitor benchmark.',
                                    'evidence':f'Tasks B-D: {count} primary pair posts; lift {lift:.2f}.',
                                    'robustness':'robust to shown association checks' if robust else 'method-dependent / provisional',
                                    'limitation':'Historical forum association is not market-share rivalry; sparse support and GM/quote rules matter.',
                                    'test':'Test cross-shopping and shared evaluations in a fresh, representative survey.'})
        if len(self.strong_associations):
            r = self.strong_associations.iloc[0]
            recommendations.append({'action':f'Investigate how {r.brand} is discussed on {r.theme} in positioning research.',
                                    'evidence':f'Task E: {r.linked_posts} linked posts; within-brand rate {r.rate:.1%}; lift {r.lift:.2f}.',
                                    'robustness':'method-dependent; direction and inherited-link sensitivity require interpretation',
                                    'limitation':'Association is topical attention, not necessarily praise or product superiority.',
                                    'test':'Review positive/negative evidence and test the attribute with current vehicle owners.'})
        if self.winners:
            recommendations.append({'action':'Research ownership barriers for the audience expressing desire for ' + ', '.join(self.winners) + '.',
                                    'evidence':f'Task F: {int(self.asp.aspiring_authors.max())} unique aspiring authors at the lead.',
                                    'robustness':'provisional until aspiration diagnostics and category sensitivities are reviewed',
                                    'limitation':'Dream ownership is not a purchase commitment; prolific users and small audiences can matter.',
                                    'test':'Separate affordability-contingent wishes from concrete plans in follow-up interviews.'})
        table(pd.DataFrame(recommendations))
        note('**' + ('Human review coverage is complete.' if enough_review else
                     'These are provisional, mechanically assembled recommendations; required human review remains incomplete.') + '**')
        changed = self.comparison.total_delta.abs().gt(.25).sum()
        note(f'**Was semantic interpretation worth its cost?** {changed} of 45 pair lifts changed by more than '
             f'0.25 (a descriptive reporting cutoff); strongest-five overlap is {self.agreement["top_five_overlap"]}/5. '
             f'The selected map is {self.primary}. The recognition-only matrix separates entity changes from the '
             'stricter relation event. Semantic links and desire labels add capabilities absent from lexical counting, '
             'but there is no controlled comparator isolating a monetary return for E/F. '
             + ('Assess the displayed audit errors and sensitivity results before claiming the additional spend changed advice.'
                if enough_review else 'Value for client advice has not yet been validated because human review is incomplete.'))
        note('**Least trusted:** sparse aspiration categories, attributes with unresolved targets, inferred GM labels, '
             'and MDS groups sensitive to measurement choice. Source corruption and flattened quotes cannot be fully '
             'reversed. Unsupervised discovery may miss low-frequency models; selected candidate contexts are not a '
             'complete alias census. No causal sales effect or current-market preference follows from these data.')

    def acceptance(self):
        statuses = [
            ('Source profile / exclusions', True),
            ('Executed NLP candidate discovery', bool(self.found)),
            ('Validated corpus-derived taxonomy', bool(self.taxonomy)),
            ('Full-corpus extraction', self.complete),
            ('Completed human review coverage', self.review_complete),
            ('Both maps computable', len(self.maps)==2),
            ('Five-brand / five-theme positioning', len(self.selected_brands)==5 and len(self.selected_themes)==5),
            ('Total API accounting <= $15', sum(r.get('charged_or_reserved_usd',0) for r in self.bundle.get('usage.json',[])) <= 15),
        ]
        table(pd.DataFrame(statuses, columns=['requirement','complete']))
        ready = all(v for _,v in statuses)
        note('**Submission readiness: ' + ('all computational and review checks passed; read the interpretations before submission.**'
                                         if ready else 'NOT READY — outstanding requirements are explicitly shown above.**'))
        return ready
