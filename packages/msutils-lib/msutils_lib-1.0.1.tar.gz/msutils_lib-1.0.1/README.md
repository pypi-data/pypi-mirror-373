# Microservice Utils library

This repository holds a submodule that includes functionality shared
across microservices. It includes communication_utils and logging_lib libraries
among other small functions shared by at least two microservices.

## Installation

`pip install msutils_lib`

**PyPI package name and import name do not match due to PyPI name availability**

Import the library as `import ms_utils` and use the functions as `ms_utils.<function_name>`

## Integration steps for new microservices

**Only follow these steps if you need to develop a new microservice and if at the same time you need to develop new functionality in ms_utils related to that new microservice. Otherwise simply include msutils_lib in your requirements table so that pip installs it directly from PyPI**

1. Locally create a submodule in the repo that will integrate ms_utils. E.g.:
    - `git submodule add -b main git@gitlab.inno.freepro.com:platforme-ia/ms_utils.git`
2. Stage and commit the new files

3. Add the dependency as `"ms_utils @ {root:uri}/ms_utils"` in the
dependencies table of pyproject.toml and ALSO add the following table somewhere
in pyproject.toml

    ```bash
    [tool.hatch.metadata]
    allow-direct-references = true
    ```

4. When using pyproject.toml and you have added the dependency and metadata
table as shown above then websockets lib and all of it's dependencies will be
automatically installed when you install your module with `pip install .`
Now you can `from ms_utils import MicroServiceWs, S3BucketClient` as it will be in your
virtual env PATH.

- **For quick development without pyproject.toml it's also possible to do the following after steps 1 & 2:**
    - Manually install it with `pip install ./ms_utils` since now it is
    in your working tree. This   useful in cases where you are developing a new
    module and don't have a pyproject.toml file set up yet. This way it will
    be available in your venv PATH and you can directly import it as e.g.
    `from ms_utils import MicroServiceWs, S3BucketClient`.

- Using pip install is nice because this way it
will also automatically install any dependencies of communication utils without
having to add them in your new modules dependency table.

## Communication Utils module

Use the classes inside this Library for different communication purpose
- Connect To communication Gateway with MicroServiceWS
- Connect and Interact with a S3 Bucket with S3BucketClient

### MicroServiceWS class

Websockets wrapper to allow easy integration into MicroServices to facilitate
communication with the Plateforme IA backend server.

#### Usage

There's a specific way to use this class in order to handle the incoming traffic asynchronously

```python
from communication_utils import MicroServiceWs
import asyncio

class UseMicroServiceWs:
    
    def __init__(self) -> None:
        self.host = ""
        self.username = ""
        self.password = ""
        
        self.websocket = None
        self.is_running = True
        
        self.disconnect_event = asyncio.Event()
        self.data_handling_tasks = set()
        
    def check_status(self):
        return self.websocket is not None and self.websocket.is_connected
        
    async def start_microservice_ws(self):
        # define MicroServiceWs
        self.websocket = MicroServiceWs(
            self.host,
            self.username,
            self.password,
            ssl=True
        )
        await self.websocket.connect()
        
    async def run(self):
        await asyncio.gather(self.start_microservice_ws(), self.loop())
    
    async def loop(self):
         while True:
            while self.websocket is None:
                await asyncio.sleep(1)

            if self.websocket is not None:
                while not self.websocket.is_connected:
                    await asyncio.sleep(1)

                # Start the receiver
                self.disconnect_event.clear()
                receiver_task = asyncio.create_task(self.receive_messages())

                try:
                    await asyncio.gather(receiver_task)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    print(f"Unexpected error in server loop: {e}")
                finally:
                    receiver_task.cancel()
                    await asyncio.gather(receiver_task, return_exceptions=True)
    
    async def receive_messages(self):
        while self.is_running:
            if not self.check_status():
                self.disconnect_event.set()
                return

            try:
                response = await asyncio.wait_for(
                    self.websocket.receive(), 1.0
                )
                if response:
                    # Create a task to handle it asynchronously
                    task = asyncio.create_task(
                        self.handle_data(response)
                    )
                    self.data_handling_tasks.add(task)
                    task.add_done_callback(self.data_handling_tasks.discard)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.stop()
                
    async def handle_data(self, data):
        ### HANDLE THE RECEIVED DATA
        pass
    
async def main():
    umws = UseMicroServiceWs()
    await umws.run()
    
if __name__ == "__main__":
    asyncio.run(main())

```

### S3 Bucket library class for S3 Object storage interactions

Connect to a S3 Object Storage endpoint and upload, download and much more

## Logging module

Inits a configured logging object. Use the classes inside this Library for to use the same logger for each repo.

#### Usage

To use the Logger class it's very simple:

```python
from logging_lib import Logger

logger = Logger.setup_logger(__name__)

logger.info("Logging info")
logger.error("Logging error")
logger.warning("Logging warning")
logger.debug("Logging debug")
```

## Encoding Utils module
