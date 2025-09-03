import os

try:
    import litellm
    from dotenv import find_dotenv, load_dotenv
except ImportError:
    raise ImportError(
        "litellm is not installed. Please install it with `pip install litellm`."
        "dotenv is not installed. Please install it with `pip install dotenv`."
    )


def rag_chat(model, messages, **kwargs):
    price_in = 0
    price_out = 0
    provider_name = model.split(':', 1)[0]
    model_name = model.split(':', 1)[1]

    if provider_name == 'siliconflow':
        provider = 'openai'
        base_url = 'https://api.siliconflow.cn/v1'
        api_key = os.getenv('SILICONFLOW_API_KEY')
    elif provider_name == 'doubao':
        provider = 'openai'
        base_url = 'https://ark.cn-beijing.volces.com/api/v3'
        api_key = os.getenv('DOUBAO_API_KEY')

    elif provider_name == 'azure':
        provider = 'azure'
        base_url = os.environ.get('AZURE_ENDPOINT')
        api_key = os.environ.get('AZURE_API_KEY')
        price_in = 0.005
        price_out = 0.015
    else:
        provider = provider_name
        base_url = None
        api_key = None

    if provider_name == 'azure':
        print('messages:', messages)
        completion = litellm.completion(
            base_url=base_url,
            api_key=api_key,
            model=f'{provider}/{model_name}',
            messages=messages,
            response_format={"type": "json_object"},
            **kwargs)
    else:
        completion = litellm.completion(
            base_url=base_url,
            api_key=api_key,
            model=f'{provider}/{model_name}',
            messages=messages,
            **kwargs)

    input_token = completion.usage.prompt_tokens
    output_token = completion.usage.completion_tokens
    cost = input_token / 1000 * price_in + output_token / 1000 * price_out
    token_use = {
        "input_token": input_token,
        "output_token": output_token,
        "cost": cost
    }
    return completion.choices[0].message.content, token_use
