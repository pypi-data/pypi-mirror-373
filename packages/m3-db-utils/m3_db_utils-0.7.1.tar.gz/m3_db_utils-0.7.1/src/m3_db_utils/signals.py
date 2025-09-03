from django.dispatch.dispatcher import (
    Signal,
)


before_handle_migrate_signal = Signal()
after_handle_migrate_signal = Signal()
