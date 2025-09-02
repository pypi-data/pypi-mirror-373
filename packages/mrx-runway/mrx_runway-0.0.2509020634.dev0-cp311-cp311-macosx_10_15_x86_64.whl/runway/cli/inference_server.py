#
#  MAKINAROCKS CONFIDENTIAL
#  ________________________
#
#  [2017] - [2025] MakinaRocks Co., Ltd.
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
import argparse
import base64
import logging
import multiprocessing
import uuid
from concurrent import futures
from typing import Any, Dict, List, Optional, Union

import cloudpickle
import numpy as np
import pandas as pd
from grpc import aio
from kserve import InferRequest, Model, ModelServer
from kserve.protocol.dataplane import DataPlane
from kserve.protocol.grpc import grpc_predict_v2_pb2_grpc
from kserve.protocol.grpc.grpc_predict_v2_pb2 import (
    ModelInferRequest,
    ModelInferResponse,
)
from kserve.protocol.grpc.interceptors import LoggingInterceptor
from kserve.protocol.grpc.server import GRPCServer
from kserve.protocol.grpc.servicer import InferenceServicer
from kserve.protocol.infer_type import InferRequest, InferResponse
from kserve.protocol.model_repository_extension import ModelRepositoryExtension
from kserve.utils.utils import get_predict_input, get_predict_response

from runway.model_registry.methods.artifacts import RunwayModelArtifacts
from runway.settings import settings

DATAFRAME_TO_TENSOR_DTYPE = {
    "object": "BYTES",
    "int32": "INT32",
    "int64": "INT64",
    "float32": "FP32",
    "float64": "FP64",
    "bool": "BOOL",
}

DTYPE_TO_GRPC_CONTENT = {
    "BYTES": "bytes_contents",
    "INT32": "int_contents",
    "INT64": "int64_contents",
    "FP32": "fp32_contents",
    "FP64": "fp64_contents",
    "BOOL": "bool_contents",
}


class RunwayModel(Model):
    def __init__(
        self,
        name: str,
        model_path: str,
        model_file: str,
        model_method_name: str,
        use_grpc: bool = False,
    ):
        super().__init__(name)
        self.model_path = model_path
        self.model_file = model_file
        self.model_method_name = model_method_name
        self.use_grpc = use_grpc

        self.load()  # Load model from the argument
        logging.info(
            f"RunwayModel is initialized: {self.use_grpc=}, {self.model_path=}, "
            f"{self.model_file=}, {self.model_method_name}, ",
        )

    def load(self) -> None:
        """Load pyfunc model logged from Link via Runway SDK"""
        # NOTE 현재는 pyfunc 더라도 python_model.pkl -> model.pkl 로 archive 하기 때문에 runway loader 를 사용한다.
        with open(self.model_file, "rb") as model_pyfunc_pkl:
            # FIXME mlflow.xxx.load_model() 로 변경해야 한다...
            self.model = cloudpickle.load(model_pyfunc_pkl)
            if not getattr(self.model, self.model_method_name):
                logging.critical(
                    f"current model doesn't have {self.model_method_name} method",
                )
                exit(-1)
        self.model_artifacts = RunwayModelArtifacts.parse(self.model_path)
        self.inputs_schema_dtype = self.get_inputs_schema_dtype(
            self.model_artifacts.model_config.signatures.get(self.model_method_name),
        )

        self.ready = True

    def predict(
        self,
        payload: Union[Dict, InferRequest, ModelInferRequest],
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[Dict, InferResponse, ModelInferResponse]:
        # NOTE get_predict_input 를 사용하기 위해 mlserver==1.3.2 을 사용하는 kserve=0.11.x 가 필요
        # - https://github.com/kserve/kserve/pull/2910
        # - https://github.com/kserve/kserve/pull/2655
        # NOTE 지금은 mlflow.pyfunc.PythonModel 을 derived class 로 구현하였기 때문에 context=None 으로 처리한다.
        # - https://www.mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
        # NOTE predict() 함수의 payload 의 inputs 은 bytes type 으로 디코딩된 value 이 올라온다.
        # get_predict_input() 를 타면 pandas.DataFrame 의 경우 모두 string type 으로 변환되어,
        # schema 를 보고 추가 변환해줘야 한다.
        # 예를 들어, "bytes_contents": ["WQ==\n"] 로 요청하면,
        # predict 에서는 b"Y" 로, get_predict_input() 을 거치면 "Y",
        # 이를 아래 전처리를 통해 "Y" (dtype=str) or b"Y" (dtype=bytes) 로 처리되어야 한다.
        predict_input = get_predict_input(payload)
        for column_name in predict_input:
            dtype = self.inputs_schema_dtype[0].get(column_name)
            if not dtype:
                continue
            # NOTE backend api-server 의 servings 의 grpc inputs_sample 다운로드하는 인코더 타입에 맞춰야 한다.
            if dtype == "bytes":
                if self.use_grpc:
                    predict_input[column_name] = predict_input[column_name].map(
                        lambda v: v.encode("ascii"),
                    )
                else:
                    # NOTE backend runway_app/servings/service.py 에서 inputs_sample 다운로드시
                    # 한번 더 해주는 string encoding 에 대응되는 decoding 코드이다.
                    predict_input[column_name] = predict_input[column_name].map(
                        lambda v: base64.decodebytes(v.encode()),
                    )

        result = getattr(self.model, self.model_method_name)(None, predict_input)
        if isinstance(result, pd.DataFrame):
            if self.use_grpc:
                response = get_predict_response(payload, result, self.name)
            else:
                # TODO 아래 코드는 legacy 코드로, pandas.DataFrame 에 대해서도
                # kserve.utils.utils.get_predict_response 를 이용하게끔 수정되어야 한다.
                # From DataFrame to K-serve v2 protocol response output format.
                outputs = []
                result_dict = result.to_dict(orient="list")
                for col_name, col_data in result_dict.items():
                    dtype = DATAFRAME_TO_TENSOR_DTYPE.get(
                        str(result[col_name].dtype),
                        "BYTES",
                    )
                    # Dictionary 로 predict의 리턴을 전달하는 경우 protocol 정보에 따라 output shape이 다르다.
                    # gRPC 프로토콜에서는 dtype이 결정된채로 데이터가 넘어가야하기 때문이다. 바로 위에서 언급한 것처럼,
                    # legacy를 해결하고 get_predict_response를 이용하게끔 수정하면 이 이슈도 해결될 것으로 보인다.
                    outputs.append(
                        {
                            "name": col_name,
                            "shape": [len(col_data)],
                            "datatype": dtype,
                            "data": col_data,
                        },
                    )
                response = {
                    "model_name": self.name,
                    "id": str(uuid.uuid4()),
                    "outputs": outputs,
                }
        elif isinstance(result, pd.Series):
            dtype = DATAFRAME_TO_TENSOR_DTYPE.get(
                str(result.dtype),
                "BYTES",
            )
            result = result.to_list()
            output: Dict[str, Any] = {
                "name": "output",
                "shape": [len(result)],
                "datatype": dtype,
            }
            if self.use_grpc:
                output["contents"] = {
                    DTYPE_TO_GRPC_CONTENT[dtype]: result,
                }
            else:
                output["data"] = result

            response = {
                "model_name": self.name,
                "id": str(uuid.uuid4()),
                "outputs": [output],
            }
        elif isinstance(result, np.ndarray):
            response = get_predict_response(payload, result, self.name)

        return response

    @staticmethod
    def get_inputs_schema_dtype(signature: Any) -> List:
        inputs_schema_dtype = []
        for i, input in enumerate(signature.inputs):
            inputs_schema_dtype.append(
                {schema.name: schema.dtype for schema in input.schema_},
            )
        return inputs_schema_dtype


class RunwayGRPCServer(GRPCServer):
    """
    kserve 의 GRPC Server 는 MAX_GRPC_MESSAGE_LENGTH = 8388608 로 고정되어 있다. (8 MiB)
    Ref) https://github.com/kserve/kserve/blob/ca691f728ac0fe6a711b2953a88abb1b3d532658/python/kserve/kserve/protocol/grpc/server.py#L29
    이를 피하기 위해, settings.MAX_GRPC_MESSAGE_LENGTH 로 해당 Limit 을 Configurable 하게 변경한다.
    """

    def __init__(
        self,
        port: int,
        data_plane: DataPlane,
        model_repository_extension: ModelRepositoryExtension,
    ):
        super().__init__(port, data_plane, model_repository_extension)

    async def start(
        self, max_workers: Optional[int] = None
    ) -> None:  # override the start method of GRPCServer
        inference_servicer = InferenceServicer(
            self._data_plane,
            self._model_repository_extension,
        )

        self._server = aio.server(
            futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()),
            interceptors=(LoggingInterceptor(),),
            options=settings.grpc_options,
        )
        grpc_predict_v2_pb2_grpc.add_GRPCInferenceServiceServicer_to_server(
            inference_servicer,
            self._server,
        )

        listen_addr = f"[::]:{self._port}"
        self._server.add_insecure_port(listen_addr)
        await self._server.start()
        await self._server.wait_for_termination()


# NOTE pyproject.toml 파일에 "tool.poetry.scripts" 을 추가해도 되는데,
# sklearn 의 cloudpickle.load 시에 libgomp.so library memory allocation error 발생
# - https://forums.developer.nvidia.com/t/sklearn-cannot-allocate-memory-in-static-tls-block/210791
# 그래서 script command 가 아닌 "python -m" 을 이용한다.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Name of model to deploy", required=True)
    parser.add_argument(
        "-p",
        "--model-path",
        help="Path to model directory",
        default="/mnt/models",
    )
    parser.add_argument(
        "-f",
        "--model-file",
        help="Path to model file",
        default="/mnt/models/data/model_dir/model.pkl",
    )
    parser.add_argument(
        "-m",
        "--model-method-name",
        help="Name of model method to deploy",
        default="predict",
    )
    parser.add_argument(
        "--use-grpc",
        help="Whether to use the grpc protocol",
        action="store_true",
        default=False,
    )
    args = parser.parse_known_args()[0]

    model = RunwayModel(
        name=args.name,
        model_path=args.model_path,
        model_file=args.model_file,
        model_method_name=args.model_method_name,
        use_grpc=args.use_grpc,
    )

    server_ = ModelServer()
    if args.use_grpc:
        # override the kserve's default GRPCServer with RunwayGRPCServer
        server_._grpc_server = RunwayGRPCServer(
            server_.grpc_port,
            server_.dataplane,
            server_.model_repository_extension,
        )

    server_.start(
        models=[model],
    )
