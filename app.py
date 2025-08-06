from flask import Flask, render_template, request, jsonify
import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/explain', methods=['POST'])
def explain_code():
    data = request.get_json()
    code_snippet = data.get('code', '')
    
    if not code_snippet:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful code assistant that explains code line by line."},
                {"role": "user", "content": f"Explain this code in detail:\n\n{code_snippet}"}
            ],
            temperature=0.7
        )
        explanation = response['choices'][0]['message']['content']
        return jsonify({'explanation': explanation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize_repo():
    data = request.get_json()
    repo_url = data.get('repo_url', '')
    
    if not repo_url:
        return jsonify({'error': 'No repository URL provided'}), 400
    
    try:
        # Extract owner and repo name from URL
        parts = repo_url.replace('https://github.com/', '').split('/')
        if len(parts) < 2:
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400
            
        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        
        # Fetch README from GitHub
        response = requests.get(api_url, headers={'Accept': 'application/vnd.github.v3+json'})
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch repository README'}), 404
            
        readme_content = response.json().get('content', '')
        
        # Get summary from OpenAI
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical documentation expert."},
                {"role": "user", "content": f"Summarize this GitHub README in clear, concise points:\n\n{readme_content}"}
            ],
            temperature=0.5
        )
        summary = gpt_response['choices'][0]['message']['content']
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
