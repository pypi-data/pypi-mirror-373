import pickle  # nosec
from typing import Any, Dict, List

from workflow.definitions.work import Work
from workflow.http.context import HTTPContext

results = HTTPContext(backends=["results"]).results


def work(works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of works from old workflow objects to new workflow objects
    that are supported by the new API.

    Args:
        works (List[Dict[str, Any]]): A list of old workflow work objects.

    Returns:
        List[Dict[str, Any]]: A list of payloads (converted), where each payload is represented as a dictionary.

    """
    converted: List[Dict[str, Any]] = []

    for work in works:
        work.pop("config")
        if not work["results"]:
            print("The following event is missing results: \n")
            print(
                {
                    "workflow_id": work["id"],
                    "event_ID": work["event"],
                    "products": work["products"],
                    "plots": work["plots"],
                }
            )
        else:
            work["results"]["locked"] = False
            payload = Work(**work).payload
            converted.append(payload)

    return converted


def get_outliers(pipeline: str) -> List[Dict[str, Any]]:
    """
    Retrieves outliers from the specified pipeline.
    Outliers are old depracated workflow objects.

    Args:
        pipeline (str): The name of the pipeline.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the retrieved outliers.

    Raises:
        Exception: If an error occurs during the retrieval process.
    """
    old_work_objs: List[Dict][str, Any] = []

    def get_single_old_work(workflow_id: str) -> List[Dict[str, Any]]:
        """
        Helper Function:
        Retrieves a single old work item based on the provided workflow ID.

        Args:
            workflow_id (str): The ID of the workflow to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the retrieved work item.

        Raises:
            Exception: If an error occurs during the retrieval process.
        """
        try:
            work = results.view(
                pipeline=pipeline,
                query={"id": workflow_id, "config": None},
                projection={},
                limit=-1,
            )
            return work
        except Exception as e:
            print(f"Error: {e}")
            return {}

    def get_single_old_work_from_event_id(
        event_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Helper Function:
        Retrieves a single old work from the given event ID.

        Args:
            event_id (str): The ID of the event.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the retrieved work.

        Raises:
            Exception: If an error occurs during the retrieval process.
        """
        try:
            work = results.view(
                pipeline=pipeline,
                query={"event": [int(event_id)], "config": None},
                projection={},
                limit=-1,
            )
            return work
        except Exception as e:
            print(f"Error: {e}")
            return {}

    try:
        with open(f"outliers_in_{pipeline}.txt") as file:
            for line in file:
                _, workflow_id = line.split()
                old_work = get_single_old_work(workflow_id)
                if old_work:
                    old_work_objs.append(get_single_old_work(workflow_id))

        with open(f"outliers_in_{pipeline}.pkl", "wb") as f:
            pickle.dump(old_work_objs, f)

    except Exception as e:
        print(f"Error: {e}")
