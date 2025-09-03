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


import torch
from piqa import SSIM

import einops


class SSIMLoss(torch.nn.Module):
    """
    Uses `piqa.SSIM` to create a structural similarity score, then convert to loss

    See [piqa.SSIM][https://piqa.readthedocs.io/en/stable/api/piqa.ssim.html#piqa.ssim.SSIM]

    ```
    ssim = SSIM(output, target)
    loss = 1 - ssim
    return loss
    ```

    !!! Warning
        If used on 4D + batch data, each 3D slice as determined by the second dimension will be calculated
        then averaged.

    """

    def __init__(self, normalise: bool = False, format: str | None = None, **ssim_kwargs: dict) -> None:
        """
        Create SSIM Loss

        Args:
            normalise (bool, optional):
                Whether to force the data to be between 0 and 1. Defaults to False.
            format (str, optional):
                Format of data if not B T C H W. Defaults to None.
            **ssim_kwargs (Any, optional):
                All kwargs passed to [piqa.SSIM][https://piqa.readthedocs.io/en/stable/api/piqa.ssim.html#piqa.ssim.SSIM]

        !!! Tip
            Useful kwargs for piqa.SSIM
            | kwarg | Description |
            | ----- | ----------- |
            | window_size (int) | The size of the window. |
            | sigma (float) | The standard deviation of the window.|
            | n_channels (int) | The number of channels |
            | reduction (str) | Specifies the reduction to apply to the output: 'none', 'mean' or 'sum'.|
        """
        super().__init__()
        self.ssim = SSIM(**ssim_kwargs)
        self.normalise = normalise

        if isinstance(format, str):
            format = format.replace("N ", "")
        self.format = format

    def rearrange(self, output, target):
        if self.format is None:
            return output, target

        if len(output.shape) > 4:
            pattern = f"N {self.format} -> N T C H W"
        else:
            pattern = f"N {self.format} -> N C H W"

        output_rearranged = einops.rearrange(output, pattern)
        target_rearranged = einops.rearrange(target, pattern)

        return (output_rearranged, target_rearranged)

    def forward(self, output: torch.Tensor, target: torch.Tensor):
        if self.normalise:
            min_value = torch.Tensor([0]).to(output)
            max_value = torch.Tensor([1]).to(output)
            output = torch.minimum(torch.maximum(output, min_value), max_value)
            target = torch.minimum(torch.maximum(target, min_value), max_value)

        output, target = self.rearrange(output, target)

        if len(output.shape) > 4:
            loss = torch.stack(
                [self.ssim(output[:, i], target[:, i]) for i in range(output.shape[1])],
                dim=-1,
            )
            loss = loss.mean(dim=-1)
        else:
            loss = self.ssim(output, target)
        return 1 - loss
