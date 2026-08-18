import threading

from app.llm import LocalLLM
from app.embedding import EmbeddingService
from app.database import Database
from app.ingestion import ingest_directory, ingest_document
from app.retrieval import retrieve
from app.gui import RAGGui
from pathlib import Path
import shutil

def main():

    # Arayüzü oluştur
    gui = RAGGui()

    # Backend nesneleri
    llm = None
    embedding_service = None
    database = None


    # ==================================================
    # Copy Document
    # ==================================================

    def copy_document_to_storage(file_path: str) -> str:
        """
        Belgeyi data/documents klasörüne kopyalar.
        Aynı isimde dosya varsa yeni isim oluşturur.
        """

        storage_dir = Path("data/documents")
        storage_dir.mkdir(parents=True, exist_ok=True)

        source = Path(file_path)

        destination = storage_dir / source.name

        counter = 1

        while destination.exists():

            destination = (
                storage_dir /
                f"{source.stem}_{counter}{source.suffix}"
            )

            counter += 1

        shutil.copy2(source, destination)

        return str(destination)

    # ==================================================
    # Backend Initialization
    # ==================================================

    def initialize_backend():

        nonlocal llm
        nonlocal embedding_service
        nonlocal database

        try:

            gui.show_loading(
                "Starting",
                "Loading language model..."
            )

            llm = LocalLLM()
            llm.load_model()

            gui.update_loading(
                "Loading embedding model..."
            )

            embedding_service = EmbeddingService()
            embedding_service.load_model()

            gui.update_loading(
                "Preparing database..."
            )

            database = Database()

            gui.update_loading(
                "Scanning documents..."
            )

            chunk_count = ingest_directory(
                "data/documents",
                database,
                embedding_service
            )

            gui.close_loading()

            gui.refresh_documents(
                database.get_sources()
            )

            gui.ready()

        except Exception as error:

            gui.close_loading()

            gui.add_message(
                "Assistant",
                f"Startup Error\n\n{error}"
            )

            gui.set_status("Error")



    # ==================================================
    # Generate Answer
    # ==================================================

    def generate_answer(question):

        results = retrieve(
            question,
            database,
            embedding_service,
            k=1
        )


        if not results:
            return None, []

        # Benzersiz kaynakları topla
        sources = list(dict.fromkeys(
            result["source"] for result in results
        ))

        context = "\n\n".join(
            result["content"]
            for result in results
        )

        system_message = (
            "You are a helpful AI assistant.\n"
            "Rules:\n"
            "- Use ONLY the information provided in the context.\n"
            "- Never make up information.\n"
            "- If the answer cannot be found in the context, say that you don't know.\n"
            "- If the user asks in Turkish, answer in Turkish.\n"
            "- If the user asks in English, answer in English.\n"
            "- Keep your answer clear and concise.\n"
            "- If the context contains the answer, answer confidently.\n"
            "- Do not mention the context unless the user asks for the source.\n"
            "- If multiple context chunks contain information about the same topic, "
            "combine them into a single answer.\n"
            "- Do not repeat the same information.\n"
            "- Avoid repeating sentences.\n"
            "- If examples are unrelated to the question, ignore them.\n"
            "- Answer directly without any internal reasoning or thinking tags."
        )

        prompt = f"""Context:
{context}

Question:
{question}

Answer:"""

        try : 
            return llm.ask(prompt, system_message=system_message), sources
        except Exception:    
            raise

    # ==================================================
    # Send Message
    # ==================================================

    def send_message():

        if None in (llm, embedding_service, database):
            return

        question = gui.get_question()

        if not question:
            return

        gui.add_message(
            "You",
            question.capitalize()
        )

        gui.clear_question()

        gui.disable_input()

        gui.set_status("Thinking...")

        def worker():

            try:

                answer, sources = generate_answer(question)

                if answer is None:

                    gui.add_message(
                        "Assistant",
                        "No relevant information found."
                    )

                else:

                    gui.add_message(
                        "Assistant",
                        answer,
                        sources=sources
                    )

            except Exception as error:

                gui.add_message(
                    "Assistant",
                    f"Error\n\n{error}"
                )

            finally:

                gui.enable_input()
                gui.set_status("Ready")

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # ==================================================
    # Add Document
    # ==================================================

    def add_document():

        if embedding_service is None:
            return

        file_path = gui.ask_file()

        if not file_path:
            return

        gui.disable_input()

        gui.set_status("Adding document...")

        def worker():

            try:

                gui.show_loading(
                    "Adding Document",
                    "Copying document..."
                )

                stored_file = copy_document_to_storage(file_path)

                gui.update_loading(
                    "Processing document..."
                )

                chunk_count = ingest_document(
                    stored_file,
                    database,
                    embedding_service
                )

                gui.close_loading()

                gui.refresh_documents(
                    database.get_sources()
                )

                gui.add_message(
                    "Assistant",
                    f"Document added successfully.\n"
                    f"Chunks added: {chunk_count}"
                )

            except Exception as error:

                gui.close_loading()

                gui.add_message(
                    "Assistant",
                    f"Error\n\n{error}"
                )

            finally:

                gui.enable_input()

                gui.set_status("Ready")

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # ==================================================
    # Remove Document
    # ==================================================

    def remove_document():

        if database is None:
            return

        source = gui.get_selected_document()

        if not source:
            return

        # Veritabanından sil
        database.delete_by_source(source)

        # Fiziksel dosyayı sil
        file_path = Path("data/documents") / source

        if file_path.exists():
            file_path.unlink()

        # Paneli güncelle
        gui.refresh_documents(
            database.get_sources()
        )

        gui.add_message(
            "Assistant",
            f"Document removed: {source}"
        )

    # ==================================================
    # Clear Chat
    # ==================================================

    def clear_chat():

        gui.clear_chat()

        gui.add_message(
            "Assistant",
            "Chat cleared."
        )

    # ==================================================
    # Enter Key
    # ==================================================

    def on_enter(event):

        send_message()

        return "break"

    # ==================================================
    # Button Events
    # ==================================================

    gui.send_button.config(
        command=send_message
    )

    gui.add_button.config(
        command=add_document
    )

    gui.remove_doc_button.config(
        command=remove_document
    )

    gui.clear_button.config(
        command=clear_chat
    )

    gui.question_entry.bind(
        "<Return>",
        on_enter
    )

    # ==================================================
    # Start Backend
    # ==================================================

    gui.root.after(
        100,
        lambda: threading.Thread(
            target=initialize_backend,
            daemon=True
        ).start()
    )
    # ==================================================
    # Run GUI

    # ==================================================
    gui.run()


if __name__ == "__main__":
    main()