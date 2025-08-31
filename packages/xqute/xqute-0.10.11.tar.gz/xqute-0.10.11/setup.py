# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xqute', 'xqute.schedulers', 'xqute.schedulers.ssh_scheduler']

package_data = \
{'': ['*']}

install_requires = \
['argx>=0.3,<0.4',
 'rich>=14,<15',
 'simplug>=0.5,<0.6',
 'uvloop>=0,<1',
 'yunpath>=0.0,<0.1']

extras_require = \
{'cloudsh': ['cloudsh>=0.1,<0.2'],
 'gcs': ['google-cloud-storage>=3,<4'],
 'gs': ['google-cloud-storage>=3,<4']}

setup_kwargs = {
    'name': 'xqute',
    'version': '0.10.11',
    'description': 'A job management system for python',
    'long_description': '# xqute\n\nA job management system for Python, designed to simplify job scheduling and execution with support for multiple schedulers and plugins.\n\n## Features\n\n- Written in async for high performance\n- Plugin system for extensibility\n- Scheduler adaptor for various backends\n- Job retrying and pipeline halting on failure\n- Support for cloud-based working directories\n- Built-in support for Google Batch Jobs, Slurm, SGE, SSH, and container schedulers\n\n## Installation\n\n```shell\npip install xqute\n```\n\n## A Toy Example\n\n```python\nimport asyncio\nfrom xqute import Xqute\n\nasync def main():\n    # Initialize Xqute with 3 jobs allowed to run concurrently\n    xqute = Xqute(forks=3)\n    for _ in range(10):\n        await xqute.put([\'sleep\', \'1\'])\n    await xqute.run_until_complete()\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```\n\n![xqute](./xqute.png)\n\n## API Documentation\n\nFull API documentation is available at: <https://pwwang.github.io/xqute/>\n\n## Usage\n\n### Xqute Object\n\nAn `Xqute` object is initialized as follows:\n\n```python\nxqute = Xqute(...)\n```\n\nAvailable arguments are:\n\n- `scheduler`: The scheduler class or name (default: `local`)\n- `plugins`: Plugins to enable/disable for this session\n- `workdir`: Directory for job metadata (default: `./.xqute/`)\n- `forks`: Number of jobs allowed to run concurrently\n- `error_strategy`: Strategy for handling errors (e.g., `halt`, `retry`)\n- `num_retries`: Maximum number of retries when `error_strategy` is set to `retry`\n- `submission_batch`: Number of jobs to submit in a batch\n- `scheduler_opts`: Additional keyword arguments for the scheduler\n- `jobname_prefix`: Prefix for job names\n- `recheck_interval`: Interval (in seconds) to recheck job status\n\n**Note:** The producer must be initialized within an event loop.\n\nTo add a job to the queue:\n\n```python\nawait xqute.put([\'echo\', \'Hello, World!\'])\n```\n\n### Using SGE Scheduler\n\n```python\nxqute = Xqute(\n    scheduler=\'sge\',\n    forks=100,\n    scheduler_opts={\n        \'qsub\': \'/path/to/qsub\',\n        \'qdel\': \'/path/to/qdel\',\n        \'qstat\': \'/path/to/qstat\',\n        \'q\': \'1-day\',  # or qsub_q=\'1-day\'\n    }\n)\n```\n\nKeyword arguments starting with `sge_` are interpreted as `qsub` options. For example:\n\n```python\n\'l\': [\'h_vmem=2G\', \'gpu=1\']\n```\nwill be expanded in the job script as:\n\n```shell\n#$ -l h_vmem=2G\n#$ -l gpu=1\n```\n\n### Using Slurm Scheduler\n\n```python\nxqute = Xqute(\n    scheduler=\'slurm\',\n    forks=100,\n    scheduler_opts={\n        \'sbatch\': \'/path/to/sbatch\',\n        \'scancel\': \'/path/to/scancel\',\n        \'squeue\': \'/path/to/squeue\',\n        \'partition\': \'1-day\',\n        \'time\': \'01:00:00\',\n    }\n)\n```\n\n### Using SSH Scheduler\n\n```python\nxqute = Xqute(\n    scheduler=\'ssh\',\n    forks=100,\n    scheduler_opts={\n        \'ssh\': \'/path/to/ssh\',\n        \'servers\': {\n            \'server1\': {\n                \'user\': \'username\',\n                \'port\': 22,\n                \'keyfile\': \'/path/to/keyfile\',\n                \'ctrl_persist\': 600,\n                \'ctrl_dir\': \'/tmp\',\n            }\n        }\n    }\n)\n```\n\n**Note:** SSH servers must share the same filesystem and use keyfile authentication.\n\n### Using Google Batch Jobs Scheduler\n\n```python\nxqute = Xqute(\n    scheduler=\'gbatch\',\n    forks=100,\n    scheduler_opts={\n        \'project\': \'your-gcp-project-id\',\n        \'location\': \'us-central1\',\n        \'gcloud\': \'/path/to/gcloud\',\n        \'taskGroups\': [ ... ],\n    }\n)\n```\n\n### Using Container Scheduler\n\n```python\nxqute = Xqute(\n    scheduler=\'container\',\n    forks=100,\n    scheduler_opts={\n        \'image\': \'docker://bash:latest\',\n        \'entrypoint\': \'/usr/local/bin/bash\',\n        \'bin\': \'docker\',\n        \'volumes\': \'/host/path:/container/path\',\n        \'envs\': {\'MY_ENV_VAR\': \'value\'},\n        \'remove\': True,\n        \'bin_args\': [\'--hostname\', \'xqute-container\'],\n    }\n)\n```\n\n### Plugins\n\nTo create a plugin for `xqute`, implement the following hooks:\n\n- `def on_init(scheduler)`: Called after the scheduler is initialized\n- `def on_shutdown(scheduler, sig)`: Called when the scheduler shuts down\n- `async def on_job_init(scheduler, job)`: Called when a job is initialized\n- `async def on_job_queued(scheduler, job)`: Called when a job is queued\n- `async def on_job_submitted(scheduler, job)`: Called when a job is submitted\n- `async def on_job_started(scheduler, job)`: Called when a job starts running\n- `async def on_job_polling(scheduler, job, counter)`: Called during job status polling\n- `async def on_job_killing(scheduler, job)`: Called when a job is being killed\n- `async def on_job_killed(scheduler, job)`: Called when a job is killed\n- `async def on_job_failed(scheduler, job)`: Called when a job fails\n- `async def on_job_succeeded(scheduler, job)`: Called when a job succeeds\n- `def on_jobcmd_init(scheduler, job) -> str`: Called during job command initialization\n- `def on_jobcmd_prep(scheduler, job) -> str`: Called before the job command runs\n- `def on_jobcmd_end(scheduler, job) -> str`: Called after the job command completes\n\nTo implement a hook, use the `simplug` plugin manager:\n\n```python\nfrom xqute import simplug as pm\n\n@pm.impl\ndef on_init(scheduler):\n    ...\n```\n\n### Implementing a Scheduler\n\nTo create a custom scheduler, subclass the `Scheduler` abstract class and implement the following methods:\n\n```python\nfrom xqute import Scheduler\n\nclass MyScheduler(Scheduler):\n    name = \'mysched\'\n\n    async def submit_job(self, job):\n        """Submit a job and return its unique ID."""\n\n    async def kill_job(self, job):\n        """Kill a job."""\n\n    async def job_is_running(self, job):\n        """Check if a job is running."""\n```\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/pwwang/xqute',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
