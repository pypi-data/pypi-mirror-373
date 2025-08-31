"""Utils for testing."""

from typing import Optional

import torch

from nucleobench.common import string_utils
from nucleobench.optimizations import model_class as mc


class CountLetterModel(torch.nn.Module, mc.TISMModelClass):
    """Count number of occurrences of first vocab letter."""

    def __init__(self, 
                 vocab_i: int = 1, 
                 flip_sign: bool = False, 
                 extra_channels: int = 0,
                 call_is_on_strings: bool = True,
                 add_unsqueeze_to_output: bool = False,
                 train_seq_len: int = 200,
                 ):
        super().__init__()
        self.vocab_i = vocab_i
        self.flip_sign = flip_sign
        self.extra_channels = extra_channels
        self.call_is_on_strings = call_is_on_strings
        self.add_unsqueeze_to_output = add_unsqueeze_to_output
        self.train_seq_len = train_seq_len

    def forward(self, x):
        assert x.ndim == 3
        assert x.shape[1] == 4, x.shape
        out_tensor = torch.sum(x[:, self.vocab_i, :], dim=[1])
        if self.flip_sign:
            out_tensor *= -1
        if self.extra_channels:
            out_tensor = torch.stack([out_tensor] + [torch.zeros_like(out_tensor)] * self.extra_channels).T
        if self.add_unsqueeze_to_output:
            out_tensor = torch.unsqueeze(out_tensor, dim=-1)
        return out_tensor

    def inference_on_tensor(self, x: torch.Tensor) -> torch.Tensor:
        return self.forward(x)
    
    def inference_on_strings(self, seqs: list[str]) -> list[float]:
        torch_seq = string_utils.dna2tensor_batch(seqs)
        result = self.inference_on_tensor(torch_seq)
        return [float(x) for x in result]

    def __call__(self, x):
        if self.call_is_on_strings:
            return self.inference_on_strings(x)
        else:
            return self.inference_on_tensor(x)
    
    # Attributes needed for gRelu.
    @property
    def data_params(self):
        return {
            'tasks': {'name':[f'task{i}' for i in range(3)] + ['Neuron']},
            'train': {'seq_len': self.train_seq_len},
        }
    
    # Method needed for gRelu.
    def get_task_idxs(self, *args, **kwargs):
        return [0, 1, 2]


def assert_proposal_respects_positions_to_mutate(
    start_sequence: str,
    proposal_sequence: str,
    positions_to_mutate: Optional[list[int]] = None,
    ):
    if positions_to_mutate is None:
        return
    
    incorrect_differences = []
    for i in range(len(start_sequence)):
        if i in positions_to_mutate:
            continue
        else:
            if start_sequence[i] != proposal_sequence[i]:
                incorrect_differences.append(i)
    assert len(incorrect_differences) == 0, incorrect_differences