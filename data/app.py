import streamlit as st
from recommender import RAGLaptopRecommender
from chat_histroy import ChatHistory
from gemini import ask_gemini

st.set_page_config(page_title="💻 Flipkart Laptop Recommender", layout="wide")

# Sidebar - Assistant and Chat History
st.sidebar.title("🧠 Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatHistory()

if "last_search_results" not in st.session_state:
    st.session_state.last_search_results = []

# Uploaded CSV
uploaded_file = st.file_uploader("📤 Upload your Flipkart laptop CSV", type=["csv"])

if uploaded_file:
    if "recommender" not in st.session_state:
        st.session_state.recommender = RAGLaptopRecommender(uploaded_file)

    # Search laptops main input
    query = st.text_input("🔍 What kind of laptop are you looking for?")

    if query:
        # Save search query in chat history as user message
        if not st.session_state.chat_history.history or (st.session_state.chat_history.history[-1]['content'] != query):
            st.session_state.chat_history.add_message("user", query)

        with st.spinner("Finding matching laptops..."):
            results = st.session_state.recommender.recommend(query)
            st.session_state.last_search_results = results

        st.subheader("🔎 Recommendations")
        for laptop in results:
            with st.container():
                st.markdown(f"### [{laptop['name']}]({laptop['url']})")
                st.markdown(f"**💰 Price**: ₹{laptop['price']:,}")
                st.markdown(f"**⭐ Rating**: {laptop['rating']} stars")
                st.markdown(f"**🧠 Processor**: {laptop['Processor']} Gen {laptop['Processor_Gen']}")
                st.markdown(f"**🧮 RAM**: {laptop['RAM']} {laptop['RAM_Type']}")
                st.markdown(f"**💾 SSD**: {laptop['SSD']}")
                st.markdown(f"**🖥️ Display**: {laptop['Display_Size']}")
                st.markdown(f"**🎮 Graphics**: {laptop['Graphics']}")
                st.markdown(f"**🧾 Specs**: {laptop['Other_Specs']}")
                st.markdown(f"**📝 Description**: {laptop['Description']}")
                st.markdown("---")

        # Prepare laptop summary for assistant prompt
        laptops_summary = ""
        for i, laptop in enumerate(results):
            laptops_summary += (
                f"{i+1}. {laptop['name']}, {laptop['Processor']} Gen {laptop['Processor_Gen']}, "
                f"{laptop['RAM']} {laptop['RAM_Type']} RAM, {laptop['SSD']} SSD, "
                f"{laptop['Graphics']} graphics, ₹{laptop['price']}, {laptop['rating']}⭐\n"
            )

        # Auto-generate assistant suggestion based on these laptops
        assistant_prompt = (
            f"You are a laptop expert assistant. Based ONLY on the following laptops, "
            f"suggest the best laptop from the list.\n\n"
            f"Laptop Options:\n{laptops_summary}\n\n"
            f"Provide a concise recommendation explaining which laptop is best and why."
        )

        assistant_reply = ask_gemini(assistant_prompt)
        st.session_state.chat_history.add_message("assistant", assistant_reply)

        st.subheader("💡 Assistant Suggestion")
        st.markdown(assistant_reply)

    # Sidebar chat input for additional questions
    chat_input = st.sidebar.text_input("Ask for help (e.g., which is best from above?)", key="chat_input")

    if chat_input and st.session_state.last_search_results:
        st.session_state.chat_history.add_message("user", chat_input)

        # Prepare laptop list summary from last search results
        laptops_summary = ""
        for i, laptop in enumerate(st.session_state.last_search_results):
            laptops_summary += (
                f"{i+1}. {laptop['name']}, {laptop['Processor']} Gen {laptop['Processor_Gen']}, "
                f"{laptop['RAM']} {laptop['RAM_Type']} RAM, {laptop['SSD']} SSD, "
                f"{laptop['Graphics']} graphics, ₹{laptop['price']}, {laptop['rating']}⭐\n"
            )

        prompt = (
            f"You are a laptop expert assistant. Based ONLY on the following laptops, "
            f"answer the user's question.\n\n"
            f"Laptop Options:\n{laptops_summary}\n\n"
            f"User Question: {chat_input}\n\n"
            f"Give a clear, helpful answer highlighting the best laptop(s) if relevant."
        )

        reply = ask_gemini(prompt)
        st.session_state.chat_history.add_message("assistant", reply)

        st.sidebar.markdown("### 💬 Assistant Reply")
        st.sidebar.write(reply)

    # Show chat history in sidebar
    st.sidebar.markdown("### 🕓 Chat History")
    for chat in st.session_state.chat_history.get_all():
        st.sidebar.markdown(f"**{chat['role'].capitalize()}**: {chat['content']}")
