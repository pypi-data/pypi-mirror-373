from collections import deque
from time import sleep
from typing import Deque

import click

from cadence.api.CadenceHTTPClient import CadenceHTTPClient
from cadence.api.exceptions import CadenceServerException
from cadence.api.model.logs import LogStream, Log


BATCH_SIZE: int = 1000

class TCLogInputStream(LogStream):
    client: CadenceHTTPClient
    project_id: str
    execution_id: str

    offset: int = -1
    buffer: Deque[Log] = deque()

    def __init__(self, client: CadenceHTTPClient, project_id: str, execution_id: str):
        self.client = client
        self.project_id = project_id
        self.execution_id = execution_id

    def read_next_log(self) -> Log | None:
        if len(self.buffer) > 0:
            return self.buffer.popleft()

        while True:
            try:
                if self.offset == -1:
                    current_of = self.client.get_current_execution_log_offset(self.project_id, self.execution_id)
                    self.offset = current_of - int(BATCH_SIZE / 2)

                    if self.offset < 0:
                        self.offset = 0

                offset = self.offset
                logs = self.client.get_execution_logs(self.project_id, self.execution_id, offset, BATCH_SIZE)

                if logs.count != 0 and len(logs.logs) > 0:
                    self.offset += logs.count
                    self.buffer.extend(logs.logs)
                    break


                status = self.client.get_execution_status(self.project_id, self.execution_id)
                if status in ["COMPLETED", "FAILED", "CANCELED"]:
                    return None


                sleep(1)
            except CadenceServerException as e:
                raise e
            except InterruptedError:
                click.echo("Stopped reading logs due to interruption")
                return None
            except Exception as e:
                click.echo(f"Got error during retrieving logs from buffer {e}")


        return self.buffer.popleft() if len(self.buffer) > 0 else None







