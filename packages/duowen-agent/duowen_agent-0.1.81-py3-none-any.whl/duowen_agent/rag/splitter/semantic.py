import re
from typing import List, Union, Literal

import numpy as np
from duowen_agent.llm.embedding_model import OpenAIEmbedding, EmbeddingCache
from duowen_agent.rag.models import Document
from duowen_agent.rag.splitter.comm import merge_documents

from .base import BaseChunk


class SemanticChunker(BaseChunk):

    def __init__(
        self,
        llm_embeddings_instance: Union[OpenAIEmbedding, EmbeddingCache],
        threshold_percentage=90,
        chunk_size: int = 512,
        token_count_type: Literal["o200k", "cl100k"] = "cl100k",
    ):
        super().__init__(token_count_type=token_count_type)
        self.llm_embeddings_instance = llm_embeddings_instance
        self.threshold_percentage = threshold_percentage
        self.chunk_size = chunk_size

    def pre_split(self, text: str):
        # Split the input text into individual sentences.
        single_sentences_list = self.__split_sentences(text)

        # Combine adjacent sentences to form a context window around each sentence.
        combined_sentences = self.__combine_sentences(single_sentences_list)

        return single_sentences_list, combined_sentences

    def merge_result(self, embeddings, single_sentences_list):
        # Calculate the cosine distances between consecutive combined sentence embeddings to measure similarity.
        distances = self.__calculate_cosine_similarities(embeddings)

        # Determine the threshold distance for identifying breakpoints based on the 80th percentile of all distances.
        breakpoint_percentile_threshold = self.threshold_percentage
        breakpoint_distance_threshold = np.percentile(
            distances, breakpoint_percentile_threshold
        )

        # Find all indices where the distance exceeds the calculated threshold, indicating a potential chunk breakpoint.
        indices_above_thresh = [
            i
            for i, distance in enumerate(distances)
            if distance > breakpoint_distance_threshold
        ]

        # Initialize the list of chunks and a variable to track the start of the next chunk.
        chunks = []
        start_index = 0

        # Loop through the identified breakpoints and create chunks accordingly.
        for index in indices_above_thresh:
            chunk = " ".join(single_sentences_list[start_index : index + 1])
            chunks.append(chunk)
            start_index = index + 1

        # If there are any sentences left after the last breakpoint, add them as the final chunk.
        if start_index < len(single_sentences_list):
            chunk = " ".join(single_sentences_list[start_index:])
            chunks.append(chunk)

        chunks = [chunk for chunk in chunks if chunk.strip()]

        data = [
            Document(
                page_content=chunk,
                metadata=dict(token_count=self.token_len(chunk), chunk_index=idx),
            )
            for idx, chunk in enumerate(chunks)
            if len(chunk.strip()) > 0
        ]
        return merge_documents(data, self.chunk_size, self.token_count_type)

    def chunk(self, text: str) -> List[Document]:

        single_sentences_list, combined_sentences = self.pre_split(text)

        # Convert the combined sentences into vector representations using a neural network model.
        embeddings = self.__convert_to_vector(combined_sentences)

        return self.merge_result(embeddings, single_sentences_list)

    async def achunk(self, text: str) -> List[Document]:
        single_sentences_list, combined_sentences = self.pre_split(text)

        # Convert the combined sentences into vector representations using a neural network model.
        embeddings = await self.__aconvert_to_vector(combined_sentences)

        return self.merge_result(embeddings, single_sentences_list)

    @staticmethod
    def __split_sentences(text):
        # Use regular expressions to split the text into sentences based on punctuation followed by whitespace.
        # sentences = re.split(r"(?<=[.。?？!！…])\s+", text)
        sentences = re.split(r"(?<=[.。?？!！…])", text)
        return sentences

    @staticmethod
    def __combine_sentences(sentences):
        # Create a buffer by combining each sentence with its previous and next sentence to provide a wider context.
        combined_sentences = []
        for i in range(len(sentences)):
            combined_sentence = sentences[i]
            if i > 0:
                combined_sentence = sentences[i - 1] + " " + combined_sentence
            if i < len(sentences) - 1:
                combined_sentence += " " + sentences[i + 1]
            combined_sentences.append(combined_sentence)
        return combined_sentences

    def __convert_to_vector(self, combined_sentences_list):
        # Try to generate embeddings for a list of texts using a pre-trained model and handle any exceptions.
        response = self.llm_embeddings_instance.get_embedding(combined_sentences_list)
        # response = openai.embeddings.create(input=combined_sentences_list, model="text-embedding-3-small")
        embeddings = np.array([item for item in response])
        return embeddings

    async def __aconvert_to_vector(self, combined_sentences_list):
        # Try to generate embeddings for a list of texts using a pre-trained model and handle any exceptions.
        response = await self.llm_embeddings_instance.aget_embedding(
            combined_sentences_list
        )
        # response = openai.embeddings.create(input=combined_sentences_list, model="text-embedding-3-small")
        embeddings = np.array([item for item in response])
        return embeddings

    @staticmethod
    def __calculate_cosine_similarities(embeddings):
        # Manually calculate the cosine similarities between consecutive embeddings.
        similarities = []
        for i in range(len(embeddings) - 1):
            vec1 = embeddings[i].flatten()
            vec2 = embeddings[i + 1].flatten()
            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)

            if norm_vec1 == 0 or norm_vec2 == 0:
                # If either vector is zero, similarity is undefined (could also return 0)
                similarity = float("nan")
            else:
                similarity = dot_product / (norm_vec1 * norm_vec2)
            similarities.append(similarity)
        return similarities
