# import pytest

# from ms_utils.vdb_utils import QdrantVdbManager


# @pytest.fixture
# def vdb_manager():
#     return QdrantVdbManager(host="localhost", dense_model_name="BAAI/bge-m3")


# def test_create_collection(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     assert collection_name in vdb_manager.client.get_collections()


# def test_insert(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     documents = ["Test document"]
#     dense_vectors = [[0.1, 0.2, 0.3]]
#     ids = vdb_manager.insert(collection_name, documents, dense_vectors)
#     assert len(ids) == 1


# def test_query(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     documents = ["Test document"]
#     dense_vectors = [[0.1, 0.2, 0.3]]
#     vdb_manager.insert(collection_name, documents, dense_vectors)
#     query = "Test query"
#     query_emb = [0.1, 0.4, 0.9]
#     top_k = 4
#     beta = 0.7
#     results = vdb_manager.query(collection_name, query, query_emb, top_k, beta)
#     assert len(results) == 1


# def test_get_emb_model(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     assert vdb_manager.get_emb_model([collection_name]) is not None


# def test_get_dense_emb_model(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     assert vdb_manager.get_dense_emb_model([collection_name]) is not None


# def test_get_sparse_emb_model(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     assert vdb_manager.get_sparse_emb_model([collection_name]) is not None


# def test_get_norm(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     assert vdb_manager.get_norm([collection_name]) is not None


# def test_insert_new_document(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     new_docs = ["New test document"]
#     dense_vectors = [[0.1, 0.2, 0.3]]
#     ids = vdb_manager.insert(collection_name, new_docs, dense_vectors)
#     assert len(ids) == 1


# def test_update_document(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     new_docs = ["New test document"]
#     dense_vectors = [[0.1, 0.2, 0.3]]
#     vdb_manager.insert(collection_name, new_docs, dense_vectors)
#     updated_dense_vectors = [[0.3, 0.2, 0.1]]
#     updated_ids = vdb_manager.update(
#         collection_name, updated_dense_vectors, new_docs
#     )
#     assert len(updated_ids) == 1


# def test_get_document(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     new_docs = ["New test document"]
#     dense_vectors = [[0.1, 0.2, 0.3]]
#     ids = vdb_manager.insert(collection_name, new_docs, dense_vectors)
#     document = vdb_manager.get_document(collection_name, ids)
#     assert document is not None


# def test_delete_document(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     new_docs = ["New test document"]
#     dense_vectors = [[0.1, 0.2, 0.3]]
#     ids = vdb_manager.insert(collection_name, new_docs, dense_vectors)
#     vdb_manager.delete_document(collection_name, ids)
#     document = vdb_manager.get_document(collection_name, ids)
#     assert document is None


# def test_collection_exists(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     assert vdb_manager.collection_exists(collection_name)


# def test_get_collection(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     assert vdb_manager.get_collection([collection_name]) is not None


# def test_delete_collection(vdb_manager):
#     collection_name = "test_collection"
#     vdb_manager.create_collection(collection_name)
#     vdb_manager.delete_collection([collection_name])
#     assert collection_name not in vdb_manager.client.get_collections()
