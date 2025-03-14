import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# def set_config():
#     # Custom CSS for the entire app
#     st.markdown("""
#     <style>
#         /* Main background and text colors */
#         .stApp {
#             background-color: #F8F4E1;
#             color: #F8F4E1;
#         }

#         /* Sidebar styling */
#         .css-1d391kg {
#             background-color: #e9ecef;
#         }

#         /* Headers */
#         h1 {
#             color: #543310;
#             font-family: 'Helvetica Neue', sans-serif;
#             font-weight: 700;
#         }
#         h2, h3 {
#             color: #74512D;
#             font-family: 'Helvetica Neue', sans-serif;
#         }

#         /* Cards and containers */
#         .custom-card {
#             background-color: white;
#             border-radius: 10px;
#             padding: 20px;
#             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#             margin-bottom: 20px;
#         }

#         /* Custom button styling */
#         .stButton>button {
#             background-color: #3b82f6;
#             color: white;
#             border-radius: 6px;
#             border: none;
#             padding: 8px 16px;
#             font-weight: 500;
#             transition: all 0.3s ease;
#         }
#         .stButton>button:hover {
#             background-color: #2563eb;
#             box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
#             transform: translateY(-2px);
#         }

#         /* Custom input field styling */
#         .stTextInput>div>div>input, .stSelectbox>div>div>input {
#             border-radius: 6px;
#             border: 1px solid #d1d5db;
#         }

#         /* Expander styling */
#         .streamlit-expanderHeader {
#             font-size: 1.1em;
#             font-weight: 600;
#             color: #1e40af;
#         }

#         /* Hide Streamlit branding */
#         #MainMenu {visibility: hidden;}
#         footer {visibility: hidden;}

#         /* Progress bar styling */
#         .stProgress > div > div > div > div {
#             background-color: #3b82f6;
#         }

#         /* Custom success/info/error message styling */
#         .stAlert {
#             border-radius: 8px;
#         }
#     </style>
#     """, unsafe_allow_html=True)


def render_introduction():
    st.title("📚 TRAZEN: Your Interactive Study Companion")

    if 'chapter_selected' not in st.session_state:
        pass
    else:
        if st.session_state['chapter_selected']:
            st.sidebar.write("Selected Chapter:")
            st.sidebar.json(st.session_state['chapter_extracted'])

    # Color source: https://colorhunt.co/palette/f8f4e1af8f6f74512d543310
    st.markdown("""
    <div style="background-color:#F8F4E1; padding:20px; border-radius:10px; margin-bottom:20px;">
        <h3 style="color:#543310;">Welcome to TRAZEN!</h3>
        <p style="color:#74512D">TRAZEN helps you study more effectively by turning your textbooks into interactive learning experiences. Upload your book, explore its content through our intelligent chatbot, and test your knowledge with automatically generated quizzes.</p>
    </div>
    """, unsafe_allow_html=True)

    # How to use section with expandable tabs
    st.header("How to Use TRAZEN")
    st.write("Follow these simple steps, and use the sidebar on the left to get started with TRAZEN.")

    with st.expander("**Step 1: Upload Your Book**", expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            # st.image("https://via.placeholder.com/150x200", caption="Upload PDF")
            st.write("The widgets look like these:")
            st.selectbox(
                label="Pick a chapter",
                options=["Chapter 1", "Chapter 2", "Chapter 3"],
                index=0,
            )
            st.button("Select Chapter")
        with col2:
            st.markdown("""
            - Currently supports PDF files. Larger books may take a moment to process.
            - Only supports high-quality PDFs with clear text for now.
            - 👈 After uploading, choose a specific chapter or section from the dropdown menu.
            - 👈 Click **"Select Chapter"** button to confirm your choice.
            - Verify that the chapter information appears in the left sidebar
            """)


    with st.expander("**Step 2: Chat with your Book**"):
        st.markdown("""
        - Navigate to Page 2 on the left sidebar.
        - Ask any question about the selected chapter, and the AI will provide accurate answers based on the book's content!
        - Explore concepts, get explanations, and clarify doubts.
        - The AI will reference the exact pages in the book where the information comes from.
        - *Note: Summarizing the entire chapter may not yield the best results. Instead, ask specific questions, with keywords for more accurate answers.*
        """)

    with st.expander("**Step 3: Generate Quizzes**"):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("The widgets look like these:")
            st.button("Generate Quiz Bank")
            st.button("Delete Quiz Bank")
        with col2:
            st.markdown("""
            - 👈 Click **"Generate Quiz Bank"** button to create quizzes based on the selected chapter.
            - 👈 To refresh the content, use the **"Delete Quiz Bank"** button and regenerate.
            - *Note: Currently, there are 10 quizzes per generation. However, if the chapter is too short there may be fewer, at a minimum of 4 quizzes.*
            """)

    with st.expander("**Step 4: Take Quizzes**"):
        st.markdown("""
        - Once you have your quiz bank, navigate to the "Quiz" tab to start testing your knowledge
        - Answer the questions -> Get instant feedback -> Check explanations and references
        """)

    # Tips section
    st.header("Tips for Best Results")

    st.markdown("""
    <div style="display: flex; gap: 20px;">
        <div style="flex: 1; background-color:#F8F4E1; padding:15px; border-radius:10px;">
            <h4 style="color:#543310">📚 What Books Work?</h4>
            <p style="color:#74512D">If you open your book on your browser (Chrome, Edge, etc.) and the chapters can be extracted, it will probably work here.</p>
        </div>
        <div style="flex: 1; background-color:#F8F4E1; padding:15px; border-radius:10px;">
            <h4 style="color:#543310">🔍 Focused Learning</h4>
            <p style="color:#74512D">Select chapters / sections at different granularities and check response quality. Start with the outer-most chapters first!</p>
        </div>
        <div style="flex: 1; background-color:#F8F4E1; padding:15px; border-radius:10px;">
            <h4 style="color:#543310">🚀 Better Questions</h4>
            <p style="color:#74512D">You want good answers, you need good questions - use keywords, important phrases, concepts, etc. anything that would help **you** navigate the book on your own.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Call to action
    st.markdown("""
    <div style="background-color:#F8F4E1; padding:20px; border-radius:10px; margin-top:30px; text-align:center;">
        <h3 style="color:#543310;">Ready to start learning?</h3>
        <p style="color:#74512D">Go to Page 1 and Upload your book.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_introduction()