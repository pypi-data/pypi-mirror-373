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
# pylint: disable=multiple-statements, missing-function-docstring


from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, ClassVar, Dict, List, Optional, Set, Tuple, Union, TYPE_CHECKING





from ...exceptions import (
    PmtCircularPyInclusionError,
    PmtInternalError,
)
from ...pyodide_logger import logger
from .root_extractors import RootFilesExtractor
from ._inclusions import InclusionConfig, ExtractorGatherer


if TYPE_CHECKING:
    from ... import PyodideMacrosPlugin













@dataclass(eq=False)
class FileExtractorWithInclusions(RootFilesExtractor):
    """
    Manage inclusions in the python files, following this kind of syntaxes:

        ## {{ [md]py_name:section:section }}
        ## {{ [py]py_name:section:section }}
        ## {{ py_name:section:section }}       ( defaults to [py] )

    relative paths usable:
        ## {{ ../bal/py_name:section }}
        ## {{ :section }}                      ( in the current py file )
    """

    _children: Dict[str, List[InclusionConfig]] = field(
        default_factory = lambda: defaultdict(list)
    )
    """
    Children of this "file", by sections as: {section: (child, section), ...}
    """

    _unresolved: Set[str] = None
    """ Names of all the sections containing inclusion instructions. """

    @property
    def inclusions_done(self):
        return not self._unresolved



    def _setup_to_extract_again(self):
        self._children.clear()
        super()._setup_to_extract_again()


    def extract_contents(self, to_resolve: ExtractorGatherer=None, **_):
        """
        Recursively create/extract the contents of individual files.
        This builds the dependency graph internally (-> self._children), but doesn't apply the
        injections.
        Since the IdeFilesExtractor instances are cached, this step will always terminate, as
        long as the inclusions aren't resolved.
        """
        super().extract_contents(to_resolve)

        for section, content in self.contents.items():
            InclusionConfig.build_inclusions(self, section, content, to_resolve)
        self._unresolved = set(self._children)


    def add_inclusion(self, section, inclusion):
        self._children[section].append(inclusion)

    def update_content(self, section, fresh_content):
        self.contents[section] =fresh_content


    def resolve_inclusions(
        self,
        section:    str,
        path:       List[Tuple[Path,str]],
        current:    Set[Tuple[Path,str]],
        to_resolve: ExtractorGatherer,
    ):
        # CONTRACTS:
        #   - @to_resolve updates/removals are handled by the caller.
        #   - @path is the ordered version of @current (logging purpose).
        #   - @path and @current are handled from the current call.
        #   - If the section to resolve doesn't contain inclusion instructions, do nothing.

        location = self.exo_py, section
        path.append(location)       # added first to show it in the error message

        if location in current:
            order = ''.join(f"\n    {py}:{section}" for py,section in path)
            raise PmtCircularPyInclusionError(
                "Cannot resolve python files inclusions because a circular reference has "
                f"been found. The current resolution order is as follow:{ order }"
            )

        current.add(location)
        children_include = self._children[section]

        # Check done "late" to be sure the error is raised if a circular dependency exist:
        if section in self._unresolved:

            for inclusion in children_include:
                for child_section in inclusion.get_children_sections():
                    child_node = inclusion.child, child_section
                    if child_node in to_resolve:
                        to_resolve.remove(child_node)

                    inclusion.child.resolve_inclusions(child_section, path, current, to_resolve)
                    # Not done inside the previous condition, otherwise cyclic dependencies cannot be found.

                inclusion.apply()

        path.pop()
        current.remove(location)
        self._unresolved.discard(section)









@dataclass(eq=False)
class CachedIdeFilesExtractor(RootFilesExtractor):
    """
    Keeping track of modifications of the files on the disk:
    Automatically triggers updates when a file has been modified.

    WARNING:
    --------

    In terms of inheritance, the CachedIdeFilesExtractor has to be in front of other children
    classes in the MRO, so that it's extract_contents() method supersedes the other ones.
    So the base class in other branches of the hierarchy must be BaseIdeFilesExtractor instead
    of CachedIdeFilesExtractor.
    """

    _need_refresh: bool = True
    """ Marked as needing a refresh from children elements. """

    _parents: Set['CachedIdeFilesExtractor'] = field(default_factory=set)

    _CACHED_EXTRACTORS: ClassVar[Dict[Path, 'CachedIdeFilesExtractor']] = None
    """
    Class level cache of instances. This HAS to be overridden in one of the children classes
    in the hierarchy, allowing different caches in different branches, all using the same
    implementation.
    """


    #---------------------------------------------------------------------------


    def __init_subclass__(cls, **kw):
        """
        Verify the hierarchy contracts are followed correctly
        """
        if cls.extract_contents is not CachedIdeFilesExtractor.extract_contents:
            MRO = ''.join(f"\n    - { kls.__name__ }" for kls in cls.mro())
            raise PmtInternalError(
                f"Erroneous class hierarchy for {cls.__name__}: {CachedIdeFilesExtractor.__name__}"
                " should be higher in the class hierarchy so that it's `extract_contents` method "
                f"is the outermost method. Otherwise, the cache logistic cannot work.\nMRO:{MRO}"
            )
        if cls._CACHED_EXTRACTORS is None:
            raise PmtInternalError(
                f"The class {cls.__name__} should override the class level property _CACHED_EXTRACTORS"
            )

    #---------------------------------------------------------------------------


    @classmethod
    def get_file_extractor_and_exo_py_for(
        cls,
        env: 'PyodideMacrosPlugin',
        py_name: Union[str,Tuple[str]],
        exo_py: Optional[Path]=...,
        *,
        extract: bool = True,
        to_resolve: ExtractorGatherer = None,
    ) -> Tuple[ Optional[Path], 'CachedIdeFilesExtractor'] :
        """
        Instantiate or retrieve the CachedIdeFilesExtractor instance for the related py_name
        file/relative path.

        @returns: a tuple, of the resolved exo_py absolute path, and the extractor instance.

        Notes:
            - The exo_py argument doesn't need to be resolved yet, it will be automatically in the
              method, and that resolved version can be found in the tuple output (first element).
            - The very same instance is reused for all IDE without a py_name argument.
            - ...so DO NOT store exo_py in the cache! (needed to build IDE editors' ids consistently
              with previous versions, making 'xx/exo.py' different from 'xx/yy/../exo.py').
        """
        if cls._CACHED_EXTRACTORS is None:
            raise PmtInternalError(
                f"{ cls.__name__ }._CACHED_EXTRACTORS has not been overridden in a child class."
            )

        cache_key, exo_py, instance_builder = cls._get_key_cache_and_instance_builder(env, py_name, exo_py)

        if not env.activate_cache or cache_key not in cls._CACHED_EXTRACTORS:
            # Always store even when not cached, so that propagate_any_refresh_needs routine can
            # find the objects (needed to reset the cache of mkdocs-addresses appropriately...)
            instance = instance_builder()
            cls._CACHED_EXTRACTORS[cache_key] = instance
        else:
            instance = cls._CACHED_EXTRACTORS[cache_key]

        if extract:
            if to_resolve is None:
                # Some macros (`section`, ...) may call this directly, hence need to define to_resolve.
                to_resolve = ExtractorGatherer()
                to_resolve.store(instance)
            instance.extract_contents(to_resolve)        # Will trigger update if needed

        return exo_py, instance

    @classmethod
    def propagate_any_refresh_needs(cls):
        to_remove = [
            k for k,extractor in cls._CACHED_EXTRACTORS.items()
              if extractor.exo_py and not extractor.exo_py.is_file()
        ]
        for k in to_remove:
            del cls._CACHED_EXTRACTORS[k]

        to_refresh = [
            extractor for extractor in cls._CACHED_EXTRACTORS.values()
                      if extractor.need_cache_refresh()
        ]
        logger.debug("Marking files extractors to refresh")
        for extractor in to_refresh:
            extractor._setup_to_extract_again_and_propagate()

    def register_parent(self, parent: 'CachedIdeFilesExtractor'):
        self._parents.add(parent)

    def need_cache_refresh(self):
        return self._need_refresh

    def mark_refreshed(self):
        self._need_refresh = False

    def show_refresh(self):
        logger.info(f'\033[33mRefreshing source\033[0m { self.docs_py }')


    def _setup_to_extract_again_and_propagate(self):
        self._setup_to_extract_again()
        for parent in self._parents:
            if not parent.need_cache_refresh():
                parent._setup_to_extract_again_and_propagate()

    def _setup_to_extract_again(self):
        self._need_refresh = True
        super()._setup_to_extract_again()


    def extract_contents(self, to_resolve: ExtractorGatherer=None, **_) -> bool :
        """
        Change of interface: return a boolean telling of the cached data has been updated or not.
        """
        if self.need_cache_refresh():
            if self.env.show_cache_refresh:
                self.show_refresh()
            super().extract_contents(to_resolve)
            # WARNING:
            #   Because of the dependency injection, the current class being second in place in the
            #   final MRO while the file content extractions are being done deeper in the hierarchy,
            #   the `self.mark_refresh()` call must be done at the bottom of the mro so that the
            #   "inclusion" level of the logic (which, again, is deeper than this call) can see
            #   Extractors marked as refreshed when a circular reference is used in the inclusion.
            #   This way, infinite extractions are prevented.


    #---------------------------------------------------------------------------


    @classmethod
    def _get_key_cache_and_instance_builder(
        cls,
        env: 'PyodideMacrosPlugin',
        py_name: Union[str,Tuple[str]],
        exo_py: Optional[Path]=...,
    ) -> Tuple[ Optional[Path], Optional[Path], Callable[[], 'CachedIdeFilesExtractor'] ]:
        raise NotImplementedError()
