from fild_ui import folder


def test_file_name():
    assert folder.generate_file_name(extension='.csv').endswith('.csv')
