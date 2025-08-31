from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def vectorstore(path: str, embedding_model: str) -> Chroma:
    """
    Load existing Chroma vectorstore.

    Parameters
    ----------
    path : str
        Path to the vectorstore persistence directory.
    embedding_model : str
        HuggingFace embedding model name.

    Returns
    -------
    Chroma
        The loaded vectorstore instance.
    """
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    try:
        vectorstore = Chroma(persist_directory=path, embedding_function=embeddings)
        vectorstore.get()  # Test query
        print(
            f"Loaded vectorstore from {path} with {vectorstore._collection.count()} documents"
        )
        return vectorstore
    except Exception as e:
        raise ValueError(f"Failed to load vectorstore from {path}: {str(e)}")
