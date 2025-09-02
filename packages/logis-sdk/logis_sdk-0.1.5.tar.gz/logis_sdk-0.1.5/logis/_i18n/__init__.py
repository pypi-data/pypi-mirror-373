from pathlib import Path

import i18n

INNER_LOCALES_DIR = Path(__file__).parent.joinpath("locales")

# 设置默认语言
i18n.set("locale", "zh")
i18n.set("fallback", "en")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("skip_locale_root_data", True)
i18n.load_path.append(str(INNER_LOCALES_DIR))


def add_locale_dir(path: str | list[str]):
    """
    添加语言包目录
    Args:
        path: 语言包目录
    """
    if isinstance(path, (str, Path)):
        paths = [path]
    else:
        paths = path

    for p in paths:
        i18n.load_path.append(p)
