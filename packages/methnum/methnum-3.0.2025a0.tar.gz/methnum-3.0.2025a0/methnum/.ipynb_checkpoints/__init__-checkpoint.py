import os
import shutil
from datetime import datetime
import glob

from travo.jupyter_course import JupyterCourse
from travo import GitLab
from typing import Optional
from travo.utils import run, git_get_origin
from travo.gitlab import ResourceRef
from travo.assignment import Submission
from travo.nbgrader_utils import remove_submission_gradebook

from nbgrader.api import Gradebook


__version__ = "3.0"


def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)


class MethNumCourse(JupyterCourse):
    ignore = [
        "feedback",
        ".ipynb_checkpoints" "*.pyc",
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

    def autograde(
        self,
        assignment_name: str,
        tag: Optional[str] = None,
        new_score_policy: str = "only_empty",
    ) -> None:
        """
        Autograde the student's assignments

        Submit the corrected assignment from submitted, wait for the student_autograde
        and collect the student gradebook.

        Examples:

        Autograde all students submissions in the current directory::

            course.autograde("Assignment1")

        Autograde all students submissions for a given student group,
        laying them out in nbgrader's format, with the student's group
        appended to the username:

            course.autograde("Assignment1",
                            student_group="MP2")
        """
        failed = []
        for assignment_dir in glob.glob(
            f"submitted/{tag}/{os.path.basename(assignment_name)}"
        ):
            student = assignment_dir.split("/")[1]
            # get student group
            url = git_get_origin(cwd=assignment_dir)
            ref = ResourceRef(url=url)
            ref.forge.login()
            project = ref.forge.get_project(ref.path)
            assignment = self.assignment(assignment_dir)
            sub = Submission(project, assignment)
            student_group = sub.repo.forked_from_project.namespace.name
            self.log.info(f"Student: {student} (group {student_group})")
            remove_submission_gradebook(
                Gradebook("sqlite:///.gradebook.db"),
                os.path.basename(assignment_name),
                student,
            )
            # re-submit the submitted
            self.log.info("- Enregistrement des changements:")
            self.forge.ensure_local_git_configuration(dir=os.getcwd())
            if (
                self.forge.git(
                    [
                        "commit",
                        "--all",
                        "-m",
                        f"Correction par {self.forge.get_current_user().username}",
                    ],
                    check=False,
                    cwd=assignment_dir,
                ).returncode
                != 0
            ):
                self.log.info("  Pas de changement à enregistrer")

            self.log.info("- Envoi des changements:")
            branch = project.default_branch
            self.forge.git(["push", url, branch], cwd=assignment_dir)
            # Force an update of origin/master (or whichever the origin default branch)
            # self.forge.git(["update-ref", f"refs/remotes/origin/{branch}", branch])
            self.log.info(
                f"- Nouvelle soumission effectuée. "
                f"Vous pouvez consulter le dépôt: {url}"
            )
            # autograde
            try:
                job = sub.ensure_autograded(force_autograde=True)
            except RuntimeError as e:
                self.log.warning(e)
                failed.append(assignment_dir)
                continue
            # collect gradebooks
            self.log.info(f"fetch autograded for {assignment_dir}")
            project.fetch_artifacts(job, path=".", prefix="")
            self.merge_autograded_db(
                assignment_name=os.path.basename(assignment_name),
                tag=tag,
                on_inconsistency="WARNING",
                new_score_policy=new_score_policy,
            )
        if failed:
            self.log.warning(f"Failed autograde: {' '.join(failed)}")

    def update(self):
        self.forge.git(["submodule", "update", "--remote", "--recursive"])
        run(
            [
                "conda",
                "env",
                "update",
                "-n",
                "methnum",
                "-f",
                "scripts/environment.yml",
                "--prune",
            ]
        )
        run(
            [
                "pip",
                "install",
                "update",
                "git+https://gitlab.com/travo-cr/travo.git",
                "--force-reinstall",
            ]
        )
        run(
            [
                "jupyter",
                "nbextension",
                "install",
                "--sys-prefix",
                "--py",
                "nbgrader",
                "--overwrite",
            ]
        )
        run(["jupyter", "nbextension", "enable", "--sys-prefix", "--py", "nbgrader"])
        run(
            ["jupyter", "serverextension", "enable", "--sys-prefix", "--py", "nbgrader"]
        )
        run(["nbgrader", "--version"])

    def release(
        self,
        assignment_name: str,
        visibility: str = "public",
        path: Optional[str] = None,
        push_instructor_repo: bool = True,
    ) -> None:
        assignment_basename = os.path.basename(assignment_name)
        teacher_url = git_get_origin()
        # peut-etre remplacer les lignes suivantes avec nbgitpuller
        self.forge.ensure_local_git_configuration(dir=os.getcwd())
        if push_instructor_repo:
            self.log.info(
                f" Poste le sujet sur le gitlab privé enseignant {teacher_url}..."
            )
            self.forge.git(["pull", teacher_url])
            self.forge.git(["add", assignment_basename])
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

    def generate_feedback(
        self, assignment_name: str, tag: str = "*", new_score_policy: str = "only_empty"
    ) -> None:
        """
        Generate the assignment feedback for the given student and propagate the scores
        in the student gradebooks.
        The student name can be given with wildcard.
        """
        # TODO: remove the convert line when travo is updated
        self.convert_from_md_to_ipynb(
            path=f"./autograded/{tag}/{os.path.basename(assignment_name)}/"
        )
        super().generate_feedback(
            assignment_name=assignment_name, tag=tag, new_score_policy=new_score_policy
        )

    def merge_autograded_db(
        self,
        assignment_name: str,
        tag: str = "*",
        on_inconsistency: str = "ERROR",
        new_score_policy: str = "only_empty",
        back: bool = False,
    ) -> None:
        # TODO: remove this function when travo is updated
        super().merge_autograded_db(
            assignment_name=os.path.basename(assignment_name),
            tag=tag,
            on_inconsistency=on_inconsistency,
            new_score_policy=new_score_policy,
            back=back,
        )

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
        # load config
        from nbgrader.apps.baseapp import NbGrader
        from travo.nbgrader_utils import remove_assignment_gradebook

        api = NbGrader()
        api.config_file = "scripts/nbgrader_config"
        api.load_config_file()
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
        self.collect_autograded(assignment_name, student_group=student_group)
        self.merge_autograded_db(
            assignment_name=os.path.basename(assignment_name),
            on_inconsistency="WARNING",
            new_score_policy="only_empty",
        )
        # formgrader
        self.formgrader()


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
    assignments_group_path="MethNum/2023-2024",
    assignments_group_name="2023-2024",
    session_path="2023-2024",
    expires_at="2024-12-31",
    script="methnum",
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
    source_directory=".",
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
