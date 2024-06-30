import dotenv
import os
import time
import tqdm

dotenv.load_dotenv()

from FluidStack.client import FluidStack
client = FluidStack(
    api_key = os.getenv('FLUIDSTACK_APIKEY')
)

def print_all_status():
    for instance in client.instances.list():
        print(f"{instance.name}: {instance.status}")

def get_instance(name):
    return [x for x in client.instances.list() if x.name == name][0]

def try_start(name, tries=60, secs=10):
    instance = get_instance(name)
    for i in range(tries):
        instance = get_instance(name)
        if instance.status == 'running':
            break
        try:
            client.instances.start(instance.id)
        except Exception as e:
            print(f"starting {name}, {i}/{tries}")
        time.sleep(secs)

def try_stop(name, tries=60, secs=10):
    instance = get_instance(name)
    for i in range(tries):
        instance = get_instance(name)
        if instance.status == 'stopped':
            break
        try:
            client.instances.stop(instance.id)
        except Exception as e:
            print(f"stopping {name}, {i}/{tries}")
        time.sleep(secs)

print_all_status()
try_start('james-a100')
try_stop('james-a100')
print_all_status()