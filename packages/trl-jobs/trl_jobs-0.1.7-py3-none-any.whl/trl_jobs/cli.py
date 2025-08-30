import json
import time
from argparse import ArgumentParser, Namespace, _SubParsersAction
from importlib.resources import files
from typing import Optional

import yaml
from huggingface_hub import HfApi, SpaceHardware
from huggingface_hub.utils import get_token_to_send, logging

logger = logging.get_logger(__name__)


SUGGESTED_FLAVORS = [item.value for item in SpaceHardware if item.value != "zero-a10g"]

CONFIGS = {
    ("Qwen/Qwen3-0.6B", "a100-large"): "Qwen3-0.6B-a100-large.yaml",
    ("Qwen/Qwen3-1.7B", "a100-large"): "Qwen3-1.7B-a100-large.yaml",
    ("Qwen/Qwen3-4B", "a100-large"): "Qwen3-4B-a100-large.yaml",
    ("Qwen/Qwen3-8B", "a100-large"): "Qwen3-8B-a100-large.yaml",
}


class SFTCommand:
    @staticmethod
    def register_subcommand(parser: _SubParsersAction) -> None:
        sft_parser = parser.add_parser("sft", help="Run a Job")
        sft_parser.add_argument(
            "--flavor",
            default="a100-large",
            type=str,
            help=f"Flavor for the hardware, as in HF Spaces. Defaults to `a100-large`. Possible values: {', '.join(SUGGESTED_FLAVORS)}.",
        )
        sft_parser.add_argument(
            "--timeout",
            type=str,
            help="Max duration: int/float with s (seconds, default), m (minutes), h (hours) or d (days).",
        )
        sft_parser.add_argument(
            "-d",
            "--detach",
            action="store_true",
            help="Run the Job in the background and print the Job ID.",
        )
        sft_parser.add_argument(
            "--namespace",
            type=str,
            help="The namespace where the Job will be created. Defaults to the current user's namespace.",
        )
        sft_parser.add_argument(
            "--token",
            type=str,
            help="A User Access Token generated from https://huggingface.co/settings/tokens",
        )
        sft_parser.add_argument(
            "--model",
            type=str,
            required=True,
            help="Model name or path (e.g., Qwen/Qwen3-4B-Base)",
        )
        sft_parser.set_defaults(func=SFTCommand)

    def __init__(self, args: Namespace, extra_args: list[str]) -> None:
        self.flavor: Optional[SpaceHardware] = args.flavor
        self.timeout: Optional[str] = args.timeout
        self.detach: bool = args.detach
        self.namespace: Optional[str] = args.namespace
        self.token: Optional[str] = args.token
        self.model: str = args.model

        # Check if the requested configuration exists
        if (self.model, self.flavor) in CONFIGS:
            config_file = CONFIGS[(self.model, self.flavor)]
        else:
            raise ValueError(
                f"No configuration file found for model {self.model} and flavor {self.flavor}"
            )

        # Load YAML file
        config_file = files("trl_jobs.configs").joinpath(config_file)
        with open(config_file, "r") as f:
            args_dict = yaml.safe_load(f)

        # Add our own hub_model_id to avoid overwriting a previously trained model
        if "hub_model_id" not in args_dict:
            timestamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
            if self.namespace:
                args_dict["hub_model_id"] = (
                    f"{self.namespace}/{self.model.split('/')[-1]}-SFT-{timestamp}"
                )
            else:
                args_dict["hub_model_id"] = (
                    f"{self.model.split('/')[-1]}-SFT-{timestamp}"
                )

        # Same for run_name
        if "run_name" not in args_dict:
            args_dict["run_name"] = f"{self.model.split('/')[-1]}-SFT-{timestamp}"

        # Parse extra_args into a dictionary
        overrides = {}
        i = 0
        while i < len(extra_args):
            if extra_args[i].startswith("--"):
                key = extra_args[i][2:]
                # handle flags without values (bools)
                if i + 1 >= len(extra_args) or extra_args[i + 1].startswith("--"):
                    overrides[key] = True
                    i += 1
                else:
                    overrides[key] = extra_args[i + 1]
                    i += 2
            else:
                i += 1

        # Override YAML args with CLI args
        merged = {**args_dict, **overrides}

        # Rebuild CLI args
        self.cli_args = []
        for k, v in merged.items():
            if isinstance(v, (dict, list, bool, type(None))):
                v_str = json.dumps(v)
            else:
                v_str = str(v)
            self.cli_args.extend([f"--{k}", v_str])

    def run(self) -> None:
        api = HfApi(token=self.token)
        job = api.run_job(
            image="qgallouedec/trl:dev",
            command=["trl", "sft", *self.cli_args],
            secrets={"HF_TOKEN": get_token_to_send(self.token)},
            flavor=self.flavor,
            timeout=self.timeout,
            namespace=self.namespace,
        )
        # Always print the job ID to the user
        print(f"Job started with ID: {job.id}")
        print(f"View at: {job.url}")

        if self.detach:
            return

        # Now let's stream the logs
        for log in api.fetch_job_logs(job_id=job.id):
            print(log)


def main():
    parser = ArgumentParser("trl-jobs", usage="hf <command> [<args>]")
    commands_parser = parser.add_subparsers(help="trl-jobs command helpers")
    SFTCommand.register_subcommand(commands_parser)

    args, extra_args = parser.parse_known_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)

    service = args.func(args, extra_args)
    if service is not None:
        service.run()


if __name__ == "__main__":
    main()
