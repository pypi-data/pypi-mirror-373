from .collection import KnowledgeCollectionService
from .data_source import KnowledgeDataSourceService


class KnowledgeService(KnowledgeCollectionService, KnowledgeDataSourceService):
    pass
