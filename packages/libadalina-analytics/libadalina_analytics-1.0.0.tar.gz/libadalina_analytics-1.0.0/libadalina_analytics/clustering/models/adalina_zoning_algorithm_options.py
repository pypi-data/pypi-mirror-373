import argparse

class AdalinaZoningAlgorithmOptions:

    def __init__(self):

        self.basedir = ""
        self.outdir = ""
        self.fileprefix = ""
        self.modeltype_str = ""
        self.export_LPfile = ""
        self.timelimit = ""
        self.log_fout = None

    @classmethod
    def from_argparse(cls,
                      options : argparse.Namespace):

        obj = cls()

        obj.basedir = options.basedir
        obj.outdir = options.outdir
        obj.fileprefix = options.fileprefix

        obj.modeltype_str = None
        if hasattr(options, "modeltype_str"):
            obj.modeltype_str = options.modeltype_str

        obj.export_LPfile = False
        if hasattr(options, "export_LPfile"):
            obj.export_LPfile = options.export_LPfile

        obj.timelimit = 60
        if hasattr(options, "timelimit"):
            obj.timelimit = options.timelimit

        return obj