# AI Travel Agent Project

Welcome to the AI Travel Agent, a Streamlit-based application powered by LangChain and Ollama that helps you find flights and hotels based on your travel queries. This project uses AI to process user inputs, fetch real-time data via SerpAPI, and send travel information via email.

## Project Overview
- **Purpose**: Assists users in planning trips by providing flight and hotel options with details like prices, ratings, and images.
- **Technologies**: Python, Streamlit, LangChain, Ollama (`llama3.1:8b`), SerpAPI, SendGrid.
- **Features**:
  - Search for flights and 4-star hotels based on location and dates.
  - Display results with images and links.
  - Option to email travel details.

## Screenshots
![Screenshot 1](images/Screenshot1.png)  
*Initial UI with travel query input.*

![Screenshot 2](images/Screenshot2.png)  
*Sample hotel results with images.*

![Screenshot 3](images/Screenshot3.png)  
*Email form.*

## Getting Started

### Prerequisites
- Python 3.11.x
- Ollama (for AI model hosting)
- SerpAPI key (for hotel/flight data)
- SendGrid API key (for email functionality)

### Installation
1. Clone the repository or navigate to `C:\Projects\travel agent`.
2. Create a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   (Create `requirements.txt` with: `streamlit==1.39.0`, `langchain==0.3.0`, `langchain-ollama==0.2.0`, `langgraph==0.2.5`, `sendgrid==6.11.0`, `python-dotenv==1.0.1`, `serpapi==0.1.5`.)
4. Set up environment variables in `.env`:
   ```
   SERPAPI_API_KEY=your_serpapi_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```

### Running the Project
1. Start the Ollama server in a separate terminal:
   ```
   ollama serve
   ```
2. Pull the model:
   ```
   ollama pull llama3.1:8b
   ```
3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
4. Open `http://localhost:8501` in your browser.

## Usage
- Enter a travel query (e.g., "Find 4-star hotels in Alappuzha, Kerala with check-in on November 10, 2025, and check-out on November 15, 2025").
- Click "Get Travel Information" to see results.
- Optionally, send the information via email using the form.

## Contributing
Feel free to fork this repository, submit issues, or pull requests to enhance the project.

## License
This project is under the MIT License (see LICENSE file for details).
