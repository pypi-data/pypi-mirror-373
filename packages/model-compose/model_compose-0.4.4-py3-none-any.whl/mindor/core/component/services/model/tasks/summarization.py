from __future__ import annotations
from typing import TYPE_CHECKING

from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from mindor.dsl.schema.component import ModelComponentConfig
from mindor.dsl.schema.action import ModelActionConfig, SummarizationModelActionConfig
from mindor.core.utils.streamer import AsyncStreamer
from mindor.core.logger import logging
from ..base import ModelTaskService, ModelTaskType, register_model_task_service
from ..base import ComponentActionContext
from threading import Thread
import asyncio

if TYPE_CHECKING:
    from transformers import PreTrainedModel, PreTrainedTokenizer, GenerationMixin
    from torch import Tensor
    import torch

class SummarizationTaskAction:
    def __init__(self, config: SummarizationModelActionConfig, model: PreTrainedModel, tokenizer: PreTrainedTokenizer, device: torch.device):
        self.config: SummarizationModelActionConfig = config
        self.model: Union[PreTrainedModel, GenerationMixin] = model
        self.tokenizer: PreTrainedTokenizer = tokenizer
        self.device: torch.device = device

    async def run(self, context: ComponentActionContext, loop: asyncio.AbstractEventLoop) -> Any:
        from transformers import TextIteratorStreamer, StopStringCriteria
        import torch

        text: Union[str, List[str]] = await context.render_variable(self.config.text)

        max_input_length  = await context.render_variable(self.config.params.max_input_length)
        max_output_length = await context.render_variable(self.config.params.max_output_length)
        min_output_length = await context.render_variable(self.config.params.min_output_length)
        do_sample         = await context.render_variable(self.config.params.do_sample)
        temperature       = await context.render_variable(self.config.params.temperature) if do_sample else None
        top_k             = await context.render_variable(self.config.params.top_k) if do_sample else None
        top_p             = await context.render_variable(self.config.params.top_p) if do_sample else None
        num_beams         = await context.render_variable(self.config.params.num_beams)
        length_penalty    = await context.render_variable(self.config.params.length_penalty) if num_beams > 1 else None
        early_stopping    = await context.render_variable(self.config.params.early_stopping) if num_beams > 1 else False
        stop_sequences    = await context.render_variable(self.config.params.stop_sequences)
        batch_size        = await context.render_variable(self.config.params.batch_size)
        stream            = await context.render_variable(self.config.stream)

        is_single_input: bool = bool(not isinstance(text, list))
        texts: List[str] = [ text ] if is_single_input else text
        results = []

        if stream and (batch_size != 1 or len(texts) != 1):
            raise ValueError("Streaming mode only supports a single input text with batch size of 1.")

        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True) if stream else None
        stopping_criteria = [ StopStringCriteria(self.tokenizer, stop_sequences) ] if stop_sequences else None
        for index in range(0, len(texts), batch_size):
            batch_texts = texts[index:index + batch_size]
            inputs: Dict[str, Tensor] = self.tokenizer(batch_texts, return_tensors="pt", max_length=max_input_length, padding=True, truncation=True)
            inputs = { k: v.to(self.device) for k, v in inputs.items() }

            def _generate():
                with torch.inference_mode():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_output_length,
                        min_length=min_output_length,
                        do_sample=do_sample,
                        temperature=temperature,
                        top_k=top_k,
                        top_p=top_p,
                        num_beams=num_beams,
                        length_penalty=length_penalty,
                        early_stopping=early_stopping,
                        pad_token_id=getattr(self.tokenizer, "pad_token_id", None),
                        eos_token_id=getattr(self.tokenizer, "eos_token_id", None),
                        stopping_criteria=stopping_criteria,
                        streamer=streamer
                    )

                if not stream:
                    outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                    results.extend(outputs)

            if stream:
                thread = Thread(target=_generate)
                thread.start()
            else:
                _generate()

        if stream:
            async def _stream_output_generator():
                async for chunk in AsyncStreamer(streamer, loop):
                    if chunk:
                        context.register_source("result[]", chunk)
                        yield (await context.render_variable(self.config.output, ignore_files=True)) if self.config.output else chunk

            return _stream_output_generator()
        else:
            result = results[0] if is_single_input else results
            context.register_source("result", result)

            return (await context.render_variable(self.config.output, ignore_files=True)) if self.config.output else result

@register_model_task_service(ModelTaskType.SUMMARIZATION)
class SummarizationTaskService(ModelTaskService):
    def __init__(self, id: str, config: ModelComponentConfig, daemon: bool):
        super().__init__(id, config, daemon)

        self.model: Optional[Union[PreTrainedModel, GenerationMixin]] = None
        self.tokenizer: Optional[PreTrainedTokenizer] = None
        self.device: Optional[torch.device] = None

    async def _serve(self) -> None:
        try:
            self.model = self._load_pretrained_model()
            self.tokenizer = self._load_pretrained_tokenizer()
            self.device = self._get_model_device(self.model)
            logging.info(f"Model and tokenizer loaded successfully on device '{self.device}': {self.config.model}")
        except Exception as e:
            logging.error(f"Failed to load model '{self.config.model}': {e}")
            raise

    async def _shutdown(self) -> None:
        self.model = None
        self.tokenizer = None
        self.device = None

    async def _run(self, action: ModelActionConfig, context: ComponentActionContext, loop: asyncio.AbstractEventLoop) -> Any:
        return await SummarizationTaskAction(action, self.model, self.tokenizer, self.device).run(context, loop)

    def _get_model_class(self) -> Type[PreTrainedModel]:
        from transformers import AutoModelForSeq2SeqLM
        return AutoModelForSeq2SeqLM

    def _get_tokenizer_class(self) -> Type[PreTrainedTokenizer]:
        from transformers import AutoTokenizer
        return AutoTokenizer
