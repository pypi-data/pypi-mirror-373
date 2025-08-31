# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pipen_poplog']
install_requires = \
['pipen==0.17.*']

entry_points = \
{'pipen': ['poplog = pipen_poplog:poplog_plugin']}

setup_kwargs = {
    'name': 'pipen-poplog',
    'version': '0.3.7',
    'description': 'Populate logs from jobs to running log of the pipeline',
    'long_description': '# pipen-poplog\n\nPopulate logs from jobs to running log of the pipeline for [pipen][1].\n\n## Installation\n\n```bash\npip install -U pipen-poplog\n```\n\n## Enabling/Disabling the plugin\n\nThe plugin is registered via entrypoints. It\'s by default enabled. To disable it:\n`plugins=[..., "no:poplog"]`, or uninstall this plugin.\n\n## Usage\n\n```python\nfrom pipen import Proc, Pipen\n\n\nclass Poplog(Proc):\n    input = "var:var"\n    input_data = [0, 1, 2]\n    script = """\n        echo -n "[PIPEN-POPLOG][INFO] Log message "\n        sleep 1  # Simulate message not read in time\n        echo "by {{in.var}} 1"\n        sleep 1\n        echo "[PIPEN-POPLOG][ERROR] Log message by {{in.var}} 2"\n        sleep 1\n        echo "[PIPEN-POPLOG][INFO] Log message by {{in.var}} 3"\n    """\n\n\nif __name__ == "__main__":\n    Pipen().run()\n```\n\n```\n01-12 11:23:52 I core    ╭═══════════════ PoplogDefault ═════════════════╮\n01-12 11:23:52 I core    ║ A default poplog proc                         ║\n01-12 11:23:52 I core    ╰═══════════════════════════════════════════════╯\n01-12 11:23:52 I core    PoplogDefault: Workdir: \'.pipen/Pipeline/PoplogDefault\'\n01-12 11:23:52 I core    PoplogDefault: <<< [START]\n01-12 11:23:52 I core    PoplogDefault: >>> [END]\n01-12 11:23:56 I poplog  PoplogDefault: [0/2] Log message by 0 1\n01-12 11:23:59 E poplog  PoplogDefault: [0/2] Log message by 0 2\n01-12 11:24:02 I poplog  PoplogDefault: [0/2] Log message by 0 3\n```\n\n## Configuration\n\n- `plugin_opts.poplog_loglevel`: The log level for poplog. Default: `info`.\n- `plugin_opts.poplog_pattern`: The pattern to match the log message. Default: `r\'\\[PIPEN-POPLOG\\]\\[(?P<level>\\w+)\\] (?P<message>.*)\'`.\n- `plugin_opts.poplog_jobs`: The job indices to be populated. Default: `[0]` (the first job).\n- `plugin_opts.poplog_max`: The total max number of the log message to be poplutated. Default: `99`.\n- `plugin_opts.poplog_source`: The source of the log message. Default: `stdout`.\n\n\n[1]: https://github.com/pwwang/pipen\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/pwwang/pipen-poplog',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
