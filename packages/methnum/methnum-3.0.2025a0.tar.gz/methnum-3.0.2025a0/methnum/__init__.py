__version__ = "3.0.2025a"


import os
import shutil
from datetime import datetime
import glob

from travo.jupyter_course import JupyterCourse
from travo import GitLab
from typing import Optional
from travo.utils import run, git_get_origin
from travo.nbgrader_utils import remove_assignment_gradebook, merge_assignment_gradebook

from nbgrader.api import Gradebook

import tempfile
import io


def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)


class MethNumCourse(JupyterCourse):
    ignore = [
        "feedback*",
        ".ipynb_checkpoints",
        "*.pyc",
        "__pycache__",
        ".DS_Store",
        "*~",
        "core*",
        "*.ipynb",
    ]

    ignore_nbgrader = ignore + [".*"]
    gitlab_ci_yml = None

    def start(self) -> None:
        """
        Ouvre le tableau de bord du cours en local avec JupyterLab
        """
        project = self.forge.get_project(f"{self.path}/ComputerLab")
        project.clone_or_pull(
            self.work_dir(), force=True, pull_can_fail=True, anonymous=True
        )
        if "JUPYTER_SERVER_ROOT" not in os.environ:
            run(["jupyter", "lab", "tableau_de_bord.md"], cwd=self.work_dir())

    def release(
        self,
        assignment_name: str,
        visibility: str = "public",
        path: Optional[str] = None,
        push_instructor_repo: bool = True,
    ) -> None:
        assignment_basename = os.path.basename(assignment_name)
        teacher_url = git_get_origin(cwd="./")
        # peut-etre remplacer les lignes suivantes avec nbgitpuller
        self.forge.ensure_local_git_configuration(dir=os.getcwd())
        if push_instructor_repo:
            self.log.info(
                f" Poste le sujet sur le gitlab privé enseignant {teacher_url}..."
            )
            self.forge.git(["pull", teacher_url])
            self.forge.git(["add", os.path.join(self.source_directory, assignment_basename)])
            # self.forge.git(["add", os.path.join("source", assignment)])
            self.forge.git(
                [
                    "commit",
                    "-n",
                    "--allow-empty",
                    f"-m '{assignment_basename} {datetime.now()}'",
                ]
            )
            self.forge.git(["push"])
            self.log.info(
                f"- Soumission du sujet effectuée sur le dépôt enseignant. "
                f"Vous pouvez consulter le dépôt enseignant {teacher_url}"
            )

        self.log.info(
            f"- Poste le sujet sur le gitlab étudiant "
            f"{self.assignment_repo_path(assignment_name=assignment_name)}."
        )
        if path is not None:
            # path is used by the instructor dashboard after Travo MR !79 to pass
            # in {course.release_directory}/{assignment}
            super().release(
                assignment_name=assignment_name, visibility=visibility, path=path
            )
        else:  # Can be discarded once Travo MR !79 is deployed everywhere
            curr_dir = os.getcwd()
            os.chdir(os.path.join(self.release_directory, assignment_basename))
            try:
                super().release(assignment_name=assignment_name, visibility=visibility)
            except Exception as e:
                self.log.error(f"Release failed\n{e}")
            finally:
                os.chdir(curr_dir)

    def generate_assignment_content(
        self,
        assignment_name: str,
        add_gitignore: bool = True,
        add_gitlab_ci: bool = True,
    ) -> None:
        """
        Generate the student version of the given assignment
        """
        assignment = self.assignment(assignment_name)
        source_path = assignment.source_path()
        if not os.path.isdir(source_path):
            raise FileNotFoundError(
                f"{source_path} is given as the instructor source files but is not"
                " found."
            )
        release_path = assignment.release_path()
        self.convert_from_md_to_ipynb(path=source_path)
        with tempfile.TemporaryDirectory() as tmpdirname:
            db = os.path.join(release_path, ".gradebook.db")
            gitdir = os.path.join(release_path, ".git")
            is_git = os.path.exists(gitdir)
            if is_git:
                tmpgitdir = os.path.join(tmpdirname, ".git")
                self.log.info("Sauvegarde de l'historique git")
                shutil.move(gitdir, tmpgitdir)
            assignment_basename = os.path.basename(assignment_name)
            try:
                run(
                    [
                        "nbgrader",
                        "generate_assignment",
                        "--force",
                        f"--CourseDirectory.source_directory={self.source_directory}",
                        f"--CourseDirectory.release_directory={self.release_directory}",
                        assignment_basename,
                        f"--db='sqlite:///.gradebook.db'",
                    ]
                )
                run(
                    [
                        "nbgrader",
                        "generate_assignment",
                        "--force",
                        f"--CourseDirectory.source_directory={self.source_directory}",
                        f"--CourseDirectory.release_directory={self.release_directory}",
                        assignment_basename,
                        f"--db='sqlite:///{db}'",
                    ]
                )
                self.log.info(f"Importation de {db} dans .gradebook.db")
                # not enough because nbgrader preprocessing of notebook is necessary
                # merge_assignment_gradebook(source=Gradebook(f"sqlite:///{db}"),
                #                            target=Gradebook("sqlite:///.gradebook.db"))
                self.convert_from_ipynb_to_md(path=release_path)
            except ():
                pass
            finally:
                if is_git:
                    self.log.info("Restauration de l'historique git")
                    # In case the target_path has been destroyed and not recreated
                    os.makedirs(release_path, exist_ok=True)
                    shutil.move(tmpgitdir, gitdir)
        if add_gitlab_ci and self.gitlab_ci_yml is not None:
            io.open(os.path.join(release_path, ".gitlab-ci.yml"), "w").write(
                self.gitlab_ci_yml.format(assignment=assignment_basename)
            )
        if add_gitignore:
            io.open(os.path.join(release_path, ".gitignore"), "w").write(
                "\n".join(self.ignore) + "\n"
            )

    def collect_in_submitted(
        self, assignment_name: str, student_group: Optional[str] = None
    ) -> None:
        """
        Collect the student's submissions following nbgrader's standard organization
        and convert markdown into ipynb notebooks.

        This wrapper for `collect`:
        - forces a login;
        - reports more information to the user (at a cost);
        - stores the output in the subdirectory `submitted/`,
          following nbgrader's standard organization.

        This is used by the course dashboard.
        """
        super().collect_in_submitted(assignment_name, student_group)
        self.convert_from_md_to_ipynb(path=f"submitted/*/{os.path.basename(assignment_name)}")

    def convert_from_md_to_ipynb(self, path: str) -> None:
        import jupytext  # type: ignore

        for mdname in glob.glob(os.path.join(path, "*.md")):
            with io.open(mdname, encoding='utf-8') as fd:
                if "nbgrader" not in fd.read():
                    self.log.debug(
                        "Skip markdown file/notebook with no nbgrader metadata:"
                        f" {mdname}"
                    )
                    continue
            ipynbname = mdname[:-3] + ".ipynb"
            if not os.path.exists(ipynbname):
                self.log.info(f"Converting {mdname} to {ipynbname}")
                notebook = jupytext.read(mdname)
                jupytext.write(notebook, ipynbname)
            else:
                self.log.info(f"{ipynbname} already exists")
            # ensure user writing permission
            os.chmod(ipynbname, 0o644)
            os.chmod(mdname, 0o644)
            self.log.info("Updating cross-links to other notebooks (.md->.ipynb)")
            with open(ipynbname, "r") as file:
                filedata = file.read()
            filedata = filedata.replace(".md)", ".ipynb)")
            # Write the file out again
            with open(ipynbname, "w") as file:
                file.write(filedata)
            run(["jupytext", mdname, "--to", "ipynb"])

    def convert_from_ipynb_to_md(self, path: str) -> None:
        import jupytext  # type: ignore

        for ipynbname in glob.glob(os.path.join(path, "*.ipynb")):
            mdname = ipynbname[:-6] + ".md"
            if not os.path.exists(mdname):
                self.log.info(f"Converting {ipynbname}  to {mdname}")
                notebook = jupytext.read(ipynbname)
                jupytext.write(notebook, mdname)
            else:
                self.log.info(f"{mdname} already exists")
            # ensure user writing permission
            os.chmod(ipynbname, 0o644)
            os.chmod(mdname, 0o644)
            self.log.info("Updating cross-links to other notebooks (.ipynb->.md)")
            with open(mdname, "r") as file:
                filedata = file.read()
            filedata = filedata.replace(".ipynb)", ".md)")
            # Write the file out again
            with open(mdname, "w") as file:
                file.write(filedata)
            run(["jupytext", ipynbname, "--to", "md"])

    def remove_solution(self, assignment_name: str) -> None:
        assignment = os.path.basename(assignment_name)
        for path in ["release", "source"]:
            ensure_dir(path)
            assignment_name = os.path.join(path, assignment)
            if os.path.isdir(assignment_name):
                shutil.rmtree(assignment_name)
        shutil.copytree(assignment, os.path.join("source", assignment))
        run(["nbgrader", "--version"])
        run(["nbgrader", "generate_assignment", assignment, "--create", "--force"])

    def test_assignment(
        self, assignment_name: str, student_group: str = "CandidatsLibres"
    ) -> None:
        """
        Perform a quick test of the pipeline : fetch/submit/collect/formgrader

        Parameters
        ----------
        assignment_name

        Returns
        -------

        """
        # clean online repos
        self.forge.login()
        try:
            gb = Gradebook("sqlite:///.gradebook.db")
            remove_assignment_gradebook(gb, os.path.basename(assignment_name))
            self.remove_submission(assignment_name, force=True)
        except Exception:
            pass
        tag = student_group + "." + self.forge.get_current_user().username
        submitted_path = os.path.join(
            "submitted", tag, os.path.basename(assignment_name)
        )
        if os.path.isdir(submitted_path):
            shutil.rmtree(submitted_path, ignore_errors=True)
        autograded_path = os.path.join(
            "autograded", tag, os.path.basename(assignment_name)
        )
        if os.path.isdir(autograded_path):
            shutil.rmtree(autograded_path, ignore_errors=True)
        # fetch the assignment and replace answers with dummy code
        self.ensure_work_dir()
        assignment_dir = self.work_dir(assignment_name=assignment_name)
        if os.path.isdir(assignment_dir):
            shutil.rmtree(assignment_dir, ignore_errors=True)
        self.fetch(assignment_name, student_group=student_group)
        shutil.copytree(
            os.path.join("source", os.path.basename(assignment_name)),
            self.work_dir(assignment_name),
            dirs_exist_ok=True,
        )
        # submit
        self.submit(assignment_name, student_group=student_group)
        # collect
        self.ensure_autograded(assignment_name, student_group=student_group)
        self.collect_in_submitted(assignment_name, student_group=student_group)
        self.collect_autograded(assignment_name, student_group=student_group)
        self.collect_autograded_post(
            assignment_name=os.path.basename(self.name),
            on_inconsistency="WARNING",
            new_score_policy="force_new_score",
        )
        # formgrader
        self.formgrader(assignment_name=assignment_name)


# image: ${CI_REGISTRY}/methnum/computerlab:master
gitlab_ci_yml = """# Autogenerated by methnum
image: gitlab.dsi.universite-paris-saclay.fr:5005/methnum/computerlab:master

variables:
  ASSIGNMENT: {assignment}
  STUDENT: $CI_PROJECT_ROOT_NAMESPACE

autograde:
  script:
    # - source activate methnum
    # skip student_autograde for instructor release
    - if [ "$STUDENT" == "MethNum" ]; then exit 0; else echo $STUDENT; fi
    - STUDENT=`echo $STUDENT | sed -e 's/-travo//;s/-/./'`
    - methnum student_autograde $ASSIGNMENT $STUDENT
  artifacts:
    paths:
      - autograded
      - feedback
    # reports:
    #   junit: feedback/scores.xml
"""

forge = GitLab("https://gitlab.dsi.universite-paris-saclay.fr/")
course = MethNumCourse(
    forge=forge,
    path="MethNum",
    name="Méthodes Numériques",
    url="https://methnum.gitlab.dsi.universite-paris-saclay.fr/",
    student_dir="~/MethNum",
    assignments_group_path="MethNum/2025-2026",
    assignments_group_name="2025-2026",
    session_path="2025-2026",
    expires_at="2026-12-31",
    script="methnum",
    version=__version__,
    group_submissions=True,
    jobs_enabled_for_students=True,
    subcourses=["L1", "L2", "L3"],
    student_groups=[
        "MP1",
        "MP2",
        "MP3",
        "MP4",
        "MP5",
        "MP6",
        "MP7",
        "MP8",
        "MP9",
        "LDD-MP1",
        "LDD-MP2",
        "LDD-MP3",
        "LDD-PC1",
        "LDD-PC2",
        "LDD-PC3",
        "LDD-GEO",
        "LDD-STAPS",
        "LDD-CSVT",
        "CandidatsLibres",
    ],
    source_directory="source",
    release_directory = "release",
    mail_extension="universite-paris-saclay.fr",
)

course.gitlab_ci_yml = gitlab_ci_yml
course.ignore += [
    "*.ipynb",
    ".DS_store",
    "*.nav",
    "*.aux",
    "*.snm",
    "*.toc",
    "*.gz",
    "*.idx",
    "*.bbl",
    "*.blg",
    "*.out",
    "*.listing",
    "*.tex",
    "*.log",
    "~*",
]  # latex
