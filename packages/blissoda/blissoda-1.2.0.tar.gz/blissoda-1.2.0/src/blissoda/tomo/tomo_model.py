from __future__ import annotations

from pathlib import Path
from typing import Literal
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from ..resources import resource_filename


class TomoProcessorModel(BaseModel, validate_assignment=True):
    workflow: str = Field(
        default="tomo_processor.json",
        description="Blissoda resources workflow file",
        examples=["tomo_processor.json"],
    )
    queue: Optional[str] = Field(
        default=None,
        description="Ewoks queue to submit the workflow to",
        examples=["tomo_queue"],
    )
    nabu_config_file: Optional[str] = None
    slice_index: Union[Literal["first", "middle", "last"], int] = "middle"
    rotation_axis_position: Union[
        int,
        float,
        Literal[
            "centered",
            "sliding-window",
            "global",
            "growing-window",
            "sino-coarse-to-fine",
            "composite-coarse-to-fine",
            "octave-accurate",
        ],
    ] = "sliding-window"
    phase_retrieval_method: Union[Literal["CTF", "Paganin", "None"], None] = "None"
    delta_beta: Union[str, float, int] = "100"
    show_last_slice: bool = Field(
        default=False,
        description="Display last reconstructed slice in Flint",
    )

    @field_validator("workflow")
    def check_workflow(cls, v):
        if not isinstance(v, str):
            raise ValueError("workflow must be a string")
        if not v.endswith(".json"):
            raise ValueError("workflow must be a JSON file")
        if not Path(resource_filename("tomo", v)).exists():
            raise FileNotFoundError(f"Workflow file {v} does not exist")
        return v

    @field_validator("queue")
    def check_queue(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("queue must be a string or None")
        return v

    @field_validator("nabu_config_file")
    def check_nabu_config_file(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("nabu_config_file must be a string or None")
        if v and not Path(v).exists():
            raise FileNotFoundError(f"Nabu config file {v} does not exist")
        return v

    @field_validator("slice_index")
    def check_slice_index(cls, v):
        if isinstance(v, str):
            if v not in ["first", "last", "middle"]:
                raise ValueError(
                    "slice_index must be 'first', 'last', 'middle' or an integer"
                )
        elif not isinstance(v, int):
            raise ValueError(
                "slice_index must be an integer or one of 'first', 'last', 'middle'"
            )
        return str(v)

    @field_validator("rotation_axis_position")
    def check_rotation_axis_position(cls, v):
        valid_positions = [
            "centered",
            "sliding-window",
            "global",
            "growing-window",
            "sino-coarse-to-fine",
            "composite-coarse-to-fine",
            "octave-accurate",
        ]
        if isinstance(v, str):
            if v not in valid_positions:
                raise ValueError(
                    f"rotation_axis_position must be one of {valid_positions}"
                )
        elif not isinstance(v, (int, float)):
            raise ValueError(
                f"rotation_axis_position must be a float, int, or one of {valid_positions}"
            )
        return v

    @field_validator("phase_retrieval_method")
    def check_phase_method(cls, v):
        if v is None:
            return "None"
        elif v not in ["CTF", "Paganin", "None"]:
            raise ValueError("phase_retrieval_method must be 'CTF', 'Paganin' or None")
        return v

    @field_validator("delta_beta")
    def check_positive_delta_beta(cls, v):
        if float(v) <= 0:
            raise ValueError("delta_beta must be positive")
        return str(v)
