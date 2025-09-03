from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
)
from snowflake.snowflake_data_validation.utils.constants import Platform


def test_dump_and_write_yaml_template():
    import tempfile
    import os

    temp_dir = tempfile.mkdtemp()

    yaml_content = """key1: value1
key2: value2
"""

    template_path = os.path.join(temp_dir, "template.yaml")
    with open(template_path, "w") as f:
        f.write(yaml_content)

    output_file_path = ArgumentsManagerBase._dump_and_write_yaml_template(
        template_path, temp_dir
    )

    assert os.path.exists(output_file_path)
    with open(output_file_path) as f:
        output_content = f.read()
        assert output_content == yaml_content
