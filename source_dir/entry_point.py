import os


def init():
    print("This is init")


def run(data):
    return {
        "EXAMPLE_ENV_VAR": os.getenv("EXAMPLE_ENV_VAR")
    }
