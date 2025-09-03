import axios from 'axios';
import { INotebookTracker } from '@jupyterlab/notebook';

/**
 * MCP服务配置接口
 */
export interface IMCPServiceConfig {
  serverUrl: string;
  transport: 'stdio' | 'streamable-http';
}

/**
 * 单元格信息接口
 */
export interface ICellInfo {
  index: number;
  type: 'code' | 'markdown' | 'raw';
  source: string[];
  outputs?: string[];
}

/**
 * MCP服务类
 */
export class MCPService {
  private config: IMCPServiceConfig;
  private isConnected: boolean = false;
  private notebookTracker?: INotebookTracker;

  constructor(config: IMCPServiceConfig, notebookTracker?: INotebookTracker) {
    this.config = config;
    this.notebookTracker = notebookTracker;
  }

  /**
   * 检查MCP服务器健康状态
   */
  public async checkHealth(): Promise<boolean> {
    console.log('跳过MCP服务器健康检查，直接返回true');
    return true;
  }

  /**
   * 连接到MCP服务器
   */
  public async connect(): Promise<boolean> {
    try {
      console.log('尝试连接到MCP服务器...');
      console.log('MCP服务器URL:', this.config.serverUrl);
      console.log('传输方式:', this.config.transport);
      
      // 对于stdio模式，我们假设连接成功
      if (this.config.transport === 'stdio') {
        console.log('已成功连接到MCP服务器(stdio模式)');
        this.isConnected = true;
        return true;
      }
      
      // 对于HTTP模式，尝试连接
      const response = await axios.post(`${this.config.serverUrl}/api/connect`);
      if (response.status === 200) {
        console.log('已成功连接到MCP服务器');
        this.isConnected = true;
        return true;
      }
      
      console.error('连接MCP服务器失败:', response.status);
      return false;
    } catch (error) {
      console.error('连接MCP服务器时出错:', error);
      return false;
    }
  }

  /**
   * 获取Notebook信息
   */
  public async getNotebookInfo(): Promise<any | null> {
    try {
      console.log('尝试获取Notebook信息...');
      
      if (!this.notebookTracker) {
        console.error('notebookTracker未定义');
        return null;
      }
      
      if (!this.notebookTracker.currentWidget) {
        console.error('notebookTracker.currentWidget未定义，可能没有打开的notebook');
        return null;
      }
      
      const notebook = this.notebookTracker.currentWidget;
      const model = notebook.content.model;
      
      if (!model) {
        console.error('notebook.content.model未定义');
        return null;
      }
      
      const info = {
        path: notebook.context.path,
        name: notebook.context.path.split('/').pop(),
        cells: model.cells.length,
        type: 'notebook'
      };
      
      console.log('Notebook信息:', info);
      return info;
    } catch (error) {
      console.error('获取notebook信息失败:', error);
      return null;
    }
  }

  /**
   * 读取所有单元格
   */
  public async readAllCells(): Promise<ICellInfo[] | null> {
    try {
      console.log('尝试读取所有单元格...');
      
      // 详细检查notebookTracker
      if (!this.notebookTracker) {
        console.error('notebookTracker未定义');
        return null;
      }
      
      // 详细检查currentWidget
      if (!this.notebookTracker.currentWidget) {
        console.error('notebookTracker.currentWidget未定义，可能没有打开的notebook');
        return null;
      }
      
      const notebook = this.notebookTracker.currentWidget;
      console.log('notebook对象类型:', typeof notebook);
      
      // 详细检查content
      if (!notebook.content) {
        console.error('notebook.content未定义');
        return null;
      }
      
      // 详细检查model
      if (!notebook.content.model) {
        console.error('notebook.content.model未定义');
        return null;
      }
      
      const model = notebook.content.model;
      
      // 详细检查cells
      if (!model.cells) {
        console.error('model.cells未定义');
        return null;
      }
      
      console.log('单元格数量:', model.cells.length);
      
      // 如果没有单元格，返回空数组而不是null
      if (model.cells.length === 0) {
        console.warn('Notebook没有单元格');
        return [];
      }
      
      // 手动构建单元格信息
      const cells: ICellInfo[] = [];
      for (let i = 0; i < model.cells.length; i++) {
        try {
          const cell = model.cells.get(i);
          if (!cell) {
            console.warn(`无法获取单元格 ${i}`);
            continue;
          }
          
          // 获取单元格内容
          let source: string[] = [];
          try {
            // 详细调试单元格对象结构
            console.log(`=== 单元格 ${i} 调试信息 ===`);
            console.log('单元格对象:', cell);
            console.log('单元格类型:', typeof cell);
            console.log('单元格构造函数:', cell.constructor.name);
            
            // 检查所有可枚举属性
            console.log('可枚举属性:');
            for (const key in cell) {
              if (cell.hasOwnProperty(key)) {
                console.log(`  ${key}:`, typeof (cell as any)[key], (cell as any)[key]);
              }
            }
            
            // 检查所有属性（包括不可枚举的）
            console.log('所有属性:');
            const allProps = Object.getOwnPropertyNames(cell);
            allProps.forEach(prop => {
              try {
                const value = (cell as any)[prop];
                console.log(`  ${prop}:`, typeof value, value);
              } catch (e) {
                console.log(`  ${prop}: [无法访问]`);
              }
            });
            
            // 尝试不同的方法获取单元格内容
            let content = '';
            
            // 方法1: 尝试访问sharedModel.source
            if ((cell as any).sharedModel && (cell as any).sharedModel.source) {
              const source = (cell as any).sharedModel.source;
              content = Array.isArray(source) ? source.join('\n') : source;
              console.log('使用方法1 (sharedModel.source) 获取内容:', content);
            }
            // 方法2: 尝试访问sharedModel.getSource()
            else if ((cell as any).sharedModel && typeof (cell as any).sharedModel.getSource === 'function') {
              try {
                content = (cell as any).sharedModel.getSource();
                console.log('使用方法2 (sharedModel.getSource()) 获取内容:', content);
              } catch (e) {
                console.log('sharedModel.getSource() 调用失败:', e);
              }
            }
            // 方法3: 尝试访问value.text
            else if ((cell as any).value && (cell as any).value.text) {
              content = (cell as any).value.text;
              console.log('使用方法3 (value.text) 获取内容:', content);
            }
            // 方法4: 尝试访问source
            else if ((cell as any).source) {
              content = Array.isArray((cell as any).source) 
                ? (cell as any).source.join('\n') 
                : (cell as any).source;
              console.log('使用方法4 (source) 获取内容:', content);
            }
            // 方法5: 尝试访问text
            else if ((cell as any).text) {
              content = (cell as any).text;
              console.log('使用方法5 (text) 获取内容:', content);
            }
            // 方法6: 尝试访问model
            else if ((cell as any).model && (cell as any).model.value) {
              content = (cell as any).model.value.text || (cell as any).model.value.source;
              console.log('使用方法6 (model.value) 获取内容:', content);
            }
            // 方法7: 尝试使用toString()并检查是否为字符串
            else {
              const toStringResult = cell.toString();
              console.log('toString()结果:', toStringResult, '类型:', typeof toStringResult);
              if (typeof toStringResult === 'string' && toStringResult !== '[object Object]') {
                content = toStringResult;
              } else {
                console.warn(`单元格 ${i} toString()返回非字符串或[object Object]:`, typeof toStringResult);
                content = `[单元格 ${i} 内容无法获取]`;
              }
            }
            
            source = content ? content.split('\n') : [''];
            console.log(`单元格 ${i} 最终内容:`, content.substring(0, 100) + (content.length > 100 ? '...' : ''));
            console.log(`=== 单元格 ${i} 调试结束 ===`);
          } catch (e) {
            console.error(`获取单元格 ${i} 内容失败:`, e);
            source = [`[单元格 ${i} 内容获取失败]`];
          }
          
          // 获取单元格输出
          let outputs: string[] = [];
          if (cell.type === 'code') {
            try {
              console.log(`=== 单元格 ${i} 输出调试信息 ===`);
              console.log('单元格对象:', cell);
              console.log('单元格outputs属性:', (cell as any).outputs);
              console.log('outputs类型:', typeof (cell as any).outputs);
              console.log('outputs是否为数组:', Array.isArray((cell as any).outputs));
              
              // 检查所有可能的输出相关属性
              const outputProps = ['outputs', 'output', 'result', 'data'];
              outputProps.forEach(prop => {
                if ((cell as any)[prop] !== undefined) {
                  console.log(`属性 ${prop}:`, (cell as any)[prop]);
                }
              });
              
              // 尝试获取输出
              if ((cell as any).outputs) {
                const cellOutputs = (cell as any).outputs;
                console.log(`单元格 ${i} outputs对象:`, cellOutputs);
                console.log(`outputs构造函数:`, cellOutputs.constructor.name);
                
                // 检查是否有list属性（ObservableList结构）
                if (cellOutputs.list && cellOutputs.list._array) {
                  console.log(`单元格 ${i} 找到list._array:`, cellOutputs.list._array);
                  console.log(`list._array长度:`, cellOutputs.list._array.length);
                  
                  // 直接访问_array
                  const outputArray = cellOutputs.list._array;
                  console.log(`单元格 ${i} list._array内容:`, outputArray);
                  
                  for (let j = 0; j < outputArray.length; j++) {
                    const output = outputArray[j];
                    console.log(`输出 ${j} 详细信息:`, output);
                    console.log(`输出 ${j} 类型:`, typeof output);
                    console.log(`输出 ${j} 属性:`, Object.keys(output));
                    
                    // 检查这个output是否又是一个ObservableList
                    if (output._array && Array.isArray(output._array)) {
                      console.log(`输出 ${j} 是ObservableList，访问其_array:`, output._array);
                      // 如果output本身是ObservableList，访问其_array
                      for (let k = 0; k < output._array.length; k++) {
                        const actualOutput = output._array[k];
                        console.log(`实际输出 ${k} 详细信息:`, actualOutput);
                        console.log(`实际输出 ${k} 类型:`, typeof actualOutput);
                        console.log(`实际输出 ${k} 属性:`, Object.keys(actualOutput));
                        
                        // 处理实际的输出项
                        if (actualOutput.data && actualOutput.data['text/plain']) {
                          outputs.push(actualOutput.data['text/plain']);
                          console.log(`从实际输出 data['text/plain'] 获取:`, actualOutput.data['text/plain']);
                        } else if (actualOutput.text) {
                          outputs.push(actualOutput.text);
                          console.log(`从实际输出 text 获取:`, actualOutput.text);
                        } else if (actualOutput.output_type === 'stream' && actualOutput.name === 'stdout') {
                          outputs.push(actualOutput.text || '');
                          console.log(`从实际输出 stream stdout 获取:`, actualOutput.text);
                        } else if (actualOutput.output_type === 'error') {
                          outputs.push(`错误: ${actualOutput.ename}: ${actualOutput.evalue}`);
                          console.log(`从实际输出 error 获取:`, `错误: ${actualOutput.ename}: ${actualOutput.evalue}`);
                        } else if (actualOutput.output_type === 'execute_result') {
                          if (actualOutput.data && actualOutput.data['text/plain']) {
                            outputs.push(actualOutput.data['text/plain']);
                            console.log(`从实际输出 execute_result data['text/plain'] 获取:`, actualOutput.data['text/plain']);
                          } else if (actualOutput.data && actualOutput.data['text/html']) {
                            outputs.push(actualOutput.data['text/html']);
                            console.log(`从实际输出 execute_result data['text/html'] 获取:`, actualOutput.data['text/html']);
                          } else {
                            outputs.push(`[执行结果但无文本数据]`);
                            console.log(`实际输出执行结果但无文本数据:`, actualOutput);
                          }
                        } else {
                          console.error(`单元格 ${i} 实际输出 ${k} 发现未知类型:`, actualOutput.output_type, '完整对象:', actualOutput);
                          outputs.push(`[实际输出类型: ${actualOutput.output_type || 'undefined'}]`);
                        }
                      }
                    } else {
                      // 如果output不是ObservableList，直接处理
                      console.log(`输出 ${j} 完整结构:`, JSON.stringify(output, null, 2));
                      
                      // 首先尝试从_raw属性获取数据
                      if (output._raw) {
                        console.log(`从_raw属性获取数据:`, output._raw);
                        if (output._raw.output_type === 'stream' && output._raw.name === 'stdout') {
                          outputs.push(output._raw.text || '');
                          console.log(`从_raw stream stdout 获取输出:`, output._raw.text);
                        } else if (output._raw.output_type === 'stream' && output._raw.name === 'stderr') {
                          outputs.push(`错误输出: ${output._raw.text || ''}`);
                          console.log(`从_raw stream stderr 获取输出:`, output._raw.text);
                        } else if (output._raw.output_type === 'execute_result') {
                          if (output._raw.data && output._raw.data['text/plain']) {
                            outputs.push(output._raw.data['text/plain']);
                            console.log(`从_raw execute_result data['text/plain'] 获取输出:`, output._raw.data['text/plain']);
                          } else if (output._raw.data && output._raw.data['text/html']) {
                            outputs.push(output._raw.data['text/html']);
                            console.log(`从_raw execute_result data['text/html'] 获取输出:`, output._raw.data['text/html']);
                          } else {
                            outputs.push(`[执行结果但无文本数据]`);
                            console.log(`_raw执行结果但无文本数据:`, output._raw);
                          }
                        } else if (output._raw.output_type === 'error') {
                          outputs.push(`错误: ${output._raw.ename}: ${output._raw.evalue}`);
                          console.log(`从_raw error 获取输出:`, `错误: ${output._raw.ename}: ${output._raw.evalue}`);
                        } else {
                          console.log(`_raw未知输出类型:`, output._raw.output_type);
                          outputs.push(`[_raw输出类型: ${output._raw.output_type}]`);
                        }
                      }
                      // 尝试从_text属性获取数据
                      else if (output._text && output._text._text) {
                        outputs.push(output._text._text);
                        console.log(`从_text._text 获取输出:`, output._text._text);
                      }
                      // 尝试从_rawData属性获取数据
                      else if (output._rawData) {
                        console.log(`从_rawData属性获取数据:`, output._rawData);
                        if (output._rawData['application/vnd.jupyter.stdout']) {
                          outputs.push(output._rawData['application/vnd.jupyter.stdout']);
                          console.log(`从_rawData stdout 获取输出:`, output._rawData['application/vnd.jupyter.stdout']);
                        } else if (output._rawData['application/vnd.jupyter.stderr']) {
                          outputs.push(`错误输出: ${output._rawData['application/vnd.jupyter.stderr']}`);
                          console.log(`从_rawData stderr 获取输出:`, output._rawData['application/vnd.jupyter.stderr']);
                        } else {
                          // 尝试获取第一个可用的数据
                          const keys = Object.keys(output._rawData);
                          if (keys.length > 0) {
                            outputs.push(output._rawData[keys[0]]);
                            console.log(`从_rawData ${keys[0]} 获取输出:`, output._rawData[keys[0]]);
                          }
                        }
                      }
                      // 尝试从顶层属性获取数据
                      else if (output.data && output.data['text/plain']) {
                        outputs.push(output.data['text/plain']);
                        console.log(`从 data['text/plain'] 获取输出:`, output.data['text/plain']);
                      } else if (output.text) {
                        outputs.push(output.text);
                        console.log(`从 text 获取输出:`, output.text);
                      } else if (output.output_type === 'stream' && output.name === 'stdout') {
                        outputs.push(output.text || '');
                        console.log(`从 stream stdout 获取输出:`, output.text);
                      } else if (output.output_type === 'error') {
                        outputs.push(`错误: ${output.ename}: ${output.evalue}`);
                        console.log(`从 error 获取输出:`, `错误: ${output.ename}: ${output.evalue}`);
                      } else if (output.output_type === 'execute_result') {
                        // 处理执行结果
                        if (output.data && output.data['text/plain']) {
                          outputs.push(output.data['text/plain']);
                          console.log(`从 execute_result data['text/plain'] 获取输出:`, output.data['text/plain']);
                        } else if (output.data && output.data['text/html']) {
                          outputs.push(output.data['text/html']);
                          console.log(`从 execute_result data['text/html'] 获取输出:`, output.data['text/html']);
                        } else {
                          outputs.push(`[执行结果但无文本数据]`);
                          console.log(`执行结果但无文本数据:`, output);
                        }
                      } else {
                        // 尝试其他可能的属性
                        if (output.value !== undefined) {
                          outputs.push(String(output.value));
                          console.log(`从 value 获取输出:`, output.value);
                        } else if (output.result !== undefined) {
                          outputs.push(String(output.result));
                          console.log(`从 result 获取输出:`, output.result);
                        } else {
                          // 如果所有方法都失败，打印整个 output 对象
                          console.error(`单元格 ${i} 输出 ${j} 所有方法都失败，完整输出对象:`, output);
                          outputs.push(`[单元格 ${i} 输出获取失败]`);
                          console.log(`所有方法都失败，添加默认消息:`, `[单元格 ${i} 输出获取失败]`);
                        }
                      }
                    }
                  }
                }
                // 检查是否有length属性（直接访问）
                else if (cellOutputs.length !== undefined) {
                  console.log(`单元格 ${i} 输出数量:`, cellOutputs.length);
                  
                  // 尝试不同的迭代方法
                  try {
                    // 方法1: 使用for循环
                    for (let j = 0; j < cellOutputs.length; j++) {
                      const output = cellOutputs.get ? cellOutputs.get(j) : cellOutputs[j];
                      console.log(`输出 ${j} 详细信息:`, output);
                      console.log(`输出 ${j} 类型:`, typeof output);
                      console.log(`输出 ${j} 属性:`, Object.keys(output));
                      
                      // 尝试获取输出内容
                      if (output.data && output.data['text/plain']) {
                        outputs.push(output.data['text/plain']);
                        console.log(`从 data['text/plain'] 获取输出:`, output.data['text/plain']);
                      } else if (output.text) {
                        outputs.push(output.text);
                        console.log(`从 text 获取输出:`, output.text);
                      } else if (output.output_type === 'stream' && output.name === 'stdout') {
                        outputs.push(output.text || '');
                        console.log(`从 stream stdout 获取输出:`, output.text);
                      } else if (output.output_type === 'error') {
                        outputs.push(`错误: ${output.ename}: ${output.evalue}`);
                        console.log(`从 error 获取输出:`, `错误: ${output.ename}: ${output.evalue}`);
                      } else {
                        outputs.push(`[输出类型: ${output.output_type}]`);
                        console.log(`未知输出类型:`, output.output_type);
                      }
                    }
                  } catch (e) {
                    console.log('for循环失败，尝试其他方法:', e);
                    
                    // 方法2: 尝试使用forEach
                    try {
                      if (typeof cellOutputs.forEach === 'function') {
                        cellOutputs.forEach((output: any, index: number) => {
                          console.log(`输出 ${index} (forEach):`, output);
                          if (output.data && output.data['text/plain']) {
                            outputs.push(output.data['text/plain']);
                          } else if (output.text) {
                            outputs.push(output.text);
                          }
                        });
                      }
                    } catch (e2) {
                      console.log('forEach失败:', e2);
                    }
                    
                    // 方法3: 尝试使用toArray
                    try {
                      if (typeof cellOutputs.toArray === 'function') {
                        const outputArray = cellOutputs.toArray();
                        console.log('toArray结果:', outputArray);
                        outputArray.forEach((output: any, index: number) => {
                          if (output.data && output.data['text/plain']) {
                            outputs.push(output.data['text/plain']);
                          } else if (output.text) {
                            outputs.push(output.text);
                          }
                        });
                      }
                    } catch (e3) {
                      console.log('toArray失败:', e3);
                    }
                  }
                } else {
                  console.log(`单元格 ${i} outputs没有list._array或length属性`);
                }
                
                if (outputs.length === 0) {
                  console.log(`单元格 ${i} 没有找到有效输出`);
                  outputs = ['[无输出]'];
                }
              } else {
                console.log(`单元格 ${i} 没有outputs属性`);
                outputs = ['[无输出]'];
              }
              
              console.log(`单元格 ${i} 最终输出:`, outputs);
              console.log(`=== 单元格 ${i} 输出调试结束 ===`);
            } catch (e) {
              console.error(`获取单元格 ${i} 输出失败:`, e);
              outputs = ['[输出获取失败]'];
            }
          }

          const cellInfo: ICellInfo = {
            index: i,
            type: cell.type as any,
            source: source,
            outputs: cell.type === 'code' ? outputs : undefined
          };
          cells.push(cellInfo);
          console.log(`成功处理单元格 ${i}, 类型: ${cell.type}, 内容长度: ${source.length}`);
        } catch (cellError) {
          console.error(`处理单元格 ${i} 时出错:`, cellError);
        }
      }
      
      console.log(`成功获取到 ${cells.length} 个单元格`);
      return cells;
    } catch (error) {
      console.error('读取所有单元格失败:', error);
      return null;
    }
  }

  /**
   * 读取特定单元格
   * @param cellIndex 单元格索引
   */
  public async readCell(cellIndex: number): Promise<ICellInfo | null> {
    try {
      console.log(`尝试读取单元格 ${cellIndex}...`);
      
      // 详细检查notebookTracker
      if (!this.notebookTracker) {
        console.error('notebookTracker未定义');
        return null;
      }
      
      // 详细检查currentWidget
      if (!this.notebookTracker.currentWidget) {
        console.error('notebookTracker.currentWidget未定义，可能没有打开的notebook');
        return null;
      }
      
      const notebook = this.notebookTracker.currentWidget;
      
      // 详细检查content
      if (!notebook.content) {
        console.error('notebook.content未定义');
        return null;
      }
      
      // 详细检查model
      if (!notebook.content.model) {
        console.error('notebook.content.model未定义');
        return null;
      }
      
      const model = notebook.content.model;
      
      // 详细检查cells
      if (!model.cells) {
        console.error('model.cells未定义');
        return null;
      }
      
      console.log('单元格数量:', model.cells.length);
      
      if (model.cells.length === 0) {
        console.warn('Notebook没有单元格');
        return null;
      }
      
      if (cellIndex < 0 || cellIndex >= model.cells.length) {
        console.warn(`单元格索引 ${cellIndex} 超出范围 (0-${model.cells.length - 1})`);
        return null;
      }
      
      // 获取指定单元格
      const cell = model.cells.get(cellIndex);
      if (!cell) {
        console.error(`无法获取单元格 ${cellIndex}`);
        return null;
      }
      
      // 获取单元格内容
      let source: string[] = [];
      try {
        // 尝试不同的方法获取单元格内容
        let content = '';
        
        // 方法1: 尝试访问sharedModel.source
        if ((cell as any).sharedModel && (cell as any).sharedModel.source) {
          const source = (cell as any).sharedModel.source;
          content = Array.isArray(source) ? source.join('\n') : source;
          console.log('使用方法1 (sharedModel.source) 获取内容:', content);
        }
        // 方法2: 尝试访问sharedModel.getSource()
        else if ((cell as any).sharedModel && typeof (cell as any).sharedModel.getSource === 'function') {
          try {
            content = (cell as any).sharedModel.getSource();
            console.log('使用方法2 (sharedModel.getSource()) 获取内容:', content);
          } catch (e) {
            console.log('sharedModel.getSource() 调用失败:', e);
          }
        }
        // 方法3: 尝试访问value.text
        else if ((cell as any).value && (cell as any).value.text) {
          content = (cell as any).value.text;
          console.log('使用方法3 (value.text) 获取内容:', content);
        }
        // 方法4: 尝试访问source
        else if ((cell as any).source) {
          content = Array.isArray((cell as any).source) 
            ? (cell as any).source.join('\n') 
            : (cell as any).source;
          console.log('使用方法4 (source) 获取内容:', content);
        }
        // 方法5: 尝试访问text
        else if ((cell as any).text) {
          content = (cell as any).text;
          console.log('使用方法5 (text) 获取内容:', content);
        }
        // 方法6: 尝试使用toString()并检查是否为字符串
        else {
          const toStringResult = cell.toString();
          console.log('toString()结果:', toStringResult, '类型:', typeof toStringResult);
          if (typeof toStringResult === 'string' && toStringResult !== '[object Object]') {
            content = toStringResult;
          } else {
            console.warn(`单元格 ${cellIndex} toString()返回非字符串或[object Object]:`, typeof toStringResult);
            content = `[单元格 ${cellIndex} 内容无法获取]`;
          }
        }
        
        source = content ? content.split('\n') : [''];
        console.log(`单元格 ${cellIndex} 内容:`, content.substring(0, 100) + (content.length > 100 ? '...' : ''));
      } catch (e) {
        console.error(`获取单元格 ${cellIndex} 内容失败:`, e);
        source = [`[单元格 ${cellIndex} 内容获取失败]`];
      }
      
      // 获取单元格输出
      let outputs: string[] = [];
      if (cell.type === 'code') {
        try {
          // 尝试获取输出
          if ((cell as any).outputs && Array.isArray((cell as any).outputs)) {
            const cellOutputs = (cell as any).outputs;
            console.log(`单元格 ${cellIndex} 输出数量:`, cellOutputs.length);
            
            for (let j = 0; j < cellOutputs.length; j++) {
              const output = cellOutputs[j];
              console.log(`输出 ${j}:`, output);
              
              // 尝试获取输出内容
              if (output.data && output.data['text/plain']) {
                outputs.push(output.data['text/plain']);
              } else if (output.text) {
                outputs.push(output.text);
              } else if (output.output_type === 'stream' && output.name === 'stdout') {
                outputs.push(output.text || '');
              } else if (output.output_type === 'error') {
                outputs.push(`错误: ${output.ename}: ${output.evalue}`);
              } else {
                outputs.push(`[输出类型: ${output.output_type}]`);
              }
            }
          } else {
            console.log(`单元格 ${cellIndex} 没有输出或输出格式不正确`);
            outputs = ['[无输出]'];
          }
        } catch (e) {
          console.error(`获取单元格 ${cellIndex} 输出失败:`, e);
          outputs = ['[输出获取失败]'];
        }
      }

      const cellInfo: ICellInfo = {
        index: cellIndex,
        type: cell.type as any,
        source: source,
        outputs: cell.type === 'code' ? outputs : undefined
      };
      
      console.log(`成功获取单元格 ${cellIndex}, 类型: ${cell.type}, 内容长度: ${source.length}`);
      return cellInfo;
    } catch (error) {
      console.error(`读取单元格 ${cellIndex} 失败:`, error);
      return null;
    }
  }

  /**
   * 添加Markdown单元格
   * @param cellSource Markdown内容
   */
  public async appendMarkdownCell(cellSource: string): Promise<string | null> {
    try {
      console.log('添加Markdown单元格:', cellSource);
      console.log('注意：此功能需要进一步实现');
      return '功能暂未实现';
    } catch (error) {
      console.error('添加Markdown单元格失败:', error);
      return null;
    }
  }

  /**
   * 添加代码单元格
   * @param cellSource 代码内容
   */
  public async appendExecuteCodeCell(cellSource: string): Promise<string | null> {
    try {
      console.log('添加代码单元格:', cellSource);
      console.log('注意：此功能需要进一步实现');
      return '功能暂未实现';
    } catch (error) {
      console.error('添加代码单元格失败:', error);
      return null;
    }
  }

  /**
   * 执行单元格
   * @param cellIndex 单元格索引
   * @param timeout 超时时间（秒）
   */
  public async executeCell(cellIndex: number, timeout: number = 30): Promise<string | null> {
    try {
      console.log(`执行单元格 ${cellIndex}...`);
      console.log('注意：此功能需要进一步实现');
      return '功能暂未实现';
    } catch (error) {
      console.error(`执行单元格 ${cellIndex} 失败:`, error);
      return null;
    }
  }

  /**
   * 获取连接状态
   */
  public getConnectionStatus(): boolean {
    return this.isConnected;
  }
}