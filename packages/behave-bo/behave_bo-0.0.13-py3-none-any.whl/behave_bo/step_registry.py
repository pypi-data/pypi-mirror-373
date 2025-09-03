"""
Provides a step registry and step decorators.
The step registry allows to match steps (model elements) with
step implementations (step definitions). This is necessary to execute steps.
"""

from behave_bo.matchers import (
    Match,
    get_matcher,
)
from behave_bo.textutil import (
    text as _text,
)


# limit import * to just the decorators
# pylint: disable=undefined-all-variable
# names = "given when then step"
# names = names + " " + names.title()
# __all__ = names.split()
__all__ = [
    "given", "when", "then", "step", "step_template",  # PREFERRED.
    "Given", "When", "Then", "Step", "Step_Template"  # Also possible.
]

GIVEN = "given"
WHEN = "when"
THEN = "then"
STEP_TEMPLATE = "step_template"
STEP = "step"

step_types = (GIVEN, WHEN, THEN, STEP_TEMPLATE, STEP,)
uniq_step_types = (STEP,)


class AmbiguousStep(ValueError):
    pass


class StepRegistry:
    def __init__(self):
        self.steps = {
            GIVEN: [],
            WHEN: [],
            THEN: [],
            STEP_TEMPLATE: [],
            STEP: {},  # uniq steps
        }

    @staticmethod
    def same_step_definition(step, other_pattern, other_location):
        return (step.pattern == other_pattern and
                step.location == other_location and
                other_location.filename != "<string>")

    def base_add_step_definition(self, keyword, step_text, func):
        step_location = Match.make_location(func)
        step_type = keyword.lower()
        step_text = _text(step_text)
        step_definitions = self.steps[step_type]

        for existing in step_definitions:
            if self.same_step_definition(existing, step_text, step_location):
                # -- EXACT-STEP: Same step function is already registered.
                # This may occur when a step module imports another one.
                return
            elif existing.match(step_text):  # -- SIMPLISTIC
                message = "%s has already been defined in\n  existing step %s"
                new_step = f"@{step_type}('{step_text}')"
                existing.step_type = step_type
                existing_step = existing.describe()
                existing_step += " at %s" % existing.location
                raise AmbiguousStep(message % (new_step, existing_step))

        step_definitions.append(get_matcher(func, step_text))

    def base_find_step_definition(self, step):
        candidates = self.steps[step.step_type]
        more_steps = self.steps[STEP_TEMPLATE]

        if step.step_type != STEP_TEMPLATE and more_steps:
            # -- ENSURE: self.step_type lists are not modified/extended.
            candidates = list(candidates)
            candidates += more_steps

        for step_definition in candidates:
            if step_definition.match(step.name):
                return step_definition

        return None

    def base_find_match(self, step):
        candidates = self.steps[step.step_type]
        more_steps = self.steps[STEP_TEMPLATE]

        if step.step_type != STEP_TEMPLATE and more_steps:
            # -- ENSURE: self.step_type lists are not modified/extended.
            candidates = list(candidates)
            candidates += more_steps

        for step_definition in candidates:
            result = step_definition.match(step.name)
            if result:
                return result

        return None

    def add_step_definition(self, keyword, step_text, func):
        step_type = keyword.lower()
        step_location = Match.make_location(func)
        step_text = _text(step_text)
        step_definitions = self.steps[step_type]

        if step_type in uniq_step_types:
            # Обрабатываем как уникальное определение шага
            if step_text not in step_definitions:
                step_definitions[step_text] = get_matcher(func, step_text)
            else:
                if not self.same_step_definition(step_definitions[step_text], step_text, step_location):
                    raise AmbiguousStep(f'existing step\n\t{step_text}')
        else:
            self.base_add_step_definition(keyword, step_text, func)
        
    def find_step_definition(self, step):
        try:
            step_definition = self.steps[STEP][step.name]
        except KeyError:
            step_definition = self.base_find_step_definition(step)

        return step_definition

    def find_match(self, step):
        try:
            step_match = self.steps[STEP][step.name].match(step.name)
        except KeyError:
            step_match = self.base_find_match(step)

        return step_match

    def make_decorator(self, step_type):
        def decorator(step_text):
            def wrapper(func):
                self.add_step_definition(step_type, step_text, func)
                return func
            return wrapper
        return decorator


registry = StepRegistry()


# -- Create the decorators
# pylint: disable=redefined-outer-name
def setup_step_decorators(run_context=None, registry=registry):
    if run_context is None:
        run_context = globals()
    for step_type in step_types:
        step_decorator = registry.make_decorator(step_type)
        run_context[step_type.title()] = run_context[step_type] = step_decorator


# -----------------------------------------------------------------------------
# MODULE INIT:
# -----------------------------------------------------------------------------
setup_step_decorators()
