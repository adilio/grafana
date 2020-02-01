from __future__ import (absolute_import, division, print_function)

from unittest import TestCase
from unittest.mock import patch, MagicMock
from ansible_collections.community.grafana.plugins.modules import grafana_team
from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic
from ansible.module_utils.urls import basic_auth_header
import json

__metaclass__ = type


class MockedReponse(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def unauthorized_resp():
    return (None, {"status": 401})


def permission_denied_resp():
    return (None, {"status": 403})


def get_version_resp():
    return {"major": 6, "minor": 0, "rev": 0}


def get_low_version_resp():
    return {"major": 4, "minor": 6, "rev": 0}


def team_exists_resp():
    server_response = json.dumps({"totalCount": 1, "teams": [{"name": "MyTestTeam", "email": "email@test.com"}]}, sort_keys=True)
    return (MockedReponse(server_response), {"status": 200})


def team_not_found_resp():
    server_response = json.dumps({"totalCount": 0, "teams": []})
    return (MockedReponse(server_response), {"status": 200})


def team_created_resp():
    server_response = json.dumps({"message": "Team created", "teamId": 2})
    return (MockedReponse(server_response), {"status": 200})


def team_updated_resp():
    server_response = json.dumps({"message": "Team updated"})
    return (MockedReponse(server_response), {"status": 200})


def team_deleted_resp():
    server_response = json.dumps({"message": "Team deleted"})
    return (MockedReponse(server_response), {"status": 200})


def team_members_resp():
    server_response = json.dumps([{
        "orgId": 1,
        "teamId": 2,
        "userId": 3,
        "email": "user1@email.com",
        "login": "user1",
        "avatarUrl": r"\/avatar\/1b3c32f6386b0185c40d359cdc733a79"
    }, {
        "orgId": 1,
        "teamId": 2,
        "userId": 2,
        "email": "user2@email.com",
        "login": "user2",
        "avatarUrl": r"\/avatar\/cad3c68da76e45d10269e8ef02f8e73e"
    }])
    return (MockedReponse(server_response), {"status": 200})


def team_members_no_members_resp():
    server_response = json.dumps([])
    return (MockedReponse(server_response), {"status": 200})


def add_team_member_resp():
    server_response = json.dumps({"message": "Member added to Team"})
    return (MockedReponse(server_response), {"status": 200})


def delete_team_member_resp():
    server_response = json.dumps({"message": "Team Member removed"})
    return (MockedReponse(server_response), {"status": 200})


class GrafanaTeamsTest(TestCase):

    def setUp(self):
        self.authorization = basic_auth_header("admin", "admin")
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)

        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)


    def test_diff_members_function(self):
        list1 = ["foo@example.com", "bar@example.com"]
        list2 = ["bar@example.com", "random@example.com"]

        res = grafana_team.diff_members(list1, list2)
        self.assertEquals(res, {"to_del": ["random@example.com"], "to_add": ["foo@example.com"]})
