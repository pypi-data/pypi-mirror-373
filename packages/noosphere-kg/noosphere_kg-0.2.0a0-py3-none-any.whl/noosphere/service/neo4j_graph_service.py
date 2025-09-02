import logging
from typing import Any
from urllib.parse import urlparse

from langchain.text_splitter import (
    MarkdownHeaderTextSplitter,
    MarkdownTextSplitter,
)
from langchain_community.graphs.graph_document import GraphDocument
from langchain_core.documents import Document
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_openai.chat_models.base import BaseChatOpenAI
from termcolor import colored

from noosphere.exceptions import (
    BuildGraphException,
    RegisterGraphDocumentsException,
)
from noosphere.models import GraphRules

logger = logging.getLogger(__name__)


class Neo4JGraphService:
    """Service for building and managing a Neo4J graph using OpenAI's LLM.

    This service is responsible for parsing the Neo4J URL, initializing the LLM,
    and providing methods to build and register graph documents.
    """

    # --------------------------------------------------------------------------
    # Class Attributes
    # --------------------------------------------------------------------------

    #
    # LLM attributes
    #
    __llm: BaseChatOpenAI

    #
    # Graph rules attributes
    #
    __graph_rules: GraphRules

    #
    # Neo4J attributes
    #
    __neo4j_url: str
    __neo4j_user: str
    __neo4j_password: str
    __neo4j_database: str
    __neo4j_graph: Neo4jGraph

    def __init__(
        self,
        neo4j_url: str,
        llm: BaseChatOpenAI,
        graph_rules: GraphRules,
    ) -> None:
        self.__llm = llm
        self.__graph_rules = graph_rules
        self.__parse_neo4j_url(neo4j_url)
        self.__init_neo4j_connection()

        logger.info("Neo4JGraphService initialized successfully.")

    # --------------------------------------------------------------------------
    # Public Instance Methods
    # --------------------------------------------------------------------------

    async def build_graph(
        self,
        documents: list[Document],
        **_: Any,
    ) -> list[GraphDocument]:
        """Build a graph from the provided documents."""

        errors = []
        for document in documents:
            if not isinstance(document, Document):
                logger.warning(
                    colored(f"Document {document.id} is not a Document.", "yellow")
                )
                errors.append(
                    (
                        document,
                        "is not a Document.",
                    )
                )
                continue

        if errors:
            logger.error(colored("Errors found in documents.", "red"))
            for error in errors:
                logger.error(colored(error[0], "red"), error[1])

            raise ValueError("Errors found in documents.")

        prompt = None
        if self.__graph_rules.prompt:
            prompt = ChatPromptTemplate.from_template(self.__graph_rules.prompt)

        chunked_documents: list[Document] = []
        for document in documents:
            try:
                splitted_documents = MarkdownHeaderTextSplitter(
                    headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")],
                ).split_text(document.page_content)

                if len(splitted_documents) > 0:
                    chunked_documents.extend(splitted_documents)
                    continue

                splitted_documents = MarkdownTextSplitter(
                    chunk_size=self.__graph_rules.chunk_size,
                    chunk_overlap=self.__graph_rules.chunk_overlap,
                    add_start_index=self.__graph_rules.add_start_index,
                    strip_whitespace=self.__graph_rules.strip_whitespace,
                ).split_text(document.page_content)

                chunked_documents.extend(
                    Document(page_content=doc) for doc in splitted_documents
                )
            except Exception as e:
                raise BuildGraphException(e) from e

        transformer = LLMGraphTransformer(
            llm=self.__llm,
            prompt=prompt,
            additional_instructions=self.__graph_rules.additional_instructions,
            strict_mode=self.__graph_rules.strict_mode,
            allowed_nodes=self.__graph_rules.allowed_nodes,
            allowed_relationships=self.__graph_rules.allowed_relationships,
            node_properties=self.__graph_rules.node_properties,
            relationship_properties=self.__graph_rules.relationship_properties,
        )

        return await transformer.aconvert_to_graph_documents(chunked_documents)

    def register_graph_documents(
        self,
        documents: list[GraphDocument],
        **_: Any,
    ) -> bool:
        """Register a graph documents."""

        try:
            errors = []
            for document in documents:
                if not isinstance(document, GraphDocument):
                    logger.warning(
                        colored(
                            f"Document {document.id} is not a GraphDocument.", "yellow"
                        )
                    )
                    errors.append(
                        (
                            document,
                            "is not a GraphDocument.",
                        )
                    )
                    continue
            if errors:
                logger.error(colored("Errors found in documents.", "red"))
                for error in errors:
                    logger.error(colored(error[0], "red"), error[1])

                raise ValueError("Errors found in documents.")

            self.__neo4j_graph.add_graph_documents(
                documents,
                baseEntityLabel=self.__graph_rules.base_entity_label or False,
                include_source=True,
            )
        except Exception as e:
            raise RegisterGraphDocumentsException(e) from e

    # --------------------------------------------------------------------------
    # Private Instance Methods
    # --------------------------------------------------------------------------

    def __parse_neo4j_url(self, url: str) -> None:
        """
        Parse the Neo4J URL to extract the host, port, and database name.
        """
        parsed_url = urlparse(url)
        url = parsed_url.netloc

        if not url:
            raise ValueError("Invalid Neo4J URL provided.")

        self.__neo4j_user = parsed_url.username or "neo4j"
        self.__neo4j_password = parsed_url.password or "password"
        self.__neo4j_database = parsed_url.path.lstrip("/") or "neo4j"
        self.__neo4j_url = (
            f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}"
        )

        logger.info(f"Parsed Neo4J URL: {self.__neo4j_url}")

        # Log the parsed components
        logger.info(f"Parsed Neo4J Database: {self.__neo4j_database}")

    def __init_neo4j_connection(self) -> None:
        """
        Initialize the Neo4J graph connection.
        """

        self.__neo4j_graph = Neo4jGraph(
            url=self.__neo4j_url,
            username=self.__neo4j_user,
            password=self.__neo4j_password,
            database=self.__neo4j_database,
        )

        logger.info(colored("Neo4J graph initialized successfully.", "green"))
