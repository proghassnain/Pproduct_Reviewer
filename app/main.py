import os
import pickle
import streamlit as st
from dotenv import load_dotenv

from client.client import llm_client
from utilities.url_read import url_read
from utilities.recursive_chunks import recursive_chunks
from utilities.embeddings import create_embeddings, vector_store
from langchain.chains import RetrievalQAWithSourcesChain
from bs4 import BeautifulSoup

load_dotenv()

# ===============================
# Product Summarizer & Recommender
# ===============================
def summarize_and_recommend(vector_data, llm):
    chain = RetrievalQAWithSourcesChain.from_llm(
        llm=llm,
        retriever=vector_data.as_retriever()
    )

    question = """
    Analyze this product based on customer reviews and description.
    Summarize the main PROS and CONS.
    Then clearly answer: Should the user BUY this product? (Yes/No + reasoning).
    """
    result = chain({"question": question}, return_only_outputs=True)
    return result["answer"]

# ===============================
# Clean product page (remove nav/ads)
# ===============================
def clean_product_page(documents):
    cleaned_docs = []
    for doc in documents:
        soup = BeautifulSoup(doc.page_content, "html.parser")

        # Remove scripts, styles, navs, headers, footers
        for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
            tag.extract()

        text = soup.get_text(separator=" ", strip=True)
        doc.page_content = text
        cleaned_docs.append(doc)

    return cleaned_docs

# ===============================
# Process URLs (single product page)
# ===============================
def process_urls(urls, status_container):
    """Process multiple URLs and combine their data"""
    all_data = []

    valid_urls = [url for url in urls if url.strip()]
    if not valid_urls:
        raise ValueError("No valid URLs provided")

    for i, url in enumerate(valid_urls, 1):
        status_container.info(f"Processing URL {i} of {len(valid_urls)}...")
        url_data = url_read([url])
        if url_data:
            url_data = clean_product_page(url_data)
            all_data.extend(url_data)

    return all_data

# ===============================
# Chat Interface (optional)
# ===============================
def show_chat_interface(file_path, llm):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.subheader("Chat History")
    if not st.session_state.messages:
        st.info("No messages yet. Start chatting!")
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about the product..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        if os.path.exists(file_path):
            with st.chat_message("assistant"):
                process_placeholder = st.empty()
                process_placeholder.text("Processing your query...")

                with open(file_path, "rb") as f:
                    vector_data = pickle.load(f)

                with st.spinner("Analyzing context and generating response..."):
                    process_placeholder.text("⏳ Processing...")
                    chain = RetrievalQAWithSourcesChain.from_llm(
                        llm=llm, retriever=vector_data.as_retriever()
                    )
                    result = chain({"question": prompt}, return_only_outputs=True)

                process_placeholder.empty()
                st.markdown(result["answer"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"]
                })

# ===============================
# Main App
# ===============================
def main():
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("GOOGLE_API_KEY not found. Please create a .env file with your Google API key: GOOGLE_API_KEY=your-api-key-here")
        return

    file_path = "vector_store.pkl"
    llm = llm_client()

    st.title("🛍️ Product Review Recommender")
    st.write("Paste a product URL, and I’ll analyze reviews & details to tell you whether you should buy it or not.")

    # Sidebar
    with st.sidebar:
        st.subheader("Product URL")
        product_url = st.text_input("Enter product URL")
        process_button = st.button("Analyze Product")

        # Reset chat
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    status_container = st.empty()

    if process_button and product_url:
        try:
            # Extract product page
            status_container.info("Processing product page...")
            combined_data = process_urls([product_url], status_container)

            if not combined_data:
                st.error("No data could be extracted from this product page.")
                return

            status_container.info("Creating text chunks...")
            chunks = recursive_chunks(combined_data)

            status_container.info("Creating embeddings...")
            embedding_model = create_embeddings()
            vector_store_data = vector_store(chunks, embedding_model)

            with open(file_path, "wb") as f:
                pickle.dump(vector_store_data, f)

            status_container.success("✅ Successfully processed the product page!")

            # Auto-summary + verdict
            status_container.info("Analyzing product and preparing recommendation...")
            recommendation = summarize_and_recommend(vector_store_data, llm)

            st.subheader("📊 Product Review Summary & Verdict")
            st.write(recommendation)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Show chat interface (after processing)
    if os.path.exists(file_path):
        show_chat_interface(file_path, llm)
    else:
        st.info("Please paste a product URL and click Analyze first.")

if __name__ == "__main__":
    main()
