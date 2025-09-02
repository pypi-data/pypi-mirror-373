import io


def upload_document(create_client_and_cleanup):
    client = create_client_and_cleanup
    file_content = b"Hello, this is the content of the file."
    file_name = "example.txt"

    # Create an in-memory byte stream
    file = io.BytesIO(file_content)

    files = {"file": (file_name, file, "multipart/form-data")}

    # Make the request
    response = client.post("/upload_file/v0", files=files)

    return response.json()


def test_read_main(create_client_and_cleanup):
    #################################
    # download file test case
    #################################
    client = create_client_and_cleanup

    upload_result = upload_document(client)
    uploaded_file_storage_token = upload_result["data"]["main"]
    parameter = {"file_storage_token": uploaded_file_storage_token}

    # Make the request
    response = client.get("/download_file/v0", params=parameter)

    # Assert the response status code
    assert response.status_code == 200
