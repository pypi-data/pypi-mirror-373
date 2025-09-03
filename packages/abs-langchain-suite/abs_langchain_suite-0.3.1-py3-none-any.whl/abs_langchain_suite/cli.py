import argparse
from .provider.provider_factory import create_provider

def main():
    parser = argparse.ArgumentParser(description="Run AI provider CLI")

    parser.add_argument("--provider", choices=["openai", "azure", "claude"], required=True)
    parser.add_argument("--api_key", type=str, required=True)
    parser.add_argument("--message", type=str, required=True)
    parser.add_argument("--model_name", type=str, default=None)
    parser.add_argument("--azure_endpoint", type=str, default=None)
    parser.add_argument("--deployment_name", type=str, default=None)

    args = parser.parse_args()

    kwargs = {"api_key": args.api_key}
    if args.model_name:
        kwargs["model_name"] = args.model_name
    if args.provider == "azure":
        kwargs["azure_endpoint"] = args.azure_endpoint
        kwargs["deployment_name"] = args.deployment_name

    provider = create_provider(args.provider, **kwargs)
    response = provider.chat(args.message)
    print("Response:\n", response)

if __name__ == "__main__":
    main()
