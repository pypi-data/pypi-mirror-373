import argparse
from .adalina_model_type import AdalinaModelType

class AdalinaAlgorithmOptions:

    def __init__(self):

        self.basedir = ""
        self.outdir = ""
        self.fileprefix = ""
        self.modeltype_str = None
        self.export_LPfile = False
        self.timelimit = 60
        self.run_hierarchical = False
        self.modeltype = None
        self.log_fout = None
        self.run_parametric_analysis = False

    @classmethod
    def from_argparse(cls, options : argparse.Namespace):

        obj = cls()

        obj.basedir = options.basedir
        obj.outdir = options.outdir
        obj.fileprefix = options.fileprefix

        if hasattr(options, "modeltype_str"):
            obj.modeltype_str = options.modeltype_str

        if hasattr(options, "export_LPfile"):
            obj.export_LPfile = options.export_LPfile

        if hasattr(options, "timelimit"):
            obj.timelimit = options.timelimit

        if obj.modeltype_str is not None:
            if "HIERARCHICAL" not in obj.modeltype_str :
                obj.modeltype = AdalinaModelType.from_label(obj.modeltype_str)
            else:
                obj.run_hierarchical = True
                if "_PA" in obj.modeltype_str:
                    obj.run_parametric_analysis = True
                obj.modeltype = AdalinaModelType.MINSUM_UNSERVED
        else:
            obj.run_hierarchical = True
            obj.modeltype = AdalinaModelType.MINSUM_UNSERVED

        return obj

    def change_model_type(self, newmodeltype):
        assert isinstance(newmodeltype, AdalinaModelType)
        self.modeltype = newmodeltype
        self.modeltype_str = newmodeltype.get_label()
