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
    'version': '0.10.10',
    'description': 'A job management system for python',
    'long_description': '# xqute\n\nA job management system for python\n\n## Features\n\n- Written in async\n- Plugin system\n- Scheduler adaptor\n- Job retrying/pipeline halting when failed\n- Support cloud working directory\n- Support Google Batch Jobs scheduler\n\n## Installation\n\n```shell\npip install xqute\n```\n\n## A toy example\n\n```python\nimport asyncio\nfrom xqute import Xqute\n\nasync def main():\n    # 3 jobs allowed to run at the same time\n    xqute = Xqute(forks=3)\n    for _ in range(10):\n        await xqute.put(\'sleep 1\')\n    await xqute.run_until_complete()\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```\n\n![xqute](./xqute.png)\n\n## API\n\n<https://pwwang.github.io/xqute/>\n\n## Usage\n\n### Xqute object\n\nAn xqute is initialized by:\n\n```python\nxqute = Xqute(...)\n```\n\nAvailable arguments are:\n\n- scheduler: The scheduler class or name\n- plugins: The plugins to enable/disable for this session\n- workdir: The job meta directory (Default: `./.xqute/`)\n- forks: The number of jobs allowed to run at the same time\n- error_strategy: The strategy when there is error happened\n- num_retries: Max number of retries when job_error_strategy is retry\n- submission_batch: The number of consumers to submit jobs\n- scheduler_opts: Additional keyword arguments for scheduler\n- jobname_prefix: The prefix of the job name\n- recheck_interval: The interval to recheck the job status\n\nNote that the producer must be initialized in an event loop.\n\nTo push a job into the queue:\n\n```python\nawait xqute.put([\'echo\', 1])\n```\n\n### Using SGE scheduler\n\n```python\nxqute = Xqute(\n    \'sge\',\n    forks=100,\n    scheduler_opts=dict(\n        qsub=\'path to qsub\',\n        qdel=\'path to qdel\',\n        qstat=\'path to qstat\',\n        q=\'1-day\',  # or qsub_q=\'1-day\'\n    )\n    ...\n)\n```\n\nKeyword-arguments with names starting with `sge_` will be interpreted as `qsub` options. `list` or `tuple` option values will be expanded. For example:\n`l=[\'h_vmem=2G\', \'gpu=1\']` will be expanded in wrapped script like this:\n\n```shell\n# ...\n\n#$ -l h_vmem=2G\n#$ -l gpu=1\n\n# ...\n```\n\n### Using Slurm scheduler\n\n```python\nxqute = Xqute(\n    \'slurm\',\n    forks=100,\n    scheduler_opts = {\n        "sbatch": \'path to sbatch\',\n        "scancel": \'path to scancel\',\n        "squeue": \'path to squeue\',\n        "partition": \'1-day\',  # or partition=\'1-day\'\n        "time": \'01:00:00\',\n        ...\n    },\n)\n```\n\n### Using ssh scheduler\n\n```python\nxqute = Xqute(\n    \'ssh\',\n    forks=100,\n    scheduler_opts={\n        "ssh": \'path to ssh\',\n        "servers": {\n            "server1": {\n                "user": ...,\n                "port": 22,\n                "keyfile": ...,\n                # How long to keep the ssh connection alive\n                "ctrl_persist": 600,\n                # Where to store the control socket\n                "ctrl_dir": "/tmp",\n            },\n            ...\n        }\n    },\n    ...\n)\n```\n\nSSH servers must share the same filesystem and using keyfile authentication.\n\n### Using Google Batch Jobs scheduler\n\n```python\nxqute = Xqute(\n    \'gbatch\',\n    forks=100,\n    scheduler_opts={\n        "project": "your-gcp-project-id",\n        "location": "us-central1",\n        "gcloud": "path to gcloud",  # must be authenticated\n        # see https://cloud.google.com/batch/docs/create-run-example-job#create-job\n        "taskGroups": [ ... ],\n    }\n)\n```\n\n### Using Container scheduler\n\n```python\nxqute = Xqute(\n    \'container\',\n    forks=100,\n    scheduler_opts={\n        "image": "docker://bash:latest",  # or path to sif file for apptainer\n        "entrypoint": "/usr/local/bin/bash",\n        "bin": "docker",  # or "podman" or "apptainer"\n        "volumes": "/path/on/host:/path/in/container",  # extra volume mapping\n        "envs": {"MY_ENV_VAR": "value"},  # environment variables to set\n        "remove": True,  # remove container after execution (Docker/Podman only)\n        # additional arguments to pass to the container runtime\n        "bin_args": ["--hostname", "xqute-container"],\n    }\n)\n```\n\n### Plugins\n\nTo write a plugin for `xqute`, you will need to implement the following hooks:\n\n- `def on_init(scheduler)`: Right after scheduler object is initialized\n- `def on_shutdown(scheduler, sig)`: When scheduler is shutting down\n- `async def on_job_init(scheduler, job)`: When the job is initialized\n- `async def on_job_queued(scheduler, job)`: When the job is queued\n- `async def on_job_submitted(scheduler, job)`: When the job is submitted\n- `async def on_job_started(scheduler, job)`: When the job is started (when status changed to running)\n- `async def on_job_polling(scheduler, job, counter)`: When job status is being polled\n- `async def on_job_killing(scheduler, job)`: When the job is being killed\n- `async def on_job_killed(scheduler, job)`: When the job is killed\n- `async def on_job_failed(scheduler, job)`: When the job is failed\n- `async def on_job_succeeded(scheduler, job)`: When the job is succeeded\n- `def on_jobcmd_init(scheduler, job) -> str`: When the job command wrapper script is initialized before the prescript is run. This will replace the placeholder `{jobcmd_init}` in the wrapper script.\n- `def on_jobcmd_prep(scheduler, job) -> str`: When the job command is right about to run in the wrapper script. This will replace the placeholder `{jobcmd_prep}` in the wrapper script.\n- `def on_jobcmd_end(scheduler, job) -> str`: When the job command wrapper script is about to end and after the postscript is run. This will replace the placeholder `{jobcmd_end}` in the wrapper script.\n\nNote that all hooks are corotines except `on_init`, `on_shutdown` and `on_jobcmd_*`, that means you should also implement them as corotines (sync implementations are allowed but will be warned).\n\nYou may also check where the hooks are called in the following diagram:\n\n![xqute-design](./xqute-design.png)\n\nTo implement a hook, you have to fetch the plugin manager:\n\n```python\nfrom simplug import Simplug\npm = Simplug(\'xqute\')\n\n# or\nfrom xqute import simplug as pm\n```\n\nand then use the decorator `pm.impl`:\n\n```python\n@pm.impl\ndef on_init(scheduler):\n    ...\n```\n\n### Implementing a scheduler\n\nCurrently there are a few builtin schedulers: `local`, `slurm`, `gbatch`, `container` and `sge`.\n\nOne can implement a scheduler by subclassing the `Scheduler` abstract class. There are three abstract methods that have to be implemented in the subclass:\n\n```python\nfrom xqute import Scheduer\n\n\nclass MyScheduler(Scheduler):\n    name = \'mysched\'\n\n    async def submit_job(self, job):\n        """How to submit a job, return a unique id in the scheduler system\n        (the pid for local scheduler for example)\n        """\n\n    async def kill_job(self, job):\n        """How to kill a job"""\n\n    async def job_is_running(self, job):\n        """Check if a job is running"""\n```\n',
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
