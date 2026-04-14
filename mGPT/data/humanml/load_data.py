import pickle
import numpy as np
import os
import math
from bisect import bisect_left, bisect_right

keys = ['smplx_root_pose', 
        'smplx_body_pose', 
        'smplx_lhand_pose', 
        'smplx_rhand_pose', 
        'smplx_jaw_pose', 
        'smplx_shape', 
        'smplx_expr'
    ]


def load_h2s_sample(ann, data_dir, need_pose=True, code_path=None, need_code=False):
    name = ann['name']
    if 'split' in ann:
        split = ann['split']
        base_dir = os.path.join(data_dir, split, 'poses', name)
    else:
        base_dir = os.path.join(data_dir, name)
    fps = ann['fps']
    frame_list = [os.path.join(base_dir, name+'_'+str(frame_id)+'_3D.pkl') for frame_id in range(len(os.listdir(base_dir)))]
    if fps > 24:
        frame_list = sample(frame_list, count=int(24*len(frame_list)/fps))
    if len(frame_list) < 4:
        return None, None, None, None
    # frame_list = frame_list[:30]
    clip_poses = np.zeros([len(frame_list), 179])
    clip_text = ann['text']  #csv[csv['SENTENCE_NAME']==basename]['SENTENCE'].item()

    if need_pose:
        for frame_id, frame in enumerate(frame_list):
            with open(frame, 'rb') as f: 
                poses = pickle.load(f)

            pose = np.concatenate([poses[key] for key in keys], 0)
            # pose = np.concatenate([pose, np.array([frame_id])],0) # Add frame_id as temporal encoding
            clip_poses[frame_id] = pose
            # if frame_id > 0:
            #     clip_poses[frame_id] = clip_poses[0]
            
        #smplx_root_pose (3,)     # 1  Joint
        #smplx_body_pose (63,)    # 21 Joints
        #smplx_lhand_pose (45,)   # 15 Joints
        #smplx_rhand_pose (45,)   # 15 Joints
        #smplx_jaw_pose (3,)      # 1  Joint
        #smplx_shape (10,)        
        #smplx_expr (10,)
        # clip_poses[:,:111] = 0
        # mean = np.mean(clip_poses, axis=0)
        # std = np.std(clip_poses, axis=0)

        # TODO: Completely detele those poses 
        # clip_poses[:, 3: (3 +3*12)] = 0. 
        # clip_poses = np.concatenate((clip_poses[:,:3], clip_poses[:,(3+3*12):]), axis=1)
        # remove lower body joints
        clip_poses = clip_poses[:,(3+3*11):]
        # remove shape
        clip_poses = np.concatenate([clip_poses[:, :-20], clip_poses[:, -10:]], axis=1) #179-36-10=133
    
    code = None
    if need_code:
        try:
            fname = os.path.join(code_path, 'how2sign', f'{name}.npy')
            code = np.load(fname)[0]
        except:
            fname = os.path.join(code_path, f'{name}.npy')
            code = np.load(fname)[0]

    return clip_poses, clip_text, name, code


def load_csl_sample(ann, data_dir, need_pose=True, code_path=None, need_code=False):
    clip_text = ann['text']
    name = ann['name']
    frame_list = sorted(os.listdir(os.path.join(data_dir, 'poses', name)))
    if len(frame_list) < 4:
        return None, None, None, None

    clip_poses = np.zeros([len(frame_list), 179])
    if need_pose:
        for frame_id, frame in enumerate(frame_list):
            frame = os.path.join(data_dir, 'poses', name, frame)
            with open(frame, 'rb') as f: 
                poses = pickle.load(f)

            pose = np.concatenate([poses[key] for key in keys], 0)
            clip_poses[frame_id] = pose

        clip_poses = clip_poses[:,(3+3*11):]
        # remove shape
        clip_poses = np.concatenate([clip_poses[:, :-20], clip_poses[:, -10:]], axis=1) #179-36-10=133

    code = None
    if need_code:
        try:
            fname = os.path.join(code_path, 'csl', f'{name}.npy')
            code = np.load(fname)[0]
        except:
            fname = os.path.join(code_path, f'{name}.npy')
            code = np.load(fname)[0]

    return clip_poses, clip_text, name, code


def load_iso_sample(ann, data_dir, need_pose=True, code_path=None, need_code=False, dataset=None):
    clip_text = ann['label']
    name = ann['name']
    start, end = ann['start'], ann['end']
    video_file = ann['video_file']
    if dataset in ['csl_iso', 'how2sign_iso']:
        frame_list = sorted(os.listdir(os.path.join(data_dir, 'poses', video_file)))
        frame_idx = [int(x.split('.pkl')[0]) for x in frame_list]
    elif dataset == 'phoenix_iso':
        frame_list = sorted(os.listdir(os.path.join(data_dir, video_file)))
        frame_idx = [int(x.split('.pkl')[0].replace('images', '')) for x in frame_list]
    if len(frame_list) < 4:
        return None, None, None, None
    
    start_idx = bisect_left(frame_idx, start)
    end_idx = bisect_right(frame_idx, end)
    frame_list = frame_list[start_idx:end_idx]
    ratio = len(frame_list) / (end-start)
    if ratio < 0.5:
        return None, None, None, None

    clip_poses = np.zeros([len(frame_list), 179])
    if need_pose:
        for frame_id, frame in enumerate(frame_list):
            if dataset == ['csl_iso', 'how2sign_iso']:
                frame = os.path.join(data_dir, 'poses', video_file, frame)
            elif dataset in ['phoenix_iso']:
                frame = os.path.join(data_dir, video_file, frame)
            with open(frame, 'rb') as f: 
                poses = pickle.load(f)

            pose = np.concatenate([poses[key] for key in keys], 0)
            clip_poses[frame_id] = pose

        clip_poses = clip_poses[:,(3+3*11):]
        # remove shape
        clip_poses = np.concatenate([clip_poses[:, :-20], clip_poses[:, -10:]], axis=1) #179-36-10=133

    code = None
    if need_code:
        try:
            if dataset == 'csl_iso':
                fname = os.path.join(code_path, 'csl', f'{name}.npy')
            elif dataset == 'phoenix_iso':
                fname = os.path.join(code_path, 'phoenix', f'{name}.npy')
            elif dataset == 'how2sign_iso':
                fname = os.path.join(code_path, 'how2sign', f'{name}.npy')
            code = np.load(fname)[0]
        except:
            fname = os.path.join(code_path, f'{name}.npy')
            code = np.load(fname)[0]

    return clip_poses, clip_text, name, code


def load_phoenix_sample(ann, data_dir, need_pose=True, code_path=None, need_code=False):
    clip_text = ann['text']
    name = ann['name']
    frame_list = sorted(os.listdir(os.path.join(data_dir, name)))
    if len(frame_list) < 4:
        return None, None, None, None

    clip_poses = np.zeros([len(frame_list), 179])
    if need_pose:
        for frame_id, frame in enumerate(frame_list):
            frame = os.path.join(data_dir, name, frame)
            with open(frame, 'rb') as f: 
                poses = pickle.load(f)

            pose = np.concatenate([poses[key] for key in keys], 0)
            clip_poses[frame_id] = pose

        clip_poses = clip_poses[:,(3+3*11):]
        # remove shape
        clip_poses = np.concatenate([clip_poses[:, :-20], clip_poses[:, -10:]], axis=1) #179-36-10=133

    code = None
    if need_code:
        try:
            fname = os.path.join(code_path, 'phoenix', f'{name}.npy')
            code = np.load(fname)[0]
        except:
            fname = os.path.join(code_path, f'{name}.npy')
            code = np.load(fname)[0]

    return clip_poses, clip_text, name, code


# Keys in Isharah opt pkl files (axis-angle, need flattening to match 179-dim layout)
isharah_opt_keys = [
    'global_orient',   # (1,3)  -> (3,)   smplx_root_pose
    'body_pose',       # (21,3) -> (63,)  smplx_body_pose
    'left_hand_pose',  # (15,3) -> (45,)  smplx_lhand_pose
    'right_hand_pose', # (15,3) -> (45,)  smplx_rhand_pose
    'jaw_pose',        # (1,3)  -> (3,)   smplx_jaw_pose
    'betas',           # (1,10) -> (10,)  smplx_shape
    'expression',      # (1,10) -> (10,)  smplx_expr
]


def load_isharah_sample(ann, data_dir, need_pose=True, code_path=None, need_code=False):
    """Load a sample from the Isharah-500 dataset.

    Expected directory layout (data_dir = poses/SI):
        data_dir/{split}/{name}/opt/frame_{frame_id:06d}_0.pkl

    Ann dict must contain: 'name', 'text', 'split'.
    """
    clip_text = ann['text']
    name = ann['name']
    split = ann['split']
    opt_dir = os.path.join(data_dir, split, name, 'opt')
    if not os.path.isdir(opt_dir):
        return None, None, None, None

    # Only keep per-person-0 frames (suffix _0.pkl) and sort by frame index
    all_files = sorted(f for f in os.listdir(opt_dir) if f.endswith('_0.pkl'))
    frame_list = [os.path.join(opt_dir, f) for f in all_files]
    if len(frame_list) < 4:
        return None, None, None, None

    clip_poses = np.zeros([len(frame_list), 179])
    if need_pose:
        try:
            for frame_id, frame_path in enumerate(frame_list):
                with open(frame_path, 'rb') as f:
                    poses = pickle.load(f)
                pose = np.concatenate([np.array(poses[k]).flatten() for k in isharah_opt_keys], axis=0)
                clip_poses[frame_id] = pose
        except Exception:
            return None, None, None, None

        # Remove lower-body joints (same masking as other datasets)
        clip_poses = clip_poses[:, (3 + 3 * 11):]
        # Remove shape params, keep expression  → 133-dim
        clip_poses = np.concatenate([clip_poses[:, :-20], clip_poses[:, -10:]], axis=1)

    code = None
    if need_code:
        try:
            fname = os.path.join(code_path, 'isharah', f'{name}.npy')
            code = np.load(fname)[0]
        except Exception:
            fname = os.path.join(code_path, f'{name}.npy')
            code = np.load(fname)[0]

    return clip_poses, clip_text, name, code


def sample(input,count):
    ss=float(len(input))/count
    return [ input[int(math.floor(i*ss))] for i in range(count) ]


