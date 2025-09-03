"""
Knowledge base of all built-in formatters.
"""

from behave_bo.formatter import (
    _registry,
)


# -----------------------------------------------------------------------------
# DATA:
# -----------------------------------------------------------------------------
# SCHEMA: formatter.name, formatter.class(_name)
_BUILTIN_FORMATS = [
    ("plain", "behave_bo.formatter.plain:PlainFormatter"),
    ("pretty", "behave_bo.formatter.pretty:PrettyFormatter"),
    ("json", "behave_bo.formatter.json:JSONFormatter"),
    ("json.pretty", "behave_bo.formatter.json:PrettyJSONFormatter"),
    ("null", "behave_bo.formatter.null:NullFormatter"),
    ("progress", "behave_bo.formatter.progress:ScenarioProgressFormatter"),
    ("progress2", "behave_bo.formatter.progress:StepProgressFormatter"),
    ("progress3", "behave_bo.formatter.progress:ScenarioStepProgressFormatter"),
    ("rerun", "behave_bo.formatter.rerun:RerunFormatter"),
    ("tags", "behave_bo.formatter.tags:TagsFormatter"),
    ("tags.location", "behave_bo.formatter.tags:TagsLocationFormatter"),
    ("steps", "behave_bo.formatter.steps:StepsFormatter"),
    ("steps.doc", "behave_bo.formatter.steps:StepsDocFormatter"),
    ("steps.catalog", "behave_bo.formatter.steps:StepsCatalogFormatter"),
    ("steps.usage", "behave_bo.formatter.steps:StepsUsageFormatter"),
    ("steps.remove_unused", "behave_bo.formatter.steps:UnusedStepsRemoveFormatter"),
    ("sphinx.steps", "behave_bo.formatter.sphinx_steps:SphinxStepsFormatter"),
]

# -----------------------------------------------------------------------------
# FUNCTIONS:
# -----------------------------------------------------------------------------
def setup_formatters():
    """Register all built-in formatters (lazy-loaded)."""
    _registry.register_formats(_BUILTIN_FORMATS)
