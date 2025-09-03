from typing import override
from rsb.adapters.adapter import Adapter

from agentle.generations.models.generation.generation_config import GenerationConfig
from agentle.generations.providers.amazon.models.inference_config import (
    InferenceConfig,
)


class GenerationConfigToInferenceConfigAdapter(
    Adapter[GenerationConfig, InferenceConfig]
):
    @override
    def adapt(self, _f: GenerationConfig) -> InferenceConfig:
        return InferenceConfig(
            maxTokens=_f.max_output_tokens or 512,
            temperature=_f.temperature or 0.6,
            topP=_f.top_p or 0.9,
        )
