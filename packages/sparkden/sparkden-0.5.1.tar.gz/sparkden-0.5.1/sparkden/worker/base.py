import os
from abc import ABC

from sparkden.models.assistant import Assistant
from sparkden.models.knowledge import KnowledgeCollection
from sparkden.queued_job.decorator import JobFunction


class SparkdenWorker(ABC):
    def __init__(
        self,
        assistants: list[Assistant] = [],
        knowledge_collections: list[KnowledgeCollection] = [],
        queued_jobs: list[JobFunction] = [],
    ):
        self.setup_environment()
        self.setup_broker()
        self.setup_assistants(assistants)
        self.setup_knowledge_collections(knowledge_collections)
        self.setup_queued_jobs(queued_jobs)

    def setup_environment(self):
        """
        Load environment variables and configure API keys.
        """
        import dashscope
        from dotenv import find_dotenv, load_dotenv

        dotenv_path = find_dotenv(usecwd=True)
        load_dotenv(dotenv_path)
        dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")

    def setup_broker(self):
        """
        Setup broker.
        """
        import dramatiq

        from .broker import create_broker

        self.broker = create_broker()
        dramatiq.set_broker(self.broker)

    def setup_assistants(self, assistants: list[Assistant]):
        """
        Setup assistants.
        """
        from sparkden.assistants.registry import assistant_registry

        self.assistants = assistants
        for assistant in assistants:
            assistant_registry.register(assistant)

    def setup_knowledge_collections(
        self, knowledge_collections: list[KnowledgeCollection]
    ):
        """
        Setup knowledge collections.
        """
        from sparkden.knowledge.registry import knowledge_collection_registry

        self.knowledge_collections = knowledge_collections
        for knowledge_collection in knowledge_collections:
            knowledge_collection_registry.register(knowledge_collection)

    def setup_queued_jobs(self, queued_jobs: list[JobFunction]):
        """
        Setup job functions.
        """
        from sparkden.queued_job.data_source_job import data_source_job

        self.queued_jobs = queued_jobs + [data_source_job]
