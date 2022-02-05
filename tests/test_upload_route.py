import io
import pathlib
import pytest
from flask import current_app, session


class TestUpload:
    @pytest.mark.parametrize(
        ["file_ending", "api_response"], (["csv", 202], ["doc", 415], ["csv.exe", 415])
    )
    def test_can_only_upload_csv(self, client, file_ending, api_response):
        response = client.post(
            "/upload",
            data={
                "files": [
                    (io.BytesIO(b"abcd"), f"mentors.{file_ending}"),
                    (io.BytesIO(b"abcd"), f"mentees.{file_ending}"),
                ]
            },
            content_type="multipart/form-data",
        )
        assert response.status_code == api_response

    @pytest.mark.parametrize(
        ["files", "api_response"],
        [
            (
                [
                    (io.BytesIO(b"abcd"), "mentors.csv"),
                    (io.BytesIO(b"abcd"), "mentees.csv"),
                ],
                202,
            ),
            ([(io.BytesIO(b"abcd"), "mentors.csv")], 415),
            ([(io.BytesIO(b"abcd"), "mentees.csv")], 415),
            (
                [
                    (io.BytesIO(b"abcd"), "mentors.csv"),
                    (io.BytesIO(b"abcd"), "mentees.csv"),
                    (io.BytesIO(b"abcd"), "other.csv"),
                ],
                415,
            ),
            (
                [
                    (io.BytesIO(b"abcd"), "unkown/random/path/mentors.csv"),
                    (io.BytesIO(b"abcd"), "unkown/random/path/mentees.csv"),
                ],
                202,
            ),
        ],
    )
    def test_must_upload_two_files(self, client, files, api_response):
        response = client.post(
            "/upload", data={"files": files}, content_type="multipart/form-data"
        )
        assert response.status_code == api_response

    @pytest.mark.parametrize(
        ["filenames", "api_response"],
        (
            (["mentors", "mentees"], 202),
            (["mentors", "menteees"], 415),
            (["MENTORS", "MENTEES"], 202),
        ),
    )
    def test_filenames_are_mentors_and_mentees(self, client, filenames, api_response):
        response = client.post(
            "/upload",
            data={
                "files": [
                    (io.BytesIO(b"abcd"), f"{filenames[0]}.csv"),
                    (io.BytesIO(b"abcd"), f"{filenames[1]}.csv"),
                ]
            },
            content_type="multipart/form-data",
        )
        assert response.status_code == api_response

    def test_upload_saves_file(self, client, test_data_path):
        client.post(
            "/upload",
            data={
                "files": [
                    (io.BytesIO(b"abcd"), "mentors.csv"),
                    (io.BytesIO(b"abcd"), "mentees.csv"),
                ]
            },
            content_type="multipart/form-data",
        )
        assert pathlib.Path(
            current_app.config["UPLOAD_FOLDER"], "abcdef", "mentors.csv"
        ).exists()

    def test_session_has_folder_name(self, client):
        client.post(
            "/upload",
            data={
                "files": [
                    (io.BytesIO(b"abcd"), "mentors.csv"),
                    (io.BytesIO(b"abcd"), "mentees.csv"),
                ]
            },
            content_type="multipart/form-data",
        )
        assert session["data-folder"] == "abcdef"
