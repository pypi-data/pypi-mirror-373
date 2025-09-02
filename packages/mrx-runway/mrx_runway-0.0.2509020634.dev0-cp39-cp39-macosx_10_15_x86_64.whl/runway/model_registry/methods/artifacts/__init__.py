#
#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2024] MakinaRocks Co., Ltd.
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
# NOTE 여기부턴 runway-taskflow 와 runway_app 에서
# 그대로 복붙해서 가져다 쓰기때문에 상대경로 모듈로 import 한다.
from pathlib import Path
from typing import Optional, Union, Dict, Any

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from ...schemas import Revisionable, Revision
from ...values import SchemaRevision


class RunwayModelArtifacts:
    @classmethod
    def parse(cls, path: Union[str, Path]) -> Revisionable:
        if isinstance(path, str):
            path = Path(path)

        revision = Revision.parse(path)
        if revision.revision == SchemaRevision.rev2:
            from .rev2.base import ModelArtifacts
        else:
            raise ValueError(f"unsupported revision: {revision.revision=}")

        return ModelArtifacts.parse(path)

    @classmethod
    def build(
        cls, revision: Optional[SchemaRevision] = None, **kwargs: Unpack[Dict[str, Any]]
    ) -> Revisionable:
        if revision is None:
            revision = SchemaRevision.get_latest_revision()

        if revision == SchemaRevision.rev2:
            from .rev2.base import ModelArtifacts
        else:
            raise ValueError(f"unsupported revision: {revision=}")

        return ModelArtifacts.build(
            Revisionable.BuilderContext(revision=revision, **kwargs),
        )
