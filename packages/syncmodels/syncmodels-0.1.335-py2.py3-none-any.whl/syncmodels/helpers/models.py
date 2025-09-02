"""
This module will help in creating synthetic or random data
for testing purposes.

- [ ] feed pytest pydantic data consistency
- [ ] feed FastAPI swagger examples
- [ ] other runtime uses

"""

from .general import new_uid
from .faker import fake, next_monotonic_uid

from ..model.enums import *
from ..model.inventory import *
from ..model.task import *
from ..model.script import *

# Other models that will be generated here
from ..model.resource import *
from ..model.planner import *


def random_item():
    return {
        "id": new_uid(),
        "name": fake.item_name(),
        # "name": fake.name(),
        # "description": fake.sentence(),
        "description": fake.paragraph(nb_sentences=1),
    }
