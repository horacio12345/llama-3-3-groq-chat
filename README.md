# Groq Chatbot with Streamlit

An interactive chatbot built with Streamlit that uses the Llama 3.3-70b model through the Groq API. The application enables conversations, allows saving them, and provides functionality to retrieve them later.

## 📋 Features

- Interactive chat interface with Streamlit
- Integration with Groq's Llama 3.3-70b model
- Conversation memory system
- Ability to save and retrieve previous conversations
- Multiple conversation management
- Intuitive user interface with icons and formatting

## 🛠️ Requirements

- Python 3.7+
- Groq account with API key
- Project dependencies:
  - streamlit
  - groq
  - langchain
  - python-dotenv

## ⚙️ Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install streamlit groq langchain python-dotenv
```

3. Create a `.env` file in the root directory and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## 🚀 Usage

1. Run the application:
```bash
streamlit run app.py
```

2. The application will open in your default web browser
3. Type your messages in the input field at the bottom
4. Use the sidebar to:
   - Save current conversations
   - Access saved conversations
   - Delete old conversations

## 🔧 Core Functionalities

### Memory Management
- Uses LangChain's `ConversationBufferMemory` to maintain conversation context
- Message formatting compatible with Groq API

### Save System
- Automatic title assignment based on first message
- Timestamp included in each saved conversation
- Ability to overwrite existing conversations with the same title

### Error Handling
- API key verification
- Model response error management
- Informative error messages for users

## 📌 Important Notes

- The application uses the `llama-3.3-70b-versatile` model
- Temperature is set to 0 for more consistent responses
- Maximum token limit is set to 8000

## 🤝 Contributing

Contributions are welcome. Please open an issue or pull request for improvement suggestions.

## 💻 Technical Details

The chatbot implements several key components:

- **State Management**: Uses Streamlit's session state to maintain conversation history and saved chats
- **Message Formatting**: Custom function to convert LangChain messages to Groq's required format
- **Conversation Titling**: Automatic title generation based on the first user message
- **Sidebar Controls**: Intuitive interface for managing conversations
- **Real-time Chat Display**: Dynamic message rendering with user and assistant icons

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.