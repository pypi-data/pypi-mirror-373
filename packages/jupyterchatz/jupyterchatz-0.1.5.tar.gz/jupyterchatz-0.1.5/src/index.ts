import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILayoutRestorer
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';
import { WidgetTracker } from '@jupyterlab/apputils';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ChatWidget } from './components/ChatWidget';

/**
 * 聊天窗口跟踪器
 */
const trackerNamespace = 'jupyterchatz-tracker';

/**
 * Initialization data for the jupyterchatz extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterchatz:plugin',
  description: 'JupyterLab的AI聊天助手扩展',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [ILayoutRestorer, IMainMenu, IFileBrowserFactory, IDocumentManager, IEditorTracker, INotebookTracker],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    restorer?: ILayoutRestorer,
    mainMenu?: IMainMenu,
    fileBrowserFactory?: IFileBrowserFactory,
    documentManager?: IDocumentManager,
    editorTracker?: IEditorTracker,
    notebookTracker?: INotebookTracker
  ) => {
    console.log('JupyterLab扩展jupyterchatz已激活!');
    
    console.log('插件激活时接收到的服务:');
    console.log('- fileBrowserFactory:', fileBrowserFactory);
    console.log('- documentManager:', documentManager);
    console.log('- editorTracker:', editorTracker);
    console.log('- notebookTracker:', notebookTracker);

    // 创建聊天窗口跟踪器
    const tracker = new WidgetTracker<ChatWidget>({
      namespace: trackerNamespace
    });

    // 添加命令
    const command = 'jupyterchatz:open';
    app.commands.addCommand(command, {
      label: '打开AI助手',
      execute: () => {
        // 检查是否已经有聊天窗口打开
        let chatWidget: ChatWidget | null = null;
        
        // 尝试获取现有窗口
        if (tracker.currentWidget) {
          chatWidget = tracker.currentWidget;
        }
        
        if (chatWidget) {
          app.shell.activateById(chatWidget.id);
          return chatWidget;
        }
        
        // 创建新的聊天窗口，传递文件系统服务
        chatWidget = new ChatWidget({
          fileBrowserFactory,
          documentManager,
          editorTracker,
          notebookTracker
        });
        
        // 将窗口添加到右侧面板
        app.shell.add(chatWidget, 'right', { rank: 1000 });
        
        // 将窗口添加到跟踪器
        void tracker.add(chatWidget);
        
        return chatWidget;
      }
    });

    // 添加到命令面板
    palette.addItem({ command, category: 'AI助手' });

    // 添加到主菜单
    if (mainMenu) {
      // 添加到帮助菜单
      const helpMenu = mainMenu.helpMenu;
      helpMenu.addGroup([{ command }]);
    }

    // 恢复布局
    if (restorer) {
      void restorer.restore(tracker, {
        command,
        name: () => 'jupyterchatz'
      });
    }
  }
};

export default plugin;
