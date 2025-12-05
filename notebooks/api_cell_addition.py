# This code should be added to notebook 8 after model loading
# Add this as a new cell after the model is loaded

import numpy as np
import time
import json
import trimesh
import base64
from io import BytesIO

def feats_to_smplx_dict(features, mean_tensor, std_tensor):
    """Convert 133-dim features to SMPL-X parameters dictionary"""
    features = features * std_tensor + mean_tensor
    T = features.shape[0]
    zero_pose = torch.zeros(T, 36).to(features)
    features_full = torch.cat([zero_pose, features], dim=-1)  # (T, 169)
    
    # Extract SMPL-X parameters as dictionary
    smplx_params = {
        'root_pose': features_full[:, 0:3].cpu().numpy().tolist(),
        'body_pose': features_full[:, 3:66].cpu().numpy().tolist(),
        'lhand_pose': features_full[:, 66:111].cpu().numpy().tolist(),
        'rhand_pose': features_full[:, 111:156].cpu().numpy().tolist(),
        'jaw_pose': features_full[:, 156:159].cpu().numpy().tolist(),
        'expression': features_full[:, 159:169].cpu().numpy().tolist(),
    }
    return smplx_params

def smplx_params_to_glb_frames(smplx_params_dict, num_frames):
    """Convert SMPL-X parameters to GLB frames (base64 encoded)"""
    # Create shape parameter
    shape_param = torch.tensor([[-0.07284723, 0.1795129, -0.27608207, 0.135155, 0.10748172,
                                 0.16037364, -0.01616933, -0.03450319, 0.01369138, 0.01108842]],
                               device=mean.device, dtype=torch.float32)
    
    glb_frames = []
    
    for i in range(num_frames):
        # Convert lists back to tensors
        root_pose = torch.tensor([smplx_params_dict['root_pose'][i]], dtype=torch.float32, device=mean.device)
        body_pose = torch.tensor([smplx_params_dict['body_pose'][i]], dtype=torch.float32, device=mean.device)
        lhand_pose = torch.tensor([smplx_params_dict['lhand_pose'][i]], dtype=torch.float32, device=mean.device)
        rhand_pose = torch.tensor([smplx_params_dict['rhand_pose'][i]], dtype=torch.float32, device=mean.device)
        jaw_pose = torch.tensor([smplx_params_dict['jaw_pose'][i]], dtype=torch.float32, device=mean.device)
        expression = torch.tensor([smplx_params_dict['expression'][i]], dtype=torch.float32, device=mean.device)
        
        # Generate mesh
        with torch.no_grad():
            vertices, _ = get_coord(
                root_pose=root_pose,
                body_pose=body_pose,
                lhand_pose=lhand_pose,
                rhand_pose=rhand_pose,
                jaw_pose=jaw_pose,
                shape=shape_param,
                expr=expression
            )
        
        # Create trimesh with WHITE color
        mesh = trimesh.Trimesh(
            vertices=vertices[0].cpu().numpy(),
            faces=smpl_x.face,
            process=False
        )
        mesh.visual.vertex_colors = np.array([[255, 255, 255, 255]] * len(mesh.vertices))
        
        # Export to GLB and encode to base64
        glb_buffer = BytesIO()
        mesh.export(file_obj=glb_buffer, file_type='glb')
        glb_data = base64.b64encode(glb_buffer.getvalue()).decode('utf-8')
        glb_frames.append(glb_data)
    
    return glb_frames

def generate_smplx_params(text, lang_token):
    """Generate SMPL-X parameters from text and language token"""
    if not text.strip():
        return None, "⚠️ Please enter some text"
    
    try:
        batch = {'text': [text], 'length': [0], 'src': [lang_token]}
        
        with torch.no_grad():
            output = model.forward(batch, task="t2m")
        
        feats = output['feats'][0] if 'feats' in output else None
        
        if feats is None:
            return None, "❌ Generation failed - no features produced"
        
        smplx_params = feats_to_smplx_dict(feats, mean, std)
        
        return smplx_params, None
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ Error: {str(e)}"

# Create Flask API
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
import socket

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint that takes lang_token and text, returns GLB frames"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        lang_token = data.get('lang_token', 'how2sign')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Generate SMPL-X parameters
        smplx_params, error = generate_smplx_params(text, lang_token)
        
        if error:
            return jsonify({'error': error}), 500
        
        num_frames = len(smplx_params['body_pose'])
        
        # Convert to GLB frames
        glb_frames = smplx_params_to_glb_frames(smplx_params, num_frames)
        
        # Return GLB frames (base64 encoded)
        return jsonify({
            'success': True,
            'glb_frames': glb_frames,
            'num_frames': num_frames,
            'text': text,
            'lang_token': lang_token
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API is running'})

def get_free_port():
    """Get a free port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

port = get_free_port()

def run_flask():
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

# Wait a moment for Flask to start
time.sleep(2)

print(f"\n✅ Flask API started!")
print(f"📡 API URL: http://localhost:{port}/api/generate")
print(f"💚 Health check: http://localhost:{port}/api/health")
print(f"\n📝 API Usage:")
print(f"  POST /api/generate")
print(f"  Body: {{'text': 'Hello world', 'lang_token': 'how2sign'}}")
print(f"  Response: {{'success': True, 'glb_frames': [...], 'num_frames': N}}")
