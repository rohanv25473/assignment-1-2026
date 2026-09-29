"""Execute the deliverable in isolation with only the notebook and original CSV."""
from pathlib import Path
import os
import shutil
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager


def verify(root):
    root = Path(root)
    with tempfile.TemporaryDirectory(prefix='assignment1-standalone-') as scratch:
        scratch = Path(scratch)
        source = root / 'Assignment1_Deliverable.ipynb'
        shutil.copy2(source, scratch / source.name)
        shutil.copy2(root / 'sample_data.csv', scratch / 'sample_data.csv')
        notebook = nbformat.read(scratch / source.name, as_version=4)
        nbformat.validate(notebook)
        km = KernelManager(kernel_name='python3')
        km.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
        env = dict(os.environ)
        for key in ['OPENAI_API_KEY','ASSIGNMENT_ROOT','EDMUNDS_DATA','PYTHONPATH']:
            env.pop(key, None)
        client = NotebookClient(notebook, km=km, timeout=600, resources={'metadata':{'path':str(scratch)}})
        try:
            client.execute(env=env)
        finally:
            if client.kc:
                client.kc.stop_channels()
            if km.has_kernel:
                km.shutdown_kernel(now=True)
            km.cleanup_resources()
        errors = [o for c in notebook.cells if c.cell_type=='code' for o in c.outputs if o.output_type=='error']
        assert not errors, errors
        assert not (scratch / 'artifacts').exists(), 'Default rerun unexpectedly wrote generation artifacts.'
        assert not any(c.execution_count is None for c in notebook.cells if c.cell_type=='code')
        print('PASS: standalone notebook + original CSV; no API key, external project modules, or artifact directory.')
        print('Code cells executed:',sum(c.cell_type=='code' for c in notebook.cells))
        print('Error outputs:',len(errors))


if __name__=='__main__':
    verify(Path(__file__).resolve().parent)
