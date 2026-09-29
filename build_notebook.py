"""Build the standalone notebook with all code and available saved records embedded."""
import argparse
import base64
import gzip
import json
from pathlib import Path
import sys
import textwrap

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

from notebook_report import collect_artifacts


def embedded_cell(bundle):
    packed = base64.b64encode(gzip.compress(json.dumps(bundle, ensure_ascii=False).encode(), mtime=0)).decode()
    return ('# Saved evidence; gzip/base64 is storage encoding, not encryption. No credentials are included.\n'
            'import base64, gzip, json\n'
            f'BUNDLE = json.loads(gzip.decompress(base64.b64decode({packed!r})))\n'
            'print("Embedded artifacts:", ", ".join(BUNDLE))')


def build(root, execute=False, output=None):
    root = Path(root)
    output = Path(output or root / 'Assignment1_Deliverable.ipynb')
    cells = []
    def md(s):
        cells.append(nbformat.v4.new_markdown_cell(textwrap.dedent(s).strip()))
    def code(s, **metadata):
        cells.append(nbformat.v4.new_code_cell(textwrap.dedent(s).strip(), metadata=metadata))
    md('''
    # Edmunds luxury-car discussions: competitive analysis for JD Power
    **Team:** Stephen, Matthew, Rohan, Valentina  
    **Course:** Problem Solving With Unstructured Data and GenAI, MSBT&AI Fall 2026

    This notebook implements the accepted Tasks A–G design. Its status checks distinguish executed
    evidence from unfinished generation or review. Never interpret a pending section as a completed result.
    The assignment specifies Canvas submission on September 28 at 11:59 p.m.

    **Reproduce saved results:** put the original `sample_data.csv` beside this notebook, install the
    packages below if needed, then Run All. All analytical code and available saved extraction records,
    prompts, schemas, usage and review annotations are embedded. Default execution makes no paid calls.
    No project Python files are needed for this notebook's default run.

    **Colab:** upload the notebook and `sample_data.csv` into the runtime. Keep `GENERATION_STAGE=None`
    to reproduce saved results. For generation, use the private `OPENAI_API_KEY` Colab secret, choose a
    persistent `WORK_ROOT` (for example, a mounted Drive folder), and run one explicit stage at a time:
    `prepare → discover → pilot → freeze → extract`. Between pilot and freeze, humans complete the
    20 development reviews. After extraction, complete the 40 random reviews and selected targeted
    reviews. The final rerun needs no review prompts. Do not discard the artifacts directory: it holds
    the cumulative spend ledger, including failed-call reservations. Save the updated notebook after
    every generation/review stage using the optional export cell at the end.
    ''')
    code('''
    # Run this once only if the environment lacks packages. This is not an API call.
    # %pip install numpy pandas scipy scikit-learn matplotlib nbformat nbclient ipykernel jsonschema requests
    from pathlib import Path
    import os, sys, types
    WORK_ROOT = Path(os.environ.get('ASSIGNMENT_ROOT', '.')).resolve()
    DATA_PATH = Path(os.environ.get('EDMUNDS_DATA', str(WORK_ROOT / 'sample_data.csv')))
    GENERATION_STAGE = None  # Explicit opt-in: 'prepare', 'discover', 'pilot', 'freeze', or 'extract'
    if not DATA_PATH.is_file():
        raise FileNotFoundError('Place the original sample_data.csv at DATA_PATH; no replacement corpus is used.')
    ''')
    md('''
    ## Reproducible implementation and saved evidence
    The next two cells contain the complete implementation rather than an external module dependency.
    The main A–G cells below invoke these functions. The implementation version, prompt, schema,
    taxonomy, input hash and model identify cached extraction; a mismatch fails visibly.
    ''')
    for name in ['analysis_pipeline', 'notebook_report']:
        source = (root / (name + '.py')).read_text(encoding='utf-8')
        # Display real readable Python in the notebook. Omit only the CLI entry point.
        source = source.split("\nif __name__ == '__main__':")[0]
        code(source + f"\n\n{name} = types.ModuleType('{name}')\n{name}.__dict__.update(globals())\n"
             f"sys.modules['{name}'] = {name}",
             tags=['implementation'])
    code(embedded_cell(collect_artifacts(root)), tags=['saved-bundle'])
    code('''
    from analysis_pipeline import run_stage, read_json, write_json, SOURCE_HASH, GATES, PRICES
    from notebook_report import Report, collect_artifacts, note, table
    if GENERATION_STAGE is not None:
        artifact_dir = WORK_ROOT / 'artifacts'
        artifact_dir.mkdir(parents=True, exist_ok=True)
        # Restore only absent embedded checkpoints. Never overwrite a newer cumulative ledger.
        for name, value in BUNDLE.items():
            destination = artifact_dir / name
            if not destination.exists():
                write_json(destination, value)
        old_ledger = BUNDLE.get('usage.json', [])
        current_ledger = read_json(artifact_dir / 'usage.json', [])
        if not {r['call_id'] for r in old_ledger} <= {r['call_id'] for r in current_ledger}:
            raise RuntimeError('Local ledger is missing embedded calls. Reconcile ledgers before any new spending.')
        if GENERATION_STAGE in {'discover', 'pilot', 'extract'} and not os.environ.get('OPENAI_API_KEY'):
            try:
                from google.colab import userdata
                os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')
            except Exception:
                raise RuntimeError('Configure OPENAI_API_KEY securely; do not place the key in this notebook.') from None
        print(run_stage(WORK_ROOT, GENERATION_STAGE, DATA_PATH))
        BUNDLE = collect_artifacts(WORK_ROOT)
    # Local artifacts are used only when explicitly requested, avoiding silent stale-cache replacement.
    USE_LOCAL_ARTIFACTS = False  # Set True after editing human review JSON in WORK_ROOT/artifacts.
    if USE_LOCAL_ARTIFACTS:
        BUNDLE = collect_artifacts(WORK_ROOT)
    report = Report(DATA_PATH, BUNDLE, root=WORK_ROOT if GENERATION_STAGE or USE_LOCAL_ARTIFACTS else None)
    report.overview()
    ''')
    md('''
    ## Measurement contract and validation
    A post contributes at most one vote per brand, theme or pair. The common denominator contains
    every retained post, including those with no target brand. Exact three-field duplicate records
    and whitespace-blank texts are excluded; identical text by different authors is retained.
    Raw text, row IDs and cleaning provenance remain available. Conservative quote rules are an
    acknowledged lexical approximation to substantive engagement.

    **GM is deliberately task-specific:** GM-only references expand to Chevrolet, Buick, GMC and
    Cadillac unless an identifiable child is present. Lexical expansion creates co-mentions, but
    GM alone creates no semantic child clique. Supported GM-to-other comparisons expand endpoints.
    Vehicle attributes may inherit with flags; GM-only aspiration never inherits.

    **Rationale and alternative:** post prevalence limits repetition effects; raw token counts
    overweight long/quoted posts. Distinct authors accompany prevalence. Removing posts with no
    top-ten brand would change the denominator and is rejected.

    **Synthetic arithmetic check:** four posts, BMW in two, Audi in three, both in two, but only
    one competitive relation: lexical lift = 4/3 and relation lift = 2/3. Audi comfort appears in
    two posts, giving rate 2/3 and lift 4/3. One author expressing concrete and conditional BMW
    desire counts as one aspiring author, not two. These are synthetic checks, not corpus findings.
    ''')
    code('''
    from analysis_pipeline import lift_matrices, positioning, aspiration, expand_brands
    import pandas as pd
    toy_posts = pd.DataFrame({'post_id':[1,2,3,4], 'author':['u1','u1','u2','u3']})
    def toy_row(i, brands, relations=(), themes=(), links=(), desires=()):
        return dict(post_id=i, brands=set(brands), relations=set(relations), themes=set(themes),
                    links=set(links), desires=set(desires), rejections=set(), directions=set())
    toy = [toy_row(1,['BMW','Audi'],[('Audi','BMW')],['performance'],[('BMW','performance')],[('BMW','concrete')]),
           toy_row(2,['BMW','Audi'],themes=['comfort'],links=[('Audi','comfort')],desires=[('BMW','conditional')]),
           toy_row(3,['Audi'],themes=['comfort'],links=[('Audi','comfort')]), toy_row(4,[])]
    import numpy as np
    assert np.isclose(lift_matrices(toy,['BMW','Audi'])[0].loc['BMW','Audi'],4/3)
    assert np.isclose(lift_matrices(toy,['BMW','Audi'],True)[0].loc['BMW','Audi'],2/3)
    assert np.isclose(positioning(toy,['Audi'],['comfort']).iloc[0]['rate'],2/3)
    assert aspiration(toy,toy_posts).iloc[0]['aspiring_authors']==1
    assert expand_brands({'GM','Cadillac'})[0]=={'Cadillac'}
    print('Synthetic counting, linked attribution, GM and author-union checks passed.')
    table(pd.DataFrame([GATES]))
    ''')
    sections = [
        ('A — Discover brands and vehicle attributes', '''
        Use TF-IDF n-grams and NMF context groups to discover candidates, then a selective structured
        LLM call to reconcile marques, models/aliases and theme/subattribute hierarchy. No supplied
        brand dictionary is used. Semantic post prevalence fixes the top ten before B/C; author
        coverage and cleaning/GM sensitivities expose concentration and artifacts.
        **Alternative:** a supplied dictionary or literal brand-token ranking is simpler but misses
        models and risks inflated artifact counts. Phrase discovery can still miss rare forms;
        unresolved candidates and evidence examples must remain visible.
        ''', 'task_a'),
        ('B — Transparent lexical competitive baseline', '''
        Match unambiguous corpus-derived aliases with word boundaries after conservative cleaning
        and quote handling. Count unordered same-post pairs once. Lift is N n_AB / (n_A n_B), with
        counts alongside. **Alternative:** sentence windows reduce incidental co-mentions but change
        the selected post-level event; smoothing changes zero evidence into positive association.
        ''', 'task_b'),
        ('C — Semantic lift and reconciliation', '''
        Shared extraction records substantive brands, supported competitive relations, linked attributes
        and ownership desire with exact evidence spans. Uncertain labels are excluded from primary
        counts but posts remain in N. Compare all 45 pairs. An intermediate semantic same-post matrix
        separates recognition from relation filtering. **Alternative:** counting every two semantic
        mentions would retain unrelated remarks. A narrower numerator alone is not improved accuracy.
        The 100-post pilot and 20 difficult development reviews precede prompt freezing; 40 random
        posts remain untouched by prompt development and are manually audited afterward.
        ''', 'task_c'),
        ('D — Competitive map and clusters', '''
        Convert lift to d=1/(1+lift), explicitly setting diagonal distances to zero. Use two-dimensional
        nonmetric MDS and report stress. Average-linkage clustering uses the full distance matrix,
        comparing two to four clusters by silhouette. Semantic input is primary only after passing
        predeclared audit and coverage gates; lexical input is the fallback.
        **Alternative:** clustering plotted coordinates would entangle group membership with projection
        distortion. Metric MDS imposes stronger magnitude assumptions. ARI ≥0.8 across the two measurement
        choices is the operational cluster-stability criterion; this is not a bootstrap stability claim.
        ''', 'task_d'),
        ('E — Brand–attribute positioning', '''
        Select the most prevalent brand in each stable cluster, then fill to five by prevalence;
        unstable clusters trigger the predeclared top-five-prevalence fallback. Select five distinct
        reconciled themes by post support before viewing linked scores. For each of 25 cells show
        linked posts k, rate k/m_brand, and lift N k/(m_brand t_theme). Unassigned themes remain in
        t_theme. Direction is separate from association.
        **Alternative:** same-post lexical attribution links unrelated features to every brand. Show
        that sensitivity and the inherited-GM-link-off result. Review two examples for each of the
        five strongest supported associations discussed, reusing earlier reviews where possible.
        ''', 'task_e'),
        ('F — Expressed ownership aspiration', '''
        Qualifying desire belongs to the author and an identifiable marque. Distinguish concrete
        acquisition intent from conditional/dream ownership. Exclude praise, current ownership alone,
        recommendations to others, negation and quoted-only wishes. Evaluate all discovered marques.
        Rank the union of concrete and conditional authors once per author–brand; report category
        counts, posts, discussing-author fractions and conflicting evidence. A later rejection does
        not erase period-level desire. **Alternative:** post ranking rewards prolific users; fraction-only
        ranking can exaggerate tiny audiences. Inspect up to ten positives and ten hard nonpositives.
        ''', 'task_f'),
        ('G — Client advice, limitations and semantic value', '''
        Recommendations must identify a client action, supporting evidence, a limitation that could
        change the advice, and a test of its value. Evidence determines the content; do not force a
        predetermined winner. Robust and method-dependent conclusions are distinguished.
        **Alternative:** a generic insight summary lacks a testable action. Historical forum evidence
        informs research priorities, not current market share, purchase conversion or causal sales effects.
        ''', 'task_g'),
    ]
    for title, prose, method in sections:
        md('## Task ' + title + '\n\n' + textwrap.dedent(prose).strip())
        code(f'report.{method}()')
    md('''
    ## API usage, human-review readiness and submission checklist
    Standard pricing is recorded with its verification date and source. The $15 cumulative cap
    includes discovery, development, retries and shared extraction. Calls reserve conservative cost
    before sending; failures without usage retain the reservation. A 50-cent buffer and the pilot's
    full-run projection protect the budget. Do not reset the ledger to work around a budget stop.

    The semantic audit must be performed by real reviewers. Generated expected labels are not human
    inspection. Targeted cases do not join the random sample's accuracy estimate. Missing annotations
    and API output remain visible blockers. Team names are retained from the earlier project draft.
    ''')
    code('''
    if not report.complete:
        report.reviews_and_cost()
    READY_FOR_SUBMISSION = report.acceptance()
    ''')
    md('''
    ## Optional: export updated evidence into the notebook
    After generation or importing completed reviews, set `EXPORT_UPDATED_NOTEBOOK=True` and run the
    cell below. It embeds the current saved records and displayed outputs into a new notebook, resets
    generation to `None`, and bundles the durable artifacts separately. Keep both exports for future
    work; submit the completed notebook and original CSV as permitted by the course instructions.
    This export never claims that incomplete reviews are complete.
    In local Jupyter, save the notebook first so the disk copy contains your latest displayed outputs.
    ''')
    code('''
    EXPORT_UPDATED_NOTEBOOK = False
    if EXPORT_UPDATED_NOTEBOOK:
        import nbformat, shutil, re
        current = collect_artifacts(WORK_ROOT) or BUNDLE
        packed = base64.b64encode(gzip.compress(json.dumps(current, ensure_ascii=False).encode(),mtime=0)).decode()
        source_line = ('import base64, gzip, json\\nBUNDLE = json.loads(gzip.decompress(base64.b64decode('
                       + repr(packed) + ')))')
        try:
            from google.colab import _message, files
            snapshot = nbformat.from_dict(_message.blocking_request('get_ipynb')['ipynb'])
            in_colab = True
        except ImportError:
            snapshot = nbformat.read(WORK_ROOT / 'Assignment1_Deliverable.ipynb', as_version=4)
            in_colab = False
        for cell in snapshot.cells:
            if 'saved-bundle' in cell.get('metadata',{}).get('tags',[]):
                cell.source = source_line
            if cell.cell_type == 'code' and cell.source.startswith('# Run this once'):
                cell.source = re.sub(r'(?m)^GENERATION_STAGE = .*$', 'GENERATION_STAGE = None', cell.source)
            if cell.cell_type == 'code':
                cell.source = re.sub(r'(?m)^USE_LOCAL_ARTIFACTS = .*$', 'USE_LOCAL_ARTIFACTS = False', cell.source)
            if cell.cell_type == 'code' and cell.source.startswith('EXPORT_UPDATED_NOTEBOOK ='):
                cell.source = cell.source.replace('EXPORT_UPDATED_NOTEBOOK = True', 'EXPORT_UPDATED_NOTEBOOK = False', 1)
        target = WORK_ROOT / 'Assignment1_Saved.ipynb'
        nbformat.write(snapshot, target)
        print('Saved', target)
        if (WORK_ROOT / 'artifacts').exists():
            archive = shutil.make_archive(str(WORK_ROOT/'assignment_artifacts'), 'zip', WORK_ROOT/'artifacts')
            if in_colab:
                files.download(archive)
        if in_colab:
            files.download(str(target))
    ''')
    md('''
    ## Source and method references
    - Assignment: `MSBT&AI_F2026_Assignment_1.docx` (supplied project document).
    - Accepted specification: `docs/NOTEBOOK_DESIGN.md`, `docs/calculation-contract.md`, and 12 ADRs.
    - Corpus: `sample_data.csv`; fingerprint checked above; no additional corpus is collected.
    - [OpenAI GPT-6 Luna model and pricing](https://developers.openai.com/api/docs/models/gpt-6-luna),
      verified September 29, 2026. Exact model availability still depends on the account.
    - [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

    Code generation assistance does not validate semantic results. Review labels retain reviewer names,
    timestamps, prediction hashes, evidence, error types and sample membership.
    ''')
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name':'Python 3','language':'python','name':'python3'},
        'language_info': {'name':'python','version':sys.version.split()[0]}})
    nbformat.validate(notebook)
    if execute:
        # A temporary kernel command avoids modifying the user's registered kernels.
        km = KernelManager(kernel_name='python3')
        km.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        client = NotebookClient(notebook, timeout=600, kernel_name='python3', km=km,
                                resources={'metadata':{'path':str(root)}})
        try:
            client.execute()
        finally:
            if client.kc:
                client.kc.stop_channels()
            if km.has_kernel:
                km.shutdown_kernel(now=True)
            km.cleanup_resources()
    nbformat.write(notebook, output)
    print(f'Built {output.name}: {len(cells)} cells; executed={execute}')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    build(Path(__file__).resolve().parent, args.execute)
