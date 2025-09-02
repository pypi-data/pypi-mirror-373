import pytest
from unittest.mock import patch, mock_open
from ara_cli.list_filter import ListFilterMonad, ListFilter, filter_list


def test_include_tags_processed():
    filter_instance = ListFilter(include_tags=['@tag1', '@tag2', 'tag3'])
    assert filter_instance.include_tags == ['tag1', 'tag2', 'tag3']


def test_exclude_tags_processed():
    filter_instance = ListFilter(exclude_tags=['@tag1', '@tag2', 'tag3'])
    assert filter_instance.exclude_tags == ['tag1', 'tag2', 'tag3']


def test_include_tags_none():
    filter_instance = ListFilter(include_tags=None)
    assert filter_instance.include_tags is None


def test_exclude_tags_none():
    filter_instance = ListFilter(exclude_tags=None)
    assert filter_instance.exclude_tags is None


@pytest.fixture
def sample_files():
    return {
        "default": ["file1.txt", "file2.log", "file3.md"]
    }


def mock_content_retrieval(file):
    contents = {
        "file1.txt": "Hello World",
        "file2.log": "Error log",
        "file3.md": "Markdown content"
    }
    return contents.get(file, "")


@pytest.mark.parametrize("input_files, expected_files", [
    ({"group1": ["file1.txt"]}, {"group1": ["file1.txt"]}),  # Case when input is a dict
    (["file1.txt", "file2.log"], {"default": ["file1.txt", "file2.log"]})  # Case when input is not a dict
])
def test_list_filter_monad_initialization(input_files, expected_files):
    monad = ListFilterMonad(input_files)
    assert monad.files == expected_files


@pytest.mark.parametrize("include_ext, exclude_ext, expected", [
    ([".txt", ".md"], None, ["file1.txt", "file3.md"]),
    (None, [".log"], ["file1.txt", "file3.md"]),
    ([".log"], [".txt"], ["file2.log"]),
    (None, None, ["file1.txt", "file2.log", "file3.md"])
])
def test_filter_by_extension(sample_files, include_ext, exclude_ext, expected):
    monad = ListFilterMonad(sample_files)
    filtered_files = monad.filter_by_extension(include=include_ext, exclude=exclude_ext).get_files()
    assert filtered_files == expected


def test_default_content_retrieval():
    mock_data = "Mock file data"
    with patch("builtins.open", mock_open(read_data=mock_data)) as mocked_file:
        content = ListFilterMonad.default_content_retrieval("dummy_path")
        assert content == mock_data
        mocked_file.assert_called_once_with("dummy_path", 'r', encoding='utf-8')


def test_default_tag_retrieval():
    result = ListFilterMonad.default_tag_retrieval("")
    assert result == []


def test_default_content_retrieval_exception():
    with patch("builtins.open", side_effect=Exception("Mocked exception")) as mocked_file:
        content = ListFilterMonad.default_content_retrieval("dummy_path")
        assert content == ""  # Expect empty string on exception
        mocked_file.assert_called_once_with("dummy_path", 'r', encoding='utf-8')


@pytest.mark.parametrize("include, exclude, expected", [
    (["Hello"], None, ["file1.txt"]),
    (None, ["Error"], ["file1.txt", "file2.log", "file3.md"]),
    (["Markdown"], ["Error"], ["file3.md"]),
    (["Markdown"], ["content"], []),
    (["Hello", "Markdown"], None, ["file1.txt", "file3.md"]),
    (["Hello", "Markdown"], None, ["file1.txt", "file3.md"]),
    (None, None, ["file1.txt", "file2.log", "file3.md"])
])
def test_overlapping_filter(sample_files, include, exclude, expected):
    def mock_retrieval_method(file):
        content_map = {
            "file1.txt": "Hello world",
            "file2.log": "This is a log file",
            "file3.md": "Markdown content"
        }
        return content_map.get(file, "")

    monad = ListFilterMonad(sample_files)

    filtered_files_dict = monad.overlapping_filter(mock_retrieval_method, include=include, exclude=exclude).files

    filtered_files = filtered_files_dict.get("default", [])

    assert filtered_files == expected


@pytest.mark.parametrize("include_content, exclude_content", [
    (["Hello"], None),
    (None, ["Error"]),
    (["Markdown"], ["content"]),
])
def test_filter_by_content(sample_files, include_content, exclude_content):
    def mock_strategy(x):
        return x

    with patch.object(ListFilterMonad, 'overlapping_filter', return_value=ListFilterMonad(sample_files)) as mock_overlapping_filter:
        monad = ListFilterMonad(sample_files, content_retrieval_strategy=mock_strategy)
        monad.filter_by_content(include=include_content, exclude=exclude_content)
        mock_overlapping_filter.assert_called_once_with(mock_strategy, include_content, exclude_content)

@pytest.mark.parametrize("include_tags, exclude_tags", [
    (["tag1"], None),
    (None, ["tag2"]),
    (["tag1"], ["tag2"]),
])
def test_filter_by_tags(sample_files, include_tags, exclude_tags):
    def mock_tags_retrieval(x):
        return x

    with patch.object(ListFilterMonad, 'overlapping_filter', return_value=ListFilterMonad(sample_files)) as mock_overlapping_filter:
        monad = ListFilterMonad(sample_files, tags_retrieval=mock_tags_retrieval)
        monad.filter_by_tags(include=include_tags, exclude=exclude_tags)
        mock_overlapping_filter.assert_called_once_with(mock_tags_retrieval, include_tags, exclude_tags)


def test_get_files_default_key(sample_files):
    monad = ListFilterMonad(sample_files)
    assert monad.get_files() == ["file1.txt", "file2.log", "file3.md"]


def test_get_files_multiple_keys():
    files = {
        "group1": ["file1.txt"],
        "group2": ["file2.log"]
    }
    monad = ListFilterMonad(files)
    assert monad.get_files() == files


@pytest.mark.parametrize("list_filter, expected_include_ext, expected_exclude_ext, expected_include_content, expected_exclude_content", [
    (ListFilter(include_extension=[".txt"], exclude_extension=None, include_content=None, exclude_content=None),
     [".txt"], None, None, None),
    (ListFilter(include_extension=None, exclude_extension=[".log"], include_content=None, exclude_content=None),
     None, [".log"], None, None),
    (ListFilter(include_extension=None, exclude_extension=None, include_content=["Hello"], exclude_content=None),
     None, None, ["Hello"], None),
    (ListFilter(include_extension=None, exclude_extension=None, include_content=None, exclude_content=["Error"]),
     None, None, None, ["Error"]),
])
def test_filter_list(sample_files, list_filter, expected_include_ext, expected_exclude_ext, expected_include_content, expected_exclude_content):
    with patch('ara_cli.list_filter.ListFilterMonad.filter_by_extension') as mock_filter_by_extension, \
         patch('ara_cli.list_filter.ListFilterMonad.filter_by_content') as mock_filter_by_content, \
         patch('ara_cli.list_filter.ListFilterMonad.get_files', return_value=sample_files):

        filter_list(
            list_to_filter=sample_files,
            list_filter=list_filter,
            content_retrieval_strategy=None,
            file_path_retrieval=None,
            tag_retrieval=None
        )

        mock_filter_by_extension.assert_called_once_with(
            include=expected_include_ext,
            exclude=expected_exclude_ext
        )

        mock_filter_by_content.assert_called_once_with(
            include=expected_include_content,
            exclude=expected_exclude_content
        )

@pytest.mark.parametrize("list_filter", [
    None,
    ListFilter(include_extension=None, exclude_extension=None, include_content=None, exclude_content=None)
])
def test_filter_list_no_filter(sample_files, list_filter):
    with patch('ara_cli.list_filter.ListFilterMonad') as mock_list_filter_monad:
        result = filter_list(
            list_to_filter=sample_files,
            list_filter=list_filter
        )

        if list_filter is None:
            assert result == sample_files
        else:
            mock_list_filter_monad.assert_called_once_with(
                files=sample_files,
                content_retrieval_strategy=None,
                file_path_retrieval=None,
                tags_retrieval=None
            )
