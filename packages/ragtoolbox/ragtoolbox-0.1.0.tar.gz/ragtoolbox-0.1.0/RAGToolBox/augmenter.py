"""
RAGToolBox augmenter module.

Provides utilities to format prompts and generate answers using either a local
Transformers model or the Hugging Face Inference API. Supports "rolling chat"
by threading prior turns as read-only disambiguation context.

Environment:
    HUGGINGFACE_API_KEY: Token used when calling the Hugging Face Inference API

See Also:
    - :py:class:`RAGToolBox.retriever.Retriever`
    - :py:class:`RAGToolBox.embeddings.Embeddings`
"""

import argparse
import logging
import os
import sys
from importlib.resources import files
from typing import Deque, Tuple, Optional, Sequence
from dataclasses import dataclass
from collections import deque
from pathlib import Path
import yaml
from RAGToolBox.types import RetrievedChunk
from RAGToolBox.retriever import Retriever, RetrievalConfig

__all__ = ["Augmenter", "GenerationConfig", "ChatConfig", "initiate_chat"]
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class GenerationConfig:
    """
    Configuration for text generation.

    Attributes:
        temperature: Controls randomness in generation
            (0.0 = deterministic, 1.0 = very random). Default: 0.25.
        max_new_tokens: Maximum number of new tokens to generate. Default: 200.

    Examples:
        >>> GenerationConfig()  # defaults
        GenerationConfig(temperature=0.25, max_new_tokens=200)
        >>> GenerationConfig(temperature=0.1, max_new_tokens=128)
        GenerationConfig(temperature=0.1, max_new_tokens=128)
    """
    temperature: float = 0.25
    max_new_tokens: int = 200

@dataclass(frozen=True)
class ChatConfig:
    """
    Configuration for interactive chat turns.

    Attributes:
        ret_config: :py:class:`RAGToolBox.retriever.RetrievalConfig` for retrieval.
        gen_config: :py:class:`GenerationConfig` for generation.
        history: Rolling deque of prior (user, assistant) turns.
        include_sources: If True, return KB sources alongside the answer.
        history_turns: How many most-recent turns to expose for disambiguation.

    Notes:
        Chat history is treated as *reference only* for resolving pronouns or
        vague language in the current query. It is not treated as ground-truth
        evidence.

    Examples:
        >>> from collections import deque
        >>> ChatConfig(history=deque(maxlen=50), include_sources=True, history_turns=3)
        ChatConfig(...)
    """
    ret_config: Optional[RetrievalConfig] = None
    gen_config: Optional[GenerationConfig] = None
    history: Deque[Tuple[str, str]] | None = None
    include_sources: bool = False
    history_turns: int = 5

def _init_chat_config(
    history: deque[tuple[str, str]], command_args: argparse.Namespace
    ) -> ChatConfig:
    """Helper function for constructing a ChatConfig"""
    ret_config = RetrievalConfig(
        top_k=command_args.top_k,
        max_retries=command_args.max_retries
        )
    gen_config = GenerationConfig(
        temperature=command_args.temperature,
        max_new_tokens=command_args.max_tokens
        )
    chat_config = ChatConfig(
        ret_config = ret_config,
        gen_config = gen_config,
        history = history,
        include_sources=command_args.sources,
        history_turns=command_args.history_turns
        )
    return chat_config

class Augmenter:
    """
    Generate answers from retrieved KB chunks and an LLM.

    The augmenter formats a prompt from the user's query, retrieved KB chunks
    (treated as ground-truth evidence), and optional chat history
    (disambiguation only). It then calls either a local Transformers model
    or the Hugging Face Inference API.

    Attributes:
        model_name: Identifier of the LLM to use
        api_key: HF token used with the Inference API (if applicable)
        use_local: If True, use a local Transformers model; otherwise use HF API
        prompt_type: Name of the selected template in ``config/prompts.yaml``

    Raises:
        ValueError: If ``prompt_type`` is not a key in ``config/prompts.yaml``
        ImportError: If required packages are missing for the chosen backend
        RuntimeError: If client/model initialization fails
    """

    def __init__(
        self, model_name: str = "google/gemma-2-2b-it", api_key: Optional[str] = None,
        use_local: bool = False, prompt_type: str = 'default'
        ):
        """
        Initialize an :py:class:`Augmenter`.

        Args:
            model_name: LLM identifier (e.g., "google/gemma-2-2b-it")
            api_key: Optional HF token. Defaults to env var ``HUGGINGFACE_API_KEY``
            use_local: If True, use a local Transformers model; otherwise use HF API
            prompt_type: Name of the prompt template from ``config/prompts.yaml``

        Raises:
            ValueError: If ``prompt_type`` is not defined in the prompts file
            ImportError: If the selected backend requires a missing package
            RuntimeError: If the backend client/model fails to initialize

        Examples:
            >>> aug = Augmenter()  # uses HF API with default template, token from env
            >>> aug = Augmenter(use_local=True)  # local route that requires transformers
            >>> aug = Augmenter(model_name="custom/model", prompt_type="verbose")
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.use_local = use_local
        with open(files('RAGToolBox').joinpath('config/prompts.yaml'), 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
            if prompt_type not in prompts:
                choices = ", ".join(prompts.keys())
                err = f"Invalid prompt_type '{prompt_type}'. Choose from: {choices}"
                logger.error(err)
                raise ValueError(err)
            self.prompt_type = prompts[prompt_type]

        # Initialize model based on preference
        if use_local:
            self._initialize_local_model()
        else:
            if not self.api_key:
                logger.warning(
                    "Warning: No API key provided. "
                    "Some models may not work without authentication."
                    )
            self._initialize_api_client()

    def _initialize_api_client(self):
        """
        Initialize the Hugging Face inference client.

        Raises:
            ImportError: If `huggingface_hub` is not installed.
            RuntimeError: If the client fails to initialize.
        """
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=self.api_key)
            logger.debug("Hugging Face InferenceClient initialized successfully")
        except ImportError as e:
            err = (
                "huggingface_hub package is required. "
                "Install with: pip install huggingface_hub"
                )
            logger.error(err, exc_info=True)
            raise ImportError(err) from e
        except Exception as e:
            err = "Error initializing Hugging Face client"
            logger.error(err, exc_info=True)
            raise RuntimeError(err) from e

    def _initialize_local_model(self):
        """Initialize the local model using transformers library."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM

            logger.info("Loading model: %s", self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            logger.debug("Model loaded successfully!")

        except ImportError as e:
            err = (
                "Transformers package is required. "
                "Install with: pip install transformers torch"
                )
            logger.error(err, exc_info=True)
            raise ImportError(err ) from e
        except Exception as e:
            err = f"Error loading model: {self.model_name}"
            logger.error(err, exc_info=True)
            raise RuntimeError(err) from e

    def _format_prompt(
        self, query: str, retrieved_chunks: Sequence[RetrievedChunk],
        chat_history: Optional[str] = None
        ) -> str:
        """
        Format the query and retrieved chunks into a prompt for the LLM.

        Args:
            query: The user's original query
            retrieved_chunks: Sequence of retrieved text chunks
            chat_history: An optional string containing chat history for when using `--chat`

        Returns:
            Formatted prompt string
        """
        if chat_history is None:
            chat_history = ''
        contx = "\n\n".join(
            f"Context {i+1}: {chunk['data']}" for i, chunk in enumerate(retrieved_chunks)
            )
        prompt = self.prompt_type.format(
            context = contx,
            chat_history = chat_history,
            query = query
            )
        return prompt

    def _call_llm(self, prompt: str, temperature: float = 0.25, max_new_tokens: int = 200) -> str:
        """
        Call the language model with the formatted prompt.

        Args:
            prompt: The formatted prompt to send to the LLM
            temperature: Controls randomness in generation (0.0 = deterministic, 1.0 = very random)
            max_new_tokens: Maximum number of tokens to generate

        Returns:
            A string:
                The generated response from the LLM
        """
        if self.use_local:
            return self._call_local_model(prompt, temperature, max_new_tokens)
        return self._call_huggingface_api(prompt, temperature, max_new_tokens)

    def _call_local_model(
        self, prompt: str, temperature: float = 0.7, max_new_tokens: int = 200
        ) -> str:
        """
        Call the local model using transformers.

        Args:
            prompt: The formatted prompt to send to the LLM
            temperature: Controls randomness in generation (0.0 = deterministic, 1.0 = very random)
            max_new_tokens: Maximum number of tokens to generate

        Returns:
            A string:
                The generated response from local LLM

        Raises:
            ImportError: If `pytorch` is not installed
            RuntimeError: If a response is not returned from the LLM
        """
        try:
            import torch

            # Tokenize the prompt
            inputs = self.tokenizer.encode(
                prompt, return_tensors="pt", truncation=True, max_length=512
                )

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode the response
            resp = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the generated part (remove the input prompt)
            generated_text = resp[len(prompt):].strip()

            if generated_text:
                return generated_text
            err = "I don't have enough information to provide a detailed answer."
            logger.error(err)
            raise RuntimeError(err)

        except ImportError as e:
            err = "Torch package is required. Install with: pip install torch"
            logger.error(err, exc_info=True)
            raise ImportError(err) from e
        except Exception as e:
            err = f"Error calling local model: {self.model_name}"
            logger.error(err, exc_info=True)
            raise RuntimeError(err) from e

    def _call_huggingface_api(
        self, prompt: str, temperature: float = 0.25, max_new_tokens: int = 200
        ) -> str:
        """
        Call the Hugging Face Inference API.

        Args:
            prompt: The formatted prompt to send to the LLM
            temperature: Controls randomness in generation (0.0 = deterministic, 1.0 = very random)
            max_new_tokens: Maximum number of tokens to generate

        Raises:
            RuntimeError:
                If the model is unavailable (404), authentication fails,
                or another API error occurs.
        """
        logger.debug("Calling %s through Hugging Face API", self.model_name)
        try:
            # Use the InferenceClient to generate text using chat completions
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_new_tokens,
                temperature=temperature
            )

            # Extract the response from the completion
            return completion.choices[0].message.content.strip()

        except Exception as e:
            # Provide helpful error message for common issues
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str or "stopiteration" in error_str:
                err_msg = (
                    f"Model '{self.model_name}' is not available on Hugging Face's inference API. "
                    f"Try using a different model like 'deepseek-ai/DeepSeek-V3-0324', "
                    f"'meta-llama/Llama-2-7b-chat-hf', "
                    f"or set use_local=True to use local models."
                    )
                logger.error(err_msg, exc_info=True)
                raise RuntimeError(err_msg) from e
            if "authentication" in error_str or "token" in error_str:
                err_msg = (
                    f"Authentication error: {str(e)}. "
                    f"Please check your HUGGINGFACE_API_KEY environment variable."
                    )
                logger.error(err_msg, exc_info=True)
                raise RuntimeError(err_msg) from e
            err_msg = "Error calling Hugging Face API"
            logger.error(err_msg, exc_info=True)
            raise RuntimeError(err_msg) from e

    def generate_response(
        self, query: str, retrieved_chunks: Sequence[RetrievedChunk],
        gen_config: Optional[GenerationConfig] = None, chat_history: Optional[str] = None
        ) -> str:
        """
        Generate a response using the retrieved chunks as context.

        Args:
            query: The user's original query as a string
            retrieved_chunks: Sequence of retrieved text chunks from the Retriever
            gen_config:
                The text generation configuration. If omitted, a default
                :class:`GenerationConfig` is used.
            chat_history: An optional chat history for subsequent interactions with the LLM

        Returns:
            The generated response string from the LLM

        Raises:
            RuntimeError: If a response is not returned from the LLM
            ImportError:
                If `pytorch` is not installed when `use_local=True`

        Example:
            >>> retriever = Retriever(embedding_model="fastembed")
            >>> chunks = retriever.retrieve("What is RAG?", RetrievalConfig(top_k=3))
            >>> aug = Augmenter(model_name="google/gemma-2-2b-it")
            >>> aug.generate_response("What is RAG?", chunks)  # doctest: +SKIP
            "Retrieval-Augmented Generation (RAG) is ..."
        """
        if not retrieved_chunks:
            invalid_resp = "I don't have enough information to answer your question. " + \
            "Please try rephrasing or expanding your query."
            logger.warning("Warning: %s", invalid_resp)
            return invalid_resp

        if gen_config is None:
            gen_config = GenerationConfig()

        prompt = self._format_prompt(query, retrieved_chunks, chat_history)

        resp = self._call_llm(prompt, gen_config.temperature, gen_config.max_new_tokens)
        logger.info("Valid response from LLM generated")
        return resp

    def generate_response_with_sources(
        self, query: str, retrieved_chunks: Sequence[RetrievedChunk],
        gen_config: Optional[GenerationConfig] = None, chat_history: Optional[str] = None
        ) -> dict:
        """
        Generate a response with source information.

        Args:
            query: The user's original query as a string
            retrieved_chunks: Sequence of retrieved text chunks from the Retriever
            gen_config:
                The text generation configuration. If omitted, a default
                :class:`GenerationConfig` is used.
            chat_history: An optional chat history for subsequent interactions with the LLM

        Returns:
            A dict as follows:
                {
                    "response": str,
                    "sources": list[dict],
                    "num_sources": int,
                    "query": str,
                    "temperature": float,
                    "max_new_tokens": int,
                    }

        Raises:
            RuntimeError: If a response is not returned from the LLM
            ImportError:
                If `pytorch` is not installed when `use_local=True`

        Example:
            >>> retriever = Retriever(embedding_model="fastembed")
            >>> chunks = retriever.retrieve("What is RAG?", RetrievalConfig(top_k=3))
            >>> aug = Augmenter(model_name="google/gemma-2-2b-it")
            >>> aug.generate_response("What is RAG?", chunks)  # doctest: +SKIP
            {"response": "Retrieval-Augmented Generation (RAG) is ...",
            "sources": <sources>, "num_sources": 3, "query": "What is RAG?",
            "temperature": 0.25, "max_new_tokens": 200}
        """
        if gen_config is None:
            gen_config = GenerationConfig()

        resp = self.generate_response(query, retrieved_chunks, gen_config, chat_history)

        return {
            "response": resp,
            "sources": retrieved_chunks,
            "num_sources": len(retrieved_chunks),
            "query": query,
            "temperature": gen_config.temperature,
            "max_new_tokens": gen_config.max_new_tokens
        }

    def _update_history(
        self, history: Optional[Deque[Tuple[str, str]]],  max_chars: int = 2000
        ) -> Optional[str]:
        """
        Turn the rolling (user, assistant) history into a synthetic context chunk
        that fits your existing prompt formatting.
        """
        if not history:
            return None
        lines = []
        for u, a in history:
            lines.append(f"User: {u}")
            lines.append(f"Assistant: {a}")
        text = "Conversation so far (for disambiguation only):\n" + "\n".join(lines)
        return text[:max_chars]

    def _process_query_once(
        self,
        query: str,
        retriever_obj: Retriever,
        chat_config: ChatConfig
        ) -> dict:
        """
        Single-turn processing:
        - build a synthetic 'history' chunk (last N turns),
        - retrieve KB chunks for the new user query,
        - call the augmenter,
        - return a dict with message + (optional) sources.
        """
        # Retrieve fresh context for this turn, will want to make this conditional as
        # subsequent user queries become vague, this will cause fresh context to be
        # less useful than past context
        retrieved = retriever_obj.retrieve(query=query, ret_config=chat_config.ret_config)

        if chat_config.history and len(chat_config.history) > 0:
            # Only include the most recent N turns
            recent = deque(
                list(chat_config.history)[-chat_config.history_turns:],
                maxlen=chat_config.history_turns
                )
        else:
            recent = None
        hist = self._update_history(recent)

        if chat_config.include_sources:
            out = self.generate_response_with_sources(
                query=query,
                retrieved_chunks=retrieved,
                gen_config=chat_config.gen_config,
                chat_history=hist
                )
            return out

        msg = self.generate_response(
            query=query,
            retrieved_chunks=retrieved,
            gen_config=chat_config.gen_config,
            chat_history=hist
            )
        return {"response": msg, "sources": retrieved, "num_sources": len(retrieved)}

def initiate_chat(
    augmenter_obj: Augmenter, retriever_obj: Retriever, command_args: argparse.Namespace
    ) -> None:
    """
    Start an interactive "rolling chat" loop (retrieve + augment per turn).

    The function reads user input from stdin, retrieves fresh KB context for
    each turn, formats a prompt that includes the last N prior turns as
    read-only disambiguation, prints the assistant reply, and continues until
    the user types ``quit`` or ``exit`` (or presses Ctrl+C). On termination,
    it exits the process with code 0.

    Args:
        augmenter_obj: An initialized :py:class:`Augmenter`.
        retriever_obj: An initialized :py:class:`RAGToolBox.retriever.Retriever`.
        command_args: Parsed CLI args (argparse.Namespace) containing:
            - ``top_k`` (int)
            - ``max_retries`` (int)
            - ``temperature`` (float)
            - ``max_tokens`` (int)
            - ``sources`` (bool)
            - ``history_turns`` (int)

    Returns:
        None. Prints responses to stdout and calls ``sys.exit(0)`` when finished.

    Raises:
        SystemExit: Always, with code 0 on normal termination.
        Exception: Any unexpected error that occurs during a turn is logged and
            surfaced to the console, then the loop continues until exit.

    Examples:
        Programmatic:
            >>> from types import SimpleNamespace
            >>> args = SimpleNamespace(
            ...     top_k=5, max_retries=3, temperature=0.25, max_tokens=200,
            ...     sources=False, history_turns=3, prompt_type='default'
            ... )
            >>> # augmenter = Augmenter()
            >>> # retriever = Retriever(embedding_model="fastembed")
            >>> # initiate_chat(augmenter, retriever, args)  # doctest: +SKIP

        CLI:
            $ python -m RAGToolBox.augmenter --chat \\
                --embedding-model fastembed \\
                --db-path assets/kb/embeddings/embeddings.db \\
                --model-name google/gemma-2-2b-it
    """
    print("Chat mode: type your message. Type 'quit' or 'exit' to leave.")
    history: deque[tuple[str, str]] = deque(maxlen=50)

    while True:
        try:
            user_msg = input("\nYou: ").strip()
            if user_msg.lower() in {"quit", "exit"}:
                break
            # process one turn
            result = augmenter_obj._process_query_once( # pylint: disable=protected-access
                query=user_msg,
                retriever_obj=retriever_obj,
                chat_config = _init_chat_config(
                    history=history,
                    command_args=command_args
                    )
                )
            assistant_msg = result["response"]
            logger.debug('Q: %s. A: %s', user_msg, result['response'])
            print(f"\nAssistant: {assistant_msg}")

            if command_args.sources:
                print(f"\n[Sources used: "
                f"{result.get('num_sources', len(result.get('sources', [])))}]")
                print(f"\nSources: {result.get('sources')}")
            history.append((user_msg, assistant_msg))

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting chat.")
            break
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception("Chat turn failed")
            print(f"Error: {str(e)}")
    sys.exit(0)

if __name__ == "__main__":

    from RAGToolBox.logging import RAGTBLogger

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="RAGToolBox Augmenter: Generate responses using retrieved context",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m RAGToolBox.augmenter "What is LIFU?"
  python -m RAGToolBox.augmenter "How does LIFU work?" --temperature 0.5 --max-tokens 300
  python -m RAGToolBox.augmenter "Tell me about the LIFU architecture" --db-path assets/custom/embeddings.db
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        'query',
        nargs = '?',
        type = str,
        help = "The query/question to answer"
        )

    group.add_argument(
        '--chat',
        action = 'store_true',
        help = 'Start an interactive chat loop (retrieval + augmentation per turn).'
        )

    # Optional arguments with defaults
    parser.add_argument(
        "-p",
        "--prompt-type",
        type=str,
        default='default',
        help='Type of prompt style to use for LLM'
    )

    parser.add_argument(
        "--embedding-model",
        type=str,
        default="fastembed",
        help="Embedding model to use for retrieval (default: fastembed)"
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("assets/kb/embeddings/embeddings.db"),
        help="Path to the embeddings database (default: assets/kb/embeddings/embeddings.db)"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.25,
        help="Temperature for response generation (0.0-1.0, default: 0.25)"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=200,
        help="Maximum number of tokens to generate (default: 200)"
    )

    parser.add_argument(
        "--model-name",
        type=str,
        default="google/gemma-2-2b-it",
        help="LLM model name to use (default: google/gemma-2-2b-it)"
    )

    parser.add_argument(
        "--use-local",
        action="store_true",
        help="Use local model instead of Hugging Face API"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="Hugging Face API key (defaults to HUGGINGFACE_API_KEY env var)"
    )

    parser.add_argument(
        '-s',
        '--sources',
        action='store_true',
        help='Include sources to the response'
    )

    parser.add_argument(
        '--top-k',
        default = 10,
        type = int,
        help = 'Number of similar chunks to retrieve'
        )

    parser.add_argument(
        '--max-retries',
        default = 5,
        type = int,
        help = 'Maximum retry attempts when calling the remote embedding model'
        )

    parser.add_argument(
        '--history-turns',
        type = int,
        default = 5,
        help = 'How many past turns to include in the synthetic history context.'
        )

    RAGTBLogger.add_logging_args(parser=parser)

    # Parse arguments
    args = parser.parse_args()

    RAGTBLogger.configure_logging_from_args(args=args)
    logger.debug("CLI args: %s", vars(args))

    try:
        # Initialize retriever
        logger.info(
            "Initializing retriever with model=%s, db_path=%s",
            args.embedding_model, args.db_path
            )
        retriever = Retriever(
            embedding_model=args.embedding_model,
            db_path=args.db_path
        )

        # Initialize augmenter
        logger.info(
            "Initializing augmenter with model=%s (use_local=%s)",
            args.model_name, args.use_local
            )
        augmenter = Augmenter(
            model_name=args.model_name,
            api_key=args.api_key,
            use_local=args.use_local,
            prompt_type=args.prompt_type
        )

        # Interactive rolling chat with LLM
        if args.chat:
            initiate_chat(
                augmenter_obj = augmenter,
                retriever_obj = retriever,
                command_args = args
                )

        # Retrieve context
        logger.info(
            "Retrieving context for query: %r (top_k=%d, max_retries=%d)",
            args.query, args.top_k, args.max_retries
            )
        context = retriever.retrieve(args.query, RetrievalConfig(args.top_k, args.max_retries))

        if not context:
            logger.warning("Warning: No relevant context found for the query.")

        # Generate response
        logger.info(
            "Generating response (temperature=%.2f, max_tokens=%d)",
            args.temperature, args.max_tokens
            )
        if args.sources:
            response = augmenter.generate_response_with_sources(
                args.query,
                context,
                gen_config = GenerationConfig(
                    temperature=args.temperature,
                    max_new_tokens=args.max_tokens
                    )
                )
        else:
            response = augmenter.generate_response(
                args.query,
                context,
                gen_config = GenerationConfig(
                    temperature=args.temperature,
                    max_new_tokens=args.max_tokens
                    )
                )

        # Print results
        print("\n" + "="*50)
        print("QUERY:")
        print(args.query)
        print("\n" + "="*50)
        print("RESPONSE:")
        print(response)
        print("\n" + "="*50)

        if context:
            print(f"Sources used: {len(context)} chunks")

    except Exception as e: # pylint: disable=broad-exception-caught
        logger.exception("Augmenter run failed")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
