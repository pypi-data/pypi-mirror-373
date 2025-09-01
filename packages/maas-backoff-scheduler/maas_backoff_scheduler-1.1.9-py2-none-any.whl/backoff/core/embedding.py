#!/usr/bin/env python
# -*-coding:utf-8-*-

from sentence_transformers import SentenceTransformer
import time
import logging
import numpy as np

logger = logging.getLogger()


class EmbeddingTest:

    model: SentenceTransformer

    def __init__(self):
        # 加载 m3e-large 模型（注意模型名称是 'moka-ai/m3e-large'）
        self.model = SentenceTransformer("moka-ai/m3e-large")

    def embedding_text(self, task_id: str) -> list[np.ndarray]:
        # 需要编码的文本
        sentences = [
            "Moka 此文本嵌入模型由 MokaAI 训练并开源，训练脚本使用 uniem",
            "Massive 此文本嵌入模型通过**千万级**的中文句对数据集进行训练",
            "Mixed 此文本嵌入模型支持中英双语的同质文本相似度计算，异质文本检索等功能，未来还会支持代码检索，ALL in one",
        ]

        # 生成嵌入向量
        embeddings: np.ndarray = self.model.encode(sentences)

        embeddings_list: list[np.ndarray] = []
        # 输出结果
        for sentence, embedding in zip(sentences, embeddings):
            # 修正日志输出格式
            logger.info(f"任务 [{task_id}] 嵌入向量前5位: {embedding[:5]}")
            embeddings_list.append(embedding)
        
        # 返回正确的列表类型
        return embeddings_list


if __name__ == "__main__":

    # 加上调用耗时，单位秒
    start_time = time.time()
    embeddingTest = EmbeddingTest()
    embeddingTest.embedding_text()
    print("耗时:", time.time() - start_time)
