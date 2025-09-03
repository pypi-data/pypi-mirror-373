# Dataflow Jupyter Extension

A JupyterLab extension for dataflow customizations


## Customizations

<details>
<summary>Added custom connection lost restart command</summary>

#### `dataflow-custom:hub-restart`
-   This command has been replaced for default `hub:restart` because of it's redirection to _/hub/spawn_ , which should not be the case. So now the it redirects to _/hub/ui_ in iframe , which will be handled by UI and "App is not running" message will be shown
- Modified the connectionLost dialog to use the `dataflow-custom:hub-restart` command

</details>

### Packaging the extension

See [RELEASE](RELEASE.md)
