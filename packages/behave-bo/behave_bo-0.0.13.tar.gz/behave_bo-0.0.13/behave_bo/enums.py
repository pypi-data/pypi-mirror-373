
class StepTypeEnum:
    """
    Типы шагов теста.
    """
    GIVEN = 'given'
    WHEN = 'when'
    THEN = 'then'

    values = {
        WHEN: 'Шаг Когда',
        THEN: 'Шаг Тогда',
    }
