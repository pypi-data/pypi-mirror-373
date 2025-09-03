# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union


class CloudInputError(ValueError):
    """Raised when invalid input is provided."""

    pass


class CloudError(RuntimeError):
    """Raised when case remote execution fails."""

    pass


class Case:
    def __init__(
        self,
        name: str,
        data_path: Optional[Union[str, Path]],
        program: str,
        program_version: Union[str, int],
        execution_type: Union[str, int],
        price_optimized: bool,
        number_of_processes: int,
        memory_per_process_ratio: str,
        **kwargs,
    ) -> None:
        self.name: str = name
        self._validate_type(self.name, str, "Case name must be a string")

        self.data_path: str = str(data_path)
        if data_path and not os.path.isabs(data_path):
            self.data_path = os.path.abspath(data_path)
        if data_path and not Path(data_path).exists():
            raise CloudInputError("Data path does not exist")

        self.program: str = program
        self._validate_type(self.program, str, "Program must be a string")

        self.program_version: Union[str, int] = program_version
        self._validate_type(
            self.program_version,
            (int, str),
            "Program version must be an integer or string (id or name)",
        )

        self.execution_type: Union[str, int] = execution_type
        self._validate_type(
            self.execution_type,
            (int, str),
            "Execution type must be an integer or string (id or name)",
        )

        self.price_optimized: bool = price_optimized
        self._validate_type(
            self.price_optimized, bool, "price_optimized must be a boolean"
        )

        self.number_of_processes: int = number_of_processes
        self._validate_type(
            self.number_of_processes, int, "Number of processes must be an integer"
        )

        self.memory_per_process_ratio: str = memory_per_process_ratio
        self._validate_type(
            self.memory_per_process_ratio,
            str,
            "Memory per process ratio must be a string",
        )

        self.repository_duration: Optional[Union[str, int]] = kwargs.get(
            "repository_duration", 2
        )
        self._validate_type(
            self.repository_duration,
            (int, str),
            "Repository duration must be an integer or string (id or name)",
        )

        self.id: Optional[int] = kwargs.get("id", None)
        self.user: Optional[str] = kwargs.get("user", None)
        self.parent_case_id: Optional[Union[int, list]] = kwargs.get(
            "parent_case_id", None
        )
        self.execution_date: Optional[datetime] = kwargs.get("execution_date", None)
        self.budget: Optional[str] = kwargs.get("budget", None)
        if self.budget is not None:
            self.budget = self.budget.strip()

        # Save In Cloud
        self.upload_only = kwargs.get("upload_only", False)

        # Model Optional Attributes

        # MyModel
        self.mymodel_program_files: Optional[str] = kwargs.get(
            "mymodel_program_files", None
        )
        self.mymodel_output_file: Optional[str] = kwargs.get(
            "mymodel_output_file", None
        )

    @staticmethod
    def _validate_type(
        value, expected_type: Union[List[type], Tuple[type], type], error_message: str
    ):
        if not isinstance(value, expected_type):
            raise CloudInputError(error_message)

    def __str__(self):
        return str(self.__dict__)

    def to_dict(self) -> dict:
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {k: serialize(v) for k, v in self.__dict__.items() if v is not None}
