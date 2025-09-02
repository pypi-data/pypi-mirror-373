
from llama_index.core import (
    VectorStoreIndex,
    ServiceContext,
    StorageContext,
)
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever


class CodeFusionRetriever:
    """
    CodeFusionRetriever class to retrieve nodes using QueryFusionRetriever

    to make this code work you have to install tree_sitter_language version 0.20 --> 0.22 does not work yet
    """
    def __init__(self, documents):
        llm = OpenAI(model_name="gpt-4o")
        service_context1 = ServiceContext.from_defaults(node_parser=self._create_code_splitter())
        nodes = service_context1.node_parser.get_nodes_from_documents(documents)

        self.storage_context = StorageContext.from_defaults()
        self.storage_context.docstore.add_documents(nodes)

        self.index = VectorStoreIndex(nodes=nodes, storage_context=self.storage_context, service_context=service_context1)
        self.vector_retriever = self.index.as_retriever(similarity_top_k=10)

        service_context2 = ServiceContext.from_defaults(llm=llm, chunk_size=2024)
        nodes2 = service_context2.node_parser.get_nodes_from_documents(documents)
        self.bm25_retriever = BM25Retriever.from_defaults(nodes=nodes2, similarity_top_k=10)

        self.retriever = QueryFusionRetriever(
            [self.vector_retriever, self.bm25_retriever],
            retriever_weights=[0.6, 0.4],
            similarity_top_k=5,
            num_queries=1,
            mode="relative_score",
            use_async=True,
            verbose=True,
        )

    def _create_code_splitter(self):
        from llama_index.core.node_parser import CodeSplitter
        return CodeSplitter(
            language="python",
            chunk_lines=80,
            chunk_lines_overlap=15,
            max_chars=1500,
        )

    def retrieve(self, query_string):
        return self.retriever.retrieve(query_string)
