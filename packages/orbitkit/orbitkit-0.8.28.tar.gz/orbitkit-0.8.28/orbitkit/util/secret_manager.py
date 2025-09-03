import json
import os
from typing import Optional
from botocore.client import BaseClient
from orbitkit.util import get_from_dict_or_env
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class SecretManager:
    @staticmethod
    def load_secret_2_env(secret_name: str,
                          override=False,
                          region_name="us-west-2",
                          sm_client: Optional[BaseClient] = None,
                          *args,
                          **kwargs):
        if sm_client is None:
            try:
                # Try to get aws keys
                aws_access_key_id = get_from_dict_or_env(
                    kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
                )
                aws_secret_access_key = get_from_dict_or_env(
                    kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
                )
                sm_client = boto3.client(
                    service_name='secretsmanager',
                    region_name=region_name,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                )
            except:
                sm_client = boto3.client(
                    service_name='secretsmanager',
                    region_name=region_name,
                )

        try:
            get_secret_value_response = sm_client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        logger.warning(f"Please be noticed that loading [{secret_name}] from AWS Secret Manager successfully.")
        secret = get_secret_value_response['SecretString']

        # Set all key/value to env
        all_secrets = json.loads(secret)
        for key, value in all_secrets.items():
            if override:
                os.environ[key] = value
            else:
                os.environ.setdefault(key, value)

    @staticmethod
    def check_if_loaded(key_name: str = "ORBIT_ENV_LOADED_CHECK"):
        return key_name in os.environ

    @staticmethod
    def load_secret_2_envs(secret_names: list,
                           override=False,
                           region_name="us-west-2",
                           avoid_repeating=False,
                           *args, **kwargs):

        if len(secret_names) <= 0:
            raise Exception("Must provide at least one secret name.")

        for secret_name in secret_names:
            # Key for avoiding repeat!
            ar_key = f"ORBIT_ENV_LOADED_CHECK#{str(secret_name).upper()}"

            if avoid_repeating and SecretManager.check_if_loaded(key_name=ar_key):
                logger.warning(f"Secret manager [{secret_name}] has already been loaded.")
                continue

            SecretManager.load_secret_2_env(secret_name, override=override, region_name=region_name, *args, **kwargs)
            os.environ[ar_key] = "PLACEHOLDER"


if __name__ == "__main__":
    sm_client = boto3.client(
        service_name="secretsmanager",
        region_name="us-west-2",
    )
    # SecretManager.load_secret_2_env("demo", sm_client=sm_client)
    SecretManager.load_secret_2_envs(["abc"])
    SecretManager.load_secret_2_envs(["abc", "def"], avoid_repeating=True)
    print(SecretManager.check_if_loaded())
