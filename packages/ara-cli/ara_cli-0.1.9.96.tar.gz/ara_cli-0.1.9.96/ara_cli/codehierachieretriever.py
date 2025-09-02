from llama_index.core.text_splitter import CodeSplitter
from llama_index.llms.openai import OpenAI
from llama_index.packs.code_hierarchy import (
    CodeHierarchyAgentPack,
    CodeHierarchyNodeParser,
)


class CodeHierarchyRetriever:
    """
    to make this code run add

    ```
        if original_node.text == "":
        continue
    ```

    to code_hierarchy.py (line 606) so that empty chunks are not considered

    """

    def __init__(self, documents):
        split_nodes = CodeHierarchyNodeParser(
            language="python",
            # You can further parameterize the CodeSplitter to split the code
            # into "chunks" that match your context window size using
            # chunck_lines and max_chars parameters, here we just use the defaults
            code_splitter=CodeSplitter(
                    language="python", max_chars=2000, chunk_lines=80
                ),
        ).get_nodes_from_documents(documents, show_progress=False)

        llm = OpenAI(model_name="gpt-4o")
        self.pack = CodeHierarchyAgentPack(split_nodes=split_nodes, llm=llm)

    def retrieve(self, query_string):
        return print(self.pack.run(query_string))
