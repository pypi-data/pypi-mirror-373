from enum import Enum


class AdalinaModelType(Enum):

    MINSUM_ALLCOST = 0
    MIN_EXTRARESOURCES = 1
    MINSUM_UNSERVED = 2
    MINMAX_UNSERVED = 3
    MINMAX_USAGEFAC = 4
    MINDIST_ASSIGNMENTS = 5
    MINSUM_USAGEFAC = 6
    MINSUM_RELOCATION = 7
    MAXSUM_DIST_UNSERVED = 8

    @staticmethod
    def get_all_labels(get_str = True):
        _label_dict = {
            "ALLCOSTS": AdalinaModelType.MINSUM_ALLCOST,
            "MIN_EXTRARESOURCES": AdalinaModelType.MIN_EXTRARESOURCES,
            "UNSERVED": AdalinaModelType.MINSUM_UNSERVED,
            "UNSERVED_MINMAX": AdalinaModelType.MINMAX_UNSERVED,
            "USAGEFAC_MINMAX": AdalinaModelType.MINMAX_USAGEFAC,
            "MINDIST_ASSIGNMENTS" : AdalinaModelType.MINDIST_ASSIGNMENTS,
            "MINSUM_USAGEFAC" : AdalinaModelType.MINSUM_USAGEFAC,
            "MINSUM_RELOCATION" : AdalinaModelType.MINSUM_RELOCATION,
            "MAXSUM_DIST_UNSERVED" : AdalinaModelType.MAXSUM_DIST_UNSERVED
        }
        if get_str:
            return ', '.join(list(_label_dict.keys()))
        else:
            return _label_dict

    def __str__(self):
        if self == AdalinaModelType.MINSUM_ALLCOST:
            return 'sumcosts'
        elif self == AdalinaModelType.MIN_EXTRARESOURCES:
            return 'misum extra resources'
        elif self == AdalinaModelType.MINSUM_UNSERVED:
            return 'count unserved'
        elif self == AdalinaModelType.MINMAX_UNSERVED:
            return 'minmax unserved'
        elif self == AdalinaModelType.MINMAX_USAGEFAC:
            return 'minmax usage facility'
        elif self == AdalinaModelType.MINDIST_ASSIGNMENTS:
            return 'minsum distance assignments'
        elif self == AdalinaModelType.MINSUM_USAGEFAC:
            return 'minsum usage facility'
        elif self == AdalinaModelType.MINSUM_RELOCATION:
            return 'minsum relocation costs'
        elif self == AdalinaModelType.MAXSUM_DIST_UNSERVED:
            return 'max sum dist unserved'

        return ''

    def get_label(self):

        _label_dict = AdalinaModelType.get_all_labels(False)

        for k, v in _label_dict.items():
            if v == self:
                return k

        return ""

    @staticmethod
    def from_label(lab):

        _label_dict = AdalinaModelType.get_all_labels(False)
        if lab in _label_dict.keys():
            return _label_dict[lab]

        raise ValueError(f"{lab} not recognized as AdalinaModelType!")
