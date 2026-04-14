"""
SOKEInference — lean inference engine.

Loads VQ-VAEs + mBART + SMPL-X directly. No Lightning, no metrics, no losses.
"""

import io
import os
import pickle
import torch
from deploy.image import VOL_MOUNT

SHAPE_PARAM = [-0.0728, 0.1795, -0.2761, 0.1352, 0.1075, 0.1604, -0.0162, -0.0345, 0.0137, 0.0111]

ABLATION = {
    "use_length": False, "predict_ratio": 0.2, "inbetween_ratio": 0.25,
    "image_size": 256, "VAE_TYPE": "actor", "VAE_ARCH": "encoder_decoder",
    "PE_TYPE": "actor", "DIFF_PE_TYPE": "actor", "SKIP_CONNECT": False,
    "MLP_DIST": False, "IS_DIST": False, "PREDICT_EPSILON": True,
}


class _SafeUnpickler(pickle.Unpickler):
    """Unpickler that stubs out missing modules (training-only deps like pandas, spacy)."""

    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except (ModuleNotFoundError, AttributeError):
            return type(name, (), {})


def _safe_torch_load(path):
    """Load a PyTorch checkpoint without requiring training-only dependencies."""
    with open(path, "rb") as f:
        buf = io.BytesIO(f.read())
    ckpt = torch.load(buf, map_location="cpu", pickle_module=_SafePickle)
    return ckpt.get("state_dict", ckpt)


class _SafePickle:
    """Drop-in pickle module replacement for torch.load that stubs missing classes."""
    Unpickler = _SafeUnpickler
    load = staticmethod(pickle.load)
    dumps = staticmethod(pickle.dumps)
    loads = staticmethod(pickle.loads)
    dump = staticmethod(pickle.dump)
    PicklingError = pickle.PicklingError
    UnpicklingError = pickle.UnpicklingError


def _load_mean_std(device):
    """Load and filter mean/std tensors (same logic as H2SDataModule)."""
    mean = torch.load(f"{VOL_MOUNT}/deps/mean.pt", map_location="cpu")
    std = torch.load(f"{VOL_MOUNT}/deps/std.pt", map_location="cpu")
    # Strip lower-body dims, collapse expression 20->10
    mean = mean[(3 + 3 * 11):]
    mean = torch.cat([mean[:-20], mean[-10:]], dim=0)
    std = std[(3 + 3 * 11):]
    std = torch.cat([std[:-20], std[-10:]], dim=0)
    return mean.to(device), std.to(device)


def _load_component(module, state_dicts, prefix):
    """Extract keys with given prefix from state dicts and load into module."""
    sd = {}
    for source in state_dicts:
        for k, v in source.items():
            if k.startswith(prefix):
                sd[k[len(prefix):]] = v
    missing, unexpected = module.load_state_dict(sd, strict=False)
    if missing:
        print(f"  {prefix} missing {len(missing)} keys (first 3: {missing[:3]})")


class SOKEInference:
    def __init__(self, device="cuda"):
        from mGPT.archs.mgpt_vq import VQVae
        from mGPT.archs.mgpt_mbart import Mbart_Based_MLM

        self.device = torch.device(device)
        self.mean, self.std = _load_mean_std(self.device)
        self.shape_param = torch.tensor([SHAPE_PARAM], device=self.device)

        # VQ-VAEs
        print("Loading VQ-VAEs...")
        body_kw = dict(quantizer='ema_reset', code_num=96, code_dim=512,
                       output_emb_width=512, down_t=2, stride_t=2, width=512,
                       depth=3, dilation_growth_rate=3, norm=None,
                       activation='relu', nfeats=43, ablation=ABLATION)
        hand_kw = {**body_kw, "code_num": 192, "nfeats": 45}

        self.body_vae = VQVae(**body_kw)
        self.lhand_vae = VQVae(**hand_kw)
        self.rhand_vae = VQVae(**hand_kw)

        # mBART LM
        print("Loading mBART LM...")
        self.lm = Mbart_Based_MLM(
            model_path=f"{VOL_MOUNT}/deps/mbart-h2s-csl-phoenix-isharah",
            model_type="mbart_multi",
            stage="lm_pretrain",
            motion_codebook_size=96,
            hand_codebook_size=192,
            rhand_codebook_size=192,
            num_heads=3,
        )

        # Load weights (safe loader stubs out training-only modules)
        print("Loading checkpoints...")
        soke_sd = _safe_torch_load(f"{VOL_MOUNT}/experiments/mgpt/SOKE/checkpoints/last.ckpt")
        deto_sd = _safe_torch_load(f"{VOL_MOUNT}/experiments/mgpt/DETO/checkpoints/last-v3.ckpt")
        sources = [soke_sd, deto_sd]

        _load_component(self.body_vae, sources, "vae.")
        _load_component(self.lhand_vae, sources, "hand_vae.")
        _load_component(self.rhand_vae, sources, "rhand_vae.")
        _load_component(self.lm, sources, "lm.")

        for m in [self.body_vae, self.lhand_vae, self.rhand_vae, self.lm]:
            m.eval().to(self.device)

        # SMPL-X (loaded lazily on first generate call)
        self._smplx_layer = None
        print("Ready.")

    def _ensure_smplx(self):
        if self._smplx_layer is not None:
            return
        import smplx
        self._smplx_layer = smplx.create(
            os.path.join(VOL_MOUNT, "deps", "smpl_models"),
            "smplx", gender="NEUTRAL", use_pca=False, use_face_contour=True,
            create_global_orient=False, create_body_pose=False,
            create_left_hand_pose=False, create_right_hand_pose=False,
            create_jaw_pose=False, create_leye_pose=False,
            create_reye_pose=False, create_betas=False,
            create_expression=False, create_transl=False,
        ).to(self.device)
        print("SMPL-X loaded.")

    @torch.no_grad()
    def generate(self, text: str, lang_token: str = "isharah"):
        """
        Returns (vertices, joints, num_frames).
        vertices: (T, 10475, 3)  joints: (T, N, 3)
        """
        # 1) Text -> motion tokens
        out = self.lm.generate_direct(
            [text], do_sample=True, src=[lang_token], name=[None], max_length=100,
        )
        body_tok = torch.clamp(out["outputs_tokens"][0], 0, self.body_vae.code_num - 1)
        lh_tok = out.get("outputs_tokens_hand", [None])[0]
        rh_tok = out.get("outputs_tokens_rhand", [None])[0]

        # 2) Decode tokens -> motion features
        m_body = self.body_vae.decode(body_tok)
        T = m_body.shape[1]

        if lh_tok is not None and len(lh_tok) > 1:
            lh_tok = torch.clamp(lh_tok, 0, self.lhand_vae.code_num - 1)
            m_lh = self.lhand_vae.decode(lh_tok)
        else:
            m_lh = torch.zeros(1, T, 45, device=self.device)

        if rh_tok is not None and len(rh_tok) > 1:
            rh_tok = torch.clamp(rh_tok, 0, self.rhand_vae.code_num - 1)
            m_rh = self.rhand_vae.decode(rh_tok)
        else:
            m_rh = torch.zeros(1, T, 45, device=self.device)

        T = min(m_body.shape[1], m_lh.shape[1], m_rh.shape[1])
        feats = torch.cat([
            m_body[:, :T, :30], m_lh[:, :T], m_rh[:, :T], m_body[:, :T, 30:43],
        ], dim=-1).squeeze(0)  # (T, 133)

        # 3) Denormalize
        feats = feats * self.std + self.mean

        # 4) Unpack SMPL-X params
        zeros36 = torch.zeros(T, 36, device=self.device)
        full = torch.cat([zeros36, feats], dim=-1)  # (T, 169)

        shape = self.shape_param.expand(T, -1)
        zero3 = torch.zeros(T, 3, device=self.device)

        # 5) SMPL-X forward
        self._ensure_smplx()
        out = self._smplx_layer(
            betas=shape, global_orient=full[:, 0:3], body_pose=full[:, 3:66],
            left_hand_pose=full[:, 66:111], right_hand_pose=full[:, 111:156],
            jaw_pose=full[:, 156:159], leye_pose=zero3, reye_pose=zero3,
            expression=full[:, 159:169],
        )
        return out.vertices, out.joints, T
