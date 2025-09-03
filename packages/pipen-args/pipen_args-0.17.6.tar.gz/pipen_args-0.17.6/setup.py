# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipen_args']

package_data = \
{'': ['*']}

install_requires = \
['pipen-annotate>=0.15,<0.16']

entry_points = \
{'pipen': ['args = pipen_args.plugin:ArgsPlugin']}

setup_kwargs = {
    'name': 'pipen-args',
    'version': '0.17.6',
    'description': 'Command-line argument parser for pipen.',
    'long_description': '# pipen-args\n\nCommand line argument parser for [pipen][1]\n\n## Usage\n\n```python\nfrom pipen import Proc, Pipen\n\n\nclass Process(Proc):\n    """My process\n\n    Input:\n        a: Input data\n    """\n    input = \'a\'\n    input_data = range(10)\n    script = \'echo {{in.a}}\'\n\nPipen().set_start(Process).run()\n```\n\n```shell\n$ python example.py --help\nUsage: test.py [-h | -h+] [options]\n\nUndescribed process.\nUse `@configfile` to load default values for the options.\n\nPipeline Options:\n  --name NAME           The name for the pipeline, will affect the default workdir and\n                        outdir. [default: pipen-0]\n  --profile PROFILE     The default profile from the configuration to run the pipeline.\n                        This profile will be used unless a profile is specified in the\n                        process or in the .run method of pipen. You can check the\n                        available profiles by running `pipen profile`\n  --outdir OUTDIR       The output directory of the pipeline [default: ./<name>-output]\n  --forks FORKS         How many jobs to run simultaneously by the scheduler\n  --scheduler SCHEDULER\n                        The scheduler to run the jobs\n\nNamespace <in>:\n  --in.a A [A ...]      Input data\n\nOptional Arguments:\n  -h, --help, -h+, --help+\n                        show help message (with + to show more options) and exit\n```\n\nSee more examples in `tests/pipelines/` folder.\n\n## Plugin options\n\n- `args_hide`: (process level) Hide the arguments in the help message. Default: `False`\n- `args_group`: (pipeline level) The group name for the arguments. Default: `pipeline options`\n- `args_flatten`: (pipeline level) Flatten the arguments in the help message when there is only one process in the pipeline. Default: `auto` (flatten if single process, otherwise not)\n- `args_dump`: (pipeline level) Whether to dump the arguments to `<outdir>/args.toml` file. Default: `False`.\n\n> [!NOTE]\n> Only `args_dump` can be passed from the command line or a configuration file.\n> Other options can only be set in the pipeline class, passed to the `Pipen` construct.\n> Because they are used to construct the argument parser and we don\'t\n> know the value of these options before the argument parser is constructed.\n\n## Metadata for Proc envs items\n\nThe metadata in the docstring of env items determines how the arguments are defined.\n\n```python\nclass Process(Proc):\n    """My process\n\n    # other docstring sections\n\n    Envs:\n        a (<metadata>): ...\n    """\n```\n\nThe metadata could be key-value pairs separated by `;`. The separator `:` or `=` is used to\nseparate the key and value. The value is optional. If the value is not specified, it\nwill be set to `True`. The keys are valid arguments of `argx.ArgumentParser.add_argument`, except that `hidden` will be interpreted as `show=False` in `argx.ArgumentParser.add_argument`. If the value of `choices` is not specified, the subkeys of the env item will be used as the choices.\n\n[1]: https://github.com/pwwang/pipen\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/pwwang/pipen-args',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
