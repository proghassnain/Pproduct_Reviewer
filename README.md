🛍️ Product Review Recommender

An AI-powered chatbot that analyzes product pages (e.g., Amazon, Flipkart) and gives you a clear summary with Pros, Cons, and a Buy/Don’t Buy recommendation.
You can also chat with the bot to ask more questions about the product.

✨ Features

Analyze a single product URL

Automatic Pros & Cons summary

Clear Buy / Don’t Buy verdict with reasoning

Interactive chat interface to ask follow-up questions

Clear chat functionality

Real-time product content analysis using LangChain + FAISS embeddings

⚙️ Setup

Clone the repository:

git clone : https://github.com/proghassnain/Pproduct_Reviewer?tab=readme-ov-file

Create a virtual environment and activate it:

python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Add your API key
Create a .env file in the root directory:

GOOGLE_API_KEY=your-api-key-here

▶️ Usage

Run the application:

streamlit run main.py


Paste a product URL in the sidebar

Click Analyze Product

View:

📊 Pros & Cons

✅ Buy / Don’t Buy Verdict

(Optional) Chat with the bot to ask follow-up questions

⚡ Notes

First-time processing may take a few moments while embeddings are created.

Accuracy depends on the content available on the product page. Some sites may block scraping.

📦 Requirements

See requirements.txt for the full list of dependencies.
Key packages:

streamlit

langchain + langchain-community

sentence-transformers

faiss-cpu

python-dotenv

beautifulsoup4

📌 Example Output
✅ Pros:
- Excellent display quality
- Good battery life
- Lightweight and portable

❌ Cons:
- Limited gaming performance
- Slightly expensive

🎯 Verdict:
YES – Recommended for students and professionals.
