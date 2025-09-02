# Dataclass objects to specify parameters for the QEC experiment
# This includes the type of error correction code, distance,
# number of rounds, appropriate decoder to be used, noise model specification as Enums

from enum import Enum
from random import randint
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictBaseModel(BaseModel):
    """
    In pydantic v2, the base model allows extra fields by default.
    This custom base model forbids that
    """

    model_config = ConfigDict(extra="forbid")


class Code(str, Enum):
    """
    Enum representing different quantum error correction codes supported
    """

    ROTATEDSURFACECODE = "rotatedsurfacecode"
    REPETITIONCODE = "repetitioncode"
    STEANECODE = "steanecode"
    SHORCODE = "shorcode"

    @classmethod
    def _missing_(cls, value):
        # Convert the input value to lowercase for case-insensitive matching
        value = str(value).lower()
        for member in cls:
            if member.value.lower() == value:
                return member
        # If no match found, raise a ValueError as default behavior
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class Decoder(str, Enum):
    """
    Enum representing different decoders to be used for QEC experiment.
    """

    PYMATCHING = "pymatching"
    BELIEFPROPAGATION = "beliefpropagation"
    UNIONFIND = "unionfind"
    LUT = "lut"

    @classmethod
    def _missing_(cls, value):
        # Convert the input value to lowercase for case-insensitive matching
        value = str(value).lower()
        for member in cls:
            if member.value.lower() == value:
                return member
        # If no match found, raise a ValueError as default behavior
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class NoiseParameters(StrictBaseModel):
    """
    Enum representing different noise models that can be used in
    quantum error correction experiments.
    """

    depolarizing: float = Field(
        default=0, validate_default=True, description="Depolarizing error rate"
    )
    measurement: float = Field(
        default=0, validate_default=True, description="Measurement error rate"
    )
    reset: float = Field(
        default=0, validate_default=True, description="Reset error rate"
    )


class QECExperiment(StrictBaseModel):
    """
    Parameters for a quantum error correction experiment.
    This includes the code type, distance, number of rounds,
    decoder to be used, and noise model.
    """

    qec_code: Code
    decoder: Decoder
    noise_parameters: NoiseParameters | list[NoiseParameters] = Field(
        default_factory=list,
        description="Parameters for the noise model used in the experiment",
    )
    max_shots: int = Field(
        default=1000000,
        description="Number of shots for the simulation of the quantum error correction experiment",
    )
    max_errors: int = Field(
        default=500,
        description="Maximum number of errors detected before the simulation is stopped",
    )
    gate_durations: dict[str, float] | None = Field(
        default=None,
        description="Duration of quantum gates used in the experiment",
        validate_default=True,
    )
    experiment_type: str = Field(
        description="Type of the experiment, e.g., memory",
    )
    pseudoseed: int = Field(
        default_factory=lambda _: randint(0, 2**32 - 1),
        description="Pseudorandom seed for the experiment. Randomized by default.",
    )

    def model_post_init(self, __context) -> None:
        """
        Post-initialization that recasts noise_parameters to a list if it is a single instance.
        """
        self.noise_parameters = (
            [self.noise_parameters]
            if isinstance(self.noise_parameters, NoiseParameters)
            else self.noise_parameters
        )


class QECExperimentXZ(QECExperiment):
    """
    Parameters for a quantum error correction experiment with both X and Z memory types.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    memory_type: Literal["Z", "X"] = Field(
        description="Type of memory used in the experiment, either 'Z' or 'X'",
    )

    @field_validator("memory_type", mode="before")
    @classmethod
    def validate_memory_type(cls, v: str) -> str:
        """
        Validate the memory_type field to ensure it is either 'Z' or 'X'.
        This is case-insensitive, so both 'Z' and 'z' are valid.
        """
        v = str(v).strip()
        if v.upper() not in {"Z", "X"}:
            raise ValueError("memory_type must be either 'Z' or 'X' (case-insensitive)")
        return v.upper()  # Normalize to uppercase if needed


class QECExperimentIndividual(QECExperimentXZ):
    """
    Parameters for a single instance of the Memory experiment with a single distance,
    number of rounds and a single set of noise parameters.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    """

    distance: int = Field(
        description="The distance of the code all individual experiments will run for",
    )
    num_round: int = Field(
        description="The number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = Field(default="individual", init=False, frozen=True)

    @model_validator(mode="after")
    @classmethod
    def validate_distance_for_steane_code(cls, values):
        """
        Steane Code has a fixed distance, set distance == 0 if using Steane Code.
        """
        if values.qec_code != Code.STEANECODE:
            return values
        if values.distance != 1:
            raise ValueError("Distance must be 1 for Steane code.")
        return values

    @field_validator("noise_parameters", mode="before")
    @classmethod
    def validate_noise_parameters(
        cls, v: NoiseParameters | list[NoiseParameters]
    ) -> NoiseParameters:
        """
        Validate the noise_parameters field to ensure that there is only 1 NoiseParameter.
        """
        if isinstance(v, NoiseParameters):
            return v
        if isinstance(v, list) and len(v) == 1 and isinstance(v[0], NoiseParameters):
            return v[0]
        raise ValueError(
            "noise_parameters must be a single NoiseParameters instance or a list with exactly one NoiseParameters instance"
        )

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]]
        data["num_rounds"] = [data["num_round"]]
        data["metadata"] = None
        data.pop("distance", None)
        data.pop("num_round", None)
        return data


class MemoryExperiment(QECExperimentXZ):
    """
    Parameters for a quantum error correction memory experiment.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    distance: int = Field(
        description="The distance of the code all memory experiments will run for",
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    @model_validator(mode="after")
    @classmethod
    def validate_distance_for_steane_code(cls, values):
        """
        Steane Code has a fixed distance, set distance == 1 if using Steane Code.
        """
        if values.qec_code != Code.STEANECODE:
            return values
        if values.distance != 1:
            raise ValueError("Distance must be 1 for Steane code.")
        return values

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]] * len(data["num_rounds"])
        data["metadata"] = None
        data.pop("distance", None)
        return data
    
class SteaneMemoryExperiment(QECExperimentXZ):
    """
    Parameters for a Steane code memory experiment.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    Specialized models help remove/auto-set certain parameters.
    """
    qec_code: Code = Field(
        default=Code.STEANECODE,
        init=False,
        frozen=True
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = Field(default="memory", init=False, frozen=True)

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [1] * len(data["num_rounds"]) # Distance is ignored if using Steane Code, Code has fixed size.
        data["metadata"] = None
        return data


class ThresholdExperiment(QECExperimentXZ):
    """
    Parameters for a quantum error correction threshold experiment.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    # All pairs of distance_range and num_rounds will be run for each noise rate.
    distance_range: list[int] = Field(
        description="The various distances the threshold experiment will run for",
    )
    num_rounds: list[int] = Field(
        description="The number of syndrome extraction rounds for each distance in distance_range",
    )
    p_values: list[float] = Field(
        description="The various p_values the threshold experiment will use for the threshold computation.",
        default_factory=list,
    )
    # Used only for Threshold.
    weighted: bool = Field(
        description="Boolean setting whether weighted statistics are considered. Defaults to False",
        default=False,
    )
    # Used for Threshold and Pseudo-Threshold.
    interp_method: Literal["linear", "cubic"] = Field(
        description="Method to be used for interpolation between data points. Currently restricted to 'linear' and 'cubic'. Defaults to 'linear'.",
        default="linear",
    )
    # Used for Threshold and Pseudo-Threshold.
    num_subsamples: int | None = Field(
        description="Number of subsamples to consider from the original Logical vs Physical error rate samples. This should be a positive integer smaller or equal to the number of samples. If set to None, no subsamples will be considered. Defaults to None.",
        default=None,
    )
    # Used for Threshold and Pseudo-Threshold.
    forward_scan: float = Field(
        description="The percentage, given as a float between 0 and 1, of data to be discarded when starting the search for a crossing. The discarded data will correspond to lower values of `p`. For example, if set to 0.25, the first 25% (smaller) values of `p` will not be considered when searching for a crossing point. Defaults to 0.",
        default=0.0,
    )
    pseudo_threshold: bool = Field(
        description="Boolean setting whether to compute the pseudo-threshold. Defaults to False.",
        default=False,
    )
    # Required Parameters if bootstrapping threshold computations.
    bootstrap: bool = Field(
        description="Boolean setting whether to use bootstrap sampling. Defaults to False.",
        default=False,
    )
    n_bootstrap_samples: int = Field(
        description="Number of bootstrap samples to use if bootstrap is True. Defaults to 1000.",
        default=1000,
    )
    experiment_type: str = Field(default="threshold", init=False, frozen=True)

    @model_validator(mode="after")
    @classmethod
    def validate_distance_for_steane_code(cls, values):
        """
        Steane Code has a fixed distance, set distance_range == [1, ..., 1] if using Steane Code.
        The length of distance_range is equal to num_rounds.
        """
        if values.qec_code != Code.STEANECODE:
            return values
        correct_distance_range_input = [1] * len(values.num_rounds)
        if values.distance_range != correct_distance_range_input:
            raise ValueError("Distance must be 1 for Steane code. The appropriate input for distance_range is {}.".format(correct_distance_range_input))
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_distance_num_rounds_for_rsc_code(cls, values):
        """
        If qec_code is rotated surface code, distance and num_rounds must be equal.
        """
        if values.qec_code == Code.ROTATEDSURFACECODE and values.distance_range != values.num_rounds:
            raise ValueError("For rotated surface code, distance and num_rounds must be equal.")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_num_rounds_distance_range_length(cls, values):
        """
        Validate the num_rounds and distance_range fields to ensure they have the same length.
        """
        if len(values.num_rounds) != len(values.distance_range):
            raise ValueError("num_rounds must have the same length as distance_range")
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_pseudo_threshold_if_only_one_distance_provided(cls, values):
        """
        Validate that pseudo_threshold is True, if only 1 distance is provided in distance_range.
        """
        if len(values.distance_range) == 1 and not values.pseudo_threshold:
            raise ValueError(
                "pseudo_threshold must be True if only 1 distance is provided"
            )
        return values

    @model_validator(mode="after")
    @classmethod
    def validate_noise_parameters_length(cls, values):
        """
        Validate the number of noise_parameters is equal to the number of p_values.
        """
        if len(values.noise_parameters) != len(values.p_values):
            raise ValueError(
                "The number of noise_parameters must be equal to the number of p_values."
            )
        return values

    @field_validator("p_values", mode="before")
    @classmethod
    def validate_p_values(cls, p_values):
        """
        Validate that there are at least 2 p_values.
        """
        if len(p_values) < 2:
            raise ValueError("There must be at least 2 p_values.")
        return p_values

    @staticmethod
    def __create_noise_parameters_from_alphas(
        alphas: list[int], relative_to_p: list[bool], p_values: list[float]
    ) -> list[NoiseParameters]:
        """
        Create noise parameters from the provided alpha values, their relation to p, and the p-values.
        """
        noise_parameters = [
            NoiseParameters(
                depolarizing=alphas[0] * (p_value ** relative_to_p[0]),
                measurement=alphas[1] * (p_value ** relative_to_p[1]),
                reset=alphas[2] * (p_value ** relative_to_p[2]),
            )
            for p_value in p_values
        ]

        return noise_parameters

    @classmethod
    def initialize_w_alphas(
        cls,
        qec_code: Code,
        decoder: Decoder,
        memory_type: Literal["Z", "X"],
        distance_range: list[int],
        num_rounds: list[int],
        alphas: list[int],
        relative_to_p: list[bool],
        p_values: list[float],
        max_shots: int = 1000000,
        max_errors: int = 500,
        gate_durations: dict[str, float] | None = None,
        pseudoseed: int = randint(0, 2**32 - 1),
        weighted: bool = False,
        interp_method: Literal["linear", "cubic"] = "linear",
        num_subsamples: int | None = None,
        forward_scan: float = 0.0,
        pseudo_threshold: bool = False,
        bootstrap: bool = False,
        n_bootstrap_samples: int = 1000,
    ) -> "ThresholdExperiment":
        """
        Initialize the `ThresholdExperiment` with alphas and p_values.
        This method creates a set of `NoiseParameters` based on the following relationship:
        For each p_value of p_values,
        p_depolarizing = alphas_{depolarising} * (p_value ** relative_to_p_{depolarising})
        p_measurement = alphas_{measurement} * (p_value ** relative_to_p_{measurement})
        p_reset = alphas_{reset} * (p_value ** relative_to_p_{reset})

        For generation of NoiseParameters.
        Threshold computations require specific patterns in the noise model, thus, we
        represent them using alphas and their relation to the p-value.

        The threshold can then be determined using a plot of the logical error rates
        against the p-value.

        Parameters
        ----------
        alphas: list[int]
            Alpha is defined as the ratio of the noise parameter to the p-value.
            In the order of [alpha_{depolarising}, alpha_{measurement}, alpha_{reset}].
            The list should contain at least 3 values (i.e., 1 alpha for each noise parameter).

        relative_to_p: list[bool]
            List of boolean values indicating whether each alpha value is relative to
            the p-value.
            In the order of [relative_to_p_{depolarising}, relative_to_p_{measurement}, relative_to_p_{reset}].
            The list should contain at least 3 values (i.e., 1 alpha for each noise parameter).

        p_values: list[float]
            List of p-values to be iterated over for the threshold experiments. The
            threshold is expected to be found within the p-values provided. There
            should be at least 2 values.

        Return
        ------
        ThresholdExperiment
            An instance of the ThresholdExperiment class initialized with specialized
            NoiseParameters.
        """

        assert len(alphas) == 3, "alphas must have a length of 3"
        assert len(relative_to_p) == 3, "relative_to_p must have a length of 3"
        assert any(relative_to_p), "at least one value in relative_to_p must be True"
        assert len(p_values) >= 2, "p_values must have at least 2 values"

        return cls(
            qec_code=qec_code,
            decoder=decoder,
            memory_type=memory_type,
            distance_range=distance_range,
            num_rounds=num_rounds,
            noise_parameters=cls.__create_noise_parameters_from_alphas(
                alphas, relative_to_p, p_values
            ),
            max_shots=max_shots,
            max_errors=max_errors,
            gate_durations=gate_durations,
            pseudoseed=pseudoseed,
            p_values=p_values,
            weighted=weighted,
            interp_method=interp_method,
            num_subsamples=num_subsamples,
            forward_scan=forward_scan,
            pseudo_threshold=pseudo_threshold,
            bootstrap=bootstrap,
            n_bootstrap_samples=n_bootstrap_samples,
        )

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to repackage inputs that are threshold specific to metadata.
        """
        data = super().model_dump(*args, **kwargs)
        metadata = {
            "metadata": {
                "p_values": data["p_values"],
                "weighted": data["weighted"],
                "interp_method": data["interp_method"],
                "num_subsamples": data["num_subsamples"],
                "forward_scan": data["forward_scan"],
                "pseudo_threshold": data["pseudo_threshold"],
                "bootstrap": data["bootstrap"],
                "n_bootstrap_samples": data["n_bootstrap_samples"],
            }
        }
        data.update(metadata)
        # Remove original fields
        data.pop("p_values", None)
        data.pop("weighted", None)
        data.pop("interp_method", None)
        data.pop("num_subsamples", None)
        data.pop("forward_scan", None)
        data.pop("pseudo_threshold", None)
        data.pop("bootstrap", None)
        data.pop("n_bootstrap_samples", None)
        return data
    

class SteaneThresholdExperiment(ThresholdExperiment):
    """
    Threshold experiment for the Steane code.
    Specialized models help remove/auto-set certain parameters.
    """
    qec_code: Code = Field(
        default=Code.STEANECODE,
        init=False,
        frozen=True
    )
    distance_range: list[int] = Field(default=None, init=False) # Remove from initialization

    def model_post_init(self, __context) -> None:
        """
        Assign distance_range automatically here.
        """
        super().model_post_init(__context)
        self.distance_range = [1] * len(self.num_rounds) # Distance is ignored if using Steane Code, Code has fixed size.


class QECResult(StrictBaseModel):
    """
    Result of a quantum error correction experiment.
    """

    timestamp: str = Field(
        description="Timestamp when the experiment was executed",
    )
    noise_parameters: NoiseParameters | list[NoiseParameters] = Field(
        description="Parameters for the noise model used in the experiment",
    )
    logical_error_rate: list[list[float]] = Field(
        description="Logical error rate of the quantum error correction experiment",
    )
    raw_results: dict = Field(
        description="Raw results of the quantum error correction experiment",
    )
    code_threshold: dict[str, float | list] | None = Field(
        default=None,
        description="Computed threshold for the quantum error correction code used in the experiment",
    )
    code_pseudothreshold: dict[str, float | dict] | None = Field(
        default=None,
        description="Computed pseudothreshold for the quantum error correction code used in the experiment. The key is the code distance and the values is the pseudo-threshold (or information about the pseudo-threshold if bootstrapped is True.)",
    )

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create an instance of QECResult from a dictionary.
        This is useful for deserializing results from JSON or other formats.
        """
        # Select result
        data = data["result"]
        # Format the noise_parameters field based on its length
        if len(data["noise_parameters"]) > 1:
            output_noise_parameters = [
                NoiseParameters(**np) for np in data["noise_parameters"]
            ]
        else:
            output_noise_parameters = NoiseParameters(**data["noise_parameters"][0])

        return cls(
            timestamp=data["timestamp"],
            noise_parameters=output_noise_parameters,
            logical_error_rate=data["logical_error_rate"],
            code_threshold=data["threshold"],
            code_pseudothreshold=data.get("pseudo_threshold", None),
            raw_results=data,
        )

    @property
    def results_overview(self) -> dict:
        """
        Returns a summary of the results sorted by noise parameters:
        - Each noise parameter will have a list of dictionaries for the various
          combinations of distance, num_rounds runs and their respective
          logical_error_rate.
        - This is useful for quickly accessing the results of the experiment.

        Example output:
        {
            "timestamp": "2023-10-01T12:00:00Z",
            "results": [
                {
                    "noise_parameters": NoiseParameters(depolarizing=0.01, measurement=0.01, reset=0.01),
                    "runs": [
                        {
                            "distance": 3,
                            "num_rounds": 5,
                            "logical_error_rate": 0.001
                        },
                        {
                            "distance": 5,
                            "num_rounds": 10,
                            "logical_error_rate": 0.002
                        }
                    ]
                },
                ...
            ],
            "code_threshold": 0.1
        }
        """
        temp_noise_parameters = (
            [self.noise_parameters]
            if isinstance(self.noise_parameters, NoiseParameters)
            else self.noise_parameters
        )
        formatted_results = []

        for i, noise_parameters in enumerate(temp_noise_parameters):
            formatted_results.append({"noise_parameters": noise_parameters, "runs": []})
            for j, (distance, num_rounds) in enumerate(
                zip(self.raw_results["distance_range"], self.raw_results["num_rounds"])
            ):
                formatted_results[i]["runs"].append(
                    {
                        "distance": distance,
                        "num_rounds": num_rounds,
                        "logical_error_rate": self.logical_error_rate[i][j],
                    }
                )

        return {
            "timestamp": self.timestamp,
            "experiment_type": self.raw_results["experiment_type"],
            "results": formatted_results,
            "code_threshold": self.code_threshold,
            "code_pseudothreshold": self.code_pseudothreshold,
        }
