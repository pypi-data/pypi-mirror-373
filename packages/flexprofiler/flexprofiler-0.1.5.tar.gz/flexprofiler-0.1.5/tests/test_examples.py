
import os
import sys
import pytest
import glob
import subprocess

# This test runs example scripts and asserts they complete successfully.
# The previous test relied on the optional `pytest-subtests` plugin to group
# subtests; to avoid an extra test dependency we use a simple parametrized
# test and include the example path in the failure message.

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '../examples')
example_files = sorted(glob.glob(os.path.join(EXAMPLES_DIR, '*.py')))

@pytest.mark.parametrize('example_path', example_files)
def test_example_runs(example_path):
    """Run each example script in the examples folder and assert successful execution.

    The example file path is included in the assertion text for easy debugging
    when a particular script fails.
    """
    # Run the example using the repository sources first by setting PYTHONPATH
    env = os.environ.copy()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_pythonpath = env.get('PYTHONPATH', '')
    env['PYTHONPATH'] = os.pathsep.join(filter(None, [repo_root, env_pythonpath]))
    result = subprocess.run([sys.executable, example_path], capture_output=True, text=True, env=env)
    assert result.returncode == 0, (
        f"Example {os.path.basename(example_path)} failed (path: {example_path})\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

