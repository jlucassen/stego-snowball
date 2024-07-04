import dotenv
import os
import time
import argparse

dotenv.load_dotenv()

from FluidStack.client import FluidStack
client = FluidStack(
    api_key = os.getenv('FLUIDSTACK_APIKEY')
)

def get_instance(name):
    return [x for x in client.instances.list() if x.name.startswith(name)][0]

def print_all_status():
    for instance in client.instances.list():
        print(f"{instance.name}: {instance.status}")
        print(f"{instance.configuration}")

def create_instance(name):
    client.instances.create(
        name=f"{name}-a100",
        gpu_type="A100_PCIE_80GB",
        ssh_key=f"{name} key"
)

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

def main():
    parser = argparse.ArgumentParser(description="Run my job")
    parser.add_argument("--start", help="Name to start the job with")
    parser.add_argument("--stop", help="Name to stop the job with")
    args = parser.parse_args()

    print_all_status()
    if args.start:
        try_start(args.start)
    if args.stop:
        try_stop(args.stop)

if __name__ == "__main__":
    main()