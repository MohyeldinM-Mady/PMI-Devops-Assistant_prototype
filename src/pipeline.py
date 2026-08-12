from src.collect import main as collect_data
from src.build_knowledge_base import build_knowledge_base
from src.Embeddings.main import main as generate_embeddings
from src.VectorDB.main import main as build_vector_db


def prepare_current_repository():
    print("=== PMI Repository Preparation ===")

    print("\n[1/4] Collecting project data...")
    collect_data()

    print("\n[2/4] Building knowledge base...")
    build_knowledge_base()

    print("\n[3/4] Generating embeddings...")
    generate_embeddings()

    print("\n[4/4] Building vector database...")
    build_vector_db()

    print("\n=== Repository is ready for PMI ===")