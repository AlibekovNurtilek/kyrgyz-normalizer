"""
Кыргызча текст нормализатор — TTS системалары үчүн.

Сандарды, даталарды, убакытты, акча бирдиктерин, аббревиатураларды
жана башка форматтарды кыргыз тилинде сөзгө айландырат.

Колдонуу:
    from kyrgyz_normalizer import normalize
    result = normalize("2024-жылы 15 км жол курулду")

    # же
    from kyrgyz_normalizer import KyrgyzTextNormalizer
    normalizer = KyrgyzTextNormalizer()
    result = normalizer.normalize("Баасы $500")
"""

__version__ = "0.1.0"

from .normalizer import KyrgyzTextNormalizer

_default_normalizer = None


def normalize(text: str) -> str:
    """
    Текстти нормализациялоо (ыңгайлуу функция).

    Args:
        text: Кирүүчү текст

    Returns:
        Нормализацияланган текст (сандар сөзгө айландырылган)
    """
    global _default_normalizer
    if _default_normalizer is None:
        _default_normalizer = KyrgyzTextNormalizer()
    return _default_normalizer.normalize(text)


__all__ = ["KyrgyzTextNormalizer", "normalize", "__version__"]
