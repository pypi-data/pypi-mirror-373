"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import ClassVar, Dict, Optional, TYPE_CHECKING


from ...exceptions import PmtInternalError
from .root_extractors import RootFilesExtractor
from .generic_extractors import CachedIdeFilesExtractor, FileExtractorWithInclusions
from .runners_extractors import _IdeFilesExtractor
from .snippets_extractor import _SnippetsExtractor

if TYPE_CHECKING:
    from ... import PyodideMacrosPlugin




@dataclass(eq=False)
class SourceFilesExtractor(CachedIdeFilesExtractor, RootFilesExtractor):

    # OVERRIDE
    _CACHED_EXTRACTORS: ClassVar[Dict[Path, 'IdeFilesExtractor']] = {}

    _mtime_infos: Dict[Path, Optional[int]] = None


    def __init_subclass__(cls, **kw):
        """
        Verify the hierarchy contracts are followed correctly
        """
        classes = cls.mro()
        i_cache = classes.index(CachedIdeFilesExtractor)
        if len(classes)==i_cache+1 or classes[i_cache+1] is not FileExtractorWithInclusions:
            MRO = ''.join(f"\n    - { kls.__name__ }" for kls in classes)
            raise PmtInternalError(
                f"Erroneous class hierarchy for {cls.__name__}: {FileExtractorWithInclusions.__name__}"
                f" should be just after {CachedIdeFilesExtractor.__name__} in the MRO, but:{ MRO }"
            )


    @classmethod
    def _get_key_cache_and_instance_builder(
        cls,
        env: 'PyodideMacrosPlugin',
        py_name: str,
        exo_py: Optional[Path]=...,
    ):
        exo_py = env.get_sibling_of_current_page(py_name, tail='.py') if exo_py is ... else exo_py
        key    = cls.get_key_cache(exo_py)
        # SURTOUT PAS!!! -> casse d'autres trucs ailleurs...
        # if exo_py:
        #     py_name = exo_py.stem
        is_snippets = exo_py and exo_py.stem == env.py_snippets_stem
        kls = SnippetsExtractor if is_snippets else IdeFilesExtractor
        builder = lambda: kls(env, py_name, exo_py=key, key_cache=key)
        return key, exo_py, builder


    def mark_refreshed(self):
        """
        Files may be added or removed on the fly, so the data tracking has to be thorough.
        """
        super().mark_refreshed()
        self._mtime_infos = {
            file: self._get_file_timestamp_infos(file)
                for file in self.iter_on_files()
        }

    def _setup_to_extract_again(self):
        self._mtime_infos = None
        super()._setup_to_extract_again()



    def _get_file_timestamp_infos(self, file:Optional[Path]):
        if file and file.is_file():
            return file.stat().st_mtime_ns
        return None


    def need_cache_refresh(self):
        # Using "!=" instead of "<" so that the files get updated with the user exchange 2 macro
        # calls with not python files in the page: this will also update the cached data (assuming
        # the files didn't get saved at the exact same timestamp...).
        needed = super().need_cache_refresh() or any(
            self._mtime_infos[file] != self._get_file_timestamp_infos(file)
            for file in self.iter_on_files()
        )
        return needed







@dataclass(eq=False)
class IdeFilesExtractor(SourceFilesExtractor, FileExtractorWithInclusions, _IdeFilesExtractor):
    pass


@dataclass(eq=False)
class SnippetsExtractor(SourceFilesExtractor, FileExtractorWithInclusions, _SnippetsExtractor):
    pass
