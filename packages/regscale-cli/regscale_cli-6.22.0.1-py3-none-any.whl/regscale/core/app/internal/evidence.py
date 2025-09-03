#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates evidence gathering into RegScale CLI"""


# standard python imports
import fnmatch
import itertools
import json
import os
import shutil
import zipfile
from datetime import datetime
from typing import Tuple

import click  # type: ignore
import pdfplumber  # type: ignore
from docx import Document  # type: ignore
from pathlib import Path
from rich.progress import Progress, TaskID

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import check_file_path, create_progress_object, error_and_exit
from regscale.models.app_models.click import regscale_ssp_id
from regscale.models.regscale_models import Assessment, File, Project, SecurityPlan


@click.group()
def evidence():
    """Welcome to the RegScale Evidence Collection Automation CLI!"""


@evidence.command()
def start():
    """Starts the evidence collection automation process."""
    run_evidence_collection()


@evidence.command(name="build_package")
@regscale_ssp_id()
@click.option(
    "--path",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
    help="Provide the desired path for creation of evidence files.",
    default=os.path.join(os.getcwd(), "evidence"),
    required=True,
)
def build_package(regscale_ssp_id: int, path: Path):
    """
    This function will build a directory of evidence with the provided RegScale SSP Id
    and RegScale Module and produce a zip file for extraction and use.
    """
    package_builder(ssp_id=regscale_ssp_id, path=path)


def run_evidence_collection():
    """
    This function will start the evidence collection automation process
    """
    import pymupdf  # type: ignore

    app = Application()
    api = Api()
    config = app.config
    check_file_path("./static")
    progress = create_progress_object()
    with progress:
        task0 = progress.add_task("[white]Setting evidence folder directory variables...", total=3)
        # call function to define variable for use outside of function
        evidence_folder, dir_name, new_cwd = set_directory_variables(
            task=task0, evidence_folder=config["evidenceFolder"], progress=progress
        )

        task1 = progress.add_task("[white]Building a required documents list from config.json...", total=3)
        # call function to define variable for use outside of function
        required_docs, document_list = parse_required_docs(
            evidence_folder=evidence_folder, task=task1, progress=progress
        )

        task2 = progress.add_task("[white]Calculating files last modified times...", total=5)
        # call function to define variable for use outside of function
        times = get_doc_timestamps(evidence_folder=new_cwd, directory=dir_name, task=task2, progress=progress)

        task3 = progress.add_task("[white]Building a required texts list from config.json...", total=3)
        # call function to define variable for use outside of function
        texts = set_required_texts(evidence_folder=evidence_folder, task=task3, progress=progress)

        task4 = progress.add_task("[white]Searching evidence folder for required files...", total=4)

        # call function to define variable for use outside of function
        folders = find_required_files_in_folder(evidence_folder=new_cwd, task=task4, progress=progress)

        task5 = progress.add_task("[white]Searching for digital signatures in documents...", total=2)

        # call function to define variable for use outside of function
        sig_results = signature_assessment_results(
            directory=folders, r_docs=required_docs, task=task5, progress=progress
        )

        task6 = progress.add_task("[white]Testing if required documents are present...", total=2)

        # call function to define variable for use outside of function
        doc_results = document_assessment_results(
            directory=folders, documents=document_list, task=task6, progress=progress
        )

        task7 = progress.add_task("[white]Extracting texts from required files...", total=4)

        # call function to define variable for use outside of function
        file_texts = parse_required_text_from_files(evidence_folder=new_cwd, task=task7, progress=progress)

        task8 = progress.add_task("[white]Searching for required text in parsed documents...", total=2)

        # call function to define variable for use outside of function
        search_results = text_string_search(f_texts=file_texts, req_texts=texts, task=task8, progress=progress)

        task9 = progress.add_task("[white]Testing if required texts are present", total=2)

        # call function to define variable for use outside of function
        text_results = text_assessment_results(searches=search_results, r_texts=texts, task=task9, progress=progress)

        task10 = progress.add_task("[white]Retrieving data from the evidence test projects...", total=3)

        # call function to define variable for use outside of function
        data = gather_test_project_data(api=api, evidence_folder=evidence_folder, task=task10, progress=progress)

        task11 = progress.add_task("[white]Testing file modification times...", total=2)

        # call function to define variable to use outside of function
        time_results = assess_doc_timestamps(timestamps=times, documents=required_docs, task=task11, progress=progress)

        task12 = progress.add_task("[white]Building assessment report...", total=4)

        # call function to define variable to use outside of function
        report = assessments_report(
            docres=doc_results,
            textres=text_results,
            timeres=time_results,
            sigres=sig_results,
            task=task12,
            progress=progress,
        )

        task13 = progress.add_task("[white]Building assessment results dataframe...", total=4)

        # call function to define variable to use outside of function
        results = build_assessment_dataframe(assessments=report, task=task13, progress=progress)

        task14 = progress.add_task("[white]Calculating assessment score...", total=1)

        # call function to define variable for use outside of function
        score_data = build_score_data(assessments=results, task=task14, progress=progress)

        task15 = progress.add_task("[white]Building a table for the assessment report...", total=4)

        # call function to define variable for use outside of function
        html_output = build_html_table(assessments=report, task=task15, progress=progress)

        task16 = progress.add_task("[white]Creating child assessment based on test results...", total=2)

        # call function to create child assessment via POST request
        create_child_assessments(
            api=api, project_data=data, output=html_output, score_data=score_data, task=task16, progress=progress
        )


def package_builder(ssp_id: int, path: Path):
    """Function to build a directory of evidence and produce a zip file for extraction and use

    :param int ssp_id: RegScale System Security Plan ID
    :param Path path: directory for file location
    :return None
    """
    app = Application()
    api = Api()
    with create_progress_object() as progress:
        task = progress.add_task("[white]Building and zipping evidence folder for audit...", total=6)
        try:
            # Obtaining MEGA Api for given Organizer Record.
            ssp = SecurityPlan.fetch_mega_api_data(ssp_id)
            module_folder_name = f'{ssp["securityPlan"]["id"]}_{ssp["securityPlan"]["systemName"]}'
            folder_contents_name = f'{ssp["securityPlan"]["id"]}_Evidence_Folder_Contents'

            module_folder = path / module_folder_name
            os.makedirs(module_folder.absolute(), exist_ok=True)

            progress.update(task, advance=1)

            # Checking MEGA Api for Attachments at SSP level
            process_ssp_attachments(
                ssp=ssp,
                path=path,
                folder_contents_name=folder_contents_name,
                module_folder_name=module_folder_name,
                api=api,
            )

            progress.update(task, advance=1)

            # Checking MEGA Api for Attachments at Control level
            process_control_attachments(
                ssp=ssp,
                path=path,
                progress=progress,
                module_folder_name=module_folder_name,
                module_folder=module_folder,
                api=api,
                task=task,
            )
            # Creating zip file and removing temporary Evidence Folder
            new_path = Path("./evidence.zip")
            zip_folder(path, new_path)
            remove_directory(module_folder)
            os.remove(path / f"{folder_contents_name}.json")
            shutil.move(new_path, path / "evidence.zip")
            progress.update(task, advance=1)
            app.logger.info("An evidence zipfile has been created and is ready for use!")
        except Exception as ex:
            app.logger.info("No SSP or Evidence exists for given Organizer Record.\n%s", ex)

        progress.update(task, advance=1)
        app.logger.info("Evidence zipfile located. Thank you!")


def process_ssp_attachments(ssp: dict, path: Path, folder_contents_name: str, module_folder_name: str, api: Api):
    """
    Process SSP attachments and download them to the evidence folder

    :param dict ssp: RegScale System Security Plan with mega API data
    :param Path path: directory for file location
    :param str folder_contents_name: name of the folder contents file
    :param str module_folder_name: name of the module folder
    :param Api api: RegScale CLI API object
    """
    if attachments := ssp.get("attachments"):
        outter_attachments = [
            {
                "fileName": i["trustedDisplayName"],
                "storedName": i["trustedStorageName"],
                "parentId": i["parentId"],
                "parentModule": i["parentModule"],
                "fileHash": i.get("fileHash") or i.get("shaHash"),
                "fileSize": i["size"],
                "dateCreated": i["dateCreated"],
            }
            for i in attachments
        ]

        json_data = json.dumps(outter_attachments, indent=4, separators=(", ", ": "))
        with open(f"{path}/{folder_contents_name}.json", "w", newline="\n") as next_output:
            next_output.write(json_data)

        # Adding any Attachments at SSP level to corresponding folder
        for f in outter_attachments:
            file = File.download_file_from_regscale_to_memory(
                api=api,
                record_id=f["parentId"],
                module=f["parentModule"],
                stored_name=f["storedName"],
                file_hash=f["fileHash"],
            )
            with open(f"{path}/{module_folder_name}/{f['fileName']}", "wb") as att:
                att.write(file)

    else:
        api.logger.info("No Evidence at SSP level for SSP. Checking for Evidence at Control level.")


def process_control_attachments(
    ssp: dict, path: Path, progress: Progress, module_folder_name: str, module_folder: Path, api: Api, task: TaskID
) -> None:
    """
    Process Control attachments and download them to the evidence folder

    :param dict ssp: RegScale System Security Plan with mega API data
    :param Path path: directory for file location
    :param Progress progress: Progress object
    :param str module_folder_name: name of the module folder
    :param Path module_folder: path to module folder
    :param Api api: RegScale CLI API object
    :param TaskID task: The task to update on the job_progress
    :rtype: None
    """
    if controls := ssp["normalizedControls"]:
        control_attachments = []
        for i in controls:
            name = i["control"]["item3"]["controlId"]

            for p in i["attachments"]:
                if not p:
                    continue
                file_name = p["trustedDisplayName"]
                stored_name = p["trustedStorageName"]
                parent_id = p["parentId"]
                parent_module = p["parentModule"]
                file_hash = p["fileHash"]
                sha_hash = p["shaHash"]
                file_size = p["size"]
                date_created = p["dateCreated"]

                control_attachments.append(
                    {
                        "controlId": name,
                        "fileName": file_name,
                        "storedName": stored_name,
                        "parentId": parent_id,
                        "parentModule": parent_module,
                        "fileHash": file_hash,
                        "shaHash": sha_hash,
                        "fileSize": file_size,
                        "dateCreated": date_created,
                    }
                )

        progress.update(task, advance=1)

        # Creating folders for Controls with Attachments
        control_folders = []
        for name in control_attachments:
            control_folders.append(name["controlId"])
            control_folders = list(set(control_folders))
        for i in control_folders:
            os.makedirs(module_folder / str(i), exist_ok=True)

        # Adding any Attachments at Control level to corresponding folder
        _download_control_attachments(control_attachments, api, path, module_folder_name)

        progress.update(task, advance=1)

    else:
        api.logger.info("No Control level Evidence for SSP.")


def _download_control_attachments(
    control_attachments: list[dict], api: Api, path: Path, module_folder_name: str
) -> None:
    """
    Download Control attachments to the evidence folder

    :param list[dict] control_attachments: List of control attachments
    :param Api api: RegScale CLI API object
    :param Path path: directory for file location
    :param str module_folder_name: name of the module folder
    :rtype: None
    """
    for f in control_attachments:
        file = File.download_file_from_regscale_to_memory(
            api=api,
            record_id=f["parentId"],
            module=f["parentModule"],
            stored_name=f["storedName"],
            file_hash=f["fileHash"],
        )

        with open(
            f"{path}/{module_folder_name}/{f['controlId']}/{f['fileName']}",
            "wb",
        ) as output:
            output.write(file)
        with open(
            f"{path}/{module_folder_name}/{f['controlId']}/{f['controlId']}_Evidence_Folder_Contents.json",
            "a",
        ) as file_drop:
            json.dump(f, file_drop, indent=4, separators=(", ", ": "))


def remove_directory(directory_path: Path) -> None:
    """
    This function removes a given directory even if files stored there

    :param Path directory_path: file path of directory to remove
    :rtype: None
    """
    shutil.rmtree(directory_path.absolute())
    create_logger().info("Temporary Evidence directory removed successfully!")


def zip_folder(folder_path: Path, zip_path: Path) -> None:
    """
    This function zips up files and folders in a given folder or directory path.

    :param Path folder_path: file path of evidence folder
    :param Path zip_path: file path for zip location of evidence folder
    :rtype: None
    """
    # Create a ZIP file object in write mode
    with zipfile.ZipFile(zip_path.absolute(), "w", zipfile.ZIP_DEFLATED) as zipf:
        # Iterate over all the files and subfolders in the given folder
        for root, dirs, files in os.walk(folder_path.absolute()):
            for file in files:
                # Get the absolute path of the current file
                file_path = os.path.join(root, file)
                # Get the relative path of the current file within the folder
                relative_path = os.path.relpath(file_path, folder_path.absolute())  # type: ignore
                # Add the file to the ZIP archive using its relative path
                zipf.write(file_path, relative_path)  # type: ignore

    create_logger().info("Folder zipped successfully!")


def remove(list_to_review: list) -> list:
    """
    Remove items that start with "."

    :param list list_to_review: list of items to review
    :return: copied list with items removed
    :rtype: list
    """
    copy_list = list_to_review.copy()
    # loop through folder/file list
    for item in list_to_review:
        # if the folder or file starts with '.'
        if item.startswith("."):
            # remove the item from the list
            copy_list.remove(item)
    return copy_list


def delta(time: datetime) -> int:
    """
    Calculates the days between provided datetime object and the datetime function was called

    :param datetime time:
    :return: # of days difference between provided date and datetime function was called
    :rtype: int
    """
    # find time difference between dates
    diff = datetime.now() - time
    # return the difference in integer days
    return diff.days


def calc_score(number: int, score_data: Tuple[list[int], list[int], list[int]]) -> int:
    """
    calculate score

    :param int number: Index in list
    :param Tuple[list[int], list[int], list[int]] score_data: List of scores
    :return: Test score
    :rtype: int
    """
    # bring in score lists
    true_scores = score_data[0]
    total_scores = score_data[2]
    # set score values
    true_score = true_scores[number]
    total_score = total_scores[number]
    # calculate test score for this result and check for zero division
    return int((true_score / total_score) * 100) if int(total_score) != 0 else 0


def find_signatures(file: str) -> int:
    """
    Determine if the file is digitally signed

    :param str file: file path
    :return: # of signatures found
    :rtype: int
    """
    import pymupdf

    number = 0
    logger = create_logger()
    # if the file is a pdf document
    if file.endswith(".pdf"):
        try:
            # open the document
            doc = pymupdf.open(file)
        except pymupdf.FileNotFoundError:
            # set sig flag equal to 0
            number = 0
            logger.warning("no such file %s .", file)
        else:
            # determine if document is digitally signed
            number = doc.get_sigflags()
        # if the sig flag is equal to 3
        if number == 3:
            logger.info("%s has signature fields and has been digitally signed.", file)
        # if the sig flag is equal to 1
        elif number == 1:
            logger.info("%s has signature fields, but has not been digitally signed.", file)
        # if the sig flag is equal to -1
        elif number == -1:
            logger.info("%s has no signature fields to hold a digital signature.", file)
    # if the file is a docx document
    if not file.endswith(".pdf"):
        # set sig flag equal to 0
        number = 0
        logger.warning("%s is not a pdf document.", file)

    # return variable for use outside of local scope
    return number


def set_directory_variables(task: TaskID, evidence_folder: str, progress: Progress) -> Tuple[str, str, str]:
    """
    Set evidence folder directory variables

    :param TaskID task: The task to update on the job_progress
    :param str evidence_folder: File path to evidence folder
    :param Progress progress: Progress object
    :return: Tuple[evidence folder path, directory name, new working directory]
    :rtype: Tuple[str, str, str]
    """
    # set evidence folder variable to init.yaml value
    # if evidence folder does not exist then create it so tests will pass
    check_file_path(evidence_folder)
    # if evidence folder does not exist or if it is empty then error out
    if evidence_folder is None or len(os.listdir(evidence_folder)) <= 1:
        error_and_exit("The directory set to evidenceFolder cannot be found or is empty.")
    else:
        # otherwise change directory to the evidence folder
        os.chdir(evidence_folder)
    progress.update(task, advance=1)
    # include RegScale projects folder
    dir_name = [filename for filename in os.listdir(os.getcwd()) if os.path.isdir(os.path.join(os.getcwd(), filename))][
        0
    ]
    progress.update(task, advance=1)
    # pick up subdirectory under the evidence folder
    new_cwd = os.getcwd() + os.sep + dir_name
    progress.update(task, advance=1)
    # return variables for use outside local scope
    return evidence_folder, dir_name, new_cwd


def parse_required_docs(evidence_folder: str, task: TaskID, progress: Progress) -> Tuple[list[dict], set[str]]:
    """
    build a list of the required documents from config.json

    :param str evidence_folder:
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: Tuple[required_docs, document_list]
    :rtype: Tuple[list[dict], set[str]]
    """
    # create an empty list to hold a list of all document requirements for the assessment
    required_docs = []
    progress.update(task, advance=1)
    # create an empty list to hold a list of all required documents
    document_list = set()
    progress.update(task, advance=1)
    # open app//evidence//config.json file and read contents
    with open(f"{evidence_folder}{os.sep}config.json", "r", encoding="utf-8") as json_file:
        # load json object into a readable dictionary
        rules = json.load(json_file)
        progress.update(task, advance=1)
        # loop through required document dicts
        for i in range(len(rules["required-documents"])):
            # add to a list of dictionaries for parsing
            required_docs.append(
                {
                    "file-name": rules["required-documents"][i].get("file-name"),
                    "last-updated-by": rules["required-documents"][i].get("last-updated-by"),
                    "signatures-required": rules["required-documents"][i].get("signatures-required"),
                    "signature-count": rules["required-documents"][i].get("signature-count"),
                }
            )
            # update contents of list if it does not already exist
            document_list.add(rules["required-documents"][i].get("file-name"))
    progress.update(task, advance=1)
    # return variables for use outside of local scope
    return required_docs, document_list


def get_doc_timestamps(evidence_folder: str, directory: str, task: TaskID, progress: Progress) -> list[dict]:
    """
    Get each file's last modified time

    :param str evidence_folder: File path to evidence folder
    :param str directory: File path to directory
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: list of dictionaries
    :rtype: list[dict]
    """
    # create empty list to hold file modified times
    modified_times: list[dict] = []
    progress.update(task, advance=1)
    # get list of folders in parent folder
    folders_list = os.listdir(evidence_folder)
    progress.update(task, advance=1)
    # remove any child folders that start with '.'
    new_folders = remove(list_to_review=folders_list)
    progress.update(task, advance=1)
    # loop through directory listing
    for folder in new_folders:
        # get list of files in each folder
        filelist = os.listdir(os.path.join(evidence_folder, folder))
        # remove any files that start with '.'
        remove(list_to_review=filelist)
        # loop through list of files in each folder
        modified_times.extend(
            {
                "program": folder,
                "file": filename,
                "last-modified": os.path.getmtime(os.path.join(directory, folder, filename)),
            }
            for filename in filelist
        )
    progress.update(task, advance=1)
    # loop through the list of timestamps
    for i, time_data in enumerate(modified_times):
        # update the last-modified value to be the count of days
        modified_times[i].update({"last-modified": delta(time=datetime.fromtimestamp(time_data["last-modified"]))})
    progress.update(task, advance=1)
    # return variable for use outside local scope
    return modified_times


def set_required_texts(evidence_folder: str, task: TaskID, progress: Progress) -> set[str]:
    """
    parse config.json file and build a list of the required texts for the assessment

    :param str evidence_folder: File path to evidence folder
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: Required text
    :rtype: set[str]
    """
    # create an empty set to hold all unique required texts for the assessment
    required_text = set()
    progress.update(task, advance=1)
    # open app//evidence//config.json file and read contents
    with open(f"{evidence_folder}{os.sep}config.json", "r", encoding="utf-8") as json_file:
        # load json object into a readable dictionary
        rules = json.load(json_file)
        progress.update(task, advance=1)
        # create iterator to traverse dictionary
        for i in range(len(rules["rules-engine"])):
            # pull out required text to look for from config
            for items in rules["rules-engine"][i]["text-to-find"]:
                # exclude duplicate text to search from required text
                required_text.add(items)
        progress.update(task, advance=1)
    # return variable for use outside of local scope
    return required_text


def find_required_files_in_folder(evidence_folder: str, task: TaskID, progress: Progress) -> list[dict]:
    """
    Pull out required files from each directory for parsing

    :param str evidence_folder: File path to evidence folder
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of directories
    :rtype: list[dict]
    """
    # create empty list to hold list of files in directory
    dir_list: list[dict] = []
    progress.update(task, advance=1)
    # build a list of all folders to iterate through
    folder_list = os.listdir(evidence_folder)
    progress.update(task, advance=1)
    # remove any folders starting with '.' from list
    new_folders_list = remove(folder_list)
    progress.update(task, advance=1)
    for folder in new_folders_list:
        # build a list of all files contained in sub-directories
        filelist = os.listdir(evidence_folder + os.sep + folder)
        # remove folders and file names that start with a .
        remove(filelist)
        dir_list.extend({"program": folder, "file": filename} for filename in filelist)
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return dir_list


def signature_assessment_results(
    directory: list[dict], r_docs: list[dict], task: TaskID, progress: Progress
) -> list[dict]:
    """
    Compares signature config parameter against signature detection

    :param list[dict] directory: List of directories
    :param list[dict] r_docs: List of documents
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: Assessment of signatures
    :rtype: list[dict]
    """
    # create empty list to hold assessment results
    sig_assessments: list[dict] = []
    progress.update(task, advance=1)
    # loop through list of found documents in each sub-folder
    for doc_file in directory:
        for required in r_docs:
            if doc_file["file"] == required["file-name"]:
                # if the signatures-required field is set to true
                if required["signatures-required"] is True:
                    # run the signature detection function for the file
                    sig_result = find_signatures(doc_file["file"])
                    # if the return value is 3 pass the test
                    if sig_result == 3:
                        # append a true result for each document tested
                        sig_assessments.append(
                            {
                                "program": doc_file["program"],
                                "file": doc_file["file"],
                                "test": "signature-required",
                                "result": True,
                            }
                        )
                    # if the return value is 1, -1 or 0 fail the test
                    else:
                        # append a false result for each document tested
                        sig_assessments.append(
                            {
                                "program": doc_file["program"],
                                "file": doc_file["file"],
                                "test": "signature-required",
                                "result": False,
                            }
                        )
                # if the signatures-required field is set to false
                if required["signatures-required"] is False:
                    # append a true result for each document not requiring a signature
                    sig_assessments.append(
                        {
                            "program": doc_file["program"],
                            "file": doc_file["file"],
                            "test": "signature-required (not required)",
                            "result": True,
                        }
                    )
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return sig_assessments


def document_assessment_results(
    directory: list[dict], documents: set[str], task: TaskID, progress: Progress
) -> list[dict]:
    """
    Test if required documents are present in each directory

    :param list[dict] directory: List of directories
    :param set[str] documents: List of documents
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of assessments of provided documents in the provided directory
    :rtype: list[dict]
    """
    # create empty list to hold assessment results
    doc_assessments: list[dict] = []
    progress.update(task, advance=1)
    # loop through list of found documents in each sub-folder
    for doc_file in directory:
        # if the file in the sub-folder is in the required documents list
        if doc_file["file"] in documents:
            # append a true result for each file in each program
            doc_assessments.append(
                {
                    "program": doc_file["program"],
                    "file": doc_file["file"],
                    "test": "required-documents",
                    "result": True,
                }
            )
        else:
            # append a false result for each file in each program
            doc_assessments.append(
                {
                    "program": doc_file["program"],
                    "file": doc_file["file"],
                    "test": "required-documents",
                    "result": False,
                }
            )
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return doc_assessments


def parse_required_text_from_files(evidence_folder: str, task: TaskID, progress: Progress) -> list[dict]:
    """
    Parse text from docx/pdf file and hold strings representing required text to test

    :param str evidence_folder: File path to the evidence folder
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: Results of text found for the files
    :rtype: list[dict]
    """
    # create an empty list to hold all strings from parsed documents
    full_text: list[dict] = []
    progress.update(task, advance=1)
    # build a list of files in the folder
    folder_list = os.listdir(evidence_folder)
    progress.update(task, advance=1)
    # remove all folders that start with '.'
    removed_folders_list = remove(folder_list)
    progress.update(task, advance=1)
    for folder in removed_folders_list:
        # create a list of files to iterate through for parsing
        file_list = os.listdir((os.path.join(evidence_folder, folder)))
        remove(file_list)
        # iterate through all files in the list
        for filename in file_list:
            # if the filename is a .docx file
            if filename.endswith(".docx"):
                # open the Word document to enable parsing
                document = Document(os.path.join(evidence_folder, folder, filename))
                output: list[str] = [para.text for para in document.paragraphs]
                # add each file and the requisite text to the dictionary to test
                full_text.append({"program": folder, "file": filename, "text": output})
            elif filename.endswith(".pdf"):
                # create empty list to hold text per file
                output_text_list: list[str] = []
                # open filename with pdfplumber
                with pdfplumber.open(filename) as pdf:
                    # set number of pages
                    pages = pdf.pages
                    # for each page in the pdf document
                    for page in pages:
                        # extract the text
                        text = page.extract_text()
                        # write the text to a list
                        output_text_list.append(text)
                    # add each file and the requisite text to the dictionary to test
                    full_text.append(
                        {
                            "program": folder,
                            "file": filename,
                            "text": output_text_list,
                        }
                    )
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return full_text


def text_string_search(f_texts: list[dict], req_texts: set[str], task: TaskID, progress: Progress) -> list[dict]:
    """
    Search for required texts in document paragraphs

    :param list[dict] f_texts: List of documents
    :param set[str] req_texts: Required text
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: Results of searched text in documents
    :rtype: list[dict]
    """
    # create empty list to hold assessment results
    search_list: list[dict] = []
    progress.update(task, advance=1)
    # iterate through each sentence in the required texts
    for parsed_file, line in itertools.product(f_texts, req_texts):
        # if the required text appears in the parsed paragraph
        if any(line in text for text in parsed_file["text"]):
            # then create a "True" entry in the empty list
            search_list.append(
                {
                    "program": parsed_file["program"],
                    "file": parsed_file["file"],
                    "text": line,
                    "result": True,
                }
            )
        else:
            # else create a "False" entry in the empty list
            search_list.append(
                {
                    "program": parsed_file["program"],
                    "file": parsed_file["file"],
                    "text": line,
                    "result": False,
                }
            )
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return search_list


def text_assessment_results(searches: list[dict], r_texts: set[str], task: TaskID, progress: Progress) -> list[dict]:
    """
    Test if required text is present in required files and return test assessment

    :param list[dict] searches: List of results
    :param set[str] r_texts: Required text
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of results
    :rtype: list[dict]
    """
    # create empty list to hold assessment results
    text_results: list[dict] = []
    progress.update(task, advance=1)
    # loop through text string search results
    for result, line in itertools.product(searches, r_texts):
        # if the text matches the required text
        if result["text"] == line and result["result"] is True:
            text_info = result["text"]
            # condense results into 1 per file
            text_results.append(
                {
                    "program": result["program"],
                    "file": result["file"],
                    "test": f"required-text ({text_info})",
                    "result": result["result"],
                }
            )
    # return variable for use outside of local scope
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return text_results


def gather_test_project_data(api: Api, evidence_folder: str, task: TaskID, progress: Progress) -> list[dict]:
    """
    Gather information from evidence test projects created in RegScale to catch data

    :param Api api: API object
    :param str evidence_folder: File path to evidence folder
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of results
    :rtype: list[dict]
    """
    # create empty list to hold project test data from GET API call
    test_data: list[dict] = []
    progress.update(task, advance=1)
    # test project information created in RegScale UI
    with open(evidence_folder + os.sep + "list.json", "r", encoding="utf-8") as json_file:
        # load json object into a readable dictionary
        lists = json.load(json_file)
        # loop through projects in the list.json
        test_data.extend(
            {
                "id": lists["parser-list"][i].get("id"),
                "program": lists["parser-list"][i].get("folder-name"),
            }
            for i in range(len(lists["parser-list"]))
        )
    progress.update(task, advance=1)
    # create empty list to hold json response data for each project
    test_info: list[dict] = []
    # iterate through test projects and make sequential GET API calls
    for item in test_data:
        # make a GET request for each project
        if project := Project.get_object(item["id"]):
            api.logger.info("Project data retrieval was successful.")
            # save the json response data
            test_info.append(
                {
                    "id": project.id,
                    "title": project.title,
                    "uuid": project.uuid,
                    "projectmanagerid": project.projectmanagerid,
                    "parentid": project.parentId,
                    "parentmodule": project.parentModule,
                    "program": project.program,
                }
            )
        else:
            api.logger.error("Project data retrieval was unsuccessful.")
    progress.update(task, advance=1)
    # return variables for use outside of local scope
    return test_info


def assess_doc_timestamps(
    timestamps: list[dict], documents: list[dict], task: TaskID, progress: Progress
) -> list[dict]:
    """
    Test file modification times

    :param list[dict] timestamps: list of modified timestamps
    :param list[dict] documents: list of documents
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of documents sorted by modified date
    :rtype: list[dict]
    """
    # create empty list to store test results
    assessed_timestamps = []
    progress.update(task, advance=1)
    # loop through timestamps
    for items in timestamps:
        # loop through required documents
        for doc_items in documents:
            # if file names match between the list of dicts
            if fnmatch.fnmatch(items["file"], doc_items["file-name"]):
                # if the required modification time is less than the last modified days
                if items["last-modified"] < doc_items["last-updated-by"]:
                    # append true result to the list of dicts
                    assessed_timestamps.append(
                        {
                            "program": items["program"],
                            "file": items["file"],
                            "test": "last-updated-by",
                            "result": True,
                        }
                    )
                else:
                    # append false results to the list of dicts
                    assessed_timestamps.append(
                        {
                            "program": items["program"],
                            "file": items["file"],
                            "test": "last-updated-by",
                            "result": False,
                        }
                    )
    progress.update(task, advance=1)
    # return variables for use outside of local scope
    return assessed_timestamps


def assessments_report(
    docres: list[dict],
    textres: list[dict],
    timeres: list[dict],
    sigres: list[dict],
    task: TaskID,
    progress: Progress,
) -> list[dict]:
    """
    Function that builds the assessment report for all results

    :param list[dict] docres: List of document results
    :param list[dict] textres: List of text results
    :param list[dict] timeres: List of time results
    :param list[dict] sigres: List of signature results
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of assessment report for all results
    :rtype: list[dict]
    """
    progress.update(task, advance=1)
    assessment_report: list[dict] = list(docres)
    progress.update(task, advance=1)
    # append all results to 1 master list
    assessment_report.extend(iter(textres))
    progress.update(task, advance=1)
    # append all results to 1 master list
    assessment_report.extend(iter(timeres))
    progress.update(task, advance=1)
    # append all results to 1 master list
    assessment_report.extend(iter(sigres))
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return assessment_report


def build_assessment_dataframe(assessments: list[dict], task: TaskID, progress: Progress) -> list[dict]:
    """
    Build dataframe for assessment results

    :param list[dict] assessments: List of results
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of results containing panda's data frames
    :rtype: list[dict]
    """
    # build out dataframe for score calculations
    import pandas as pd  # Optimize import performance

    result_df = pd.DataFrame(assessments)
    progress.update(task, advance=1)
    # fill in NaN cells
    result_df = result_df.fillna(" ")
    progress.update(task, advance=1)
    # loop through the program column and split based on values
    dfs = [d for _, d in result_df.groupby("program")]
    # create an empty list to store dataframe results
    result_list: list[dict] = []
    progress.update(task, advance=1)
    # loop through dataframes
    for dfr in dfs:
        # pull out unique value counts for true
        true_counts = dfr["result"].value_counts()
        true_counts = dict(true_counts)
        # pull out unique value counts for false
        false_counts = dfr["result"].value_counts()
        false_counts = dict(false_counts)
        # create ints to hold count values
        pass_count: int
        fail_count: int
        pass_count = 0
        fail_count = 0
        # loop through true_counts list
        for i in true_counts:
            # if value is true
            if i is True:
                # set equal to pass value
                pass_count = true_counts[i]
            if i is False:
                # set equal to fail value
                fail_count = false_counts[i]
        # output results to list of results
        result_list.append(
            {
                "program": dfr["program"].iloc[0],
                "true": max(pass_count, 0),
                "false": max(fail_count, 0),
                "total": len(dfr),
            }
        )
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return result_list


def build_score_data(
    assessments: list[dict], task: TaskID, progress: Progress
) -> Tuple[list[int], list[int], list[int]]:
    """
    Build assessment score lists

    :param list[dict] assessments: list of assessments to build scores
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: Tuple[list of integers of true list, list of integers of false list, list of integers of total list]
    :rtype: Tuple[list[int], list[int], list[int]]
    """
    # create empty lists to hold true/false counts
    true_list: list[int] = []
    progress.update(task, advance=1)
    false_list: list[int] = []
    progress.update(task, advance=1)
    total_list: list[int] = []
    progress.update(task, advance=1)
    # loop through assessment report data
    for item in assessments:
        # append true/false/total values to lists
        true_list.append(item["true"])
        false_list.append(item["false"])
        total_list.append(item["total"])
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return true_list, false_list, total_list


def build_html_table(assessments: list[dict], task: TaskID, progress: Progress) -> list[dict]:
    """
    This wil be a dictionary to html table conversion

    :param list[dict] assessments: List of file assessments
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :return: List of assessments with HTML formatted data tables
    :rtype: list[dict]
    """
    import pandas as pd  # Optimize import performance

    output_list: list[dict] = []
    # create a dataframe of a list of dicts
    table_df = pd.DataFrame(data=assessments)
    progress.update(task, advance=1)
    # fill in N/A cells with blank string
    table_df = table_df.fillna(" ")
    progress.update(task, advance=1)
    # split dataframe into list of dataframes
    dfs = [d for _, d in table_df.groupby("program")]
    progress.update(task, advance=1)
    # loop through dataframes
    for table_df in dfs:
        # output dataframe to an HTML table
        output = table_df.to_html()
        progress.update(task, advance=1)
        # replace false values with inline styling conditional to red colors for False values
        output = output.replace("<td>False</td>", '<td style="color:red;">False</td>')
        progress.update(task, advance=1)
        # replace true values with inline styling conditional to green colors for True values
        output = output.replace("<td>True</td>", '<td style="color:green;">True</td>')
        progress.update(task, advance=1)
        # build list of outputs to loop through for API POST calls
        output_list.append({"program": table_df["program"].iloc[0], "html": output})
    progress.update(task, advance=1)
    # return variable for use outside of local scope
    return output_list


def create_child_assessments(
    api: Api,
    project_data: list[dict],
    output: list[dict],
    score_data: Tuple[list[int], list[int], list[int]],
    task: TaskID,
    progress: Progress,
) -> None:
    """
    Create assessments based on results of text parsing tests into RegScale via API

    :param Api api: API object
    :param list[dict] project_data: list of results to part and upload to RegScale
    :param list[dict] output: HTML output of the results
    :param Tuple[list[int], list[int], list[int]] score_data: list of scores
    :param TaskID task: The task to update on the job_progress
    :param Progress progress: Progress object
    :rtype: None
    """
    # set completion datetime to required format
    completion_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    progress.update(task, advance=1)
    # loop through test projects and make an API call for each
    for i, project in enumerate(project_data):
        # call score calculation function
        test_score = calc_score(i, score_data)
        # if file name matches html output table program name
        if project_data[i]["program"] == output[i]["program"]:
            # build assessment data
            assessment_data = Assessment(
                status="Complete",
                leadAssessorId=api.config["userId"],
                title="Evidence Collection Automation Assessment",
                assessmentType="Inspection",
                projectId=project["id"],
                parentId=project["id"],
                parentModule="projects",
                assessmentReport=output[i]["html"],
                assessmentPlan="Review automated results of evidence collection tests",
                createdById=api.config["userId"],
                lastUpdatedById=api.config["userId"],
                complianceScore=test_score,
                plannedFinish=completion_date,
                plannedStart=completion_date,
                actualFinish=completion_date,
            )
            # if all tests passed above score update POST call information
            if test_score >= api.config["passScore"]:
                # update assessment data API body information
                assessment_data.assessmentResult = "Pass"
            # if all tests failed below score update POST call information
            elif test_score <= api.config["failScore"]:
                # update assessment data API body information
                assessment_data.assessmentResult = "Fail"
                # if some tests passed in between score update POST call information
            else:
                # update assessment data API body information
                assessment_data.assessmentResult = "Partial Pass"
            if assessment_data.create():
                api.logger.info("Child assessment creation was successful.")
            else:
                api.logger.warning("Child assessment creation was not successful.")
    progress.update(task, advance=1)
