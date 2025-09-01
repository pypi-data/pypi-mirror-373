"""
Nmk workspace plugin builders.
"""

import fnmatch
import subprocess
from pathlib import Path
from typing import Union

from nmk.model.builder import NmkTaskBuilder


class SubProjectsBuilder(NmkTaskBuilder):
    """
    Builder for sub-projects in the workspace tree.

    This builder is used to iterate on workspace sub-projects and trigger nmk build for each.
    """

    def build(  # type: ignore
        self,
        root: str,
        to_build_first: list[str],
        to_build: list[str],
        to_build_after: list[str],
        excluded: list[str],
        args: Union[list[str], str],
        ignore_failures: bool = False,
    ):
        """
        Build specified tasks for each sub-project.

        :param root: Root path of the workspace
        :param to_build_first: List of sub-projects paths to build first
        :param to_build: List of all sub-projects paths to be built (including the ones in to_build_first and to_build_after)
        :param to_build_after: List of sub-projects paths to build after all the others
        :param excluded: List of sub-projects glob patterns to exclude from building
        :param args: List of nmk args to use for each sub-project
        :param ignore_failures: Whether to ignore failure of sub-project builds
        """

        # Prepare args list
        args_list = args if isinstance(args, list) else [a for a in args.split(" ") if a]

        # Prepare global list of sub-projects to be built
        sub_projects: list[str] = []
        sub_projects.extend([p for p in to_build_first if p in to_build])
        sub_projects.extend([p for p in to_build if p not in to_build_after])
        sub_projects.extend([p for p in to_build_after if p in to_build])

        # Iterate on sub-projects
        built_projects: set[str] = set()
        for sub_project in sub_projects:
            # Handle duplicates
            if sub_project in built_projects:
                # Already done, skip
                continue
            built_projects.add(sub_project)

            # Some log info...
            self.logger.info(self.task.emoji, ">> ----------------------------------------------------------------")
            self.logger.info(self.task.emoji, f">> Building sub-project: {sub_project}")
            self.logger.info(self.task.emoji, ">> ----------------------------------------------------------------")

            # Handle exclusions
            if any(fnmatch.fnmatch(sub_project, pattern) for pattern in excluded):
                self.logger.info(self.task.emoji, ">> skipped (excluded)")
                continue

            # Delegate build
            sub_project_path = Path(root) / sub_project
            nmk_args = ["nmk", "--log-prefix", f"{sub_project}/"] + args_list
            self.logger.debug(">> Running command: " + " ".join(nmk_args))
            cp = subprocess.run(nmk_args, cwd=sub_project_path)

            # Handle build failure
            if cp.returncode != 0:
                error_msg = f"!! Failed to build sub-project: {sub_project} !!"
                if ignore_failures:
                    self.logger.error(error_msg)
                else:
                    raise RuntimeError(error_msg)
