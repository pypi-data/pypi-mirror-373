import asyncio
import logging
from functools import wraps
from os import getenv
from pathlib import Path
from typing import Any, Callable

import rich_click as click
from docling.datamodel.base_models import InputFormat
from langchain_openai import ChatOpenAI
from termcolor import colored

from noosphere.__version__ import version
from noosphere.models.graph_rules import GraphRules
from noosphere.service.neo4j_graph_service import Neo4JGraphService

logger = logging.getLogger(__name__)

ENV_LOG_LEVEL = getenv("LOG_LEVEL", "INFO").upper()

try:
    LEVEL = getattr(logging, ENV_LOG_LEVEL)
except AttributeError:
    LEVEL = logging.INFO

logging.basicConfig(
    level=LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def __extend_options(options: list[Any]) -> Any:
    def _extend_options(func: Any) -> Any:
        for option in reversed(options):
            func = option(func)
        return func

    return _extend_options


def __async_cmd(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


GRAPH_SERVICE_KEY = "graph_service"


def __inject_dependencies(func):
    """Decorator to inject dependencies into async Click commands."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        from functools import partial

        from noosphere.service import Neo4JGraphService

        # Graph rules is required
        if (config_path := kwargs.get("config_path")) is None:
            raise ValueError("Graph rules are required.")

        graph_rules = GraphRules.load_from_yaml_file(file_path=config_path)

        # Neo4J URL is required
        if (neo4j_url := kwargs.get("neo4j_url")) is None:
            raise ValueError("Neo4J URL is required.")

        # LLM API key is required
        if (llm_api_key := kwargs.get("llm_api_key")) is None:
            raise ValueError("LLM API key is required.")

        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=llm_api_key,
        )

        kwargs.update(
            {
                GRAPH_SERVICE_KEY: partial(
                    Neo4JGraphService,
                    neo4j_url=neo4j_url,
                    llm=llm,
                    graph_rules=graph_rules,
                )
            }
        )

        return func(*args, **kwargs)

    return wrapper


# ------------------------------------------------------------------------------
# GROUPS DEFINITIONS
# ------------------------------------------------------------------------------


@click.group(
    "stellar-cli",
    help="Stellar CLI",
)
@click.version_option(version)
def main():
    pass


@main.group(
    "test",
    help="Perform tests for configuration and execution",
)
def test():
    pass


@main.group(
    "kg",
    help="Knowledge graph operations",
)
def kg():
    pass


__SHARED_OPTIONS = [
    click.option(
        "--neo4j-url",
        type=click.STRING,
        prompt=True,
        required=True,
        show_default=True,
        show_envvar=True,
        envvar="NEO4J_URL",
        help="The URL to the Neo4J database.",
    ),
    click.option(
        "--llm-api-key",
        type=click.STRING,
        prompt=True,
        required=False,
        show_default=True,
        hide_input=True,
        show_envvar=True,
        envvar="LLM_API_KEY",
        help="The API key to use for the LLM.",
    ),
]


__KG_CONFIG_OPTION = click.option(
    "-c",
    "--config-path",
    show_default=True,
    required=True,
    type=click.Path(exists=True, readable=True, path_type=Path),
    help=("The path to the configuration file to use for the test."),
)


@test.command(
    "config",
    help="Test configuration",
)
@__KG_CONFIG_OPTION
def test_config(config_path: Path):

    logger.info(f"Config path: {config_path}")

    graph_rules = GraphRules.load_from_yaml_file(file_path=config_path)

    # Import on demand to avoid circular imports
    from json import dumps

    logger.info(f"Graph rules OK: {dumps(graph_rules.model_dump(), indent=2)}")


@kg.command(
    "build",
    help="Build the knowledge graph",
)
@click.option(
    "-d",
    "--documents-path",
    type=click.Path(exists=True, readable=True, path_type=Path),
    required=True,
    help="The folder containing the documents to build the knowledge graph.",
)
@click.option(
    "-p",
    "--pattern",
    type=click.STRING,
    required=False,
    help=(
        "The pattern to use to search for documents. It should be a string with"
        " wildcards. Example: '*.pdf'. If not provided, all documents will be "
        "used. Only documents with the following extensions will be used: "
        + ", ".join([i.value for i in InputFormat])
    ),
)
@__KG_CONFIG_OPTION
@__extend_options(__SHARED_OPTIONS)
@__inject_dependencies
@__async_cmd
async def kg_build(
    graph_service: Callable[[], Neo4JGraphService],
    documents_path: Path,
    pattern: str,
    **_: Any,
) -> None:

    try:
        target_paths = (
            documents_path.glob(pattern) if pattern else documents_path.glob("**/*")
        )

        if not target_paths:
            raise ValueError("No documents found.")

        from docling.datamodel.document import ConversionResult
        from docling.document_converter import DocumentConverter
        from langchain_core.documents import Document

        target_documents: list[ConversionResult] = []

        for document in target_paths:

            converter = DocumentConverter()
            result: ConversionResult = converter.convert(document)

            if result.errors:
                logger.error(f"Errors found in document {document}: {result.errors}")
                continue

            # Persist markdown to /tmp folder
            markdown = result.document.export_to_markdown()

            output_path = Path("/tmp").joinpath(document.name).with_suffix(".md")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)

            logger.debug(f"Document {document} converted successfully.")

            target_documents.append(result)

        if len(target_documents) == 0:
            raise ValueError("No documents found.")

        logger.debug(f"Documents: {target_documents}")

        documents = [
            Document(page_content=result.document.export_to_markdown())
            for result in target_documents
        ]

        graph_service: Neo4JGraphService = graph_service()

        graph_documents = await graph_service.build_graph(documents=documents)

        logger.debug(f"Graph documents: {graph_documents}")

        if graph_service.register_graph_documents(graph_documents) is False:
            raise ValueError("Failed to register graph documents.")

        click.echo(colored("Graph documents registered successfully.", "green"))
    except Exception as e:
        logger.exception(e)
        click.echo(colored(f"Error building the knowledge graph: {e}", "red"))
