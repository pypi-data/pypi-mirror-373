import axios from 'axios';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { INotebookTracker } from '@jupyterlab/notebook';
import { PathExt } from '@jupyterlab/coreutils';
import { Contents } from '@jupyterlab/services';
import { MCPService } from './mcpService';

/**
 * 聊天消息类型
 */
export interface IChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * 聊天历史记录
 */
export interface IChatHistory {
  messages: IChatMessage[];
}

/**
 * 聊天服务选项
 */
export interface IChatServiceOptions {
  fileBrowserFactory?: IFileBrowserFactory;
  documentManager?: IDocumentManager;
  editorTracker?: IEditorTracker;
  notebookTracker?: INotebookTracker;
}

/**
 * 文件信息接口
 */
export interface IFileInfo {
  path: string;
  name: string;
  extension: string;
  content?: string;
  isDirectory: boolean;
}

/**
 * AI聊天服务
 */
export class ChatService {
  private apiKey: string = 'sk-7W5ztpH97ea2RjWVC3BbC375Aa6d4bD98550EbFcBc7146Ec';
  private apiUrl: string = 'https://api.aihubmix.com/v1/chat/completions';
  private model: string = 'gpt-4o-mini';
  
  private fileBrowserFactory?: IFileBrowserFactory;
  private documentManager?: IDocumentManager;
  private editorTracker?: IEditorTracker;
  private notebookTracker?: INotebookTracker;
  
  // MCP服务相关
  private mcpService?: MCPService;
  private mcpServerUrl: string = 'http://localhost:8888';  // 修改为您的JupyterLab服务器地址
  
  /**
   * 构造函数
   * @param options 服务选项
   */
  constructor(options: IChatServiceOptions = {}) {
    this.fileBrowserFactory = options.fileBrowserFactory;
    this.documentManager = options.documentManager;
    this.editorTracker = options.editorTracker;
    this.notebookTracker = options.notebookTracker;
    
    // 初始化MCP服务
    this.initMCPService();
  }
  
  /**
   * 初始化MCP服务
   */
  private async initMCPService(): Promise<void> {
    try {
      // 创建MCP服务实例
      this.mcpService = new MCPService({
        serverUrl: this.mcpServerUrl,
        transport: 'stdio'
      }, this.notebookTracker);
      
      // 检查MCP服务器健康状态
      const isHealthy = await this.mcpService.checkHealth();
      if (isHealthy) {
        console.log('MCP服务器连接正常');
      } else {
        console.warn('MCP服务器连接异常，部分功能可能不可用');
      }
    } catch (error) {
      console.error('初始化MCP服务失败:', error);
    }
  }

  /**
   * 获取当前工作目录路径
   * @returns 当前工作目录路径
   */
  public getCurrentDirectory(): string | null {
    console.log('获取当前工作目录...');
    
    // 首先尝试从 fileBrowserFactory 获取
    if (this.fileBrowserFactory) {
      try {
        console.log('尝试从 fileBrowserFactory 获取当前路径');
        const browser = this.fileBrowserFactory.tracker.currentWidget;
        if (browser) {
          const path = browser.model.path;
          console.log('从 fileBrowserFactory 获取的路径:', path);
          return path;
        }
      } catch (error) {
        console.error('从 fileBrowserFactory 获取路径时出错:', error);
      }
    } else {
      console.warn('fileBrowserFactory 未定义');
    }
    
    // 如果 fileBrowserFactory 方法失败，尝试从 notebookTracker 获取
    if (this.notebookTracker && this.notebookTracker.currentWidget) {
      try {
        console.log('尝试从 notebookTracker 获取当前路径');
        const path = this.notebookTracker.currentWidget.context.path;
        // 获取目录部分（去掉文件名）
        const lastSlashIndex = path.lastIndexOf('/');
        if (lastSlashIndex >= 0) {
          const dirPath = path.substring(0, lastSlashIndex);
          console.log('从 notebookTracker 获取的目录路径:', dirPath);
          return dirPath;
        }
        console.log('从 notebookTracker 获取的路径:', path);
        return ''; // 如果没有斜杠，说明文件在根目录
      } catch (error) {
        console.error('从 notebookTracker 获取路径时出错:', error);
      }
    }
    
    // 如果 notebookTracker 方法失败，尝试从 documentManager 获取
    if (this.documentManager) {
      try {
        console.log('尝试从 documentManager 获取当前路径');
        return this.documentManager.services.contents.localPath('');
      } catch (error) {
        console.error('从 documentManager 获取路径时出错:', error);
      }
    }
    
    // 如果都失败了，返回一个默认路径
    console.warn('无法获取当前路径，使用默认路径');
    return '';
  }
  
  /**
   * 获取当前目录下的文件列表
   * @returns 文件列表
   */
  public async getCurrentDirectoryContents(): Promise<IFileInfo[]> {
    console.log('获取当前目录内容...');
    
    if (!this.documentManager) {
      console.warn('documentManager 未定义');
      return [];
    }
    
    try {
      // 获取当前路径
      const currentPath = this.getCurrentDirectory() || '';
      console.log('使用路径获取目录内容:', currentPath);
      
      // 直接使用 documentManager 获取目录内容
      const dirContents = await this.documentManager.services.contents.get(currentPath);
      
      if (!dirContents || !dirContents.content) {
        return [];
      }
      
      // 转换为文件信息数组
      return dirContents.content.map((item: Contents.IModel) => {
        return {
          path: item.path,
          name: item.name,
          extension: item.type === 'directory' ? '' : PathExt.extname(item.name),
          isDirectory: item.type === 'directory'
        };
      });
    } catch (error) {
      console.error('获取目录内容失败:', error);
      return [];
    }
  }
  
  /**
   * 获取当前打开的文件信息
   * @returns 当前打开的文件信息
   */
  public getCurrentOpenedFile(): IFileInfo | null {
    // 检查编辑器
    if (this.editorTracker && this.editorTracker.currentWidget) {
      const editor = this.editorTracker.currentWidget;
      const context = editor.context;
      const path = context.path;
      const model = editor.content.model;
      
      return {
        path: path,
        name: PathExt.basename(path),
        extension: PathExt.extname(path),
        content: model.toString(),
        isDirectory: false
      };
    }
    
    // 检查笔记本
    if (this.notebookTracker && this.notebookTracker.currentWidget) {
      const notebook = this.notebookTracker.currentWidget;
      const context = notebook.context;
      const path = context.path;
      
      // 获取笔记本内容（这里简化处理，只获取代码单元格）
      let content = '';
      const model = notebook.content.model;
      
      if (model) {
        for (let i = 0; i < model.cells.length; i++) {
          const cell = model.cells.get(i);
          if (cell.type === 'code') {
            content += `# Cell ${i + 1}\n${cell.toString()}\n\n`;
          }
        }
      }
      
      return {
        path: path,
        name: PathExt.basename(path),
        extension: PathExt.extname(path),
        content: content,
        isDirectory: false
      };
    }
    
    return null;
  }
  
  /**
   * 连接到当前打开的Notebook
   * @returns 连接结果
   */
  public async connectToCurrentNotebook(): Promise<boolean> {
    // 确保MCP服务初始化
    if (!this.mcpService) {
      console.log('初始化MCP服务...');
      this.mcpService = new MCPService({
        serverUrl: this.mcpServerUrl,
        transport: 'stdio'
      }, this.notebookTracker);
    }
    
    // 检查是否有打开的Notebook
    if (!this.notebookTracker || !this.notebookTracker.currentWidget) {
      console.warn('当前没有打开的Notebook');
      return false;
    }
    
    const notebook = this.notebookTracker.currentWidget;
    const path = notebook.context.path;
    
    console.log(`尝试连接到Notebook: ${path}`);
    
    try {
      // 连接到当前Notebook
      const connected = await this.mcpService.connect();
      
      if (connected) {
        console.log(`已成功连接到Notebook: ${path}`);
      } else {
        console.warn(`连接到Notebook ${path} 失败`);
      }
      
      return connected;
    } catch (error) {
      console.error('连接到Notebook时出错:', error);
      return false;
    }
  }
  
  /**
   * 读取指定文件的内容
   * @param path 文件路径
   * @returns 文件内容
   */
  public async readFile(path: string): Promise<string | null> {
    if (!this.documentManager) {
      return null;
    }
    
    try {
      const contents = await this.documentManager.services.contents.get(path, { content: true });
      if (contents.type === 'file') {
        return contents.content as string;
      }
      return null;
    } catch (error) {
      console.error('读取文件失败:', error);
      return null;
    }
  }
  
  /**
   * 获取Notebook信息
   * @returns Notebook信息
   */
  public async getNotebookInfo(): Promise<string> {
    if (!this.mcpService) {
      return '未初始化MCP服务';
    }
    

    
    try {
      const info = await this.mcpService.getNotebookInfo();
      if (!info) {
        return '无法获取Notebook信息';
      }
      
      return `**Notebook信息:**\n\n` +
             `- **文档ID:** ${info.document_id}\n` +
             `- **单元格总数:** ${info.total_cells}\n` +
             `- **单元格类型统计:** ${JSON.stringify(info.cell_types)}`;
    } catch (error: any) {
      console.error('获取Notebook信息失败:', error);
      return `获取Notebook信息失败: ${error?.message || '未知错误'}`;
    }
  }
  
  /**
   * 读取所有单元格
   * @returns 所有单元格信息
   */
  public async readAllCells(): Promise<string> {
    if (!this.mcpService) {
      return '未初始化MCP服务';
    }
    
    try {
      const cells = await this.mcpService.readAllCells();
      if (!cells || cells.length === 0) {
        return '无法获取单元格或Notebook为空';
      }
      
      let result = `Notebook包含 ${cells.length} 个单元格:\n\n`;
      
      cells.forEach((cell, index) => {
        result += `**单元格 ${cell.index} (${cell.type}):**\n\n`;
        
        // 代码内容
        result += '```';
        
        // 根据单元格类型添加语言标识
        if (cell.type === 'code') {
          result += 'python';
        } else if (cell.type === 'markdown') {
          result += 'markdown';
        }
        
        result += '\n';
        
        // 确保单元格内容正确显示
        if (cell.source && cell.source.length > 0) {
          // 如果source是数组，将其连接起来
          result += cell.source.join('');
        } else {
          result += '# 空单元格';
        }
        
        result += '\n```\n\n';
        
        // 输出内容
        if (cell.outputs && cell.outputs.length > 0) {
          result += '**输出:**\n';
          result += '```\n';
          result += cell.outputs.join('\n');
          result += '\n```\n\n';
        } else {
          result += '**输出:** 无输出\n\n';
        }
      });
      
      return result;
    } catch (error: any) {
      console.error('读取所有单元格失败:', error);
      return `读取所有单元格失败: ${error?.message || '未知错误'}`;
    }
  }
  
  /**
   * 读取指定单元格
   * @param cellIndex 单元格索引
   * @returns 单元格信息
   */
  public async readCell(cellIndex: number): Promise<string> {
    if (!this.mcpService) {
      return '未初始化MCP服务';
    }
    

    
    try {
      const cell = await this.mcpService.readCell(cellIndex);
      if (!cell) {
        return `无法获取单元格 ${cellIndex}`;
      }
      
      let result = `**单元格 ${cell.index} (${cell.type}):**\n\n`;
      
      // 代码内容
      result += '```';
      
      // 根据单元格类型添加语言标识
      if (cell.type === 'code') {
        result += 'python';
      } else if (cell.type === 'markdown') {
        result += 'markdown';
      }
      
      result += '\n';
      
      // 确保单元格内容正确显示
      if (cell.source && cell.source.length > 0) {
        // 如果source是数组，将其连接起来
        result += cell.source.join('');
      } else {
        result += '# 空单元格';
      }
      
      result += '\n```\n\n';
      
      // 输出内容
      if (cell.outputs && cell.outputs.length > 0) {
        result += '**输出:**\n';
        result += '```\n';
        result += cell.outputs.join('\n');
        result += '\n```\n';
      } else {
        result += '**输出:** 无输出\n';
      }
      
      return result;
    } catch (error: any) {
      console.error(`读取单元格 ${cellIndex} 失败:`, error);
      return `读取单元格 ${cellIndex} 失败: ${error?.message || '未知错误'}`;
    }
  }
  
  /**
   * 添加Markdown单元格
   * @param content Markdown内容
   * @returns 操作结果
   */
  public async appendMarkdownCell(content: string): Promise<string> {
    if (!this.mcpService) {
      return '未初始化MCP服务';
    }
    

    
    try {
      const result = await this.mcpService.appendMarkdownCell(content);
      if (!result) {
        return '添加Markdown单元格失败';
      }
      
      return `成功添加Markdown单元格: ${result}`;
    } catch (error: any) {
      console.error('添加Markdown单元格失败:', error);
      return `添加Markdown单元格失败: ${error?.message || '未知错误'}`;
    }
  }
  
  /**
   * 添加并执行代码单元格
   * @param code 代码内容
   * @returns 执行结果
   */
  public async appendExecuteCodeCell(code: string): Promise<string> {
    if (!this.mcpService) {
      return '未初始化MCP服务';
    }
    

    
    try {
      const outputs = await this.mcpService.appendExecuteCodeCell(code);
      if (!outputs) {
        return '添加并执行代码单元格失败';
      }
      
      let result = '代码执行结果:\n\`\`\`\n';
      result += Array.isArray(outputs) ? outputs.join('\n') : outputs;
      result += '\n\`\`\`';
      
      return result;
    } catch (error: any) {
      console.error('添加并执行代码单元格失败:', error);
      return `添加并执行代码单元格失败: ${error?.message || '未知错误'}`;
    }
  }
  
  /**
   * 执行指定单元格
   * @param cellIndex 单元格索引
   * @returns 执行结果
   */
  public async executeCell(cellIndex: number): Promise<string> {
    if (!this.mcpService) {
      return '未初始化MCP服务';
    }
    

    
    try {
      const outputs = await this.mcpService.executeCell(cellIndex);
      if (!outputs) {
        return `执行单元格 ${cellIndex} 失败`;
      }
      
      let result = `单元格 ${cellIndex} 执行结果:\n\`\`\`\n`;
      result += Array.isArray(outputs) ? outputs.join('\n') : outputs;
      result += '\n\`\`\`';
      
      return result;
    } catch (error: any) {
      console.error(`执行单元格 ${cellIndex} 失败:`, error);
      return `执行单元格 ${cellIndex} 失败: ${error?.message || '未知错误'}`;
    }
  }
  
  /**
   * 发送聊天消息并获取响应
   * @param messages 聊天历史
   * @returns 返回AI的响应
   */
  public async sendMessage(messages: IChatMessage[]): Promise<string> {
    try {
      // 检查消息中是否包含特殊命令
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'user') {
        const content = lastMessage.content.toLowerCase().trim();
        console.log('处理用户消息:', content);
        
        // 处理特殊命令
        if (content === '/pwd' || content === '/cwd' || content.includes('当前目录')) {
          console.log('执行获取当前目录命令');
          try {
            const currentDir = this.getCurrentDirectory();
            console.log('获取到的当前目录:', currentDir);
            return `当前工作目录: ${currentDir || '未知'}`;
          } catch (error: any) {
            console.error('获取当前目录时出错:', error);
            return `获取当前目录时出错: ${error?.message || '未知错误'}`;
          }
        }
        
        if (content === '/ls' || content.includes('列出文件') || content.includes('显示文件列表')) {
          console.log('执行列出文件命令');
          try {
            const files = await this.getCurrentDirectoryContents();
            console.log('获取到的文件列表:', files);
            
            if (files.length === 0) {
              return '当前目录为空或无法访问目录内容。';
            }
            
            const fileList = files.map(file => 
              `${file.isDirectory ? '[目录] ' : '[文件] '}${file.name}`
            ).join('\\n');
            
            return `当前目录 (${this.getCurrentDirectory() || '未知'}) 的内容:\\n${fileList}`;
          } catch (error: any) {
            console.error('获取文件列表时出错:', error);
            return `获取文件列表时出错: ${error?.message || '未知错误'}`;
          }
        }
        
        // 获取当前文件
        if (content === '/current' || content.includes('当前文件') || content.includes('显示当前文件')) {
          console.log('执行获取当前文件命令');
          try {
            const currentFile = this.getCurrentOpenedFile();
            console.log('获取到的当前文件:', currentFile);
            
            if (!currentFile) {
              return '当前没有打开的文件。';
            }
            
            let response = `当前打开的文件: ${currentFile.path}\n\n`;
            if (currentFile.content) {
              // 如果文件内容太长，只显示前1000个字符
              const contentPreview = currentFile.content.length > 1000 
                ? currentFile.content.substring(0, 1000) + '...(内容已截断)'
                : currentFile.content;
              response += `文件内容:\n\`\`\`${PathExt.extname(currentFile.name).substring(1)}\n${contentPreview}\n\`\`\``;
            } else {
              response += '无法获取文件内容。';
            }
            
            return response;
          } catch (error: any) {
            console.error('获取当前文件时出错:', error);
            return `获取当前文件时出错: ${error?.message || '未知错误'}`;
          }
        }
        
        // 读取指定文件
        const readFileMatch = content.match(/\/read\s+(.+)/) || content.match(/读取文件\s+(.+)/);
        if (readFileMatch) {
          console.log('执行读取指定文件命令');
          try {
            const filePath = readFileMatch[1].trim();
            console.log('要读取的文件路径:', filePath);
            
            const currentDir = this.getCurrentDirectory() || '';
            console.log('当前目录:', currentDir);
            
            const fullPath = filePath.startsWith('/') ? filePath : PathExt.join(currentDir, filePath);
            console.log('完整文件路径:', fullPath);
            
            const fileContent = await this.readFile(fullPath);
            console.log('文件内容是否获取成功:', fileContent !== null);
            
            if (fileContent === null) {
              return `无法读取文件: ${fullPath}`;
            }
            
            // 如果文件内容太长，只显示前1000个字符
            const contentPreview = fileContent.length > 1000 
              ? fileContent.substring(0, 1000) + '...(内容已截断)'
              : fileContent;
            
            return `文件 ${fullPath} 的内容:\n\`\`\`${PathExt.extname(fullPath).substring(1)}\n${contentPreview}\n\`\`\``;
                      } catch (error: any) {
              console.error('读取指定文件时出错:', error);
              return `读取指定文件时出错: ${error?.message || '未知错误'}`;
          }
        }
        
        // MCP相关命令
        
        // 连接到当前Notebook
        if (content === '/connect' || content.includes('连接notebook')) {
          console.log('执行连接到当前Notebook命令');
          try {
            const connected = await this.connectToCurrentNotebook();
            return connected 
              ? '已成功连接到当前Notebook' 
              : '连接到当前Notebook失败，请确保已打开Notebook并且MCP服务器正在运行';
          } catch (error: any) {
            console.error('连接到当前Notebook时出错:', error);
            return `连接到当前Notebook时出错: ${error?.message || '未知错误'}`;
          }
        }
        
        // 获取Notebook信息
        if (content === '/notebook-info' || content.includes('notebook信息')) {
          console.log('执行获取Notebook信息命令');
          return await this.getNotebookInfo();
        }
        
        // 读取所有单元格
        if (content === '/cells' || content.includes('所有单元格')) {
          console.log('执行读取所有单元格命令');
          return await this.readAllCells();
        }
        
        // 读取指定单元格
        const readCellMatch = content.match(/\/cell\s+(\d+)/) || content.match(/单元格\s+(\d+)/);
        if (readCellMatch) {
          const cellIndex = parseInt(readCellMatch[1]);
          console.log(`执行读取单元格 ${cellIndex} 命令`);
          return await this.readCell(cellIndex);
        }
        
        // 添加Markdown单元格
        const addMarkdownMatch = content.match(/\/add-markdown\s+(.+)/s) || content.match(/添加markdown\s+(.+)/s);
        if (addMarkdownMatch) {
          const markdownContent = addMarkdownMatch[1].trim();
          console.log('执行添加Markdown单元格命令');
          return await this.appendMarkdownCell(markdownContent);
        }
        
        // 添加并执行代码单元格
        const addCodeMatch = content.match(/\/add-code\s+(.+)/s) || content.match(/添加代码\s+(.+)/s);
        if (addCodeMatch) {
          const codeContent = addCodeMatch[1].trim();
          console.log('执行添加并执行代码单元格命令');
          return await this.appendExecuteCodeCell(codeContent);
        }
        
        // 执行指定单元格
        const execCellMatch = content.match(/\/exec\s+(\d+)/) || content.match(/执行单元格\s+(\d+)/);
        if (execCellMatch) {
          const cellIndex = parseInt(execCellMatch[1]);
          console.log(`执行单元格 ${cellIndex} 命令`);
          return await this.executeCell(cellIndex);
        }
      }
      
      // 正常处理消息
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: messages
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      );

      if (response.data && response.data.choices && response.data.choices.length > 0) {
        return response.data.choices[0].message.content;
      } else {
        throw new Error('无效的API响应');
      }
    } catch (error) {
      console.error('AI聊天API调用失败:', error);
      return '抱歉，我无法连接到AI服务。请检查网络连接或API密钥是否有效。';
    }
  }
}
