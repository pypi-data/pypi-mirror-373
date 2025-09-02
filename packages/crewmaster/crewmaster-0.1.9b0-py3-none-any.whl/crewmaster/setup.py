from setuptools import setup, find_packages

setup(
    name="crewmaster",
    version="0.1.1",
    packages=find_packages(),
    description="Core y Manejador de agentes",
    author=[
        {'name': "Imolko", "email": "info@imolko.com"},
        {'name': "Carlos N", "email": "machinery.e@gmail.com"}
    ],
    contributors=[
        {'name': "Carlos N", "email": "machinery.e@gmail.com"}
    ],
    url="https://gitlab.com/imolko/crewmaster.git",
    install_required=[
        "langchain",
        "langgraph",
        "langserve",
        "langchain-community",
        "langchain-postgres",
        "langchain-openai",
        "langchain-cli",
        "langchain-core",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "pyyaml",
        "pytest",
        "pytest-watcher",
        "pytest-mock",
        "pytest-asyncio",
        "structlog",
        "setuptools",
        "fastapi",
        "google",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "deepeval"
    ]
)