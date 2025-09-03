# Copyright Commonwealth of Australia, Bureau of Meteorology 2024.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import annotations

from typing import Any

from abc import ABCMeta


from pyearthtools.utils.initialisation import InitialisationRecordingMixin

from pyearthtools.pipeline.controller import Pipeline
from pyearthtools.training.wrapper.wrapper import ModelWrapper


class Predictor(InitialisationRecordingMixin, metaclass=ABCMeta):
    """
    Wrapper to enable prediction

    Hooks:
        `after_predict` (prediction) -> prediction:
        Function executed after data has been reversed from prediction.

    Usage:
        >>> model = ModelWrapper(MODEL_GOES_HERE, DATA_PIPELINE)
        >>> predictor = Predictor(model)
        >>> predictor.predict('2000-01-01T00')
    """

    def __init__(self, model: ModelWrapper, reverse_pipeline: Pipeline | int | str | None):
        """
        Use a `model` to run a prediction.

        Retrieves initial conditions for `model.get_sample`, so set it's `Pipeline` accordingly.

        Args:
            model (ModelWrapper):
                Model and Data source to use.
            reverse_pipeline (Pipeline | int | str | None):
                If not given, will default to using `model.pipelines`.
                Override for `Pipeline` to use on the undo operation.
                If `str` or `int` use value to index into `model.pipelines`. Useful if `model.pipelines`
                is a dictionary or tuple.
                Or can be `Pipeline` it self to use. If `reverse_pipeline.has_source()` is True, run `reverse_pipeline.undo`. otherwise
                apply pipeline with `reverse_pipeline.apply`
        """
        super().__init__()
        self.record_initialisation()
        self.model = model
        self._reverse_pipeline = reverse_pipeline

    def _predict(self, data, *args, **kwargs) -> Any:
        """
        Run prediction with `model` on given `data`, calling `self.model.predict`.

        """
        return self.model.predict(data, *args, **kwargs)

    def get_sample(self, idx, *, fake_batch_dim: bool = False):
        return self.model.get_sample(idx, fake_batch_dim=fake_batch_dim)

    @property
    def pipelines(self):
        return self.model.pipelines

    @property
    def datamodule(self):
        return self.model.datamodule

    @property
    def reverse_pipeline(self) -> Pipeline:
        if self._reverse_pipeline is None:
            if not isinstance(self.pipelines, Pipeline):
                raise TypeError(
                    "`reverse_pipeline` was not given but `datamodule` is not a simple `Pipeline`. Either set `reverse_pipeline` to an index, or a `Pipeline`."
                )
            return self.pipelines
        elif isinstance(self._reverse_pipeline, Pipeline):
            return self._reverse_pipeline
        elif isinstance(self._reverse_pipeline, (str, int)):
            if not isinstance(self.pipelines, (tuple, dict, list)):
                raise TypeError(
                    f"Cannot index into underlying `Pipelines` with {self._reverse_pipeline!r} as they are not indexable."
                )
            try:
                return self.pipelines[self._reverse_pipeline]  # type: ignore
            except IndexError as e:
                raise IndexError(
                    f"Indexing into the pipelines of type {type(self.pipelines)} with index {self._reverse_pipeline!r} failed"
                ) from e
        raise TypeError(f"Cannot parse `reverse_pipeline` of {type(self._reverse_pipeline)}.")

    def reverse(self, data):
        """
        Run `reverse_pipeline` on `data`.
        """
        reverse_pipeline = self.reverse_pipeline

        if reverse_pipeline.has_source():
            return reverse_pipeline.undo(data)
        return reverse_pipeline.apply(data)

    def predict(self, idx: Any, fake_batch_dim: bool = False, **kwargs) -> Any:
        """
        Run prediction with `model` with data from `idx`

        Args:
            idx (Any):
                Index to get initial conditions from
            fake_batch_dim (bool, optional):
                Whether to fake the batch dim. Defaults to True.

        Returns:
            (Any):
                Prediction data after being run through `reverse` and `after_predict`.
        """
        predicted_data = self._predict(self.get_sample(idx, fake_batch_dim=fake_batch_dim), **kwargs)
        if fake_batch_dim:
            predicted_data = predicted_data[0]
        return self.after_predict(self.reverse(predicted_data))

    def after_predict(self, prediction):
        """Hook to modify prediction, post `predict`."""
        return prediction
