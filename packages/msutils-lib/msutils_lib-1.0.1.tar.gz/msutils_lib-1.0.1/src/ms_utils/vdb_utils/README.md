# Qdrant VDB

## Introduction

QdrantVDB is a lightweight wrapper for the Qdrant vector database,
designed to simplify integration and enable advanced features like weighted hybrid search.
This adapter makes it easy to work with collections of vectorized data,
perform efficient searches, and manage metadata.

Implements weighted hybrid search.

## Usage

### Parameters
```python
    # set the useful parameters for this implementation
    top_k = 4
    w_dense_retrieval = 0.7
    collection_name = "hybrid_search_collection"
    query = "what are the latest advancements in artificial intelligence?"

    # prepare some docs to add in the vdb
    documents = [
        "Machine learning is a subset of artificial intelligence focused on creating algorithms that can learn from data.",
        "Deep learning, a part of machine learning, is widely used for tasks such as image and speech recognition.",
        "Natural language processing enables machines to understand and generate human language.",
        "Artificial intelligence is revolutionizing industries, from healthcare to finance.",
        "Neural networks mimic the human brain to solve complex problems.",
        "Data science combines statistics, mathematics, and programming to analyze and interpret complex data.",
        "Blockchain technology is used for secure and transparent digital transactions.",
        "Cloud computing provides scalable resources for data storage and processing.",
        "Reinforcement learning focuses on training agents to make sequences of decisions in uncertain environments.",
        "The latest advancements in AI are helping to develop autonomous vehicles.",
    ]
```
### Instantiation
```python
    # instantiate vdb
    vdb_manager = QdrantVdbManager(
        dense_model_name="BAAI/bge-m3",
    )
    print(f"pre-creation {vdb_manager.client.get_collections()}")
    # output:
    # pre-creation collections=[]
```
### Create collection
```python
    vdb_manager.create_collection(collection_name)
    vdb_manager.insert(
        collection_name=collection_name,
        docs=documents,
        dense_vectors=[
            [0.1, 0.2, 0.3],
            [0.11, 0.21, 0.31],
            [0.12, 0.22, 0.32],
            [0.13, 0.23, 0.33],
            [0.14, 0.24, 0.34],
            [0.15, 0.25, 0.35],
            [0.16, 0.26, 0.36],
            [0.17, 0.27, 0.37],
            [0.18, 0.28, 0.38],
            [0.19, 0.29, 0.39],

        ]
    )
    print(f"post-creation {vdb_manager.client.get_collections()}")
    # output:
    # post-creation collections=[CollectionDescription(name='hybrid_search_collection')]
```
### Querying
```python
    # some queries to use as tests
    _ = [
        "What are the applications of machine learning?",  # Dense retrieval (synonyms and broader context)
        "Blockchain technology in digital transactions",  # Sparse retrieval (exact match on keywords)
        "Neural networks in deep learning",  # Dense + sparse hybrid (synonym resolution and overlap)
        "AI revolution in healthcare",  # Ambiguity: relevant documents vs. distractors
        "How do autonomous systems make decisions?",  # Dense retrieval: focus on related concepts
        "Cloud-based data storage solutions",  # Sparse match: direct alignment with keywords
        "What is reinforcement learning?",  # Sparse and dense interplay (direct definition and concepts)
        "The role of AI in language processing",  # Ambiguity: focus on NLP vs. general AI
        "Statistical methods in data science",  # Sparse retrieval: keyword-focused
        "Advancements in artificial intelligence",  # Broad dense retrieval: explore connections across topics
    ]

    print(f"Querying with '{query}'...")
    results = vdb_manager.query(
        collection_name=collection_name,
        query=query,
        query_emb=[0.1, 0.4, 0.9],
        top_k=top_k,
        beta=w_dense_retrieval
    )

    print(results)

    for i, point in enumerate(results):
        print(f"# {i+1}")
        doc_id = point.id
        payload = point.payload
        print(
            f"\t Document ID: {doc_id},"
            f"\n\t Text: {payload['text']}"
            f"\n\t Timestamp: {payload['timestamp']}"
        )
    # output:
    # Querying with 'what are the latest advancements in artificial intelligence?'...
    # [ScoredPoint(id='079252d6-5b64-527d-acae-27b7db6eb13b', version=0, score=5.5612382888793945, payload={'text': 'The latest advancements in AI are helping to develop autonomous vehicles.', 'collection_name': 'hybrid_search_collect
    # ion', 'dense_encoder': 'BAAI/bge-m3', 'sparse_encoder': 'BM25', 'norm': False, 'timestamp': '2024-11-27 10:36:46'}, vector=None, shard_key=None, order_value=None), ScoredPoint(id='719ba93f-c41a-565e-a641-d05c1231f7f4', version=0
    # , score=5.576037883758545, payload={'text': 'Artificial intelligence is revolutionizing industries, from healthcare to finance.', 'collection_name': 'hybrid_search_collection', 'dense_encoder': 'BAAI/bge-m3', 'sparse_encoder': '
    # BM25', 'norm': False, 'timestamp': '2024-11-27 10:36:46'}, vector=None, shard_key=None, order_value=None), ScoredPoint(id='e470bb35-67ac-5173-b4c2-487dc59844c8', version=0, score=5.517308235168457, payload={'text': 'Machine lear
    # ning is a subset of artificial intelligence focused on creating algorithms that can learn from data.', 'collection_name': 'hybrid_search_collection', 'dense_encoder': 'BAAI/bge-m3', 'sparse_encoder': 'BM25', 'norm': False, 'time
    # stamp': '2024-11-27 10:36:46'}, vector=None, shard_key=None, order_value=None), ScoredPoint(id='82019439-0d8a-5fff-8a41-b8308e1cf99e', version=0, score=26.824133871857896, payload={'text': 'Neural networks mimic the human brain 
    # to solve complex problems.', 'collection_name': 'hybrid_search_collection', 'dense_encoder': 'BAAI/bge-m3', 'sparse_encoder': 'BM25', 'norm': False, 'timestamp': '2024-11-27 10:36:46'}, vector=None, shard_key=None, order_value=None)]
    # # 1
    #          Document ID: 079252d6-5b64-527d-acae-27b7db6eb13b,
    #          Text: The latest advancements in AI are helping to develop autonomous vehicles.
    #          Timestamp: 2024-11-27 10:36:46
    # # 2
    #          Document ID: 719ba93f-c41a-565e-a641-d05c1231f7f4,
    #          Text: Artificial intelligence is revolutionizing industries, from healthcare to finance.
    #          Timestamp: 2024-11-27 10:36:46
    # # 3
    #          Document ID: e470bb35-67ac-5173-b4c2-487dc59844c8,
    #          Text: Machine learning is a subset of artificial intelligence focused on creating algorithms that can learn from data.
    #          Timestamp: 2024-11-27 10:36:46
    # # 4
    #          Document ID: 82019439-0d8a-5fff-8a41-b8308e1cf99e,
    #          Text: Neural networks mimic the human brain to solve complex problems.
    #          Timestamp: 2024-11-27 10:36:46
```
### Get some useful metadata
```python
    print(f"Embedding model of {collection_name}: {vdb_manager.get_emb_model([collection_name])}")
    print(f"Dense embedding model of {collection_name}: {vdb_manager.get_dense_emb_model([collection_name])}")
    print(f"Sparse embedding model of {collection_name}: {vdb_manager.get_sparse_emb_model([collection_name])}")
    print(f"Normalization of {collection_name}: {vdb_manager.get_norm([collection_name])}")
    # output:
    # Embedding model of hybrid_search_collection: ['BAAI/bge-m3', 'BM25']
    # Dense embedding model of hybrid_search_collection: ['BAAI/bge-m3']
    # Sparse embedding model of hybrid_search_collection: ['BM25']
    # Normalization of hybrid_search_collection: [False]
```
### Insertion
```python
    # add a new document with custom dense vectors, metadata
    new_docs = [
        "progress is unstoppable: Last week, a new cutting-edge machine learning model now enables humans to talk to whales."
    ]
    print(f"Insert a new doc: \n{new_docs}")
    ids = vdb_manager.insert(
        collection_name=collection_name,
        docs=new_docs,
        dense_vectors=[[0.1, 0.2, 0.3]],
        metadatas=[{"comment": "this is a new doc."}],
    )
    print(f"ids of the inserted docs : \n{ids}")
    print(vdb_manager.get_document(
        collection_name=collection_name,
        doc_ids=ids
    ))
    # output:
    # Insert a new doc: 
    # ['progress is unstoppable: Last week, a new cutting-edge machine learning model now enables humans to talk to whales.']
    # ids of the inserted docs : 
    # ['c9002ddc-b2f1-54d4-9e6c-1d59a2950d77']
    # [Record(id='c9002ddc-b2f1-54d4-9e6c-1d59a2950d77', payload={'text': 'progress is unstoppable: Last week, a new cutting-edge machine learning model now enables humans to talk to whales.', 'collection_name': 'hybrid_search_collection', 'dense_encoder': 'BAAI/bge-m3', 'sparse_encoder': 'BM25', 'norm': False, 'timestamp': '2024-11-27 10:36:46', 'comment': 'this is a new doc.'}, vector=None, shard_key=None, order_value=None)]
```
### Updating
```python
    print(f"update a new doc: \n{new_docs}")
    ids = vdb_manager.update(
        collection_name=collection_name,
        dense_vectors=[[0.3, 0.2, 0.1]],
        docs=new_docs,
        metadatas=[{"comment": "metadata modifications."}],
    )
    print(f"ids of the updated docs : \n{ids}")
    print(vdb_manager.get_document(
        collection_name=collection_name,
        doc_ids=ids
    ))
    # output:
    # update a new doc:
    # ['progress is unstoppable: Last week, a new cutting-edge machine learning model now enables humans to talk to whales.']
    # ids of the updated docs : 
    # ['c9002ddc-b2f1-54d4-9e6c-1d59a2950d77']
    # [Record(id='c9002ddc-b2f1-54d4-9e6c-1d59a2950d77', payload={'text': 'progress is unstoppable: Last week, a new cutting-edge machine learning model now enables humans to talk to whales.', 'collection_name': 'hybrid_search_collectShow the collection: hybrid_search_collection
    # Show the collection: hybrid_search_collection
    # {'hybrid_search_collection': CollectionInfo(status=<CollectionStatus.GREEN: 'green'>, optimizer_status=<OptimizersStatusOneOf.OK: 'ok'>, vectors_count=None, indexed_vectors_count=0, points_count=10, segments_count=1, config=CollectionConfig(params=CollectionParams(vectors={'text-dense': VectorParams(size=1024, distance=<Distance.EUCLID: 'Euclid'>, hnsw_config=None, quantization_config=None, on_disk=None, datatype=None, multivector_config=None)}, shard_number=None, sharding_method=None, replication_factor=None, write_consistency_factor=None, read_fan_out_factor=None, on_disk_payload=None, sparse_vectors={'text-sparse': SparseVectorParams(index=SparseIndexParams(full_scan_threshold=None, on_disk=False, datatype=None), modifier=None)}), hnsw_config=HnswConfig(m=16, ef_construct=100, full_scan_threshold=10000, max_indexing_threads=0, on_disk=None, payload_m=None), optimizer_config=OptimizersConfig(deleted_threshold=0.2, vacuum_min_vector_number=1000, default_segment_number=0, max_segment_size=None, memmap_threshold=None, indexing_threshold=20000, flush_interval_sec=5, max_optimization_threads=1), wal_config=WalConfig(wal_capacity_mb=32, wal_segments_ahead=0), quantization_config=None), payload_schema={})}
```
### Get a document
```python
    print(f"get a new doc: \n{ids}")
    print(vdb_manager.get_document(
        collection_name=collection_name,
        doc_ids=ids
    ))
    # ouput:
    # get a new doc:
    # ['c9002ddc-b2f1-54d4-9e6c-1d59a2950d77']
    # [Record(id='c9002ddc-b2f1-54d4-9e6c-1d59a2950d77', payload={'text': 'progress is unstoppable: Last week, a new cutting-edge machine learning model now enables humans to talk to whales.', 'collection_name': 'hybrid_search_collection', 'dense_encoder': 'BAAI/bge-m3', 'sparse_encoder': 'BM25', 'norm': False, 'timestamp': '2024-11-27 16:03:36', 'comment': 'metadata modifications.'}, vector=None, shard_key=None, order_value=None)]
```
### Deleting a document
```python
    print(f"Delete new docs: \n{ids}")
    vdb_manager.delete_document(
        collection_name=collection_name,
        doc_ids=ids
    )
    print(f"ids of the deleted docs : \n{ids}")
    print(vdb_manager.get_document(
        collection_name=collection_name,
        doc_ids=ids
    ))
    # output:
    # Delete new docs:
    # ['c9002ddc-b2f1-54d4-9e6c-1d59a2950d77']
    # ids of the deleted docs :
    # ['c9002ddc-b2f1-54d4-9e6c-1d59a2950d77']
    # []
```
### Check if a collection exists
```python
    print(f"Does {collection_name} exists as a collection ?")
    print(vdb_manager.collection_exists(collection_name))
    # output:
    # Does hybrid_search_collection exists as a collection ?
    # True
```
### Get a collection
```python
    print(f"Show the collection: {collection_name}")
    print(vdb_manager.get_collection([collection_name]))
    # ouput:
    # Show the collection: hybrid_search_collection
    # {'hybrid_search_collection': CollectionInfo(status=<CollectionStatus.GREEN: 'green'>, optimizer_status=<OptimizersStatusOneOf.OK: 'ok'>, vectors_count=None, indexed_vectors_count=0, points_count=10, segments_count=1, config=Coll
    # ectionConfig(params=CollectionParams(vectors={'text-dense': VectorParams(size=1024, distance=<Distance.EUCLID: 'Euclid'>, hnsw_config=None, quantization_config=None, on_disk=None, datatype=None, multivector_config=None)}, shard_
    # number=None, sharding_method=None, replication_factor=None, write_consistency_factor=None, read_fan_out_factor=None, on_disk_payload=None, sparse_vectors={'text-sparse': SparseVectorParams(index=SparseIndexParams(full_scan_thres
    # hold=None, on_disk=False, datatype=None), modifier=None)}), hnsw_config=HnswConfig(m=16, ef_construct=100, full_scan_threshold=10000, max_indexing_threads=0, on_disk=None, payload_m=None), optimizer_config=OptimizersConfig(delet
    # ed_threshold=0.2, vacuum_min_vector_number=1000, default_segment_number=0, max_segment_size=None, memmap_threshold=None, indexing_threshold=20000, flush_interval_sec=5, max_optimization_threads=1), wal_config=WalConfig(wal_capacity_mb=32, wal_segments_ahead=0), quantization_config=None), payload_schema={})}
```
### Delete a collection
```python
    print(f"Delete the collection: {collection_name}")
    print(vdb_manager.delete_collection([collection_name]))
    print(vdb_manager.get_collection([collection_name]))
    # output:
    # Delete the collection: hybrid_search_collection
    # None
    # {'hybrid_search_collection': None}
```


### References:

https://github.com/qdrant/qdrant-client/blob/master/qdrant_client/qdrant_client.py
https://qdrant.github.io/fastembed/examples/Hybrid_Search/?h=sparsetextembedding#create-dense-embeddings
https://qdrant.tech/documentation/tutorials/hybrid-search-fastembed/
https://qdrant.tech/documentation/tutorials/neural-search/
https://github.com/qdrant/qdrant-client/blob/master/qdrant_client/qdrant_client.py
https://qdrant.tech/documentation/concepts/vectors/#sparse-vectors
https://qdrant.github.io/fastembed/examples/Supported_Models/#supported-text-embedding-models
