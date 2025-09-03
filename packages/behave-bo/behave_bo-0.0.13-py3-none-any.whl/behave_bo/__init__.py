"""behave_bo is behaviour-driven development, Python style

Behavior-driven development (or BDD) is an agile software development
technique that encourages collaboration between developers, QA and
non-technical or business participants in a software project.

*behave_bo* uses tests written in a natural language style, backed up by Python
code.

To get started, we recommend the `tutorial`_ and then the `test language`_ and
`api`_ references.

.. _`tutorial`: tutorial.html
.. _`test language`: gherkin.html
.. _`api`: api.html
"""

from behave_bo.fixture import (
    fixture,
    use_fixture,
)
from behave_bo.matchers import (
    register_type,
    use_step_matcher,
)
from behave_bo.step_registry import *  # pylint: disable=wildcard-import


# pylint: disable=undefined-all-variable
__all__ = [
    "given", "when", "then", "step", "step_template", "use_step_matcher", "register_type",
    "Given", "When", "Then", "Step", "Step_Template",
    "fixture", "use_fixture",
]
__version__ = "1.2.6"
