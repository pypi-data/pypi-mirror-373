# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from asteroid_odyssey.agents_v2_gen.api.execution_api import ExecutionApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from asteroid_odyssey.agents_v2_gen.api.execution_api import ExecutionApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
