from collections.abc import Callable, Sequence
import enum
from typing import Annotated, overload

from numpy.typing import ArrayLike
import scipy

import _jormungandr.autodiff


class EqualityConstraints:
    """A vector of equality constraints of the form cₑ(x) = 0."""

    def __init__(self, equality_constraints: Sequence[EqualityConstraints]) -> None:
        """
        Concatenates multiple equality constraints.

        This overload is for Python bindings only.

        Parameter ``equality_constraints``:
            The list of EqualityConstraints to concatenate.
        """

    def __bool__(self) -> bool:
        """Implicit conversion operator to bool."""

class InequalityConstraints:
    """A vector of inequality constraints of the form cᵢ(x) ≥ 0."""

    def __init__(self, inequality_constraints: Sequence[InequalityConstraints]) -> None:
        """
        Concatenates multiple inequality constraints.

        This overload is for Python bindings only.

        Parameter ``inequality_constraints``:
            The list of InequalityConstraints to concatenate.
        """

    def __bool__(self) -> bool:
        """Implicit conversion operator to bool."""

class ExitStatus(enum.Enum):
    """Solver exit status. Negative values indicate failure."""

    SUCCESS = 0
    """Solved the problem to the desired tolerance."""

    CALLBACK_REQUESTED_STOP = 1
    """
    The solver returned its solution so far after the user requested a
    stop.
    """

    TOO_FEW_DOFS = -1
    """The solver determined the problem to be overconstrained and gave up."""

    LOCALLY_INFEASIBLE = -2
    """
    The solver determined the problem to be locally infeasible and gave
    up.
    """

    GLOBALLY_INFEASIBLE = -3
    """
    The problem setup frontend determined the problem to have an empty
    feasible region.
    """

    FACTORIZATION_FAILED = -4
    """The linear system factorization failed."""

    LINE_SEARCH_FAILED = -5
    """
    The backtracking line search failed, and the problem isn't locally
    infeasible.
    """

    NONFINITE_INITIAL_COST_OR_CONSTRAINTS = -6
    """
    The solver encountered nonfinite initial cost or constraints and gave
    up.
    """

    DIVERGING_ITERATES = -7
    """
    The solver encountered diverging primal iterates xₖ and/or sₖ and gave
    up.
    """

    MAX_ITERATIONS_EXCEEDED = -8
    """
    The solver returned its solution so far after exceeding the maximum
    number of iterations.
    """

    TIMEOUT = -9
    """
    The solver returned its solution so far after exceeding the maximum
    elapsed wall clock time.
    """

class IterationInfo:
    """Solver iteration information exposed to an iteration callback."""

    @property
    def iteration(self) -> int:
        """The solver iteration."""

    @property
    def x(self) -> Annotated[ArrayLike, dict(dtype='float64', shape=(None), order='C')]:
        """The decision variables."""

    @property
    def g(self) -> scipy.sparse.csc_matrix[float]:
        """The gradient of the cost function."""

    @property
    def H(self) -> scipy.sparse.csc_matrix[float]:
        """The Hessian of the Lagrangian."""

    @property
    def A_e(self) -> scipy.sparse.csc_matrix[float]:
        """The equality constraint Jacobian."""

    @property
    def A_i(self) -> scipy.sparse.csc_matrix[float]:
        """The inequality constraint Jacobian."""

class Problem:
    """
    This class allows the user to pose a constrained nonlinear
    optimization problem in natural mathematical notation and solve it.

    This class supports problems of the form: @verbatim minₓ f(x) subject
    to cₑ(x) = 0 cᵢ(x) ≥ 0 @endverbatim

    where f(x) is the scalar cost function, x is the vector of decision
    variables (variables the solver can tweak to minimize the cost
    function), cᵢ(x) are the inequality constraints, and cₑ(x) are the
    equality constraints. Constraints are equations or inequalities of the
    decision variables that constrain what values the solver is allowed to
    use when searching for an optimal solution.

    The nice thing about this class is users don't have to put their
    system in the form shown above manually; they can write it in natural
    mathematical form and it'll be converted for them.
    """

    def __init__(self) -> None:
        """Construct the optimization problem."""

    @overload
    def decision_variable(self) -> _jormungandr.autodiff.Variable:
        """
        Create a decision variable in the optimization problem.

        Returns:
            A decision variable in the optimization problem.
        """

    @overload
    def decision_variable(self, rows: int, cols: int = 1) -> _jormungandr.autodiff.VariableMatrix:
        """
        Create a matrix of decision variables in the optimization problem.

        Parameter ``rows``:
            Number of matrix rows.

        Parameter ``cols``:
            Number of matrix columns.

        Returns:
            A matrix of decision variables in the optimization problem.
        """

    def symmetric_decision_variable(self, rows: int) -> _jormungandr.autodiff.VariableMatrix:
        """
        Create a symmetric matrix of decision variables in the optimization
        problem.

        Variable instances are reused across the diagonal, which helps reduce
        problem dimensionality.

        Parameter ``rows``:
            Number of matrix rows.

        Returns:
            A symmetric matrix of decision varaibles in the optimization
            problem.
        """

    @overload
    def minimize(self, cost: _jormungandr.autodiff.Variable) -> None:
        """
        Tells the solver to minimize the output of the given cost function.

        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.

        Parameter ``cost``:
            The cost function to minimize.
        """

    @overload
    def minimize(self, cost: _jormungandr.autodiff.VariableMatrix) -> None: ...

    @overload
    def minimize(self, cost: float) -> None: ...

    @overload
    def maximize(self, objective: _jormungandr.autodiff.Variable) -> None:
        """
        Tells the solver to maximize the output of the given objective
        function.

        Note that this is optional. If only constraints are specified, the
        solver will find the closest solution to the initial conditions that's
        in the feasible set.

        Parameter ``objective``:
            The objective function to maximize.
        """

    @overload
    def maximize(self, objective: _jormungandr.autodiff.VariableMatrix) -> None: ...

    @overload
    def maximize(self, objective: float) -> None: ...

    @overload
    def subject_to(self, constraint: EqualityConstraints) -> None:
        """
        Tells the solver to solve the problem while satisfying the given
        equality constraint.

        Parameter ``constraint``:
            The constraint to satisfy.
        """

    @overload
    def subject_to(self, constraint: InequalityConstraints) -> None:
        """
        Tells the solver to solve the problem while satisfying the given
        inequality constraint.

        Parameter ``constraint``:
            The constraint to satisfy.
        """

    def cost_function_type(self) -> _jormungandr.autodiff.ExpressionType:
        """
        Returns the cost function's type.

        Returns:
            The cost function's type.
        """

    def equality_constraint_type(self) -> _jormungandr.autodiff.ExpressionType:
        """
        Returns the type of the highest order equality constraint.

        Returns:
            The type of the highest order equality constraint.
        """

    def inequality_constraint_type(self) -> _jormungandr.autodiff.ExpressionType:
        """
        Returns the type of the highest order inequality constraint.

        Returns:
            The type of the highest order inequality constraint.
        """

    def solve(self, **kwargs) -> ExitStatus:
        """
        Solve the optimization problem. The solution will be stored in the
        original variables used to construct the problem.

        Parameter ``tolerance``:
            The solver will stop once the error is below this tolerance.
            (default: 1e-8)

        Parameter ``max_iterations``:
            The maximum number of solver iterations before returning a solution.
            (default: 5000)

        Parameter ``timeout``:
            The maximum elapsed wall clock time before returning a solution.
            (default: infinity)

        Parameter ``feasible_ipm``:
            Enables the feasible interior-point method. When the inequality
            constraints are all feasible, step sizes are reduced when necessary to
            prevent them becoming infeasible again. This is useful when parts of the
            problem are ill-conditioned in infeasible regions (e.g., square root of a
            negative value). This can slow or prevent progress toward a solution
            though, so only enable it if necessary.
            (default: False)

        Parameter ``diagnostics``:
            Enables diagnostic prints.

            <table>
              <tr>
                <th>Heading</th>
                <th>Description</th>
              </tr>
              <tr>
                <td>iter</td>
                <td>Iteration number</td>
              </tr>
              <tr>
                <td>type</td>
                <td>Iteration type (normal, accepted second-order correction, rejected second-order correction)</td>
              </tr>
              <tr>
                <td>time (ms)</td>
                <td>Duration of iteration in milliseconds</td>
              </tr>
              <tr>
                <td>error</td>
                <td>Error estimate</td>
              </tr>
              <tr>
                <td>cost</td>
                <td>Cost function value at current iterate</td>
              </tr>
              <tr>
                <td>infeas.</td>
                <td>Constraint infeasibility at current iterate</td>
              </tr>
              <tr>
                <td>complement.</td>
                <td>Complementary slackness at current iterate (sᵀz)</td>
              </tr>
              <tr>
                <td>μ</td>
                <td>Barrier parameter</td>
              </tr>
              <tr>
                <td>reg</td>
                <td>Iteration matrix regularization</td>
              </tr>
              <tr>
                <td>primal α</td>
                <td>Primal step size</td>
              </tr>
              <tr>
                <td>dual α</td>
                <td>Dual step size</td>
              </tr>
              <tr>
                <td>↩</td>
                <td>Number of line search backtracks</td>
              </tr>
            </table>
            (default: False)

        Parameter ``spy``:
            Enables writing sparsity patterns of H, Aₑ, and Aᵢ to files named H.spy,
            A_e.spy, and A_i.spy respectively during solve. Use tools/spy.py to plot them.
            (default: False)
        """

    def add_callback(self, callback: Callable[[IterationInfo], bool]) -> None:
        """
        Adds a callback to be called at the beginning of each solver
        iteration.

        The callback for this overload should return bool.

        Parameter ``callback``:
            The callback. Returning true from the callback causes the solver
            to exit early with the solution it has so far.
        """

    def clear_callbacks(self) -> None:
        """Clears the registered callbacks."""
