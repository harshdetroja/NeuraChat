from uuid import uuid4
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Chunker:

    def __init__(self,chunk_size=800, chunk_overlap=120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    
    def chunk_pages(self, pages, chat_id, file_id):

        results = []
        chunk_index = 0

        for page in pages:
            for text_chunk in self.text_splitter.split_text(page["text"]):
                results.append({
                    "id": str(uuid4()),
                    "text": text_chunk,
                    "chunk_index": chunk_index,
                    "page_number": page["page_number"],
                    "chat_id": str(chat_id),
                    "file_id": str(file_id),
                    "word_count": len(text_chunk.split())
                })

                chunk_index += 1

        return results

chunker = Chunker()