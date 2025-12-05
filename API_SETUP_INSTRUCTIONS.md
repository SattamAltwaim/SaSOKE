# API Setup Instructions

This guide explains how to set up the Flask API in Colab notebook 8 and use the standalone frontend.

## Part 1: Setting up the API in Colab Notebook 8

### Step 1: Install Additional Dependencies

In the notebook cell where dependencies are installed, add `flask` and `flask-cors`:

```python
!pip install -q flask flask-cors
```

### Step 2: Add API Functions

After the model is loaded, add a new cell with the code from `notebooks/api_cell_addition.py`. This includes:

- `feats_to_smplx_dict()` - Converts features to SMPL-X parameters dictionary
- `smplx_params_to_glb_frames()` - Converts SMPL-X parameters to GLB frames
- `generate_smplx_params()` - Generates SMPL-X parameters from text
- Flask API endpoints

### Step 3: API Endpoints

The API provides two endpoints:

1. **POST `/api/generate`**
   - Input: `{'text': 'Hello world', 'lang_token': 'how2sign'}`
   - Output: `{'success': True, 'glb_frames': [...], 'num_frames': N, 'text': '...', 'lang_token': '...'}`
   - Returns base64-encoded GLB frames ready for display

2. **GET `/api/health`**
   - Health check endpoint
   - Returns: `{'status': 'ok', 'message': 'API is running'}`

### Step 4: Get the API URL

When you run the Flask API cell, it will print:
- The API URL (e.g., `http://localhost:5000/api/generate`)
- Health check URL

**Important**: In Colab, you'll need to use `ngrok` or Colab's built-in port forwarding to expose the API publicly. The frontend needs to access it.

## Part 2: Using the Standalone Frontend

### Step 1: Update API URL

Open `apple_viewer_frontend.html` and update the `API_URL` constant:

```javascript
const API_URL = 'http://your-colab-url/api/generate';
```

If using ngrok:
```javascript
const API_URL = 'https://your-ngrok-url.ngrok.io/api/generate';
```

### Step 2: Open the Frontend

Simply open `apple_viewer_frontend.html` in your web browser. No server needed - it's a standalone HTML file.

### Step 3: Use the Interface

1. Enter text in the text field
2. Select a language (ASL, CSL, or DGS)
3. Click the circular white button with arrow-up icon
4. Wait for the animation to generate
5. Use the Play/Pause/Reset controls to control playback

## Features

- ✅ Apple-style glassmorphic UI
- ✅ Text input field
- ✅ Language token selector
- ✅ Circular white upload button with arrow-up icon
- ✅ Real-time 3D animation display
- ✅ Playback controls
- ✅ Frame indicator
- ✅ Error handling

## Troubleshooting

### CORS Issues

If you see CORS errors, make sure:
1. Flask-CORS is installed: `!pip install flask-cors`
2. CORS is enabled: `CORS(app)` in the Flask setup

### API Not Accessible

In Colab, you need to expose the API:
1. Use ngrok: `!pip install pyngrok && ngrok http 5000`
2. Or use Colab's port forwarding features
3. Update the frontend `API_URL` to match

### GLB Frames Not Loading

Check:
1. The API is returning `glb_frames` in the response
2. The frames are base64-encoded GLB data
3. Browser console for any errors

## File Structure

```
SaSOKE/
├── notebooks/
│   ├── 8_gradio_web_ui.ipynb          # Main notebook (add API code here)
│   └── api_cell_addition.py           # Code to add to notebook
├── apple_viewer_frontend.html         # Standalone frontend
└── API_SETUP_INSTRUCTIONS.md          # This file
```
