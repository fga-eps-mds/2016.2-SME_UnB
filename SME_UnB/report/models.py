from __future__ import unicode_literals

from django.db import models

class Report(models.Model):

    class Meta:
        permissions = (
            ("can_generate", "Can Generate Reports"),
        )
    """Function to fix single permission exception"""

    def _get_all_permissions(opts, ctype):
        builtin = _get_builtin_permissions(opts)
        custom = list(opts.permissions)
        _check_permission_clashing(custom, builtin, ctype)
        return builtin + custom
