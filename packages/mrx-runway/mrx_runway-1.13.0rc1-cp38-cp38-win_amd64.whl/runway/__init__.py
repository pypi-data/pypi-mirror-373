#
#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2023] MakinaRocks Co., Ltd.
#  All Rights Reserved.
#
#  NOTICE:  All information contained herein is, and remains
#  the property of MakinaRocks Co., Ltd. and its suppliers, if any.
#  The intellectual and technical concepts contained herein are
#  proprietary to MakinaRocks Co., Ltd. and its suppliers and may be
#  covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law. Dissemination
#  of this information or reproduction of this material is
#  strictly forbidden unless prior written permission is obtained
#  from MakinaRocks Co., Ltd.

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type : ignore

__version__ = importlib_metadata.version("mrx-runway")


from runway.dataset import (  # pylint: disable=wrong-import-position
    save_dataset,
    create_dataset,
    create_dataset_version,
    get_dataset,
    get_dataset_list,
)
from runway.workspaces import (
    get_joined_workspaces,
    set_joined_workspace,
)
from runway.projects import (
    get_joined_projects,
    set_joined_project,
)

from runway.model_registry.methods.methods import (
    set_model_registry,
    get_model_registry_list,
)

from runway.model_registry.methods.mlflow import log_model
from runway.model_registry.methods import mlflow
from runway.common.utils import get_runway_environment
from runway.users.methods import get_user_profile, login, logout


class mlflow_module:
    from runway.model_registry.methods.mlflow import log_runway_model_artifacts  # type: ignore


import sys

sys.modules["runway.model_registry.mlflow"] = mlflow_module  # type: ignore

from runway.inference_services import get_inference_services, get_inference_service
from runway.inference_services.values import InferenceDatabaseRecordsMatchType, InferenceDatabaseRecordsSortOrderType
from runway.inference_services.schemas import (
    InferenceDatabaseRecordsFilter,
    InferenceDatabaseRecordsSorting,
    InferenceDatabaseRecordsQuery,
)

# indicate all modules provided
__all__ = [
    "save_dataset",
    "create_dataset",
    "create_dataset_version",
    "get_dataset",
    "get_dataset_list",
    "log_model",
    "get_joined_workspaces",
    "set_joined_workspace",
    "get_joined_projects",
    "set_joined_project",
    "mlflow",
    "set_model_registry",
    "get_model_registry_list",
    "get_user_profile",
    "login",
    "logout",
    "get_runway_environment",
    "get_inference_services",
    "get_inference_service",
    "InferenceDatabaseRecordsMatchType",
    "InferenceDatabaseRecordsSortOrderType",
    "InferenceDatabaseRecordsFilter",
    "InferenceDatabaseRecordsSorting",
    "InferenceDatabaseRecordsQuery",
]
