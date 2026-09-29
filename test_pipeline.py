"""Meaningful arithmetic, evidence, audit and budget tests; all semantic fixtures are synthetic."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
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

    def test_unknown_targets_and_unsupported_endpoints(self):
        wrong = copy.deepcopy(self.r)
        wrong['attributes'][0]['targets'] = ['Audi']
        with self.assertRaises(ValueError):
            validate_records([wrong],self.posts,self.tax)
        wrong = copy.deepcopy(self.r)
        wrong['brands'][0]['certainty'] = 'uncertain'
        with self.assertRaises(ValueError):
            validate_records([wrong],self.posts,self.tax)

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
        return {'id':'test_only','status':'completed','usage':{'input_tokens':100,'output_tokens':10,
                'total_tokens':110,'input_tokens_details':{'cached_tokens':0}},
                'output':[{'content':[{'type':'output_text','text':'{"answer":"ok"}'}]}]}

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
            self.assertAlmostEqual(cost,.000015)

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
                r['status']='incomplete'
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
