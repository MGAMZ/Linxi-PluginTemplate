from tiansuo.processor import DefaultProcessor, PROCESS_STAGES, register_as_tiansuo_processor


@register_as_tiansuo_processor(stage=PROCESS_STAGES.PREPROCESS)
class ExamplePluginProcessor(DefaultProcessor):
    """Example TianSuo preprocess processor."""

    def _process(self, context):
        return context