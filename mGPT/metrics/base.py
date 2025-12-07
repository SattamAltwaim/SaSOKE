from torch import Tensor, nn
from os.path import join as pjoin
from .mr import MRMetrics
from .t2m import TM2TMetrics
from .mm import MMMetrics
from .m2t import M2TMetrics
from .m2m import PredMetrics


class BaseMetrics(nn.Module):
    def __init__(self, cfg, datamodule, debug, **kwargs) -> None:
        super().__init__()

        njoints = datamodule.njoints
        
        # Check if metrics are enabled in config
        metric_types = cfg.METRIC.get('TYPE', [])

        data_name = datamodule.name
        if data_name in ["humanml3d", "kit"] and len(metric_types) > 0:
            if 'TM2TMetrics' in metric_types:
                self.TM2TMetrics = TM2TMetrics(
                    cfg=cfg,
                    dataname=data_name,
                    diversity_times=30 if debug else cfg.METRIC.DIVERSITY_TIMES,
                    dist_sync_on_step=cfg.METRIC.DIST_SYNC_ON_STEP,
                )
            if 'M2TMetrics' in metric_types:
                self.M2TMetrics = M2TMetrics(
                    cfg=cfg,
                    w_vectorizer=datamodule.hparams.w_vectorizer,
                    diversity_times=30 if debug else cfg.METRIC.DIVERSITY_TIMES,
                    dist_sync_on_step=cfg.METRIC.DIST_SYNC_ON_STEP)
            if 'MMMetrics' in metric_types:
                self.MMMetrics = MMMetrics(
                    cfg=cfg,
                    mm_num_times=cfg.METRIC.MM_NUM_TIMES,
                    dist_sync_on_step=cfg.METRIC.DIST_SYNC_ON_STEP,
                )

        self.MRMetrics = MRMetrics(
            njoints=njoints,
            jointstype=cfg.DATASET.JOINT_TYPE,
            dist_sync_on_step=cfg.METRIC.DIST_SYNC_ON_STEP,
        )
        self.PredMetrics = PredMetrics(
            cfg=cfg,
            njoints=njoints,
            jointstype=cfg.DATASET.JOINT_TYPE,
            dist_sync_on_step=cfg.METRIC.DIST_SYNC_ON_STEP,
            task=cfg.model.params.task,
        )
