# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the backend folder with:
```
GROQ_API_KEY=your_groq_api_key_here
```

**Get your Groq API key:** https://console.groq.com/

### 3. Run the Server
```powershell
python main.py
```

The API will start at: `http://localhost:8080`

### 4. Test in Browser
Open: http://localhost:8080/docs

### 5. Test with Postman
See `POSTMAN_EXAMPLES.md` for detailed instructions.

## 📝 Quick Test

**Endpoint:** POST `http://localhost:8080/mealplan`

**Body:**
```json
{
  "input_text": "I am a 25-year-old male, 70kg, 175cm, moderately active, want to lose weight. Prefer Kerala cuisine."
}
```

## 🔗 Next Steps
- Read `README.md` for full documentation
- Check `GITHUB_SETUP.md` to push to GitHub
- See `POSTMAN_EXAMPLES.md` for Postman testing

