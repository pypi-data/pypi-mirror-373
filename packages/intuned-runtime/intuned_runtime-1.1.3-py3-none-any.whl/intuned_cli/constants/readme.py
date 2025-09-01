readme = r"""# Intuned CLI

## Development Commands

For each command, add `--help` to see more details and options.

### Initialize a Project
`pipx run --spec intuned-runtime intuned init`

Once you install the dependencies, you will have `intuned` command available in your environment.

### Run an API
`intuned run api <api-name> <parameters>`


### Deploy a Project
`intuned deploy [project-name]`



### Create an auth session
`intuned run authsession create <parameters>`



### Validate an auth session
`intuned run authsession validate <auth-session-name>`

## Configuration

### Environment Variables and Settings
- `workspaceId`: Your Intuned workspace ID ([How to get your workspaceId](https://docs.intunedhq.com/docs/guides/platform/how-to-get-a-workspace-id))
  - Set in `intuned.json` file under the `workspaceId` property
  - Or provide via CLI with `--workspace-id` flag during deployment

- `projectName`: The name of your Intuned project
  - Set in `intuned.json` file under the `projectName` property
  - Or override via command line when deploying with `yarn intuned deploy my-project-name` or `npm run intuned deploy my-project-name`

- `INTUNED_API_KEY`: Your Intuned API key
  - Set as an environment variable: `export INTUNED_API_KEY=your_api_key_here`
  - Or include in your .env file for development
  - Or provide via CLI with `--api-key` flag during deployment

## Project Structure

### Generated Artifacts
- `./intuned.json`: Project configuration file
- `./api`: Folder containing API implementation files
- `./auth-sessions`: Folder containing auth-session APIs if you use them
- `./auth-sessions-instances`: Folder containing auth session instances

## Types of auth sessions
- `MANUAL`: Manual auth session, records the session using a recorder and stores it in the `auth-sessions-instances` folder
- `API`: Auth session created via create API, stores the session in the `auth-sessions-instances` folder

### Notes
- All commands should be run from the project root directory
- Verify you're in the correct location by confirming the presence of package.json and intuned.json
- Running commands from subdirectories may result in errors
- You can manage your deployed projects through the Intuned platform

## `Intuned.json` Reference
```jsonc
{
  // Your Intuned workspace ID.
  // Optional - If not provided here, it must be supplied via the \`--workspace-id\` flag during deployment.
  "workspaceId": "your_workspace_id",

  // The name of your Intuned project.
  // Optional - If not provided here, it must be supplied via the command line when deploying.
  "projectName": "your_project_name",

  // Replication settings
  "replication": {
    // The maximum number of concurrent executions allowed via Intuned API. This does not affect jobs.
    // A number of machines equal to this will be allocated to handle API requests.
    // Not applicable if api access is disabled.
    "maxConcurrentRequests": 1,

    // The machine size to use for this project. This is applicable for both API requests and jobs.
    // "standard": Standard machine size (6 shared vCPUs, 2GB RAM)
    // "large": Large machine size (8 shared vCPUs, 4GB RAM)
    // "xlarge": Extra large machine size (1 performance vCPU, 8GB RAM)
    "size": "standard"
  }

  // Auth session settings
  "authSessions": {
    // Whether auth sessions are enabled for this project.
    // If enabled, "auth-sessions/check.py" API must be implemented to validate the auth session.
    "enabled": true,

    // Whether to save Playwright traces for auth session runs.
    "saveTraces": false,

    // The type of auth session to use.
    // "API" type requires implementing "auth-sessions/create.py" API to create/recreate the auth session programmatically.
    // "MANUAL" type uses a recorder to manually create the auth session.
    "type": "API",

    // Recorder start URL for the recorder to navigate to when creating the auth session.
    // Required if "type" is "MANUAL". Not used if "type" is "API".
    "startUrl": "https://example.com/login",

    // Recorder finish URL for the recorder. Once this URL is reached, the recorder stops and saves the auth session.
    // Required if "type" is "MANUAL". Not used if "type" is "API".
    "finishUrl": "https://example.com/dashboard",

    // Recorder browser mode
    // "fullscreen": Launches the browser in fullscreen mode.
    // "kiosk": Launches the browser in kiosk mode (no address bar, no navigation controls).
    // Only applicable for "MANUAL" type.
    "browserMode": "fullscreen"
  }

  // API access settings
  "apiAccess": {
    // Whether to enable consumption through Intuned API. If this is false, the project can only be consumed through jobs.
    // This is required for projects that use auth sessions.
    "enabled": true
  },

  // Whether to run the deployed API in a headful browser. Running in headful can help with some anti-bot detections. However, it requires more resources and may work slower or crash if the machine size is "standard".
  "headful": false,

  // The region where your Intuned project is hosted.
  // For a list of available regions, contact support or refer to the documentation.
  // Optional - Default: "us"
  "region": "us"
}
```

"""
