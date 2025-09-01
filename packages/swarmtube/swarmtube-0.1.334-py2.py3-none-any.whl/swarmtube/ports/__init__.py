"""
@tags: Hexagonal, model, pydantic

This module contains all primary port definition such request / responses models, etc
used to communicate with the outside world, no matter is it comes from an API REST
interface or CLI interface.

This module does not contain implementation of how to create these classes.
These features must be implemented in CLI or API modules.

Encapsulating such data structure into model classes allows us to use pydantic for
checking the consistency of any IO message exchange by the logic.

"""

from .preferences import *
