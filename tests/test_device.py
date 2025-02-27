import asyncio
import json
import uuid
from random import choice
from unittest import skip

from pydantic import Field

from tests.base import TestCaseWithLog, TestWithLocations, async_test
from tests.testutil import available_mac_address, calling_users, create_workspace_with_webex_calling
from wxc_sdk.devices import TagOp
from wxc_sdk.workspaces import Workspace, CallingType, WorkspaceSupportedDevices


# TODO: validate all new endpoint signatures

class TestDevice(TestCaseWithLog):
    def test_001_list(self):
        """
        list all devices
        """
        devices = list(self.api.devices.list())
        print(f'Got {len(devices)} devices.')
        dn_len = max((len(d.display_name) for d in devices))
        prod_len = max((len(d.product) for d in devices))
        print('\n'.join(f'{d.display_name:{dn_len}}, {d.product:{prod_len}}, '
                        f'{"personal" if d.person_id else "workspace"}'
                        for d in devices))

    @async_test
    async def test_002_list_validate_workspace_id(self):
        """
        List all devices and get workspace details
        """
        devices = [d for d in self.api.devices.list()
                   if d.workspace_id]
        print(f'Got {len(devices)} devices with workspace IDs')
        if not devices:
            self.skipTest('No devices with workspace ids')
        workspace_ids = set(d.workspace_id for d in devices)
        workspaces = await asyncio.gather(*[self.async_api.workspaces.details(workspace_id=ws_id)
                                            for ws_id in workspace_ids])
        print(f'Got details for {len(workspaces)} workspaces.')

    @async_test
    async def test_003_list_by_type(self):
        """
        Try to list devices by type and verify if only devices of given type are returned
        """
        product_types = sorted(set(device.product_type for device in self.api.devices.list()))
        if not product_types:
            self.skipTest('no devices with product type')

        # get list of devices for each product type
        device_lists = await asyncio.gather(*[self.async_api.devices.list(product_type=pt) for pt in product_types],
                                            return_exceptions=True)

        # check each list
        err = False
        for product_type, device_list in zip(product_types, device_lists):
            listed_types = set(device.product_type for device in device_list)
            if len(listed_types) > 1:
                print(f'list for product type "{product_type}" has devices '
                      f'with product types: {", ".join(sorted(listed_types))}')
                err = True
            if product_type not in listed_types:
                print(f'list for product type "{product_type}" has no devices of that type')
                err = True
        self.assertFalse(err, 'Failed: see output')

    @async_test
    async def test_004_details(self):
        """
        Get details for all devices
        """
        devices = list(self.api.devices.list())
        if not devices:
            self.skipTest('No devices')
        details = await asyncio.gather(*[self.async_api.devices.details(device_id=device.device_id)
                                         for device in devices])
        print(f'Got details for {len(details)} devices')

    def test_005_patch_tags(self):
        """
        try to patch tags
        """
        with self.no_log():
            devices = list(self.api.devices.list())
        if not devices:
            self.skipTest('No devices')
        target = choice(devices)
        target = self.api.devices.details(device_id=target.device_id)
        tags = target.tags
        new_tags = [str(uuid.uuid4()) for _ in range(3)]
        self.api.devices.modify_device_tags(device_id=target.device_id,
                                            op=TagOp.add, value=new_tags)
        details = self.api.devices.details(device_id=target.device_id)
        tags_after = details.tags
        try:
            self.assertEqual(set(tags + new_tags), set(tags_after))
        finally:
            self.api.devices.modify_device_tags(device_id=target.device_id,
                                                op=TagOp.remove,
                                                value=new_tags)
            details = self.api.devices.details(device_id=target.device_id)
            self.assertEqual(tags, details.tags)


class CreateDevice(TestWithLocations):
    """
    Various tests to create devices
    """
    workspaces: list[Workspace] = Field(default_factory=list)

    def setUp(self) -> None:
        super().setUp()
        self.workspaces = list(self.api.workspaces.list())

    def workspaces_w_calling(self) -> list[Workspace]:
        result = [w for w in self.workspaces
                  if w.calling and w.calling.type == CallingType.webex]
        return result

    def get_or_create_calling_workspace_wo_devices(self,
                                                   supported_devices: WorkspaceSupportedDevices = None) -> Workspace:
        """
        Get or create a calling enabled workspace with no devices. This workspace can then be used for device creation
        tests
        """
        supported_devices = supported_devices or WorkspaceSupportedDevices.phones
        workspace_w_devices = set(device.workspace_id for device in self.api.devices.list()
                                  if device.workspace_id)
        workspaces = [w for w in self.workspaces_w_calling()
                      if w.supported_devices == supported_devices and w.workspace_id not in workspace_w_devices]
        if workspaces:
            return choice(workspaces)
        location = choice(self.locations)
        workspace = create_workspace_with_webex_calling(api=self.api, target_location=location,
                                                        supported_devices=supported_devices)
        return workspace

    def test_001_activation_code_workspace_room(self):
        """
        Try to create an activation code for a workspace room device
        """
        target = self.get_or_create_calling_workspace_wo_devices(
            supported_devices=WorkspaceSupportedDevices.collaboration_devices)
        ac_result = self.api.devices.activation_code(workspace_id=target.workspace_id)
        print(f'Workspace "{target.display_name}", new activation code "{ac_result.code}" '
              f'valid until {ac_result.expiry_time}')

    def test_001_activation_code_workspace_mpp(self):
        """
        Try to create an activation code for a workspace MPP device
        """
        model = 'DMS Cisco 8851'
        target = self.get_or_create_calling_workspace_wo_devices(supported_devices=WorkspaceSupportedDevices.phones)
        ac_result = self.api.devices.activation_code(workspace_id=target.workspace_id, model=model)
        print(json.dumps(json.loads(ac_result.json()), indent=2))
        print(f'Workspace "{target.display_name}", new activation code "{ac_result.code}" '
              f'valid until {ac_result.expiry_time}')

    def test_002_activation_code_user_room(self):
        """
        activation code for user room device
        """
        users = calling_users(api=self.api)
        target_user = choice(users)
        print(f'Trying to create a room device activation code for: {target_user.display_name}')
        ac_result = self.api.devices.activation_code(person_id=target_user.person_id)
        print(json.dumps(json.loads(ac_result.json()), indent=2))

        ...

    def test_002_activation_code_user_mpp(self):
        """
        activation code for user MPP device
        """
        users = calling_users(api=self.api)
        target_user = choice(users)
        print(f'Trying to create an MPP activation code for: {target_user.display_name}')
        ac_result = self.api.devices.activation_code(person_id=target_user.person_id,
                                                     model='DMS Cisco 8851')
        print(json.dumps(json.loads(ac_result.json()), indent=2))

    def test_003_mac_user(self):
        """
        Add MPP by mac for a user
        """
        # get an available MAC address
        mac = next(available_mac_address(api=self.api))

        # pick a random user
        users = calling_users(api=self.api)
        target_user = choice(users)
        print(f'Trying to create an MPP with mac {mac} for user: {target_user.display_name}')

        # add device by MAC
        result = self.api.devices.create_by_mac_address(mac=mac,
                                                        person_id=target_user.person_id,
                                                        model='DMS Cisco 8851')
        print(json.dumps(json.loads(result.json()), indent=2))
        self.assertIsNotNone(result.created, '"created" not set')

    def test_004_mac_workspace(self):
        """
        Add MPP by mac for a workspace
        """
        # get an available MAC address
        mac = next(available_mac_address(api=self.api))

        target = self.get_or_create_calling_workspace_wo_devices()

        print(f'Trying to create an MPP with mac {mac} for workspace: {target.display_name}')

        # add device by MAC
        result = self.api.devices.create_by_mac_address(mac=mac,
                                                        workspace_id=target.workspace_id,
                                                        model='DMS Cisco 8851')
        print(json.dumps(json.loads(result.json()), indent=2))


@skip
class TestDelete(TestCaseWithLog):
    @async_test
    async def test_001_delete_test_phones(self):
        """
        Delete MPPs with DEADDEAD mac addresses or stll in 'activating"
        """
        targets = [device for device in self.api.devices.list(product_type='phone')
                   if device.mac and device.mac.startswith('DEADDEAD') or
                   device.connection_status and device.connection_status == 'activating']
        if not targets:
            self.skipTest('No targets')
        print(f'Deleting {len(targets)} devices')
        results = await asyncio.gather(*[self.async_api.devices.delete(device_id=device.device_id)
                                         for device in targets],
                                       return_exceptions=True)
        failed = any(isinstance(r, Exception) for r in results)
        self.assertFalse(failed, f'failed to delete devices')
