from . import acm, ecs, elbv2, ssm


def register_bundled_types(registry):
    acm.register_bundled_types(registry)
    ecs.register_bundled_types(registry)
    elbv2.register_bundled_types(registry)
    ssm.register_bundled_types(registry)
