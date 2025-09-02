import importlib
import inspect
from typing import Dict, List, Union

from mosec import Worker

import tiinfer


def load_workers() -> List[Dict]:
    module = importlib.import_module(tiinfer.IMPORT_MODULE_NAME)
    tiinfer_v1_styled = False
    for x in dir(module):
        if inspect.isclass(getattr(module, x)) and issubclass(
            getattr(module, x), tiinfer.Model
        ):
            tiinfer_v1_styled = True
            break
    if tiinfer_v1_styled:
        tiinfer.print_envs()
        if not tiinfer.Is_Multi_Framework_Type():
            return [
                {
                    "worker": tiinfer.Inference,
                    "num": tiinfer.get_ti_inference_nums(),
                    "max_batch_size": tiinfer.get_ti_inference_max_batch_size(),
                    "start_method": "spawn",
                    "env": None,
                }
            ]
        else:
            workers = []
            if tiinfer.get_ti_preprocess_nums() > 0:
                workers.append(
                    {
                        "worker": tiinfer.Preprocess,
                        "num": tiinfer.get_ti_preprocess_nums(),
                        "max_batch_size": 1,
                        "start_method": "spawn",
                        "env": None,
                    }
                )
            workers.append(
                {
                    "worker": tiinfer.Inference,
                    "num": tiinfer.get_ti_inference_nums(),
                    "max_batch_size": tiinfer.get_ti_inference_max_batch_size(),
                    "start_method": "spawn",
                    "env": None,
                }
            )
            if tiinfer.get_ti_postprocess_nums() > 0:
                workers.append(
                    {
                        "worker": tiinfer.Postprocess,
                        "num": tiinfer.get_ti_postprocess_nums(),
                        "max_batch_size": 1,
                        "start_method": "spawn",
                        "env": None,
                    }
                )
            return workers
    else:
        return tiinfer.get_mosec_workers()


def load_model_service() -> tiinfer.Model:
    module = importlib.import_module(tiinfer.IMPORT_MODULE_NAME)
    module_class = [
        getattr(module, x)
        for x in dir(module)
        if inspect.isclass(getattr(module, x))
        and issubclass(getattr(module, x), tiinfer.Model)
    ]
    if len(module_class)==0:
        raise Exception("not find tiinfer.Model class in model_service")
    return module_class[0](tiinfer.get_ti_model_dir())


class Preprocess(Worker):
    """Sample Preprocess worker"""

    def __init__(self):
        super().__init__()
        self.model_cls = load_model_service()

    def forward(self, request: Union[Dict, List]) -> Union[Dict, List]:
        return self.model_cls.preprocess(request)


class Inference(Worker):
    """Sample Inference worker"""

    def __init__(self):
        super().__init__()
        self.model_cls = load_model_service()
        ok = self.model_cls.load()
        if not ok:
            raise Exception("load model error")
        self.is_multi_framework = tiinfer.Is_Multi_Framework_Type()

    def forward(self, request: Union[Dict, List]) -> Union[Dict, List]:
        if self.is_multi_framework:
            return self.model_cls.predict(request)
        return self.model_cls(request)


class Postprocess(Worker):
    """Sample Postprocess worker"""

    def __init__(self):
        super().__init__()
        self.model_cls = load_model_service()

    def forward(self, request: Union[Dict, List]) -> Union[Dict, List]:
        return self.model_cls.postprocess(request)
