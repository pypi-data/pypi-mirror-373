import random
from abc import ABC, abstractmethod

from typing_extensions import Dict, List, override

from program_searcher.exceptions import RemoveStatementError
from program_searcher.program_model import Program, Statement


class MutationStrategy(ABC):
    """
    Abstract base class for mutation strategies.

    Each implementation should modify the given `Program` object **in-place**
    rather than returning a new object. This ensures that mutation is applied
    directly without requiring extra copying or reassignment logic.
    """

    @abstractmethod
    def mutate(self, program: Program):
        """
        Mutates the given program in-place.

        Parameters
        ----------
        program : Program
            The program object to be mutated.

        Returns
        -------
        None
            The mutation is applied directly to `program`; no new object
            should be returned.
        """
        raise NotImplementedError


class RemoveStatementMutationStrategy(MutationStrategy, ABC):
    """
    Mutation strategy that attempts to remove a random statement from a program.

    The strategy selects a random statement index and removes it from the program,
    while ensuring that the `return` statement (if present) is never removed.
    If the selected statement cannot be removed due to variable dependencies
    (or other constraints enforced by `Program.remove_statement`), the strategy
    retries up to ``remove_retries`` times before giving up.

    Attributes:
        remove_retries (int): Maximum number of attempts to remove a statement.
                              Defaults to 3.

    Methods:
        mutate(program: Program) -> None:
            Tries to remove one statement from the given program.
            If no removable statements are available, or all retries fail,
            the program remains unchanged.
    """

    def __init__(self, remove_retries: int = 3):
        self.remove_retries = remove_retries

    @override
    def mutate(self, program: Program):
        max_index = len(program) - (1 if program.has_return_statement() else 0)

        if max_index <= 0:
            return

        for _ in range(self.remove_retries):
            try:
                statement_to_remove_idx = random.randrange(max_index)
                program.remove_statement(statement_to_remove_idx)
                return
            except RemoveStatementError:
                pass


class ReplaceStatementMutationStrategy(MutationStrategy, ABC):
    """
    Mutation strategy that replaces the function and arguments of an existing
    statement in the program.

    A random statement (excluding the final `return`, if present) is chosen, and
    its `func` and `args` fields are replaced with a randomly selected function
    from the available function set and a matching number of arguments sampled
    from the program's variables. The target variable of the statement
    (i.e. its result variable name) remains unchanged.

    Attributes:
        available_functions (Dict[str, int]):
            A mapping from function name to the required number of arguments
            that function expects.

    Methods:
        mutate(program: Program) -> None:
            Replaces one statement's function and arguments. If the program
            has no eligible statements (only a `return` or is empty),
            the program remains unchanged.
    """

    def __init__(self, available_functions: Dict[str, int]):
        self.available_functions = available_functions

    @override
    def mutate(self, program: Program):
        func_name = random.choice(list(self.available_functions.keys()))
        args_size = self.available_functions[func_name]

        if not program.variables and args_size > 0:
            return

        args = random.choices(program.variables, k=args_size)

        max_index = len(program) - (1 if program.has_return_statement() else 0)
        if max_index <= 0:
            return

        replace_index = random.randrange(max_index)
        replace_statement = program.get_statement(replace_index)
        replace_statement.func = func_name
        replace_statement.args = args


class UpdateStatementArgsMutationStrategy(MutationStrategy, ABC):
    """
    Mutation strategy that replaces the arguments of a random statement in a program.

    This strategy selects a random statement (including the return statement, if present)
    and replaces its arguments with new variables randomly chosen from the program's
    current variables. The number of arguments remains the same as in the original
    statement. The statement's function and target variable are not modified.

    Methods:
        mutate(program: Program) -> None:
            Updates the arguments of one statement in the program. If the program
            is empty, no mutation is performed.
    """

    @override
    def mutate(self, program: Program):
        if len(program) == 0:
            return

        statement_idx = random.randrange(len(program))
        statement = program.get_statement(statement_idx)
        statement_args_count = len(statement.args)

        new_args = random.choices(program.variables, k=statement_args_count)
        statement.args = new_args


class InsertStatementMutationStrategy(MutationStrategy, ABC):
    """
    Mutation strategy that inserts a random statement into a program.

    The statement is inserted at a random position before the return statement
    (if present) to ensure the program remains valid. The new statement is
    generated based on the allowed functions and their argument counts.

    Attributes
    ----------
    available_functions : Dict[str, int]
        A mapping of function names to the number of arguments they require.
    """

    def __init__(self, available_functions: Dict[str, int]):
        self.available_functions = available_functions

    @override
    def mutate(self, program: Program):
        if len(program) == 0:
            return

        max_index = len(program) - (1 if program.has_return_statement() else 0)
        if max_index <= 0:
            return

        insert_index = random.randrange(max_index)

        statement = self._generate_random_statement(program.variables)
        program.insert_statement(statement, insert_index)

    def _generate_random_statement(self, program_vars: List[str]) -> Statement:
        func_name = random.choice(list(self.available_functions.keys()))
        allowed_args_size = self.available_functions[func_name]
        args = random.choices(program_vars, k=allowed_args_size)
        return Statement(func=func_name, args=args)
