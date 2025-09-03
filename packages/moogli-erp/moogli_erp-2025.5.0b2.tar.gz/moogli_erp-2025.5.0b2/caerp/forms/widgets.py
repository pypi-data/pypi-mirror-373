import deform


class CleanMappingWidget(deform.widget.MappingWidget):
    template = "clean_mapping.pt"


class DateRangeMappingWidget(deform.widget.MappingWidget):
    template = "daterange_mapping.pt"


class CleanSequenceWidget(deform.widget.SequenceWidget):
    template = "clean_sequence.pt"


class FixedLenSequenceWidget(deform.widget.SequenceWidget):
    template = "fixed_len_sequence.pt"
    item_template = "fixed_len_sequence_item.pt"
