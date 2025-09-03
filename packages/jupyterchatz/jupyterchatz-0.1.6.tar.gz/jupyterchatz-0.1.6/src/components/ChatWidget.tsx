import React, { useState, useEffect, useRef } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ChatService, IChatMessage } from '../services/chatService';

/**
 * Markdown渲染组件
 */
const MarkdownRenderer: React.FC<{ content: string }> = ({ content }) => {
  const renderMarkdown = (text: string) => {
    // 处理代码块
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(text)) !== null) {
      // 添加代码块前的文本
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: text.slice(lastIndex, match.index)
        });
      }

      // 添加代码块
      parts.push({
        type: 'code',
        language: match[1] || 'text',
        content: match[2]
      });

      lastIndex = match.index + match[0].length;
    }

    // 添加剩余的文本
    if (lastIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.slice(lastIndex)
      });
    }

    return parts;
  };

  const renderText = (text: string) => {
    // 处理粗体文本
    const boldRegex = /\*\*(.*?)\*\*/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = boldRegex.exec(text)) !== null) {
      // 添加粗体前的文本
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }

      // 添加粗体文本
      parts.push(<strong key={match.index}>{match[1]}</strong>);

      lastIndex = match.index + match[0].length;
    }

    // 添加剩余的文本
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  const parts = renderMarkdown(content);

  return (
    <div>
      {parts.map((part, index) => {
        if (part.type === 'code') {
          return (
            <div key={index} className="jp-AIChat-codeBlock">
              <div className="jp-AIChat-codeHeader">
                <span className="jp-AIChat-codeLanguage">{part.language}</span>
              </div>
              <pre className="jp-AIChat-codeContent">
                <code className={`language-${part.language}`}>{part.content}</code>
              </pre>
            </div>
          );
        } else {
          return (
            <div key={index} className="jp-AIChat-textContent">
              {part.content.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {renderText(line)}
                  {i < part.content.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
          );
        }
      })}
    </div>
  );
};

/**
 * 聊天组件属性
 */
interface IChatProps {
  fileBrowserFactory?: IFileBrowserFactory;
  documentManager?: IDocumentManager;
  editorTracker?: IEditorTracker;
  notebookTracker?: INotebookTracker;
}

/**
 * 聊天React组件
 */
const ChatComponent: React.FC<IChatProps> = (props) => {
  const [messages, setMessages] = useState<IChatMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const chatService = new ChatService({
    fileBrowserFactory: props.fileBrowserFactory,
    documentManager: props.documentManager,
    editorTracker: props.editorTracker,
    notebookTracker: props.notebookTracker
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: IChatMessage = {
      role: 'user',
      content: input
    };

    // 更新UI显示用户消息
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 准备发送给API的消息历史
      const messageHistory = [...messages, userMessage];
      
      // 调用API获取回复
      const response = await chatService.sendMessage(messageHistory);
      
      // 更新UI显示AI回复
      const assistantMessage: IChatMessage = {
        role: 'assistant',
        content: response
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('发送消息失败:', error);
      
      // 显示错误消息
      const errorMessage: IChatMessage = {
        role: 'assistant',
        content: '抱歉，发生了错误。请稍后再试。'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 处理按键事件（回车发送）
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="jp-AIChat-container">
      <div className="jp-AIChat-header">
        <h3>AI 助手</h3>
      </div>
      
      <div className="jp-AIChat-messages">
        {messages.length === 0 ? (
          <div className="jp-AIChat-welcome">
            <p>欢迎使用 AI 助手！请输入您的问题。</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div 
              key={index} 
              className={`jp-AIChat-message ${
                msg.role === 'user' ? 'jp-AIChat-userMessage' : 'jp-AIChat-assistantMessage'
              }`}
            >
              <div className="jp-AIChat-messageContent">
                <MarkdownRenderer content={msg.content} />
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="jp-AIChat-message jp-AIChat-assistantMessage">
            <div className="jp-AIChat-messageContent jp-AIChat-loading">
              思考中...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="jp-AIChat-inputArea">
        <textarea
          className="jp-AIChat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入您的问题..."
          disabled={isLoading}
        />
        <button 
          className="jp-AIChat-sendButton"
          onClick={handleSendMessage}
          disabled={isLoading || !input.trim()}
        >
          发送
        </button>
      </div>
    </div>
  );
};

/**
 * 聊天窗口部件接口
 */
interface IChatWidgetOptions {
  fileBrowserFactory?: IFileBrowserFactory;
  documentManager?: IDocumentManager;
  editorTracker?: IEditorTracker;
  notebookTracker?: INotebookTracker;
}

/**
 * 聊天窗口部件
 */
export class ChatWidget extends ReactWidget {
  private fileBrowserFactory?: IFileBrowserFactory;
  private documentManager?: IDocumentManager;
  private editorTracker?: IEditorTracker;
  private notebookTracker?: INotebookTracker;

  /**
   * 构造函数
   */
  constructor(options: IChatWidgetOptions = {}) {
    super();
    this.addClass('jp-AIChat-widget');
    this.id = 'jupyterchatz-chat';
    this.title.label = 'AI 助手';
    this.title.closable = true;

    this.fileBrowserFactory = options.fileBrowserFactory;
    this.documentManager = options.documentManager;
    this.editorTracker = options.editorTracker;
    this.notebookTracker = options.notebookTracker;
    
    console.log('ChatWidget 构造函数中的服务:');
    console.log('- fileBrowserFactory:', this.fileBrowserFactory);
    console.log('- documentManager:', this.documentManager);
    console.log('- editorTracker:', this.editorTracker);
    console.log('- notebookTracker:', this.notebookTracker);
  }

  render(): JSX.Element {
    return <ChatComponent 
      fileBrowserFactory={this.fileBrowserFactory}
      documentManager={this.documentManager}
      editorTracker={this.editorTracker}
      notebookTracker={this.notebookTracker}
    />;
  }
}
