import pytest
from app.chatbot import Chatbot

def test_chatbot_response():
    chatbot = Chatbot()
    response = chatbot.get_response("Hello")
    assert response is not None
    assert isinstance(response, str)

def test_chatbot_fallback():
    chatbot = Chatbot()
    response = chatbot.get_response("Unknown input")
    assert response == "I'm sorry, I didn't understand that."  # Example fallback response

def test_chatbot_edge_case():
    chatbot = Chatbot()
    response = chatbot.get_response("")
    assert response == "Please say something!"  # Example edge case response