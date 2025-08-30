class ExecutionError(Exception):
    """Exceção base para erros relacionados à execução."""

class ExecutionAlreadyFinishedError(ExecutionError):
    """Lançada quando uma operação é chamada em uma execução já finalizada."""

class ExecutionFieldError(ExecutionError):
    """Lançada quando o campo informado não existe no ExecutionModel."""

class ExecutionUpdateError(ExecutionError):
    """Lançada quando ocorre falha ao atualizar a execução no servidor."""

class ExecutionNotStardedError(ExecutionError):
    """Lançada quando ocorre falha ao atualizar a execução no servidor."""


class TaskError(Exception):
    """Exceção base para erros relacionados à task."""

class TaskUpdateError(TaskError):
    """Lançada quando ocorre falha ao atualizar a execução no servidor."""

class TaksNotStardedError(TaskError):
    """Lançada quando ocorre falha ao atualizar a execução no servidor."""


