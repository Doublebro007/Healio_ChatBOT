import sys
import textwrap
import openai
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS if you're making cross-origin requests

# Retrieve the OpenAI API key from environment variables
openai_api_key = "YOUR_API_KEY"  # Use your actual OpenAI API key

# Initialize OpenAI API
openai.api_key = openai_api_key
waiting_for_location = False

def get_nearby_medical_centers(location, radius=5000):
    """
    Fetches nearby medical centers based on user location using Google Places API.

    Args:
        location (str): The user's location (City/ZIP Code).
        radius (int): The radius (in meters) within which to search for medical centers.

    Returns:
        list: A list of medical centers with their names and addresses.
    """
    api_key = "YOUR_GOOGLE_PLACES_API_KEY"  # Replace with your actual API key
    endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    # Search query for medical centers
    query = f"medical centers in {location}"
    params = {
        "query": query,
        "radius": radius,
        "key": api_key
    }

    # Make the API request
    response = requests.get(endpoint, params=params)

    # Debugging: Print the request URL
    (f"Request URL: {response.url}")

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Unable to fetch data from Google Places API. Status Code: {response.status_code}")
        return []

    results = response.json().get("results", [])

    # Debugging: Print the raw response
    (f"Response: {response.json()}")

    # Extract relevant information from the results
    centers = []
    for result in results:
        name = result.get("name")
        address = result.get("formatted_address")
        centers.append((name, address))

    return centers  # Return the list of centers if found

def is_health_related(user_input):
    """
    Uses OpenAI API to determine if the user's input is health-related.
    """
    relevance_prompt = f"Is the following query related to health? '{user_input}'"
    relevance_response = get_ai_response([{"role": "user", "content": relevance_prompt}], max_tokens=10)

    # Expecting "yes" or "no" as a response
    return "yes" in relevance_response.lower()

# Function to get AI response
def get_ai_response(chat_history, max_tokens=500, temperature=0.7):
    """
    Sends the chat history to the OpenAI API and retrieves the response.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" if you don't have access to GPT-4
            messages=chat_history,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"An error occurred while contacting OpenAI: {e}")  # Improved error logging
        return "I'm sorry, but I'm unable to process your request at the moment."

# Global variable to track the current state of the conversation
@app.route("/", methods=["GET", "POST"])
def index():
    global waiting_for_location  # Use the global state variable
    
    if request.method == "POST":
        user_input = request.form['input'].strip()  # Ensure 'input' matches your HTML
        print(f"User input received: {user_input}")  # Debugging statement

        # If waiting for location input
        if waiting_for_location:
            found_centers = get_nearby_medical_centers(user_input)
            waiting_for_location = False  # Reset the state
            
            if found_centers:
                centers_response = "\n".join([f"{name} - {address}" for name, address in found_centers[:5]])  # Limit to 5 centers
                return jsonify({'conversation': centers_response})
            else:
                return jsonify({'conversation': "Error: No medical centers found near your location."})

        # Check if the input is health-related
        if not is_health_related(user_input):
            return jsonify({'conversation': "I only respond to health care questions. Please ask me anything related to health."})

        # Check if the input indicates an interest in medical centers
        if any(keyword in user_input.lower() for keyword in ["medical", "doctor", "hospital", "clinics", "healthcare"]):
            return jsonify({'conversation': "Would you like information about nearby medical centers? (yes/no)"})

        # Check for user agreement
        if user_input.lower() in ["yes", "y"]:
            waiting_for_location = True  # Set state to waiting for location input
            return jsonify({'conversation': "Please enter your location (City/ZIP Code):"})

        # Check for user refusal
        if user_input.lower() in ["no", "n"]:
            waiting_for_location = False  # Reset the state
            return jsonify({'conversation': "Okay, feel free to ask me anything else related to health."})

        # Generate AI response based on the user input
        ai_response = get_ai_response([{"role": "user", "content": user_input}])
        return jsonify({'conversation': ai_response})

    return render_template("index.html", conversation="Hello! I'm your Health Assistant Chatbot. You can ask me any health-related questions.")

def wrap_text(text, width=70):
    """
    Wraps text to a specified width for better readability in the console.
    """
    return textwrap.fill(text, width=width)

def greet_user(chat_history):
    """
    Adds a greeting message to the chat history.
    """
    greeting = """
    Hello! I'm your Health Assistant Chatbot.
    You can ask me any health-related questions, and I'll do my best to provide helpful information.
    Please note that I am not a substitute for professional medical advice.
    """
    chat_history.append({"role": "system", "content": greeting})
    print(wrap_text(greeting))
    print("\n" + "-"*70 + "\n")

def is_this_a_greeting(user_input):
    """
    Determines if the user's input is a greeting similar to "hello" or "bye".
    
    Args:
        user_input (str): The user's input string.
        
    Returns:
        bool: True if the input is a greeting, False otherwise.
    """
    relevance_prompt_2 = f"Is the following a greeting similar to hello or bye? '{user_input}'"
    
    # Use get_ai_response to check if the input is a greeting
    relevance_response_2 = get_ai_response([{"role": "user", "content": relevance_prompt_2}], max_tokens=10)
    
    # Check if the AI response contains 'yes'
    return "yes" in relevance_response_2.lower()

def main():
    """
    The main loop of the chatbot that continuously takes user input and provides responses.
    """
    # Initialize chat history with system prompt
    chat_history = []
    greet_user(chat_history)

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            goodbye_message = "Thank you for using the Health Assistant Chatbot. Stay healthy!"
            chat_history.append({"role": "assistant", "content": goodbye_message})
            print(wrap_text(f"Chatbot: {goodbye_message}"))
            sys.exit()

        if not user_input:
            print(wrap_text("Chatbot: Please enter a question or type 'exit' to quit.\n"))
            continue

        # Check if the input is health-related using AI
        if not is_health_related(user_input):
            print(wrap_text("Chatbot: I only respond to health care questions. Please ask me anything related to health."))
            continue
        
                # Check if the user input contains keywords related to medical centers
        keywords = ["medical", "doctor", "hospital", "clinics", "healthcare", "assistance", ""]
        if any(keyword in user_input.lower() for keyword in keywords):
            response = input("Chatbot: Would you like information about nearby medical centers? (yes/no) ").strip().lower()
            if response == "yes":
                location = input("Chatbot: Please enter your location (City/ZIP Code): ").strip()

                # Define radius values to test
                radius_values = [1000, 5000, 10000, 20000, 30000, 50000]
                found_centers = []

                # Search for medical centers within specified radius values
                for radius in radius_values:
                    centers = get_nearby_medical_centers(location, radius)
                    if centers:
                        found_centers.extend(centers)

                if found_centers:
                    # Remove duplicates if any
                    found_centers = list(set(found_centers))
                    # Limit to 5 closest
                    closest_centers = found_centers[:5]

                    # Output each center in the format "name - address"
                    for name, address in closest_centers:
                        print(wrap_text(f"{name} - {address}\n"))
                else:
                    print(wrap_text(f"Error: No medical centers found near {location} within the specified radii."))

                continue
        # Append user input to chat history
        chat_history.append({"role": "user", "content": user_input})

        # Generate AI response based on the entire chat history
        ai_response = get_ai_response(chat_history)

        # Append AI response to chat history
        chat_history.append({"role": "assistant", "content": ai_response})

        print(wrap_text(f"Chatbot: {ai_response}\n"))
                   
if __name__ == "__main__":
    app.run(debug=True)
    #main()
    