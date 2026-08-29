import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock, ANY

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github_tools.create_repo import create_repo
from github_tools.create_file import create_file
from github_tools.delete_file import delete_file
from github_tools.get_file_list import get_file_list
from github_tools.read_file import read_file
from github_tools.write_file import write_file

@pytest.fixture(autouse=True)
def mock_github_key(monkeypatch):
    fake_token = "fake_token"
    import github_tools.create_repo
    import github_tools.create_file
    import github_tools.delete_file
    import github_tools.get_file_list
    import github_tools.read_file
    import github_tools.write_file

    monkeypatch.setattr(github_tools.create_repo, 'github_key', fake_token)
    monkeypatch.setattr(github_tools.create_file, 'github_key', fake_token)
    monkeypatch.setattr(github_tools.delete_file, 'github_key', fake_token)
    monkeypatch.setattr(github_tools.get_file_list, 'github_key', fake_token)
    monkeypatch.setattr(github_tools.read_file, 'github_key', fake_token)
    monkeypatch.setattr(github_tools.write_file, 'github_key', fake_token)
    monkeypatch.setenv("GITHUB_PAT", fake_token)

@patch('github_tools.create_repo.requests.post')
def test_create_repo_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"name": "test-repo", "private": False}
    mock_post.return_value = mock_response

    result = create_repo("test-repo", public=True)

    mock_post.assert_called_once_with(
        "https://api.github.com/user/repos",
        headers={"Authorization": "token fake_token", "Accept": "application/vnd.github_tools.v3+json"},
        json={"name": "test-repo", "private": False}
    )
    assert result == {"name": "test-repo", "private": False}

@patch('github_tools.create_repo.requests.post')
def test_create_repo_private(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"name": "private-repo", "private": True}
    mock_post.return_value = mock_response

    result = create_repo("private-repo", public=False)

    mock_post.assert_called_once_with(
        "https://api.github.com/user/repos",
        headers={"Authorization": "token fake_token", "Accept": "application/vnd.github_tools.v3+json"},
        json={"name": "private-repo", "private": True}
    )
    assert result["private"] is True

@patch('github_tools.create_file.requests.get')
@patch('github_tools.create_file.requests.put')
def test_create_file_new(mock_put, mock_get):
    mock_get_response = MagicMock()
    mock_get_response.status_code = 404
    mock_get.return_value = mock_get_response

    mock_put_response = MagicMock()
    mock_put_response.status_code = 201
    mock_put_response.json.return_value = {"content": {"name": "hello.py"}}
    mock_put.return_value = mock_put_response

    result = create_file("owner/repo", "src/hello.py", "print('Hello')", "Create file", "main")

    mock_put.assert_called_once()
    args, kwargs = mock_put.call_args
    assert kwargs["json"]["message"] == "Create file"
    assert kwargs["json"]["branch"] == "main"
    assert "content" in kwargs["json"]
    assert result == {"content": {"name": "hello.py"}}

@patch('github_tools.create_file.requests.get')
def test_create_file_already_exists(mock_get):
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get.return_value = mock_get_response

    with pytest.raises(Exception) as excinfo:
        create_file("owner/repo", "hello.py", "content")
    assert "already exists" in str(excinfo.value)

@patch('github_tools.delete_file.requests.get')
@patch('github_tools.delete_file.requests.delete')
def test_delete_file_success(mock_delete, mock_get):
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {"sha": "abc123"}
    mock_get.return_value = mock_get_response

    mock_delete_response = MagicMock()
    mock_delete_response.status_code = 200
    mock_delete_response.json.return_value = {"commit": {"sha": "new_commit"}}
    mock_delete.return_value = mock_delete_response

    result = delete_file("owner/repo", "hello.py", "Delete file", "main")

    mock_delete.assert_called_once()
    args, kwargs = mock_delete.call_args
    assert kwargs["json"]["sha"] == "abc123"
    assert kwargs["json"]["message"] == "Delete file"
    assert kwargs["json"]["branch"] == "main"
    assert result == {"commit": {"sha": "new_commit"}}

@patch('github_tools.delete_file.requests.get')
def test_delete_file_not_found(mock_get):
    mock_get_response = MagicMock()
    mock_get_response.status_code = 404
    mock_get.return_value = mock_get_response

    with pytest.raises(Exception) as excinfo:
        delete_file("owner/repo", "missing.txt")
    assert "not found" in str(excinfo.value)

@patch('github_tools.get_file_list.requests.get')
def test_get_file_list_root(mock_get):
    def side_effect(url, headers):
        if url.endswith("/contents/"):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = [
                {"type": "file", "name": "README.md", "path": "README.md"},
                {"type": "dir", "name": "src", "path": "src"},
            ]
            return mock_resp
        elif "src" in url:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = []
            return mock_resp
        else:
            raise AssertionError("Unexpected URL")

    mock_get.side_effect = side_effect

    result = get_file_list("owner/repo")

    assert isinstance(result, dict)
    assert "files" in result
    files_list = result["files"]
    assert isinstance(files_list, list)
    assert len(files_list) == 2
    items = [item for item in files_list if isinstance(item, str)]
    dirs = [item for item in files_list if isinstance(item, dict)]
    assert "README.md" in items
    assert len(dirs) == 1
    assert "src" in dirs[0]

@patch('github_tools.get_file_list.requests.get')
def test_get_file_list_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_file_list("owner/repo", "nonexistent")
    assert isinstance(result, dict)
    assert "error" in result
    assert "not found" in result["error"]

@patch('github_tools.read_file.requests.get')
def test_read_file_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "content": "cHJpbnQoJ0hlbGxvJyk=",
        "sha": "abc123"
    }
    mock_get.return_value = mock_response

    content = read_file("owner/repo", "hello.py")
    assert content == "print('Hello')"

@patch('github_tools.write_file.requests.get')
@patch('github_tools.write_file.requests.put')
def test_write_file_new(mock_put, mock_get):
    mock_get_response = MagicMock()
    mock_get_response.status_code = 404
    mock_get.return_value = mock_get_response

    mock_put_response = MagicMock()
    mock_put_response.status_code = 200
    mock_put_response.json.return_value = {"content": {"name": "hello.py"}}
    mock_put.return_value = mock_put_response

    result = write_file(repo="owner/repo", path="hello.py", content="print('Hi')", message="Write file")
    mock_put.assert_called_once()
    assert result == {"content": {"name": "hello.py"}}

@patch('github_tools.write_file.requests.get')
@patch('github_tools.write_file.requests.put')
def test_write_file_update(mock_put, mock_get):
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = {"sha": "old_sha"}
    mock_get.return_value = mock_get_response

    mock_put_response = MagicMock()
    mock_put_response.status_code = 200
    mock_put_response.json.return_value = {"content": {"name": "hello.py"}}
    mock_put.return_value = mock_put_response

    result = write_file(repo="owner/repo", path="hello.py", content="print('Updated')", message="Update file")
    args, kwargs = mock_put.call_args
    assert kwargs["json"]["sha"] == "old_sha"
    assert kwargs["json"]["message"] == "Update file"