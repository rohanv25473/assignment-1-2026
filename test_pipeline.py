"""Meaningful arithmetic, evidence, audit and budget tests; all semantic fixtures are synthetic."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pandas as pd

from analysis_pipeline import *


def brand(name, evidence=None, certainty='supported'):
    return dict(brand=name, evidence=evidence or name, kind='brand', certainty=certainty)


def record(i, brands=(), relations=(), attributes=(), aspirations=()):
    return dict(post_id=i, brands=list(brands), relations=list(relations), attributes=list(attributes),
                aspirations=list(aspirations), unresolved=[])


def attr(theme, targets, evidence, certainty='supported', direction='positive'):
    return dict(theme=theme, subattribute=theme, targets=targets, evidence=evidence,
                certainty=certainty, direction=direction)


def desire(b, category, evidence, certainty='supported'):
    return dict(brand=b, category=category, evidence=evidence, certainty=certainty)


def relation(a, b, evidence, certainty='supported'):
    return dict(a=a, b=b, evidence=evidence, certainty=certainty, kind='comparison')


class ArithmeticTests(unittest.TestCase):
    def setUp(self):
        self.posts = pd.DataFrame({'post_id':[1,2,3,4], 'author':['u1','u1','u2','u3']})
        self.records = [
            record(1,[brand('BMW'),brand('Audi')],[relation('BMW','Audi','BMW instead of Audi')],
                   [attr('performance',['BMW'],'BMW handles well')],[desire('BMW','concrete','I plan to buy BMW')]),
            record(2,[brand('BMW'),brand('Audi')], attributes=[attr('comfort',['Audi'],'Audi seats are comfortable')],
                   aspirations=[desire('BMW','conditional','I would love a BMW')]),
            record(3,[brand('Audi')],attributes=[attr('comfort',['Audi'],'Audi seats are comfortable')]),record(4)]
        self.labels = semantic_labels(self.records)

    def test_contract_and_author_union(self):
        b, counts, marg = lift_matrices(self.labels,['BMW','Audi'])
        c = lift_matrices(self.labels,['BMW','Audi'],True)[0]
        self.assertAlmostEqual(b.loc['BMW','Audi'],4/3)
        self.assertAlmostEqual(c.loc['BMW','Audi'],2/3)
        self.assertEqual(counts.loc['BMW','Audi'],2)
        self.assertEqual(marg['Audi'],3)
        self.assertTrue(np.isnan(b.loc['BMW','BMW']))
        pos = positioning(self.labels,['BMW','Audi'],['comfort','performance'])
        row = pos[(pos.brand=='Audi') & (pos.theme=='comfort')].iloc[0]
        self.assertAlmostEqual(row.rate,2/3)
        self.assertAlmostEqual(row.lift,4/3)
        row = aspiration(self.labels,self.posts).iloc[0]
        self.assertEqual(row.aspiring_authors,1)
        self.assertEqual(row.concrete_authors,1)
        self.assertEqual(row.conditional_authors,1)
        self.assertEqual(row.aspiration_posts,2)

    def test_zeros_and_undefined(self):
        labels = semantic_labels([record(1,[brand('A')]), record(2,[brand('B')])])
        matrix = lift_matrices(labels,['A','B','Missing'])[0]
        self.assertEqual(matrix.loc['A','B'],0)
        self.assertTrue(np.isnan(matrix.loc['A','Missing']))
        with self.assertRaises(ValueError):
            distance(matrix)

    def test_deduplicated_theme_and_direction(self):
        r = record(1,[brand('BMW')],attributes=[attr('comfort',['BMW'],'comfortable'),
                                               attr('comfort',['BMW'],'uncomfortable',direction='negative')])
        labels = semantic_labels([r])
        self.assertEqual(labels[0]['links'],{('BMW','comfort')})
        self.assertEqual(positioning(labels,['BMW'],['comfort']).iloc[0].linked_posts,1)
        self.assertEqual(len(labels[0]['directions']),2)

    def test_unassigned_theme_stays_in_denominator(self):
        records = [record(1,[brand('BMW')],attributes=[attr('comfort',[],'comfortable')]),
                   record(2,[brand('BMW')],attributes=[attr('comfort',['BMW'],'BMW comfortable')])]
        row = positioning(semantic_labels(records),['BMW'],['comfort']).iloc[0]
        self.assertEqual(row.theme_posts,2)
        self.assertEqual(row.linked_posts,1)
        self.assertEqual(row.lift,.5)

    def test_uncertain_sensitivity_and_rejection(self):
        records = [record(1,[brand('BMW')],aspirations=[desire('BMW','conditional','wish','uncertain')]),
                   record(2,[brand('BMW')],aspirations=[desire('BMW','rejection','never')])]
        primary = aspiration(semantic_labels(records),self.posts.iloc[:2])
        upper = aspiration(semantic_labels(records,uncertain=True),self.posts.iloc[:2])
        self.assertEqual(primary.iloc[0].aspiring_authors,0)
        self.assertEqual(upper.iloc[0].aspiring_authors,1)
        self.assertEqual(upper.iloc[0].conflicting_authors,1)

    def test_gm_cases(self):
        records = [record(1,[brand('GM')]),record(2,[brand('GM'),brand('Toyota')],
                    [relation('GM','Toyota','GM versus Toyota')], [attr('comfort',['GM'],'GM rides well')],
                    [desire('GM','conditional','I want GM')]),record(3,[brand('GM'),brand('Cadillac'),brand('Lexus')],
                    [relation('Cadillac','Lexus','Cadillac vs Lexus')])]
        labels = semantic_labels(records)
        self.assertEqual(labels[0]['brands'],GM_CHILDREN)
        self.assertEqual(labels[0]['relations'],set())
        self.assertEqual(len(labels[1]['relations']),4)
        self.assertEqual(len(labels[1]['links']),4)
        self.assertEqual(labels[1]['desires'],set())
        self.assertEqual(labels[2]['brands'],{'Cadillac','Lexus'})
        self.assertEqual(len(labels[2]['relations']),1)
        off = semantic_labels(records,expansion=False)
        self.assertEqual(off[0]['brands'],set())
        no_links = semantic_labels(records,inherit_attributes=False)
        self.assertEqual(no_links[1]['links'],set())
        self.assertEqual(no_links[1]['brands'],labels[1]['brands'])
        self.assertEqual(no_links[1]['themes'],labels[1]['themes'])

    def test_quotes_and_cleaning(self):
        raw = '" kia hyundai nice " kia hyundai but real Kia and Hyundai cars. mercedes-benz benz benz'
        cleaned, provenance = clean_text(raw)
        self.assertIn('real Kia and Hyundai',cleaned)
        self.assertNotIn('benz benz',cleaned)
        self.assertEqual(len(provenance),2)
        self.assertNotIn('BMW',lexical_text('"BMW is great" Audi is fine.'))
        self.assertTrue(match_phrase('BMW BMW','BMW'))
        self.assertFalse(match_phrase('Audio','Audi'))

    def test_map_full_distances_and_45_pairs(self):
        names = [f'B{i}' for i in range(10)]
        rng = np.random.default_rng(24)
        labels = []
        for i in range(100):
            present = {b for b in names if rng.random() < .4}
            labels.append(dict(post_id=i, brands=present, relations=set(itertools.combinations(sorted(present),2))))
        b,bc,_ = lift_matrices(labels,names)
        comparison, stats = compare_matrices(b,b,b,bc,bc)
        self.assertEqual(len(comparison),45)
        self.assertAlmostEqual(stats['spearman'],1)
        self.assertEqual(stats['top_five_overlap'],5)
        mapped = map_brands(b)
        self.assertEqual(mapped['points'].shape,(10,3))
        self.assertTrue(np.all(np.diag(mapped['distance'])==0))
        self.assertTrue(np.isfinite(mapped['stress']))


class EvidenceAndAuditTests(unittest.TestCase):
    def setUp(self):
        self.posts = pd.DataFrame({'post_id':[1], 'author':['u'], 'clean_text':['BMW is comfortable.']})
        self.tax = {'aliases':[dict(surface='BMW',brand='BMW',kind='brand',unambiguous=True,
                                   post_id=1,evidence='BMW')],
                    'themes':[{'theme':'comfort','subattributes':[{'name':'comfort','phrases':['comfortable']}],
                               'rationale':'synthetic'}], 'unresolved':[]}
        self.r = record(1,[brand('BMW')],attributes=[attr('comfort',['BMW'],'comfortable')])

    def test_exact_evidence_and_missing_posts(self):
        validate_records([self.r],self.posts,self.tax)
        wrong = copy.deepcopy(self.r)
        wrong['brands'][0]['evidence'] = 'invented'
        with self.assertRaises(ValueError):
            validate_records([wrong],self.posts,self.tax)
        with self.assertRaises(ValueError):
            validate_records([],self.posts,self.tax)
        with self.assertRaises(ValueError):
            validate_records([self.r,self.r],self.posts,self.tax)

    def test_taxonomy_evidence_repair(self):
        posts = pd.DataFrame({'post_id':[0,1,2,3], 'clean_text':[
            'i am not sold on bmw at this time.',
            'someone who finds a 4-5 year old caddy an attractive car.',
            '$4k more than my e46. seems reasonable for more horsepower and more options.',
            'the CTS-V will be going after the M5.']})
        a = lambda s, b, p, e: dict(surface=s, brand=b, kind='alias', unambiguous=True, post_id=p, evidence=e)
        tax = dict(aliases=[a('BMW','BMW',0,'bmw at this time'),               # already valid
                            a('CTS-V','Cadillac',2,'the cts-v will be going after'),  # wrong post, case
                            a('Caddy','Cadillac',1,'find a 4-5 year old caddy'),      # changed word
                            a('E46','BMW',2,'more options than my e46'),              # reordered clauses
                            a('Audi','Audi',0,'audi is great')],                      # nowhere
                   themes=[], unresolved=[])
        fixed, repairs = repair_taxonomy(tax, posts)
        texts = posts.set_index('post_id').clean_text
        self.assertEqual([x['surface'] for x in fixed['aliases']], ['BMW','CTS-V','Caddy','E46'])
        for alias in fixed['aliases']:
            self.assertIn(alias['evidence'], texts[alias['post_id']])
            self.assertIn(alias['surface'].lower(), alias['evidence'].lower())
        self.assertEqual(fixed['aliases'][1]['post_id'], 3)
        self.assertEqual(fixed['unresolved'][0]['surface'], 'Audi')
        self.assertEqual(len(repairs), 4)
        self.assertEqual(len(tax['aliases']), 5)  # input untouched
        held_out = repair_taxonomy(tax, posts, exclude=[3])[0]  # holdout text never anchors evidence
        self.assertEqual([x['surface'] for x in held_out['unresolved']], ['CTS-V','Audi'])

    def test_extraction_evidence_repair(self):
        text = ('why buy mercedes-benz mercedes-benz mercedes-benz and bmw when lexus offered more? '
                'the audi looks bad. the displays must go. i agree the bmw is worse. his wife\'s bmw is fine. '
                'i would never buy an audi.')
        posts = pd.DataFrame({'post_id':[7,8], 'clean_text':[text, 'BMW is comfortable.']})
        tax = copy.deepcopy(self.tax)
        tax['aliases'] += [dict(surface=s,brand=s,kind='brand',unambiguous=True,post_id=1,evidence='BMW')
                           for s in ['Audi','Lexus','Mercedes-Benz']]
        r = record(7,[brand('Mercedes-Benz','why buy mercedes-benz and bmw'),       # collapsed artifact
                      brand('BMW',"my wife's bmw"),                                  # changed word, short
                      brand('Audi','the audi looks bad. ... i agree'),               # elision
                      brand('Lexus','lexus offered more', 'uncertain'),
                      brand('Saab','saab')],                                         # not in taxonomy
                   [relation('Mercedes-Benz','Lexus','why buy mercedes-benz and bmw when lexus offered more?'),
                    relation('BMW','Saab','bmw')],
                   [attr('comfort',['BMW','Saab'],'bmw is fine'),
                    dict(attr('comfort',['BMW'],'bmw is fine'), subattribute='invented')],
                   [desire('Audi','concrete','i would buy an audi')])                # negation lost: no fuzzy
        fixed, repairs, missing = repair_records([r, record(99)], posts, tax)
        self.assertEqual(missing, [8])                                              # never invented
        out = fixed[0]
        for g in EVENT_GROUPS:
            for e in out[g]:
                self.assertIn(e['evidence'], text)
        self.assertEqual([b['brand'] for b in out['brands']], ['Mercedes-Benz','BMW','Audi','Lexus'])
        self.assertEqual(out['brands'][1]['evidence'], "wife's bmw")
        self.assertEqual(out['relations'][0]['certainty'], 'uncertain')              # downgraded, not upgraded
        self.assertEqual(len(out['relations']), 1)
        self.assertEqual(out['attributes'][0]['targets'], ['BMW'])
        self.assertEqual(len(out['attributes']), 1)
        self.assertEqual(out['aspirations'], [])
        self.assertEqual(len(out['unresolved']), 4)
        self.assertEqual(r['brands'][0]['evidence'], 'why buy mercedes-benz and bmw')  # input untouched
        self.assertTrue(any(x['post_id'] == 99 and x['action'] == 'dropped' for x in repairs))
        validate_records(fixed, posts[posts.post_id.eq(7)], tax)

    def stage_fixture(self, tmp, n):
        art = Path(tmp) / 'artifacts'
        posts = pd.DataFrame({'post_id':list(range(n)), 'author':['u']*n, 'clean_text':['x']*n})
        plan = {'seed':1, 'holdout':[], 'development':[0], 'pilot':list(range(n))}
        write_json(art / 'discovery.json', {'candidates':[]})
        write_json(art / 'taxonomy.json', self.tax)
        return art, [patch('analysis_pipeline.prepare', return_value=(posts, posts, {})),
                     patch('analysis_pipeline.sample_plan', return_value=plan),
                     patch('analysis_pipeline.validate_taxonomy')]

    def test_model_names_map_to_canonical_brands(self):
        tax = copy.deepcopy(self.tax)
        tax['aliases'] += [dict(surface='Lexus', brand='Lexus', kind='brand', unambiguous=True, post_id=1, evidence='BMW'),
                           dict(surface='LS400', brand='Lexus', kind='model', unambiguous=True, post_id=1, evidence='BMW')]
        resolve = brand_resolver(tax)
        self.assertEqual(resolve('Lexus LS400'), 'Lexus')
        self.assertEqual(resolve('BMW 3 Series (compact)'), 'BMW')
        self.assertIsNone(resolve('Ferrari'))
        self.assertIsNone(resolve('BMW vs Lexus'))                       # ambiguous: never guessed
        posts = pd.DataFrame({'post_id':[5], 'clean_text':['the bmw 3 series beats the lexus ls400 on comfort.']})
        r = record(5, [brand('BMW','bmw 3 series'), brand('Lexus LS400','lexus ls400')],
                   [relation('BMW 3 Series','Lexus LS400','the bmw 3 series beats the lexus ls400')],
                   [dict(attr('comfort',['BMW 3 Series','Ferrari'],'comfort'))])
        fixed, repairs, missing = repair_records([r], posts, tax)
        out = fixed[0]
        self.assertEqual([b['brand'] for b in out['brands']], ['BMW','Lexus'])
        self.assertEqual((out['relations'][0]['a'], out['relations'][0]['b']), ('BMW','Lexus'))
        self.assertEqual(out['attributes'][0]['targets'], ['BMW'])
        with tempfile.TemporaryDirectory() as tmp:                    # replay by coverage, any grouping
            params = message_params('ins', {'posts':[{'post_id':5,'clean_text':'x'}]}, EXTRACTION_SCHEMA, 10)
            write_json(Path(tmp)/'a.json', {'request':params, 'parsed':{'posts':[r]}})
            self.assertEqual([ids for ids, _ in cached_extractions(tmp, 'ins', {5, 6})], [[5]])
            self.assertEqual(list(cached_extractions(tmp, 'other', {5})), [])
            self.assertEqual(list(cached_extractions(tmp, 'ins', {6})), [])

    def test_freeze_gate_override_is_explicit_and_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            n = 6
            art, patches = self.stage_fixture(tmp, n)
            posts = pd.DataFrame({'post_id': list(range(n)), 'author': ['u'] * n, 'clean_text': ['BMW'] * n})
            plan = {'seed': 1, 'holdout': [], 'development': list(range(n)), 'pilot': list(range(n))}
            prov = provenance_hash(self.tax)
            pilot = [record(i) for i in range(n)]                       # misses every gold brand
            write_json(art / 'pilot.json', {'provenance': prov, 'records': pilot, 'completed': True})
            write_json(art / 'development_review.json', [dict(
                post_id=i, provenance=prov, prediction_hash=digest(pilot[i]), expected=record(i, [brand('BMW')]),
                reviewer='AI', reviewed_at='t', ai_reviewed=True, human_reviewed=False) for i in range(n)])
            write_json(art / 'usage.json', [dict(step='C/E/F pilot', status='completed', model=MODEL, tag=prov,
                                                 charged_or_reserved_usd=.001)])
            with patch('analysis_pipeline.prepare', return_value=(posts, posts, {})), \
                 patch('analysis_pipeline.sample_plan', return_value=plan), patch('analysis_pipeline.validate_taxonomy'):
                with self.assertRaises(ValueError):
                    run_stage(tmp, 'freeze', source=Path(tmp) / 'x.csv')
                with self.assertRaises(ValueError):                         # a token reason is not a decision
                    run_stage(tmp, 'freeze', source=Path(tmp) / 'x.csv', freeze_override='ok')
                self.assertFalse((art / 'freeze.json').exists())
                reason = 'Team decision: accept despite low development F1; random audit decides map input.'
                result = run_stage(tmp, 'freeze', source=Path(tmp) / 'x.csv', freeze_override=reason)
            self.assertTrue(result['gate_override'])
            frozen = read_json(art / 'freeze.json')
            self.assertEqual(frozen['gate_override']['failed_fields'], ['brands'])
            self.assertEqual(frozen['gate_override']['reason'], reason)

    def test_bad_batch_does_not_stop_stage(self):
        batches = []
        def fake_request(self_, step, instructions, payload, schema, max_output=10000, tag=None):
            ids = [p['post_id'] for p in payload['posts']]
            batches.append(ids)
            self.assertIn('"themes"', instructions)                # static taxonomy lives in the prefix
            self.assertEqual(set(payload), {'posts'})
            if ids == [4, 5, 6, 7]:
                raise ValueError('Incomplete/refused response; not negative evidence.')
            return {'posts': [record(i) for i in ids[1:]]}   # also drops one post per batch
        with tempfile.TemporaryDirectory() as tmp:
            art, patches = self.stage_fixture(tmp, 10)
            write_json(art / 'pilot.json', {'provenance':'old', 'records':[record(0)], 'completed':False})
            with patches[0], patches[1], patches[2], patch('analysis_pipeline.BATCH_SIZE', 4), patch.object(BudgetAPI, 'request', fake_request):
                result = run_stage(tmp, 'pilot', source=Path(tmp) / 'x.csv')
                self.assertEqual(len(batches), 3)
                self.assertEqual(result['pending'], [0, 4, 5, 6, 7, 8])
                self.assertFalse(read_json(art / 'pilot.json')['completed'])
                self.assertTrue((art / 'archive' / 'pilot.old.json').exists())
                log = read_json(art / 'pilot_repairs.json')
                self.assertIn('ValueError', {f['error_type'] for f in log['failures']})
                self.assertFalse((art / 'development_review.json').exists())
                with patch.object(BudgetAPI, 'request', side_effect=BudgetStop('cap')):
                    with self.assertRaises(BudgetStop):
                        run_stage(tmp, 'pilot', source=Path(tmp) / 'x.csv')

    def test_probe_and_failure_streak_stop_spending(self):
        with tempfile.TemporaryDirectory() as tmp:
            art, patches = self.stage_fixture(tmp, 400)
            calls = []
            def broken(self_, *args, **kwargs):
                calls.append(1)
                raise RuntimeError('OpenAI HTTP 400; reservation retained.')
            with patches[0], patches[1], patches[2], patch('analysis_pipeline.BATCH_SIZE', 4), patch.object(BudgetAPI, 'request', broken):
                with self.assertRaises(RuntimeError):
                    run_stage(tmp, 'pilot', source=Path(tmp) / 'x.csv')
            self.assertEqual(len(calls), 1)                      # probe failed: nothing concurrent sent
            calls.clear()
            def flaky(self_, step, instructions, payload, schema, max_output=10000, tag=None):
                calls.append(1)
                if len(calls) > 1:
                    time.sleep(.05)
                    raise RuntimeError('OpenAI HTTP 500; reservation retained.')
                return {'posts': [record(p['post_id']) for p in payload['posts']]}
            with patches[0], patches[1], patches[2], patch('analysis_pipeline.BATCH_SIZE', 4), patch.object(BudgetAPI, 'request', flaky):
                result = run_stage(tmp, 'pilot', source=Path(tmp) / 'x.csv')
            self.assertEqual(result['completed'], 4)
            self.assertLess(len(calls), 60)   # queued work cancelled; only in-flight requests were sent

    def test_unknown_targets_and_unsupported_endpoints(self):
        wrong = copy.deepcopy(self.r)
        wrong['attributes'][0]['targets'] = ['Audi']
        with self.assertRaises(ValueError):
            validate_records([wrong],self.posts,self.tax)
        wrong = copy.deepcopy(self.r)
        wrong['brands'][0]['certainty'] = 'uncertain'
        with self.assertRaises(ValueError):
            validate_records([wrong],self.posts,self.tax)

    def test_development_reviews_carry_to_new_predictions_but_random_audit_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'review.json'
            old = [dict(post_id=1, provenance='old', prediction_hash='h1', expected=self.r, reviewer='R',
                        reviewed_at='t', ai_reviewed=True, human_reviewed=False, error_types=['x'], notes='n')]
            write_json(path, old)
            new = [dict(post_id=1, provenance='new', prediction_hash='h2', expected=None, reviewer='',
                        reviewed_at='', human_reviewed=False, error_types=[], notes='')]
            with self.assertRaises(ValueError):                         # random audit: never carried
                save_template(path, copy.deepcopy(new))
            save_template(path, copy.deepcopy(new), carry=True)
            got = read_json(path)[0]
            self.assertEqual((got['provenance'], got['prediction_hash']), ('new', 'h2'))
            self.assertEqual(got['expected'], self.r)
            self.assertTrue(is_reviewed(got) and got['ai_reviewed'] and not got['human_reviewed'])
            self.assertEqual(got['carried_from'], 'old')
            self.assertTrue(got['notes'].startswith('[Carried from prediction version old'))

    def test_human_provenance_and_untouched_samples(self):
        a = dict(post_id=1,reviewer='',reviewed_at='',human_reviewed=False,expected=None,
                 provenance='p',prediction_hash=digest(self.r))
        m = audit_metrics([a],[self.r],[1],self.posts,self.tax,'p')
        self.assertEqual(m.reviewed_posts.iloc[0],0)
        a.update(reviewer='Synthetic test reviewer',reviewed_at='test',human_reviewed=True,expected=self.r)
        m = audit_metrics([a],[self.r],[1],self.posts,self.tax,'p')
        self.assertEqual(m.set_index('field').loc['brands','f1'],1)
        a['provenance']='stale'
        with self.assertRaises(ValueError):
            audit_metrics([a],[self.r],[1],self.posts,self.tax,'p')
        posts = pd.DataFrame({'post_id':range(200),'raw_text':['BMW 330i " quote GM']*200})
        plan = sample_plan(posts)
        self.assertFalse(set(plan['holdout']) & set(plan['pilot']))
        self.assertTrue(set(plan['development']) <= set(plan['pilot']))
        self.assertEqual(len(plan['pilot']),100)


class BudgetTests(unittest.TestCase):
    def response(self, body):
        return {'id':'test_only','stop_reason':'end_turn','usage':{'input_tokens':100,'output_tokens':10,
                'cache_read_input_tokens':0,'cache_creation_input_tokens':0},
                'content':[{'type':'text','text':'{"answer":"ok"}'}]}

    def test_cache_avoids_calls_and_persistent_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            def transport(body):
                calls.append(body)
                return self.response(body)
            api=BudgetAPI(tmp,key='synthetic-not-a-secret',transport=transport)
            schema=obj(answer=S)
            self.assertEqual(api.request('test','test',{},schema),{'answer':'ok'})
            api2=BudgetAPI(tmp,transport=lambda b:self.fail('cache should prevent transport'))
            api2.request('test','test',{},schema)
            self.assertEqual(len(calls),1)
            self.assertEqual(len(read_json(Path(tmp)/'usage.json')),1)
            cost=read_json(Path(tmp)/'usage.json')[0]['charged_or_reserved_usd']
            self.assertAlmostEqual(cost,.00015)   # 100 x $1 + 10 x $5 per million

    def test_concurrent_calls_share_one_consistent_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            api = BudgetAPI(tmp, key='test', transport=lambda b: (time.sleep(.02), self.response(b))[1])
            with ThreadPoolExecutor(12) as pool:
                list(pool.map(lambda i: api.request('test', 'test', {'i': i}, obj(answer=S), tag='t'), range(40)))
            ledger = read_json(Path(tmp) / 'usage.json')
            self.assertEqual(len(ledger), 40)
            self.assertEqual({r['status'] for r in ledger}, {'completed'})
            self.assertEqual({r['tag'] for r in ledger}, {'t'})
            self.assertFalse((Path(tmp) / 'budget.lock').exists())

    def test_usage_cost_stacks_cache_and_batch_prices(self):
        usage = {'input_tokens': 1000, 'output_tokens': 2000, 'cache_read_input_tokens': 5000,
                 'cache_creation_input_tokens': 3000,
                 'cache_creation': {'ephemeral_1h_input_tokens': 3000, 'ephemeral_5m_input_tokens': 0}}
        realtime = (1000 * 1 + 5000 * .1 + 3000 * 2 + 2000 * 5) / 1e6
        self.assertAlmostEqual(usage_cost(usage), realtime)
        self.assertAlmostEqual(usage_cost(usage, batch=True), realtime / 2)

    def fake_batch_api(self, tmp, errored=()):
        created = {}
        def message(ids):
            text = json.dumps({'posts': [record(i) for i in ids]})
            return {'id': 'm', 'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': text}],
                    'usage': {'input_tokens': 100, 'output_tokens': 10,
                              'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}}
        def results(bid):
            for r in created[bid]:
                ids = batch_ids(r['custom_id'])
                if ids[0] in errored:
                    yield SimpleNamespace(custom_id=r['custom_id'], result=SimpleNamespace(type='errored'))
                else:
                    m = message(ids)
                    yield SimpleNamespace(custom_id=r['custom_id'], result=SimpleNamespace(
                        type='succeeded', message=SimpleNamespace(model_dump=lambda m=m: m)))
        def create(requests):
            bid = f'batch{len(created)}'
            created[bid] = requests
            return SimpleNamespace(id=bid)
        api = BudgetAPI(tmp, key='test')
        api._client = SimpleNamespace(messages=SimpleNamespace(batches=SimpleNamespace(
            create=create, retrieve=lambda bid: SimpleNamespace(processing_status='ended'), results=results)))
        return api, created

    def test_rolling_batches_respect_worst_case_budget_and_resume(self):
        schema = EXTRACTION_SCHEMA
        make = lambda ids: message_params('prompt', {'posts': ids}, schema, 4000)
        groups = [[i] for i in range(7)]
        with tempfile.TemporaryDirectory() as tmp, patch('analysis_pipeline.POLL_SECONDS', 0),              patch('analysis_pipeline.BATCH_CHUNK', 2):
            api, created = self.fake_batch_api(tmp, errored={5})
            worst = api.upper_cost(make([0]), batch=True)
            # Room for exactly one 2-request chunk at worst case: chunks must wait for settlement.
            write_json(Path(tmp) / 'usage.json', [{'charged_or_reserved_usd': BUDGET - BUFFER - 2.5 * worst}])
            state = Path(tmp) / 'state.json'
            write_json(state, {'tag': 't', 'open': []})
            handled, failed = [], []
            handle = lambda ids, parsed, exc: (failed if exc else handled).append(ids[0])
            stop = run_message_batches(api, state, 'test', groups, make, schema, 't', handle, lambda force=False: None)
            self.assertIsNone(stop)
            self.assertEqual(sorted(handled), [0, 1, 2, 3, 4, 6])
            self.assertEqual(failed, [5])                               # errored result: pending, unbilled
            self.assertEqual(len(created), 4)
            self.assertEqual(read_json(state)['open'], [])
            ledger = read_json(Path(tmp) / 'usage.json')[1:]
            self.assertEqual({r['status'] for r in ledger}, {'completed'})
            actual = usage_cost({'input_tokens': 100, 'output_tokens': 10}, batch=True)
            self.assertAlmostEqual(sum(r['charged_or_reserved_usd'] for r in ledger), 6 * actual)
            # Resume after a disconnect: an open batch is collected, never resubmitted.
            created['old'] = [{'custom_id': batch_custom_id([9]), 'params': make([9])}]
            row = api.reserve('test', worst, 't')
            write_json(state, {'tag': 't', 'open': [{'batch_id': 'old', 'call_id': row['call_id'],
                                                     'custom_ids': [batch_custom_id([9])]}]})
            handled.clear()
            run_message_batches(api, state, 'test', [[9], [0]], make, schema, 't', handle, lambda force=False: None)
            self.assertEqual(sorted(handled), [0, 9])                   # [0] replayed from cache for free
            self.assertEqual(len(created), 5)                          # nothing new submitted
            with self.assertRaises(ValueError):                        # open batches of another version
                write_json(state, {'tag': 'old', 'open': [{'batch_id': 'x', 'call_id': 'y', 'custom_ids': []}]})
                run_message_batches(api, state, 'test', [], make, schema, 't', handle, lambda force=False: None)

    def test_estimate_reservations_submit_everything_in_one_round(self):
        schema = EXTRACTION_SCHEMA
        make = lambda ids: message_params('prompt', {'posts': ids}, schema, 4000)
        with tempfile.TemporaryDirectory() as tmp, patch('analysis_pipeline.POLL_SECONDS', 0), \
             patch('analysis_pipeline.BATCH_CHUNK', 2):
            api, created = self.fake_batch_api(tmp)
            worst = api.upper_cost(make([0]), batch=True)
            estimate = worst / 10
            old = api.reserve('test', worst * 4, 't')                   # an open batch reserved at worst case
            api._settle(old['call_id'], status='submitted')
            created['old'] = [{'custom_id': batch_custom_id([9]), 'params': make([9])}]
            state = Path(tmp) / 'state.json'
            write_json(state, {'tag': 't', 'open': [{'batch_id': 'old', 'call_id': old['call_id'],
                                                     'custom_ids': [batch_custom_id([9])]}]})
            # Room for the 7 new requests exists only after the open batch is re-reserved at the estimate.
            write_json(Path(tmp) / 'usage.json', read_json(Path(tmp) / 'usage.json') +
                       [{'charged_or_reserved_usd': BUDGET - BUFFER - worst * 4 - estimate * 8}])
            order = []
            handle = lambda ids, parsed, exc: order.append(ids[0])
            run_message_batches(api, state, 'test', [[i] for i in range(7)], make, schema, 't', handle,
                                lambda force=False: None, estimate=estimate)
            self.assertEqual(sorted(order), [0, 1, 2, 3, 4, 5, 6, 9])
            ledger = read_json(Path(tmp) / 'usage.json')
            self.assertEqual({r.get('status') for r in ledger if r.get('call_id')}, {'completed'})

    def test_guard_stops_before_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_json(Path(tmp)/'usage.json',[{'charged_or_reserved_usd':14.4999}])
            api=BudgetAPI(tmp,key='test',transport=lambda b:self.fail('must stop before request'))
            with self.assertRaises(RuntimeError):
                api.request('test','test',{},obj(answer=S))

    def test_failed_call_keeps_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fail(body):
                raise TimeoutError('synthetic')
            api=BudgetAPI(tmp,key='test',transport=fail)
            with self.assertRaises(TimeoutError):
                api.request('test','test',{},obj(answer=S))
            row=read_json(Path(tmp)/'usage.json')[0]
            self.assertEqual(row['status'],'failed')
            self.assertEqual(row['charged_or_reserved_usd'],row['reserved_usd'])
            self.assertGreater(row['charged_or_reserved_usd'],0)

    def test_incomplete_is_not_empty_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            def incomplete(body):
                r=self.response(body)
                r['stop_reason']='max_tokens'
                return r
            with self.assertRaises(ValueError):
                BudgetAPI(tmp,key='test',transport=incomplete).request('test','test',{},obj(answer=S))
            self.assertEqual(read_json(Path(tmp)/'usage.json')[0]['status'],'failed')
            self.assertFalse(list((Path(tmp)/'api_cache').glob('*.json')))


class ReportIntegrationTests(unittest.TestCase):
    def test_every_report_section_on_synthetic_evidence(self):
        """Fixtures live only in memory; no synthetic labels enter project artifacts."""
        from notebook_report import Report
        import notebook_report as nr
        brands = [f'Brand{i}' for i in range(10)]
        themes = [f'Theme{i}' for i in range(6)]
        records, rows = [], []
        for i in range(180):
            selected = [brands[i%10], brands[(i+1)%10], brands[(i+3)%10]]
            theme = themes[i%6]
            text = ' '.join(selected) + ' ' + theme + ' I want ' + selected[0]
            rows.append(dict(post_id=i,author=f'u{i%30}',date_label='6-Oct',raw_text=text,
                             clean_text=text,cleaning=[],exclusion=''))
            records.append(record(i,[brand(b) for b in selected],
                                  [relation(selected[0],selected[1],' '.join(selected[:2]))],
                                  [attr(theme,[selected[0]],theme)],
                                  [desire(selected[0],'conditional','I want '+selected[0])]))
        posts=pd.DataFrame(rows)
        tax=dict(aliases=[dict(surface=b,brand=b,kind='brand',unambiguous=True,
                               post_id=next(r['post_id'] for r in rows if b in r['clean_text']),evidence=b) for b in brands],
                 themes=[dict(theme=t,subattributes=[dict(name=t,phrases=[t])],rationale='synthetic test') for t in themes],
                 unresolved=[])
        provenance=provenance_hash(tax)
        plan=sample_plan(posts)
        reviews={}
        for name,ids in [('development',plan['development']),('random',plan['holdout'])]:
            annotations=review_template(posts,records,ids,provenance,name)
            for a in annotations:
                a.update(expected=a['predicted'],reviewer='SYNTHETIC TEST ONLY',human_reviewed=True,reviewed_at='test')
            reviews[name+'_review.json']=annotations
        bundle={'taxonomy.json':tax,'extractions.json':{'records':records,'provenance':provenance},
                'freeze.json':{'provenance':provenance},**reviews}
        with patch.object(nr,'prepare',return_value=(posts,posts,{'retained_posts':len(posts)})), \
             patch.object(nr,'display'), patch.object(nr,'heatmap'), patch.object(nr,'plot_map'), \
             patch.object(nr,'note'), patch.object(nr,'table'):
            report=Report('synthetic-only',bundle)
            report.overview()
            for method in ['task_a','task_b','task_c','task_d','task_e','task_f','task_g']:
                getattr(report,method)()
            self.assertEqual(len(report.comparison),45)
            self.assertEqual(len(report.pos),25)
            self.assertEqual(len(report.maps),2)
            self.assertFalse(report.acceptance())  # Extra targeted reviews still absent.

    def test_report_without_extraction_never_invents_results(self):
        from notebook_report import Report
        import notebook_report as nr
        posts=pd.DataFrame({'post_id':range(150),'author':['u']*150,'raw_text':['text']*150,
                            'clean_text':['text']*150,'cleaning':[[] for _ in range(150)],'exclusion':['']*150})
        with patch.object(nr,'prepare',return_value=(posts,posts,{})),patch.object(nr,'note'),patch.object(nr,'table'):
            report=Report('synthetic-only',{})
            for method in ['task_a','task_b','task_c','task_d','task_e','task_f','task_g']:
                getattr(report,method)()
            self.assertFalse(report.complete)
            self.assertFalse(hasattr(report,'winners'))
            self.assertFalse(report.acceptance())


if __name__=='__main__':
    unittest.main(verbosity=2)
