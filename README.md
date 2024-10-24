# Healio_ChatBOT
Healio chatbot for all your healthcare related questions along with access to locations for nearby medical centers
This code implements a **Flask-based Health Assistant Chatbot** that uses the **OpenAI API** and **Google Places API** to respond to health-related queries and provide nearby medical center information.

### Key Features:
1. **Flask Web Application**:
   - Handles user input through a simple chatbot interface, supporting both `GET` and `POST` requests.
   - CORS is enabled to allow cross-origin requests.

2. **OpenAI Integration**:
   - Uses GPT-4 (or GPT-3.5) for generating responses to user queries.
   - The function `get_ai_response()` sends user inputs to the OpenAI API and returns relevant responses.

3. **Google Places API**:
   - The `get_nearby_medical_centers()` function retrieves nearby medical centers based on the user's location and search radius, returning names and addresses.

4. **Health-Related Query Filtering**:
   - The chatbot checks if the user's input is health-related using `is_health_related()`.
   - If the input involves medical services (e.g., "hospital," "doctor"), the bot offers nearby center information.

5. **Conversation Flow**:
   - The bot tracks the conversation state (`waiting_for_location`) to guide users in providing necessary information, like their location.

6. **Command-Line Interface**:
   - A `main()` loop allows for a command-line interaction with the chatbot, processing inputs and outputs directly in the console.
