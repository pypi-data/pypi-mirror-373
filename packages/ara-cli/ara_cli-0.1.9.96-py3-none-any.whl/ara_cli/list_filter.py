from dataclasses import dataclass


@dataclass
class ListFilter:
    include_extension: list[str] | None = None
    exclude_extension: list[str] | None = None
    include_content: list[str] | None = None
    exclude_content: list[str] | None = None
    include_tags: list[str] | None = None
    exclude_tags: list[str] | None = None

    def __post_init__(self):
        if self.include_tags is not None:
            self.include_tags = [tag.replace('@', '') for tag in self.include_tags]
        if self.exclude_tags is not None:
            self.exclude_tags = [tag.replace('@', '') for tag in self.exclude_tags]


class ListFilterMonad:
    def __init__(self, files, content_retrieval_strategy=None, file_path_retrieval=None, tags_retrieval=None):
        if isinstance(files, dict):
            self.files = files
        else:
            self.files = {"default": files}
        self.content_retrieval_strategy = content_retrieval_strategy or self.default_content_retrieval
        self.file_path_retrieval = file_path_retrieval or self.default_file_path_retrieval
        self.tags_retrieval = tags_retrieval or self.default_tag_retrieval

    def bind(self, func):
        self.files = func(self.files)
        return self

    @staticmethod
    def default_content_retrieval(file):
        # Default strategy assumes file is a path and attempts to read it
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            return ""

    @staticmethod
    def default_file_path_retrieval(file):
        return file

    @staticmethod
    def default_tag_retrieval(file):
        return []

    def filter_by_extension(self, include=None, exclude=None):
        def filter_files_by_include(files, include):
            if not include:
                return files
            return [f for f in files if any(self.file_path_retrieval(f).endswith(ext) for ext in include)]

        def filter_files_by_exclude(files, exclude):
            if not exclude:
                return files
            return [f for f in files if not any(self.file_path_retrieval(f).endswith(ext) for ext in exclude)]

        def filter_logic(files):
            for key, original_files in files.items():
                filtered_files = filter_files_by_include(original_files, include)
                filtered_files = filter_files_by_exclude(filtered_files, exclude)
                files[key] = filtered_files
            return files

        return self.bind(filter_logic)

    def overlapping_filter(self, retrieval_method, include=None, exclude=None):
        def matches_include(item, include):
            return include and any(inc in item for inc in include)

        def matches_exclude(item, exclude):
            return exclude and any(exc in item for exc in exclude)

        def should_include_item(item, include, exclude):
            include_match = matches_include(item, include)
            exclude_match = matches_exclude(item, exclude)
            return (include_match or include_match is None) and not exclude_match

        def filter_logic(files_dict):
            if not include and not exclude:
                return files_dict

            for key, file_list in files_dict.items():
                filtered_files = [
                    file for file in file_list
                    if should_include_item(retrieval_method(file), include, exclude)
                ]
                files_dict[key] = filtered_files

            return files_dict

        return self.bind(filter_logic)

    def filter_by_content(self, include=None, exclude=None):
        return self.overlapping_filter(self.content_retrieval_strategy, include, exclude)

    def filter_by_tags(self, include=None, exclude=None):
        return self.overlapping_filter(self.tags_retrieval, include, exclude)

    def get_files(self):
        # Return the files dictionary. If it only contains the "default" key, return its list.
        if self.files and len(self.files) == 1 and "default" in self.files:
            return self.files["default"]
        return self.files


def filter_list(
    list_to_filter,
    list_filter: ListFilter | None = None,
    content_retrieval_strategy=None,
    file_path_retrieval=None,
    tag_retrieval=None
):
    if list_filter is None:
        return list_to_filter
    include_extension = list_filter.include_extension
    exclude_extension = list_filter.exclude_extension
    include_content = list_filter.include_content
    exclude_content = list_filter.exclude_content
    include_tags = list_filter.include_tags
    exclude_tags = list_filter.exclude_tags

    filter_monad = ListFilterMonad(
        files=list_to_filter,
        content_retrieval_strategy=content_retrieval_strategy,
        file_path_retrieval=file_path_retrieval,
        tags_retrieval=tag_retrieval
    )

    filter_monad.filter_by_extension(
        include=include_extension,
        exclude=exclude_extension
    )
    filter_monad.filter_by_content(
        include=include_content,
        exclude=exclude_content
    )
    filter_monad.filter_by_tags(
        include=include_tags,
        exclude=exclude_tags
    )

    return filter_monad.get_files()
