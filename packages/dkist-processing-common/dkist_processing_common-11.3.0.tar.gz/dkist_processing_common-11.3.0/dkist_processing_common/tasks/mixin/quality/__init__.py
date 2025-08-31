"""Mixin class supporting the generation of the quality reports.

To improve readability the top-level mixin, `QualityMixin`, contains only base functionality and the separate
metrics are grouped into sub-mixins. To protect a user, this mixin-on-mixin stack is hidden in protected modules
and only the top-level mixin (`QualityMixin`) is exposed.
"""

from ._base import QualityMixin
