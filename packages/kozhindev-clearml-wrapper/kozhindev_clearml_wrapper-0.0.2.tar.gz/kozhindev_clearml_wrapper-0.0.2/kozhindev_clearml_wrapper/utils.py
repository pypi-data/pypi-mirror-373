from typing import Literal

from clearml import Task, Dataset


def log_metrics(task: Task):
    """
    Decorator for logging scalar metrics to ClearML

    The decorated function should yield tuples in the format:
    (title, series, metric, iteration)

    Each yielded metric will be reported to the provided ClearML Task logger
    using report_scalar

    Args:
        task: ClearML Task object to log metrics to

    Returns:
        Callable: Decorator that logs metrics from the wrapped function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for title, series, metric, iteration in func(*args, **kwargs):
                task.get_logger().report_scalar(
                    title=title,
                    series=series,
                    value=metric,
                    iteration=iteration
                )
        return wrapper
    return decorator


def get_local_dataset_path(
    dataset_id: str,
    dataset_name: str,
    **kwargs
) -> str:
    """
    Retrieves the local path to a specific dataset file or folder using ClearML

    Downloads the dataset with the given ID if not already available locally,
    and constructs the full local path by appending the dataset_name

    Args:
        dataset_id: The ClearML dataset ID
        dataset_name: The name of the file or folder within the dataset
        **kwargs: Additional keyword arguments passed to Dataset.get

    Returns:
        str: The local path to the specified dataset file
    """
    dataset = Dataset.get(dataset_id=dataset_id, **kwargs)
    dataset_path = f'{dataset.get_local_copy()}/{dataset_name}'
    return dataset_path


def prepare_task(
    task_type: Literal['local', 'remote'],
    train_params: dict = None,
    **kwargs
) -> Task:
    """
    Initializes or retrieves a ClearML Task depending on the specified type

    If 'local', creates a new ClearML Task using the provided arguments
    If 'remote', retrieves the current ClearML Task and connects training parameters

    Args:
        task_type: Specifies whether to create a new task ('local') or use the current one ('remote')
        train_params: Training parameters to connect to the task (used for 'remote')
        **kwargs: Additional keyword arguments passed to Task.init

    Returns:
        Task: The initialized or retrieved ClearML Task
    """
    if task_type not in ['local', 'remote']:
        raise ValueError("task_type must be either 'local' or 'remote'")
    if task_type == 'local':
        task = Task.init(**kwargs)
    elif task_type == 'remote':
        task = Task.current_task()
        task.connect(train_params)
    return task


def get_local_model_path(task_id: str, artifact_name: str) -> str:
    """
    Returns the local path to a model artifact from a ClearML task

    Downloads the artifact with the given name from the specified task if not already available locally

    Args:
        task_id: ID of the ClearML task containing the artifact
        artifact_name: Name of the artifact to retrieve

    Returns:
        str: Local path to the specified model artifact
    """
    task = Task.get_task(task_id=task_id)
    path_to_model = task.artifacts[artifact_name].get_local_copy()
    return path_to_model
