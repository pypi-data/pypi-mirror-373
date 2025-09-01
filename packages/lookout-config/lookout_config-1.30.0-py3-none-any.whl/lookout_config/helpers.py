import yaml


class YamlDumper(yaml.Dumper):
    """
    A YAML dumpler that show lists on the same line if they do not contain dicts or list
    """

    def represent_sequence(self, tag, sequence, flow_style=None):
        if isinstance(sequence, list) and all(
            [not isinstance(item, (dict, list)) for item in sequence]
        ):
            flow_style = True
        return super().represent_sequence(tag, sequence, flow_style)

    def represent_mapping(self, tag, mapping, flow_style=None):
        flow_style = False
        return super().represent_mapping(tag, mapping, flow_style)
