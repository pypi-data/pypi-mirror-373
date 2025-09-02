# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pref_voting', 'pref_voting.io']

package_data = \
{'': ['*'],
 'pref_voting': ['data/examples/condorcet_winner/*',
                 'data/voting_methods_properties.json',
                 'data/voting_methods_properties.json',
                 'data/voting_methods_properties.json.lock',
                 'data/voting_methods_properties.json.lock']}

install_requires = \
['filelock>=3.12.2,<4.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'nashpy>=0.0.40,<0.0.41',
 'networkx>=3.0,<4.0',
 'numba>=0.61.0,<0.62.0',
 'ortools>=9.8.0,<10.0.0',
 'pathos>=0.3.3,<0.4.0',
 'preflibtools>=2.0.22,<3.0.0',
 'prefsampling>=0.1.16,<0.2.0',
 'random2>=1.0.1,<2.0.0',
 'scipy>=1.0.0,<2.0.0',
 'seaborn>=0.13.2,<0.14.0',
 'tabulate>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'pref-voting',
    'version': '1.16.27',
    'description': 'pref_voting is a Python package that contains tools to reason about elections and margin graphs, and implementations of voting methods.',
    'long_description': 'pref_voting\n==========\n[![DOI](https://joss.theoj.org/papers/10.21105/joss.07020/status.svg)](https://doi.org/10.21105/joss.07020) [![DOI](https://zenodo.org/badge/578984957.svg)](https://doi.org/10.5281/zenodo.14675583)\n\n[![Tests](https://github.com/voting-tools/pref_voting/actions/workflows/tests.yml/badge.svg)](https://github.com/voting-tools/pref_voting/actions/workflows/tests.yml)\n\n\n> [!NOTE]\n> - [**Documentation**](https://pref-voting.readthedocs.io/)\n> - [**Installation**](https://pref-voting.readthedocs.io/en/latest/installation.html)  \n> - [**Example Notebooks**](https://github.com/voting-tools/pref_voting/tree/main/examples)  \n> - [**Example Elections**](https://github.com/voting-tools/election-analysis)\n> - [**► pref_voting web app**](https://pref.tools/pref_voting/)\n\nSee the [COMSOC community page](https://comsoc-community.org/tools) for an overview of other software tools related to Computational Social Choice.\n\n## Installation\n\nThe package can be installed using the ``pip3`` package manager:\n\n```bash\npip3 install pref_voting\n```\n**Notes**: \n* The package requires Python 3.10 or higher and has been tested on Python 3.12.\n\n* Since the package uses Numba, refer to the [Numba documentation for the latest supported Python version](https://numba.readthedocs.io/en/stable/user/installing.html#version-support-information).\n* If you have both Python 2 and Python 3 installed on your system, make sure to use ``pip3`` instead of pip to install packages for Python 3. Alternatively, you can use ``python3 -m pip`` to ensure you\'re using the correct version of pip. If you have modified your system\'s defaults or soft links, adjust accordingly.\n\nSee the [installation guide](https://pref-voting.readthedocs.io/en/latest/installation.html) for more detailed instructions.\n\n## Example Usage\n\nA profile (of linear orders over the candidates) is created by initializing a `Profile` class object.  Simply provide a list of rankings (each ranking is a tuple of numbers) and a list giving the number of voters with each ranking:\n\n```python\nfrom pref_voting.profiles import Profile\n\nrankings = [\n    (0, 1, 2, 3), # candidate 0 is ranked first, candidate 1 is ranked second, candidate 2 is ranked 3rd, and candidate 3 is ranked last.\n    (2, 3, 1, 0), \n    (3, 1, 2, 0), \n    (1, 2, 0, 3), \n    (1, 3, 2, 0)]\n\nrcounts = [5, 3, 2, 4, 3] # 5 voters submitted the first ranking (0, 1, 2, 3), 3 voters submitted the second ranking, and so on.\n\nprof = Profile(rankings, rcounts=rcounts)\n\nprof.display() # display the profile\n```\n\nThe function `generate_profile` is used to generate a profile for a given number of candidates and voters:  \n\n```python\nfrom pref_voting.generate_profiles import generate_profile\n\n# generate a profile using the Impartial Culture probability model\nprof = generate_profile(3, 4) # prof is a Profile object with 3 candidates and 4 voters\n\n# generate a profile using the Impartial Anonymous Culture probability model\nprof = generate_profile(3, 4, probmod = "IAC") # prof is a Profile object with 3 candidates and 4 voters \n```\n\nThe `Profile` class has a number of methods that can be used to analyze the profile. For example, to determine the margin of victory between two candidates, the plurality scores, the Copeland scores, the Borda scores, the Condorcet winner, the weak Condorcet winner, and the Condorcet loser, and whether the profile is uniquely weighted, use the following code:\n\n```python\n\nprof = Profile([\n    [2, 1, 0, 3], \n    [3, 2, 0, 1], \n    [3, 1, 0, 2]], \n    rcounts=[2, 2, 3])\n\nprof.display()\n\nprint(f"The margin of 1 over 3 is {prof.margin(1, 3)}")\nprint(f"The Plurality scores are {prof.plurality_scores()}")\nprint(f"The Copeland scores are {prof.copeland_scores()}")\nprint(f"The Borda scores are {prof.borda_scores()}")\nprint(f"The Condorcet winner is {prof.condorcet_winner()}")\nprint(f"The weak Condorcet winner is {prof.weak_condorcet_winner()}")\nprint(f"The Condorcet loser is {prof.condorcet_loser()}")\nprint(f"The profile is uniquely weighted: {prof.is_uniquely_weighted()}")\n\n```\n\nTo use one of the many voting methods, import the function from `pref_voting.voting_methods` and apply it to the profile: \n\n```python\nfrom pref_voting.generate_profiles import generate_profile\nfrom pref_voting.voting_methods import *\n\nprof = generate_profile(3, 4) # create a profile with 3 candidates and 4 voters\nsplit_cycle(prof) # returns the sorted list of winning candidates\nsplit_cycle.display(prof) # displays the winning candidates\n\n```\n\nAdditional notebooks that demonstrate how to use the package can be found in the [examples directory](https://github.com/voting-tools/pref_voting/tree/main/examples)\n\nSome interesting political elections are analyzed using pref_voting in the [election-analysis repository](https://github.com/voting-tools/election-analysis).\n\nConsult the documentation [https://pref-voting.readthedocs.io](https://pref-voting.readthedocs.io) for a complete overview of the package. \n\n\n## Testing\n \nTo ensure that the package is working correctly, you can run the test suite using [pytest](https://docs.pytest.org/en/stable/). The test files are located in the `tests` directory. Follow the instructions below based on your setup.\n\n### Prerequisites\n\n- **Python 3.9 or higher**: Ensure you have a compatible version of Python installed.\n- **`pytest`**: Install `pytest` if it\'s not already installed.\n\n### Running the tests\n\nIf you are using **Poetry** to manage your dependencies, run the tests with:\n\n```bash\npoetry run pytest\n\n```\n \nFrom the command line, run:\n\n```bash\npytest\n```\n\nFor more detailed output, add the -v or --verbose flag:\n\n```bash\npytest -v\n```\n\n## How to cite\n \nIf you would like to acknowledge our work in a scientific paper,\nplease use the following citation:\n\nWesley H. Holliday and Eric Pacuit (2025). pref_voting: The Preferential Voting Tools package for Python. Journal of Open Source Software, 10(105), 7020. https://doi.org/10.21105/joss.07020\n\n### BibTeX:\n\n```bibtex\n@article{HollidayPacuit2025, \n  author = {Wesley H. Holliday and Eric Pacuit}, \n  title = {pref_voting: The Preferential Voting Tools package for Python}, \n  journal = {Journal of Open Source Software},\n  year = {2025}, \n  publisher = {The Open Journal}, \n  volume = {10}, \n  number = {105}, \n  pages = {7020}, \n  doi = {10.21105/joss.07020}\n}\n\n```\n\nAlternatively, you can cite the archived code repository\nat [zenodo](https://doi.org/10.5281/zenodo.14675583).\n\n## Contributing\n\nIf you would like to contribute to the project, please see the [contributing guidelines](CONTRIBUTING.md).\n\n## Questions?\n\nFeel free to [send an email](https://pacuit.org/) if you have questions about the project.\n\n## License\n\n[MIT](https://github.com/voting-tools/pref_voting/blob/main/LICENSE.txt)\n',
    'author': 'Eric Pacuit',
    'author_email': 'epacuit@umd.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/voting-tools/pref_voting',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
