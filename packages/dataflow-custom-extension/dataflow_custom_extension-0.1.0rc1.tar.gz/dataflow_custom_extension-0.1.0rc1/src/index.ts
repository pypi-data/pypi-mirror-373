import {
  ConnectionLost,
  IConnectionLost,
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  JupyterLab
} from '@jupyterlab/application';
import { Dialog, ICommandPalette, showDialog } from '@jupyterlab/apputils';
import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection, ServiceManager } from '@jupyterlab/services';
import { ITranslator } from '@jupyterlab/translation';

const CUSTOM_DATAFLOW_CONNECTION_LOST = 'dataflow-custom:hub-restart';


const dataflowExtension: JupyterFrontEndPlugin<void> = {
  activate: activateDataflowExtension,
  id: 'dataflow-custom-extension:plugin',
  description: 'A JupyterLab extension for dataflow customization',
  autoStart: true,
  requires: [JupyterFrontEnd.IPaths, ITranslator],
  optional: [ICommandPalette],
};

function activateDataflowExtension(
  app: JupyterFrontEnd, 
  paths: JupyterFrontEnd.IPaths,
  translator: ITranslator,
  palette: ICommandPalette | null,
){
  const trans = translator.load('jupyterlab');
  const hubHost = paths.urls.hubHost || '';
  const hubPrefix = paths.urls.hubPrefix || '';
  const hubUser = paths.urls.hubUser || '';
  const hubServerName = paths.urls.hubServerName || '';
  
  if (!hubPrefix) {
    return;
  }

const spawnBase = URLExt.join(hubPrefix, 'ui', 'connection-lost');
  let restartUrl = hubHost + spawnBase;
  if (hubServerName) {
    const suffix = URLExt.join(spawnBase, hubUser, hubServerName);
    if (!suffix.startsWith(spawnBase)) {
      throw new Error('Can only be used for spawn requests');
    }
    restartUrl = hubHost + suffix;
  }

  const { commands } = app;

  commands.addCommand(CUSTOM_DATAFLOW_CONNECTION_LOST, {
    label: trans.__('Restart Server'),
    caption: trans.__('Request that the Hub restart this server'),
    execute: () => {
      window.location.href = restartUrl;
    }
  });

}

const connectionlost: JupyterFrontEndPlugin<IConnectionLost> = {
    id: 'dataflow-custom-extension:plugin:connectionlost',
    description:
      'Provides a service to be notified when the connection to the hub server is lost.',
    requires: [JupyterFrontEnd.IPaths, ITranslator],
    optional: [JupyterLab.IInfo],
    activate: (
      app: JupyterFrontEnd,
      paths: JupyterFrontEnd.IPaths,
      translator: ITranslator,
      info: JupyterLab.IInfo | null
    ): IConnectionLost => {
      const trans = translator.load('jupyterlab');
      const hubPrefix = paths.urls.hubPrefix || '';
      const baseUrl = paths.urls.base;

      if (!hubPrefix) {
        return ConnectionLost;
      }

      let showingError = false;
      const onConnectionLost: IConnectionLost = async (
          manager: ServiceManager.IManager,
          err: ServerConnection.NetworkError
        ): Promise<void> => {
          if (showingError) {
            return;
          }

          showingError = true;
          if (info) {
            info.isConnected = false;
          }

          const result = await showDialog({
            title: trans.__('Server not responding'),
            body: trans.__(
              'Your server at %1 is not running.\nWould you like to restart it?',
              baseUrl
            ),
            buttons: [
              Dialog.okButton({ label: trans.__('Restart') }),
              Dialog.cancelButton({ label: trans.__('Dismiss') })
            ]
          });

          if (info) {
            info.isConnected = true;
          }
          showingError = false;

          if (result.button.accept) {
            await app.commands.execute(CUSTOM_DATAFLOW_CONNECTION_LOST);
          }
        };
      return onConnectionLost;
    },
    autoStart: true,
    provides: IConnectionLost
  };

export default [dataflowExtension, connectionlost] as JupyterFrontEndPlugin<any>[];
