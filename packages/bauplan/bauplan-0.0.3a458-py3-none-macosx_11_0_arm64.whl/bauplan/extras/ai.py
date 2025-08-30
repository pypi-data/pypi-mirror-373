import os
from typing import Any, Optional

import pyarrow as pa
from litellm import completion, embedding, exceptions
from litellm.types.utils import Message
from tenacity import retry, stop_after_attempt, wait_random_exponential

AVAILABLE_COMPLETION_MODELS = [
    'bedrock/amazon.titan-text-express-v1',
    'bedrock/meta.llama3-70b-instruct-v1:0',
    'bedrock/amazon.titan-text-lite-v1',
]
AVAILABLE_EMBEDDING_MODELS = [
    'bedrock/amazon.titan-embed-text-v2:0',
    'bedrock/amazon.titan-embed-image-v1',
]


def _get_default_kwargs(model: str, kwargs: dict[str, Any]) -> dict:
    # if the kwargs are not set, we may set some default values
    if model.startswith('bedrock/'):
        # if it is an amazon model, we need aws_region_name to be set
        if not kwargs.get('aws_region_name'):
            if not os.environ.get('AWS_REGION'):
                raise ValueError(f"Model '{model}' requires 'aws_region_name' to be set in kwargs.")
            kwargs['aws_region_name'] = os.environ['AWS_REGION']

    return kwargs


def _check_available_completion_models(model: str, **kwargs) -> bool:
    if model not in AVAILABLE_COMPLETION_MODELS:
        raise ValueError(
            f"Model '{model}' is not available. "
            f'Available models are: {", ".join(AVAILABLE_COMPLETION_MODELS)}'
        )

    return True


def _check_available_embedding_models(model: str, **kwargs) -> bool:
    if model not in AVAILABLE_EMBEDDING_MODELS:
        raise ValueError(
            f"Model '{model}' is not available. Available models are: {', '.join(AVAILABLE_EMBEDDING_MODELS)}"
        )

    return True


@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
def get_completion(
    model: str,
    messages: list,
    temperature: float = 0.7,
    top_p: float = 1,
    max_tokens: Optional[int] = None,
    stop: Optional[list] = None,
    **kwargs,
) -> Optional[Message]:
    # make sure the model is available
    _check_available_completion_models(model, **kwargs)
    # now, run the model completion
    try:
        response = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop,
            **_get_default_kwargs(model, kwargs),
        )
        return response.choices[0].message
    except exceptions.BadRequestError as ex:
        # if the request is not valid, we can catch the error and print it
        # but we don't want to retry the request as it's not valid
        print(f'BAD REQUEST: request not valid {ex}')
    except Exception as e:
        print(f'ERROR: Model not available {e}: retrying now if applicable')
        raise e

    return None


@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(3))
def get_embeddings(
    model: str,
    input: list,
    **kwargs,
) -> Optional[pa.Table]:
    # make sure the model is available
    _check_available_embedding_models(model, **kwargs)
    try:
        response = embedding(
            model=model,
            input=input,
            **_get_default_kwargs(model, kwargs),
        )
        # returning the embeddings as a pyarrow table
        return pa.Table.from_arrays([[_.embedding for _ in response.data]], names=['embedding'])
    except exceptions.BadRequestError as ex:
        # if the request is not valid, we can catch the error and print it
        # but we don't want to retry the request as it's not valid
        print(f'BAD REQUEST: request not valid {ex}')
    except Exception as e:
        print(f'ERROR: Model not available {e}: retrying now if applicable')
        raise e

    return None
