from setuptools import setup, find_packages

setup(
    name="init-agent-docker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "pyjwt",
        "uvicorn"
    ],
    entry_points={
        "console_scripts": [
            "init-agent-docker = init_agent_docker.agent:run",
        ],
    },
)
