# GooglePhotoDownloader

Google Photo Dowloader is a python CLI scripts to list and/or download media from your google photo library.
The CLI is interactive and guides you.

The Main Menu is the following:

```
[?] Please select an action: 
 > List Media
   Download Media
   Exit
```

Both for *List Media* and *Download Media* the interactive CLI will ask a starting and an ending YEAR and MONTH. The system will list or download media from **1/START_MONTH/START_YEAR** to **1/END_MONTH/END_YEAR** - **1 DAY**

for instance:
- START_YEAR = 2024
- START_MONTH = 1
- END_YEAR = 2024
- END_MONTH = 2

It will list or download media from 01/01/2024 until 31/01/2024 (01/02/2024 - 1 day)

## Requirements
### Docker Dev Container (Suggested)
https://code.visualstudio.com/docs/devcontainers/containers

Dev Containers will manage dependency and dev environment for you. You need:
- Docker Desktop
- VSCode (I worked on that)

**Known Issues**:
Running the script you can have the following consol error: 
```
Error: Cannot find module '/home/vscode/.vscode-server/data/User/workspaceStorage/de8c3e9b49b22778d4f90a95c95d58d9/ms-vscode.js-debug/bootloader.js'
Require stack:
- internal/preload
    at Module._resolveFilename (node:internal/modules/cjs/loader:1077:15)
    at Module._load (node:internal/modules/cjs/loader:922:27)
    at internalRequire (node:internal/modules/cjs/loader:174:19)
    at Module._preloadModules (node:internal/modules/cjs/loader:1433:5)
    at loadPreloadModules (node:internal/process/pre_execution:605:5)
    at setupUserModules (node:internal/process/pre_execution:124:3)
    at prepareExecution (node:internal/process/pre_execution:115:5)
    at prepareMainThreadExecution (node:internal/process/pre_execution:40:3)
    at node:internal/main/run_main_module:10:1 {
  code: 'MODULE_NOT_FOUND',
  requireStack: [ 'internal/preload' ]
}
```
to fix it you have to disable and re-enable *Auto-Attach* from VSCode: 
1. Press F1
2. Select *Debug: Toggle Auto Attach*
3. Select *Disabled*
4. Press F1
5. Select *Debug: Toggle Auto Attach*
6. Select *Smart*
Reference [StackOvervlow](https://stackoverflow.com/questions/75708866/vscode-dev-container-fails-to-load-ms-vscode-js-debug-extension-correctly)

### Manual
- Install Python 3
- install requirements: `pip install --user -r requirements.txt`

## Run it
`python main.py`

or downloading the binary from [Releases](https://github.com/PaoloOranges/GooglePhotoDownloader/releases).

You **MUST** create a *client_secrets.json* file similar to:
```
{{
    "installed": {
        "client_id": "<some-client-id>",
        "project_id": "<some-name>",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "<some-secret>",
        "redirect_uris": [
            "http://localhost"
        ]
    }
}
```
as specified in [Google OAuth 2.0 Python Client](https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth.md)

**REMARK**: I have not published any Google Project that allow you to simple log int via OAuth 2.0 and use the script, you have to do it yourself from Google API Console. 

## Known Issue as per 24/03/2024

- VSCode error on run from dev container mentioned [here](https://github.com/PaoloOranges/GooglePhotoDownloader?tab=readme-ov-file#docker-dev-container-suggested)
- Artifacts are not working due to a missing file for *alive_progress* not packaged correctly from PyInstaller [here](https://github.com/alvinlindstam/grapheme/pull/20#pullrequestreview-1956524023) is the PR that fix the issue on pakcage *grapheme*, used by *alive-progress*
- Script might not be able to refresh token if expired. delete *sessions* folder or its content to fix it
- Media downloaded will be placed in a folder called DownloadedMedia. It must not exists, the script will throw an exception if it does exist
