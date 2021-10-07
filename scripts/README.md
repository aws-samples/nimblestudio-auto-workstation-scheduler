# Nimble Studio Automated Workstation Scheduler Configuration Scripts

## Summary
The scripts in this directory are helper scripts for configuring the Nimble Studio Automated Workstation Scheduler.

## Scripts

### Get Auto Launch Config

This is a helper script to retrieve Nimble Studio Auto Workstation Scheduler config entries.

To have the script prompt for appropriate input data, run the script from the repository directory without arguments as follows:

```bash
python3 scripts/get_auto_launch_config.py
```

This script requires credentials with the following API permissions:
* dynamodb:getItem
* dynamodb:scan
* nimble:getLaunchProfile
* nimble:getStreamingImage
* nimble:getStudio
* nimble:listStudios
* nimble:listStudioMemebers
* identitystore:listUsers
* identitystore:describeUser

To run the script with input parameters to retrieve config for a specific user, run as follows:

```bash
python3 scripts/get_auto_launch_config.py --sso-id sso_id
```

To run the script to retrieve config for all users, run as follows:

```bash
python3 scripts/get_auto_launch_config.py --all-users
```

To run the script to retrieve config based on whether or not the config is enabled or disabled, run as follows:

Filter Enabled:

```bash
python3 scripts/get_auto_launch_config.py --all-users --filter-enabled
```

Filter Disabled:

```bash
python3 scripts/get_auto_launch_config.py --all-users --filter-disabled
```

For help with script parameters, run the following:

```bash
python3 scripts/get_auto_launch_config.py -h
```

### Update Auto Launch Config for User

This is a helper script to update Nimble Studio Auto Workstation Scheduler config for a studio user at a certain start time.

To have the script prompt for appropriate input data, run the script from the repository directory without arguments as follows:

```bash
python3 scripts/update_auto_launch_config.py
```

This script requires credentials with the following API permissions:
* dynamodb:getItem
* dynamodb:putItem
* dynamodb:scan
* dynamodb:updateItem
* nimble:getLaunchProfile
* nimble:listLaunchProfiles
* nimble:getStreamingImage
* nimble:listStudioMemebers
* nimble:listStudios
* identitystore:listUsers
* identitystore:describeUser

To run the script with all necessary input parameters provided, run as follows:

```bash
python3 scripts/update_auto_launch_config.py --sso-id sso_user_id --studio-id studio_id --start-time 00:00 --days monday,tuesday,wednesday,thursday,friday --launch-profile launch_profile_id --streaming-image streaming_image_component_id --instance-type g4dn.xlarge 
```

To skip validation of parameters requiring service calls, use the skip validation flag (--skip-validation):

```bash
python3 scripts/update_auto_launch_config.py --sso-id sso_user_id --studio-id studio_id --start-time 00:00 --days monday,tuesday,wednesday,thursday,friday --launch-profile launch_profile_id --streaming-image streaming_image_component_id --instance-type g4dn.xlarge --skip-validation
```

In this case, only the dynamodb permissions are required. However, the configuration will not be validated before being saved.

For help with script parameters, run the following:

```bash
python3 scripts/update_auto_launch_config.py -h
```

### Delete Auto Launch Config

This is a helper script to delete Nimble Studio Auto Workstation Scheduler config entries.

To have the script prompt for appropriate input data, run the script from the repository directory without arguments as follows:

```bash
python3 scripts/delete_auto_launch_config.py
```

This script requires credentials with the following API permissions:
* dynamodb:deleteItem
* dynamodb:getItem
* dynamodb:scan
* nimble:getLaunchProfile
* nimble:getStreamingImage
* nimble:getStudio
* nimble:listStudios
* nimble:listStudioMemebers
* identitystore:listUsers
* identitystore:describeUser

To run the script with input parameters to delete config for a specific user, run as follows:

```bash
python3 scripts/delete_auto_launch_config.py --sso-id sso_id
```

To run the script to delete config based on whether or not the config is enabled or disabled, run as follows:

Filter Enabled:

```bash
python3 scripts/delete_auto_launch_config.py --all-users --filter-enabled
```

Filter Disabled:

```bash
python3 scripts/delete_auto_launch_config.py --all-users --filter-disabled
```

The filters can also be used when specifying a specific user, as follows:

```bash
python3 scripts/delete_auto_launch_config.py --sso-id sso_id --filter-disabled
```

For help with script parameters, run the following:

```bash
python3 scripts/delete_auto_launch_config.py -h
```

### Toggle Auto Launch for Users

This is a helper script to update existing Nimble Studio Auto Workstation Scheduler config for a given user, toggling the auto launch on or off.

To update the automated workstation launch enabled status to `True` for all users, run the script from the repository directory as follows:

```bash
python3 scripts/toggle_auto_launch_for_users.py
```

To disable launch for all users, add the `--disable` flag:

```bash
python3 scripts/toggle_auto_launch_for_users.py --disable
```

To update the automated workstation launch enabled status to `True` for specific users for a certain studio ID, run the script as follows:

```bash
python3 scripts/toggle_auto_launch_for_users.py --user-ids user_id_1,user_id_2 --studio-id studio_id
```

For help with script parameters, run the following:

```bash
python3 scripts/toggle_auto_launch_for_users.py -h
```