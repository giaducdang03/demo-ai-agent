# Chatbot Microservice

This project is a simple chatbot microservice built using FastAPI. It is designed to handle user input and generate responses based on predefined logic.

## Project Structure

```
chatbot-microservice
├── app
│   ├── __init__.py
│   ├── main.py
│   └── chatbot.py
├── tests
│   ├── __init__.py
│   └── test_chatbot.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd chatbot-microservice
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the chatbot microservice, execute the following command:
```
uvicorn app.main:app --reload
```

You can then access the API at `http://127.0.0.1:8000`.

## Running Tests

To run the unit tests, ensure your virtual environment is activated and execute:
```
pytest
```

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.