from django.conf import (
    settings,
)


def get_context_extractor_class():
    # TODO BOBUH-23698 Вынести настройку CONTEXT_EXTRACTOR из web_bb_behave
    context_extractor_cls = settings.WEB_BB_BEHAVE__CONTEXT_EXTRACTOR
    context_extractor_cls_path = context_extractor_cls.split('.')
    # Allow for relative paths
    if len(context_extractor_cls_path) > 1:
        extractor_module_name = '.'.join(context_extractor_cls_path[:-1])
    else:
        extractor_module_name = '.'
    extractor_module = __import__(extractor_module_name, {}, {}, context_extractor_cls_path[-1])
    return getattr(extractor_module, context_extractor_cls_path[-1])


context_extractor_class = get_context_extractor_class()
context_extractor = context_extractor_class()
