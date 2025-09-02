
import pytest
from reasoning_core.template import Task, DATASETS
from reasoning_core.tasks import arithmetics, causal_reasoning, formal_maths, grammar, logic, planning, regex_following, sequential_induction, set_operations

# This import is necessary to trigger the registration of the tasks in the DATASETS dictionary.
# Every time a new task is added, it should be imported here.
# TODO: Find a way to automatically import all modules in the tasks directory.

failing_tasks = [
    "logicnli",
    "evidenceretrieval",
    "entailmenttask",
    "premiseselectiontask",
]

@pytest.mark.parametrize("task_name, task_cls", DATASETS.items())
def test_task_consistency(task_name, task_cls):
    """
    Tests that for any given task, the score of the correct answer is 1.
    """
    if task_name in failing_tasks:
        pytest.xfail(f"Task {task_name} is known to fail due to environment issues (eprover).")
    
    task = task_cls()
    problem = task.generate_example()
    score = task.score_answer(problem.answer, problem)
    assert score == 1, f"Task {task_name} failed consistency check. For a generated problem, the score of the correct answer should be 1, but it was {score}."

