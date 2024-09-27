import streamlit as st
import requests


BASE_URL = "http://localhost:3003"  

# Helper function to include JWT token in request headers
def get_headers():
    headers = {}
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
    return headers

with st.sidebar:
    st.markdown(f"<h1 style='font-weight:bold;'>Authentication</h1>", unsafe_allow_html=True)

    name = st.text_input("Enter your name:")
    email = st.text_input("Enter your email address:")
    password = st.text_input("Enter your password", type = "password")
    
   
    if st.button("Login"):
        if email and password:
            response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})

            if response.status_code == 200:
                user_data = response.json()
                st.session_state["user_id"] = user_data["user_id"]
                st.session_state["name"] = user_data["name"]
                st.session_state["access_token"] = user_data["access_token"]
                st.success("Login successful!")

                session_response = requests.get(f"{BASE_URL}/user/{user_data['user_id']}/sessions", headers=get_headers())

                if session_response.status_code == 200:
                    sessions = session_response.json().get("sessions", [])
                    
                    if sessions:
                        latest_session = sessions[-1]
                        st.session_state["session_id"] = latest_session["session_id"]
                        st.success(f"Loaded previous session ID: {st.session_state['session_id']}")

                        history_response = requests.get(f"{BASE_URL}/messages/{st.session_state['session_id']}")
                        if history_response.status_code == 200:
                            messages = history_response.json()
                            st.session_state["messages"] = []
                            for msg in messages:
                                if "human" in msg:
                                    st.session_state["messages"].append({"role": "user", "content": msg['human']})
                                else:
                                    st.session_state["messages"].append({"role": "assistant", "content": msg['ai']})
                            st.success("Previous chat history loaded.")
                        else:
                            st.error("Failed to load previous chat history.")
                    else:
                        session_response = requests.post(f"{BASE_URL}/session", json={"user_id": user_data["user_id"]}, headers=get_headers())
                        if session_response.status_code == 200:
                            st.session_state["session_id"] = session_response.json()["session_id"]
                            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
                            st.success(f"New session created with ID: {st.session_state['session_id']}")
                        else:
                            st.error("Failed to create a new session.")
                else:
                    st.error("Failed to fetch user sessions.")
            else:
                st.error("Invalid email or password. Please try again.")
        else:
            st.warning("Please enter both email and password.")
    

    if st.button("Create New Session"):
        user_id = st.session_state.get("user_id")
        
        if user_id:
            session_response = requests.post(f"{BASE_URL}/session", json={"user_id": user_id}, headers=get_headers())
            if session_response.status_code == 200:
                st.session_state["session_id"] = session_response.json()["session_id"]
                st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
                st.success(f"New session created with ID: {st.session_state['session_id']}")
            else:
                st.error("Failed to create a new session.")
        else:
            st.error("Please log in first.")

   
    if st.button("Register"):
        if name and email and password:  
            register_response = requests.post(f"{BASE_URL}/register-user", json={"name": name, "email": email, "password":password})
            if register_response.status_code == 200:
                st.success("User registered successfully! Creating session...")

                user_data = register_response.json()

                if "user_id" in user_data and "name" in user_data:
                    st.session_state["user_id"] = user_data["user_id"]
                    st.session_state["name"] = user_data["name"]
                    st.session_state["access_token"] = user_data["access_token"]

                session_response = requests.post(f"{BASE_URL}/session", json={"user_id": user_data["user_id"]}, headers=get_headers())
                if session_response.status_code == 200:
                    st.session_state["session_id"] = session_response.json()["session_id"]
                    st.success("Session created successfully!")
                else:
                    st.error("Failed to create session.")
            else:
                st.error(register_response.json().get("detail", "Registration failed."))
        else:
            st.warning("Please enter your name, password and email to register.")

    st.markdown(f"<h1 style='font-weight:bold;'>Options</h1>", unsafe_allow_html=True)

    tone = st.selectbox("Choose Tone", ["default",
        "real-time", "formal", "casual", "sports",
        "science", "history", "technology", "entertainment", "education", "funny"
    ])

    st.write("---")  
    

    if st.button("View History"):
        user_id = st.session_state.get("user_id")
        
        if user_id:
            session_response = requests.get(f"{BASE_URL}/user/{user_id}/sessions")
            
            if session_response.status_code == 200:
                sessions = session_response.json().get("sessions", [])
                
                if sessions:
                    for session in sessions:
                        session_id = session["session_id"]
                        history_response = requests.get(f"{BASE_URL}/messages/{session_id}")
                        
                        if history_response.status_code == 200:
                            messages = history_response.json()
                            st.markdown(f"<h3 style='font-weight:bold;'>Session ID: {session_id}</h3>", unsafe_allow_html=True)

                            
                            
                            for msg in messages:
                                if "human" in msg:
                                    st.write(f"**User:** {msg['human']}")
                                else:
                                    st.write(f"**Assistant:** {msg['ai']}")
                        else:
                            st.error(f"Error fetching messages for session {session_id}: {history_response.text}")
                else:
                    st.info("No sessions found for this user.")
            else:
                st.error(f"Error fetching sessions: {session_response.text}")
    else:
        st.warning("Please log in to view history.")

        
st.markdown(
    "<h1 style='display: flex; align-items: center;'><img src='https://cloud-1de12d.b-cdn.net/media/iW=611&iH=611&oX=28&oY=0&cW=555&cH=611/460183bb42da2034851f4ef49a0191fd/smartBotGenius%20favicon.png' width='100' style='margin-right: 10px;' /> SmartGPT</h1>",
    unsafe_allow_html=True
)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        col1, col2 = st.columns([0.2, 2])
        with col1:
            st.image("https://static.vecteezy.com/system/resources/previews/007/225/199/non_2x/robot-chat-bot-concept-illustration-vector.jpg", width=50)
        with col2:
            st.write(f"**Assistant:** {msg['content']}")
    else:
        st.chat_message(msg["role"]).write(msg["content"])

# PDF file uploader
pdf_file = st.file_uploader("Upload a PDF for context (optional)", type="pdf")

if pdf_file:
    files = {"file": pdf_file}
    try:
        response = requests.post(f"{BASE_URL}/up", files=files, headers=get_headers())
        if response.status_code == 200:
            st.success("PDF uploaded and processed successfully.")
        else:
            st.error(f"Error processing PDF. Status code: {response.status_code}, Details: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading PDF: {e}")


# Input for user messages
if prompt := st.chat_input():
    if "session_id" not in st.session_state:
        st.info("Please log in to continue.")
        st.stop()

    # Prepare the payload
    payload = {
        "session_id": str(st.session_state["session_id"]),  # session_id as a string
        "query": prompt,
        "tone": tone
    }

    # Send query to the backend
    response = requests.post(f"{BASE_URL}/talk-to-bot", json=payload)

    if response.status_code == 200:
        bot_response = response.json()["response"]
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    else:
        # Debugging: Print response content to see the error details
        st.error(f"Error getting response from the bot. Status code: {response.status_code}, Details: {response.text}")