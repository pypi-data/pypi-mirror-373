import pytest
from unittest.mock import MagicMock, patch, mock_open, call
from ara_cli.file_classifier import FileClassifier
from ara_cli.classifier import Classifier
from ara_cli.artefact_models.artefact_load import artefact_from_content
from ara_cli.artefact_models.artefact_load import artefact_from_content


@pytest.fixture
def mock_file_system():
    return MagicMock()


@pytest.fixture
def mock_error_handler():
    with patch('ara_cli.file_classifier.error_handler') as mock_handler:
        yield mock_handler


@pytest.fixture
def mock_classifier():
    with patch.object(Classifier, 'ordered_classifiers', return_value=['py', 'txt', 'bin']):
        yield


@pytest.fixture
def mock_get_artefact_title():
    with patch.object(Classifier, 'get_artefact_title', side_effect=lambda classifier: f"{classifier.upper()} Title"):
        yield


def test_file_classifier_init(mock_file_system):
    classifier = FileClassifier(mock_file_system)
    assert classifier.file_system == mock_file_system


def test_read_file_content(mock_file_system):
    classifier = FileClassifier(mock_file_system)
    test_file_path = "test_file.txt"
    test_file_content = "This is a test file."

    with patch("builtins.open", mock_open(read_data=test_file_content)) as mock_file:
        content = classifier.read_file_content(test_file_path)
        mock_file.assert_called_once_with(
            test_file_path, 'r', encoding='utf-8')
        mock_file.assert_called_once_with(
            test_file_path, 'r', encoding='utf-8')
        assert content == test_file_content


def test_is_binary_file(mock_file_system):
    classifier = FileClassifier(mock_file_system)
    test_binary_file_path = "test_binary_file.bin"
    test_text_file_path = "test_text_file.txt"
    binary_content = b'\x00\x01\x02\x03\x04\x80\x81\x82\x83'
    text_content = "This is a text file."

    with patch("builtins.open", mock_open(read_data=binary_content)) as mock_file:
        result = classifier.is_binary_file(test_binary_file_path)
        mock_file.assert_called_once_with(test_binary_file_path, 'rb')
        assert result is True

    with patch("builtins.open", mock_open(read_data=text_content.encode('utf-8'))) as mock_file:
        result = classifier.is_binary_file(test_text_file_path)
        mock_file.assert_called_once_with(test_text_file_path, 'rb')
        assert result is False

    with patch("builtins.open", side_effect=Exception("Unexpected error")):
        result = classifier.is_binary_file(test_binary_file_path)
        assert result is False


def test_is_binary_file_handles_error(mock_file_system, mock_error_handler):
    classifier = FileClassifier(mock_file_system)
    test_binary_file_path = "test_binary_file.bin"

    # Simulate an exception being raised when attempting to open the file
    with patch("builtins.open", side_effect=Exception("Unexpected error")):
        result = classifier.is_binary_file(test_binary_file_path)
        assert result is False

    # Check that the error handler's report_error method was called
    mock_error_handler.report_error.assert_called_once()
    # You can also verify the specific arguments if needed
    args, kwargs = mock_error_handler.report_error.call_args
    assert "Unexpected error" in str(args[0])
    assert "checking if file is binary" in args[1]


def test_read_file_with_fallback(mock_file_system):
    classifier = FileClassifier(mock_file_system)
    test_file_path = "test_file.txt"
    utf8_content = 'This is a test file.'
    latin1_content = 'This is a test file with latin1 encoding.'

    with patch("builtins.open", mock_open(read_data=utf8_content)) as mock_file:
        content = classifier.read_file_with_fallback(test_file_path)
        mock_file.assert_called_once_with(
            test_file_path, 'r', encoding='utf-8')
        mock_file.assert_called_once_with(
            test_file_path, 'r', encoding='utf-8')
        assert content == utf8_content

    with patch("builtins.open", mock_open(read_data=utf8_content)) as mock_file:
        mock_file.side_effect = [UnicodeDecodeError(
            "mock", b"", 0, 1, "reason"), mock_open(read_data=latin1_content).return_value]
        mock_file.side_effect = [UnicodeDecodeError(
            "mock", b"", 0, 1, "reason"), mock_open(read_data=latin1_content).return_value]
        content = classifier.read_file_with_fallback(test_file_path)
        assert content == latin1_content

    with patch("builtins.open", mock_open(read_data=utf8_content)) as mock_file:
        mock_file.side_effect = [UnicodeDecodeError(
            "mock", b"", 0, 1, "reason"), UnicodeDecodeError("mock", b"", 0, 1, "reason")]
        mock_file.side_effect = [UnicodeDecodeError(
            "mock", b"", 0, 1, "reason"), UnicodeDecodeError("mock", b"", 0, 1, "reason")]
        content = classifier.read_file_with_fallback(test_file_path)
        assert content is None


def test_file_contains_tags(mock_file_system):
    classifier = FileClassifier(mock_file_system)
    test_file_path = "test_file.txt"
    file_content = "tag1 tag2 tag3"

    with patch.object(classifier, 'read_file_with_fallback', return_value=file_content):
        result = classifier.file_contains_tags(
            test_file_path, ['tag1', 'tag2'])
        result = classifier.file_contains_tags(
            test_file_path, ['tag1', 'tag2'])
        assert result is True

        result = classifier.file_contains_tags(
            test_file_path, ['tag1', 'tag4'])
        result = classifier.file_contains_tags(
            test_file_path, ['tag1', 'tag4'])
        assert result is False

        with patch.object(classifier, 'read_file_with_fallback', return_value=None):
            result = classifier.file_contains_tags(
                test_file_path, ['tag1', 'tag2'])
            result = classifier.file_contains_tags(
                test_file_path, ['tag1', 'tag2'])
            assert result is False


def test_classify_file(mock_file_system, mock_classifier):
    classifier = FileClassifier(mock_file_system)
    test_file_path = "test_file.py"

    with patch.object(classifier, 'is_binary_file', return_value=False), \
            patch.object(classifier, 'file_contains_tags', return_value=True):
        result = classifier.classify_file(test_file_path, tags=['tag1'])
        assert result == 'py'

    with patch.object(classifier, 'is_binary_file', return_value=True):
        result = classifier.classify_file(test_file_path, tags=['tag1'])
        assert result is None

    with patch.object(classifier, 'file_contains_tags', return_value=False):
        result = classifier.classify_file(test_file_path, tags=['tag1'])
        assert result is None


def test_classify_files_skips_binary_files(mock_file_system, mock_classifier):
    mock_file_system.walk.return_value = [
        ('.', [], ['file1.py', 'file2.txt', 'file3.bin'])]
    mock_file_system.walk.return_value = [
        ('.', [], ['file1.py', 'file2.txt', 'file3.bin'])]
    mock_file_system.path.join.side_effect = lambda root, file: f"{root}/{file}"

    classifier = FileClassifier(mock_file_system)

    with patch.object(classifier, 'is_binary_file', return_value=True):
        result = classifier.classify_files(tags=['tag1', 'tag2'])

    expected = {
        'py': [],
        'txt': [],
        'bin': []
    }
    assert result == expected


def test_classify_file_no_match(mock_file_system, mock_classifier):
    classifier = FileClassifier(mock_file_system)
    test_file_path = "test_file.unknown"

    with patch.object(classifier, 'is_binary_file', return_value=False), \
            patch.object(classifier, 'file_contains_tags', return_value=True):
        result = classifier.classify_file(test_file_path, tags=['tag1'])
        assert result is None


@pytest.mark.parametrize("walk_return_value, classify_file_side_effect, expected_result", [
    (
        [('.', [], ['file1.py', 'file2.txt', 'file3.bin'])],
        ['py', 'txt', 'bin'],
        {'py': [{'file_path': './file1.py', 'title': 'file1'}], 'txt': [{'file_path': './file2.txt', 'title': 'file2'}], 'bin': [{'file_path': './file3.bin', 'title': 'file3'}]}
    ),
    (
        [('.', [], [])],
        [],
        {'py': [], 'txt': [], 'bin': []}
    ),
    (
        [('.', [], ['file1.py', 'file2.unknown'])],
        ['py', None],
        {'py': [{'file_path': './file1.py', 'title': 'file1'}], 'txt': [], 'bin': []}
    ),
    (
        [('.', [], ['file1.py', 'file2.txt', 'file3.unknown', 'file4.bin'])],
        ['py', 'txt', None, 'bin'],
        {'py': [{'file_path': './file1.py', 'title': 'file1'}], 'txt': [{'file_path': './file2.txt', 'title': 'file2'}], 'bin': [{'file_path': './file4.bin', 'title': 'file4'}]}
    ),
])
def test_classify_files(mock_file_system, mock_classifier, walk_return_value, classify_file_side_effect, expected_result):
    mock_file_system.walk.return_value = walk_return_value
    mock_file_system.path.join.side_effect = lambda root, file: f"{root}/{file}"

    classifier = FileClassifier(mock_file_system)

    with patch.object(classifier, 'classify_file', side_effect=classify_file_side_effect):
        result = classifier.classify_files()

    assert result == expected_result


@pytest.mark.parametrize("files_by_classifier, expected_output", [
    (
        {'py': [MagicMock(file_path='file1.py')], 'txt': [], 'bin': []},
        "PY Title files:\n  - ./file1.py\n\n"
    ),
    (
        {'txt': [MagicMock(file_path='file2.txt')], 'py': [], 'bin': []},
        "TXT Title files:\n  - ./file2.txt\n\n"
    ),
    (
        {'bin': [MagicMock(file_path='file3.bin')], 'py': [], 'txt': []},
        "BIN Title files:\n  - ./file3.bin\n\n"
    ),
    (
        {'py': [MagicMock(file_path='file1.py')], 'txt': [
            MagicMock(file_path='file2.txt')], 'bin': []},
        "PY Title files:\n  - ./file1.py\n\nTXT Title files:\n  - ./file2.txt\n\n"
    ),
])
def test_print_classified_files(mock_file_system, mock_classifier, mock_get_artefact_title, files_by_classifier, expected_output, capsys):
    classifier = FileClassifier(mock_file_system)
    classifier.print_classified_files(files_by_classifier)
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_find_closest_artefact_name_match(mock_file_system):
    classifier = FileClassifier(mock_file_system)
    classifier.classify_files = MagicMock(return_value={
        'py': [{'title': 'file1'}, {'title': 'file2'}],
        'txt': []
    })

    # Exact match
    assert classifier.find_closest_artefact_name_match(
        'file1', 'py') == 'file1'

    # Fuzzy match
    with patch('ara_cli.file_classifier.find_closest_name_matches', return_value='file2') as mock_fuzzy:
        assert classifier.find_closest_artefact_name_match(
            'file3', 'py') == 'file2'
        mock_fuzzy.assert_called_once_with('file3', ['file1', 'file2'])

    # No match for classifier
    assert classifier.find_closest_artefact_name_match('file1', 'txt') is None


@pytest.mark.parametrize("walk_return_value, expected_result", [
    (
        [('.', ['subdir'], ['file1.py']), ('subdir.data', [], ['file_in_data.txt'])],
        {'py': [{'file_path': './file1.py', 'title': 'file1'}], 'txt': [], 'bin': []}
    ),
    (
        [('.', ['subdir'], ['file1.py']), ('subdir', [], ['file2.txt'])],
        {'py': [{'file_path': './file1.py', 'title': 'file1'}], 'txt': [{'file_path': 'subdir/file2.txt', 'title': 'file2'}], 'bin': []}
    )
])
def test_classify_files_skips_data_directories(mock_file_system, mock_classifier, walk_return_value, expected_result):
    mock_file_system.walk.return_value = walk_return_value
    mock_file_system.path.join.side_effect = lambda root, file: f"{root}/{file}"

    classifier = FileClassifier(mock_file_system)

    result = classifier.classify_files()

    assert result == expected_result
