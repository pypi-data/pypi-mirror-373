import datetime
import functools
import json
import os
import socket
import sys
import traceback
from typing import Sequence, Optional, Callable

import requests

import sfu_torch_lib.mlflow as mlflow
import sfu_torch_lib.parameters as parameters_lib
import sfu_torch_lib.utils as utils


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def notify(
    function: Callable,
    webhook_url: Optional[str] = os.getenv('SLACK_URL'),
    user_ids: Optional[Sequence[str]] = None,
    on_start: bool = not utils.to_bool_or_false(os.getenv('DEVELOPMENT_MODE')),
    on_complete: bool = not utils.to_bool_or_false(os.getenv('DEVELOPMENT_MODE')),
    on_failure: bool = not utils.to_bool_or_false(os.getenv('DEVELOPMENT_MODE')),
) -> Callable:
    """
    Executes a function and sends a Slack notification with the final status (successfully finished or
    crashed). Also sends a Slack notification before executing the function.
    Visit https://api.slack.com/incoming-webhooks#create_a_webhook for more details.
    Visit https://api.slack.com/methods/users.identity for more details.

    :param function: Function to annotate and execute.
    :param webhook_url: The webhook URL to your Slack channel. If missing, no notifications will be made.
    :param user_ids: Optional user ids to notify.
    :param on_start: Send notifications on start.
    :param on_complete: Send notifications on complete.
    :param on_failure: Send notification on failure.
    """
    if user_ids is None:
        user_ids = [os.environ['SLACK_USER']] if os.getenv('SLACK_USER') else []

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if not webhook_url:
            return function(*args, **kwargs)

        script_name = sys.argv[0]
        user_mentions = ', '.join(f'<@{user_id}>' for user_id in user_ids)

        parameters = '\n'.join(
            f'\t{key}: {value}'
            for key, value in parameters_lib.get_script_parameters(function, ignore_keyword_arguments=False).items()
        )

        start_time = datetime.datetime.now()
        host_name = socket.gethostname()

        if 'RANK' in os.environ:
            master_process = int(os.environ['RANK']) == 0
            host_name += f' - RANK: {os.environ["RANK"]}'
        else:
            master_process = True

        if master_process and on_start:
            contents = [
                '*🎬 Your job has started*',
                f'Script: {script_name}',
                f'Machine name: {host_name}',
                f'Starting time: {start_time.strftime(DATE_FORMAT)}',
                f'Parameters:\n{parameters}',
                f'User: {user_mentions}',
            ]

            message = {'text': '\n'.join(contents)}
            requests.post(webhook_url, json.dumps(message))

        try:
            value = function(*args, **kwargs)

            if master_process and on_complete:
                metrics = '\n'.join(f'\t{key}: {value}' for key, value in mlflow.get_metrics().items())

                end_time = datetime.datetime.now()
                elapsed_time = end_time - start_time
                contents = [
                    '*🎉 Your job is complete*',
                    f'Script: {script_name}',
                    f'Machine name: {host_name}',
                    f'Starting time: {start_time.strftime(DATE_FORMAT)}',
                    f'End date: {end_time.strftime(DATE_FORMAT)}',
                    f'Duration: {elapsed_time}',
                    f'Returned value: {value}',
                    f'Parameters:\n{parameters}',
                    f'Metrics:\n{metrics}',
                    f'User: {user_mentions}',
                ]

                message = {'text': '\n'.join(contents)}
                requests.post(webhook_url, json.dumps(message))

            return value

        except Exception as exception:
            if master_process and on_failure:
                end_time = datetime.datetime.now()
                elapsed_time = end_time - start_time
                contents = [
                    '*☠️ Your job has crashed*',
                    f'Script: {script_name}',
                    f'Machine name: {host_name}',
                    f'Starting time: {start_time.strftime(DATE_FORMAT)}',
                    f'End date: {end_time.strftime(DATE_FORMAT)}',
                    f'Duration: {elapsed_time}\n\n',
                    f'Error:\n{exception}\n\n',
                    f'Traceback:\n{traceback.format_exc()}',
                    f'User: {user_mentions}',
                ]

                message = {'text': '\n'.join(contents)}
                requests.post(webhook_url, json.dumps(message))

            raise exception

    return wrapper
