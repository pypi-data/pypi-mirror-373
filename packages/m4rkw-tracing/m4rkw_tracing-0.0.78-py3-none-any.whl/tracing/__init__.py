import os
import sys
import time
import uuid
import json
import datetime
import traceback
import requests
import requests.auth
import socket
import importlib
from pushover import Client

class Tracing:

    def __init__(self, context):
        self.log("initialising tracing")

        self.start_time = time.time()

        timestamp = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        self.log(f"start time: {timestamp}")

        if type(context) == str:
            self.function_name = context
        else:
            self.function_name = context.function_name

        self.endpoint = os.environ['TRACING_ENDPOINT']

        if 'TRACING_USERNAME' in os.environ and 'TRACING_PASSWORD' in os.environ:
            self.auth = requests.auth.HTTPBasicAuth(
                os.environ['TRACING_USERNAME'],
                os.environ['TRACING_PASSWORD']
            )
        else:
            self.auth = None

        self.pushover = Client(os.environ['TRACING_PUSHOVER_USER'], api_token=os.environ['TRACING_PUSHOVER_APP'])


    def log(self, message):
        if sys.stdin.isatty():
            sys.stdout.write(message + "\n")
            sys.stdout.flush()


    def get_state(self):
        try:
            resp = requests.get(
                f"{self.endpoint}/tracing/{self.function_name}",
                timeout=10,
                auth=self.auth
            )

            data = json.loads(resp.text)
        except Exception as e:
            return {}

        return data


    def success(self):
        timestamp = int(time.time())
        runtime = time.time() - self.start_time

        self.state = self.get_state()

        if 'success' in self.state and not self.state['success']:
            self.pushover.send_message('resolved', title=self.function_name)

        try:
            self.send_state(True, timestamp, runtime)
        except Exception as e:
            sys.stderr.write(f"failed to send metrics: {str(e)}\n")
            sys.stderr.flush()

            raise e


    def send_state(self, success, timestamp, runtime):
        self.log(f"emitting state:\n")
        self.log(f"success: {int(success)}\n")
        self.log(f"runtime: {runtime:.2f} seconds\n")

        try:
            resp = requests.post(
                f"{self.endpoint}/tracing/{self.function_name}",
                json={
                    'success': success,
                    'key': self.function_name,
                    'timestamp': timestamp,
                    'runtime': runtime,
                },
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=10,
                auth=self.auth
            )
        except Exception as e:
            pass


    def failure(self):
        timestamp = int(time.time())
        runtime = time.time() - self.start_time

        self.state = self.get_state()

        exc_type, exc_value, exc_traceback = sys.exc_info()

        data={
            'success': False,
            'key': self.function_name,
            'timestamp': timestamp,
            'runtime': runtime,
            'exception_type': str(exc_type.__name__),
            'exception_message': str(exc_value),
        }

        if 'exception_type' not in self.state or 'exception_message' not in self.state or data['exception_type'] != self.state['exception_type'] or data['exception_message'] != self.state['exception_message']:
            trace_identifier = f"{self.function_name}_{int(time.time() * 1000000)}"

            exception = traceback.format_exc()

            content = f"Function: {self.function_name}\n"
            content += f"Runtime: {runtime:.2f} seconds\n"
            content += f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            content += traceback.format_exc()

            url = f"{self.endpoint}/trace/{self.function_name}/{trace_identifier}"

            exception = traceback.format_exception_only(*sys.exc_info()[:2])[-1].strip()

            self.pushover.send_message(exception, title=self.function_name, url=url)

            data['trace_identifier'] = trace_identifier
            data['trace'] = content

        try:
            resp = requests.post(
                f"{self.endpoint}/tracing/{self.function_name}",
                json=data,
                headers={
                    'Content-Type': 'application/json'
                },
                timeout=10,
                auth=self.auth
            )
        except Exception as e:
            pass
