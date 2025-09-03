from typing import Dict, Optional, Union, Iterator, List, Any
from datetime import datetime


def format_messages(content):
    messages = []
    messages.append({"role": "user", "content": content})
    return messages


class OpenLLMChat:
    """A chat interface for large language models with eager loading."""

    def __init__(
            self,
            model_name: str,
            device: str = None,
            verbose: bool = False,
            trust_remote_code: bool = False,
            **kwargs
    ):
        """Initialize OpenLLMChat with immediately loaded components"""
        self.verbose = verbose
        self._log("Initializing model: %s", model_name)
        self.start_time = datetime.now()

        # Store initialization parameters
        self.model_name = model_name
        self.trust_remote_code = trust_remote_code
        self.model_config = kwargs.get("model_config", {})
        self.tokenizer_config = kwargs.get("tokenizer_config", {})
        self.generate_config = kwargs.get("generate_config", {})

        # Eager load PyTorch
        try:
            import torch
            self.torch = torch
            self._log("PyTorch loaded successfully")
        except ImportError:
            raise ImportError("PyTorch is required but not installed")

        # Determine device
        self.device = device
        if self.device is None:
            self.device = self._get_default_device()

        # Eager load tokenizer
        try:
            from transformers import AutoTokenizer
            self._log("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=self.trust_remote_code,
                **self.tokenizer_config
            )
            self._log("Tokenizer loaded successfully")
        except ImportError:
            raise ImportError("Transformers library is required")

        # Eager load model
        try:
            from transformers import (
                AutoModelForCausalLM,
                BitsAndBytesConfig,
                GPTQConfig
            )
            # Build kwargs
            model_config = dict(self.model_config)  # Make a copy to avoid modifying the original
            model_config["trust_remote_code"] = self.trust_remote_code
            quantization = model_config.pop("quantization", None)

            self._log("Loading model: device=%s, quantization=%s", self.device, quantization)

            # Apply quantization if specified
            if quantization:
                if quantization == "8bit":
                    model_config["device_map"] = "auto"
                    model_config["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
                    self._log("Using 8-bit quantization")
                elif quantization == "4bit":
                    model_config["device_map"] = "auto"
                    model_config["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=self.torch.float16,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_use_double_quant=True
                    )
                    self._log("Using 4-bit quantization")
                elif quantization == "gptq":
                    model_config["device_map"] = "auto"
                    model_config["quantization_config"] = GPTQConfig(bits=4)
                    self._log("Using GPTQ quantization")

            # Load the model
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_config)
            # Move to device if needed
            # TODO check this
            if model_config.get("device_map", None) != "auto":
                self.model = self.model.to(self.device)
            self.model.eval()
            self._log("Model loaded successfully, took: %.2f seconds",
                      (datetime.now() - self.start_time).total_seconds())

        except ImportError as e:
            raise ImportError(f"Required library not found: {str(e)}")
        except Exception as e:
            self._log("Error loading model: %s", str(e))
            raise

    def _log(self, message: str, *args) -> None:
        """Configurable logging function"""
        if not self.verbose:
            return
        try:
            from ..constants import YELLOW, RESET
            print(f"{YELLOW}[LLM] {message % args}{RESET}")
        except ImportError:
            # Fallback if constants not available
            print(f"[LLM] {message % args}")

    def _get_default_device(self) -> str:
        """Determine the best available device"""
        if self.torch.cuda.is_available():
            return "cuda"
        elif hasattr(self.torch.backends, "mps") and self.torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def chat(
            self,
            prompt: str,
            **kwargs
    ) -> Union[str, Iterator[str]]:
        # Set generation parameters
        generate_config = dict(self.generate_config)  # Make a copy
        generate_config.update({
            "output_attentions": True,
            "output_hidden_states": True,
            "output_scores": True,
            "return_dict_in_generate": False,
        })
        generate_config.update(**kwargs)  # 可以单独在这里改generate_kwargs，但不会影响默认的generate_kwargs

        # Prepare messages
        messages = []
        system_prompt = generate_config.get("system_prompt", None)
        if system_prompt is not None:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({"role": "user", "content": prompt})

        if not self.tokenizer.chat_template:
            self.tokenizer.chat_template = self.tokenizer_config.get("chat_template_if_None", None)

        formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        self._log("Prompt: %s", formatted_prompt)

        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # TODO how attention mask works
        output = self.model.generate(**inputs, **generate_config)

        input_length = inputs["input_ids"].shape[1]
        response_ids = output.sequences[0, input_length:]
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
        self._log("Response: %s", response)

        return response

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "verbose": self.verbose,
            "model_name": self.model_name,
            "device": self.device,
            "trust_remote_code": self.trust_remote_code,
            "model_config": self.model_config,
            "tokenizer_config": self.tokenizer_config,
            "generate_config": self.generate_config,
        }
