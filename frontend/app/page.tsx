'use client';

import { useState, useRef ,useEffect} from 'react';
import Image from 'next/image';
import axios from "axios";
import { uploadImage } from '../utils/uploadImage';

interface Message {
  id: string;
  text: string;
  image?: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [webSearchResults, setWebSearchResults] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [retrievedContext, setRetrievedContext] = useState<string>('');
  const [selectedChunk, setSelectedChunk] = useState<{index: number; content: string} | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
    setImagePreview('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() && !selectedImage) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      image: imagePreview,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    removeImage();
    setLoading(true);
    setRetrievedContext('');

    try {
      let imageUrl = null;
      if (selectedImage) {
        imageUrl = await uploadImage(selectedImage);
      }
      const response = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/chat`, {
        message: input,
        image_url: imageUrl
      });

      const answer = response.data.answer;
      const usedWebSearch = response.data.used_web_fallback;
      const context = response.data.retrieved_context || '';
      const webSearchResults = response.data.web_search_results || '';
      const messageText = usedWebSearch 
        ? `${answer}\n\n📡 Used WebSearch` 
        : answer;

      setRetrievedContext(context);
      setWebSearchResults(webSearchResults);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: messageText,
        sender: 'bot',
        timestamp: new Date(),

      };
      setLoading(false);
      setMessages((prev) => [...prev, botMessage]);
      scrollToBottom();
    } catch (error) {
      console.error('Error sending message:', error);
      setLoading(false);
    }
  };
  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="border-b border-slate-200/50 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Study Assistant</h1>
            <p className="text-sm text-slate-500 mt-0.5">Ask questions, upload images, get answers</p>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex bg-white overflow-hidden px-6 py-6 gap-4">
        {/* Messages Section - 60% */}
        <div className="flex-[0.6] flex flex-col border border-slate-200/50 rounded-xl overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center space-y-3">
                  <div className="text-4xl">📚</div>
                  <p className="text-lg font-medium text-slate-900">Start a conversation</p>
                  <p className="text-slate-500 text-sm">Ask questions about your textbook or upload an image</p>
                </div>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
              >
                <div
                  className={`max-w-xl rounded-2xl px-5 py-3.5 space-y-2 ${
                    message.sender === 'user'
                      ? 'bg-slate-900 text-white rounded-br-sm'
                      : 'bg-slate-100 text-slate-900 rounded-bl-sm border border-slate-200/50'
                  }`}
                >
                  {message.image && (
                    <div className="mb-2 rounded-lg overflow-hidden border border-slate-200">
                      <img
                        src={message.image}
                        alt="User uploaded"
                        className="max-w-sm max-h-48 object-cover"
                      />
                    </div>
                  )}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  <span className={`text-xs opacity-60 block ${message.sender === 'user' ? 'text-slate-300' : 'text-slate-500'}`}>
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-100 text-slate-900 rounded-2xl rounded-bl-sm p-4 border border-slate-200/50">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Image Preview */}
          {imagePreview && (
            <div className="px-6 pb-4 border-t border-slate-200/50">
              <div className="relative inline-block group">
                <img
                  src={imagePreview}
                  alt="Selected"
                  className="max-w-xs max-h-32 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors"
                />
                <button
                  onClick={removeImage}
                  className="absolute -top-2 -right-2 bg-slate-900 hover:bg-slate-800 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold transition-colors shadow-md"
                  title="Remove image"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t border-slate-200/50 p-4 bg-white">
            <div className="flex gap-3 items-end">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-3.5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors flex items-center gap-2 font-medium text-sm"
                title="Attach image"
              >
                📎
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="hidden"
              />
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Type your question..."
                className="flex-1 px-4 py-2.5 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-lg focus:outline-none focus:border-slate-400 focus:ring-1 focus:ring-slate-400 transition-colors bg-white"
              />
              <button
                onClick={handleSendMessage}
                disabled={!input.trim() && !selectedImage}
                className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium text-sm"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Retrieved Context Sidebar - 40% */}
        <div className="flex-[0.4] flex flex-col border border-slate-200/50 rounded-xl overflow-hidden bg-slate-50">
          <div className="px-4 py-3 border-b border-slate-200/50 bg-white">
            <h2 className="text-sm font-semibold text-slate-900">Retrieved Context</h2>
            <p className="text-xs text-slate-500 mt-0.5">From textbook sources</p>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {retrievedContext || webSearchResults ? (
              <div className="space-y-3">
                {retrievedContext && retrievedContext.split('Source').slice(1).map((source, idx) => (
                  <div
                    key={`textbook-${idx}`}
                    onClick={() => setSelectedChunk({index: idx + 1, content: source})}
                    className="bg-white rounded-lg p-3 border border-slate-200/50 text-xs cursor-pointer hover:border-slate-300 hover:shadow-md transition-all group"
                  >
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <div className="font-semibold text-slate-900 flex-shrink-0">Source {idx + 1}</div>
                      <div className="text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">→</div>
                    </div>
                    <div className="text-slate-600 line-clamp-3">{source.trim().substring(0, 150)}...</div>
                  </div>
                ))}
                
                {webSearchResults && (
                  <>
                    <div className="px-2 py-1 mt-4">
                      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Web Results</p>
                    </div>
                    {webSearchResults.split('\n\n').filter((result) => result.trim()).map((result, idx) => (
                      <div
                        key={`web-${idx}`}
                        onClick={() => setSelectedChunk({index: -1, content: result})}
                        className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-200/50 text-xs cursor-pointer hover:border-blue-300 hover:shadow-md transition-all group"
                      >
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <div className="font-semibold text-blue-900 flex-shrink-0 flex items-center gap-1">
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Web</span>
                          </div>
                          <div className="text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">→</div>
                        </div>
                        <div className="text-blue-900 line-clamp-3">{result.trim().substring(0, 150)}...</div>
                      </div>
                    ))}
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400">
                <div className="text-center">
                  <p className="text-sm">No context retrieved yet</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Chunk Popup Modal */}
        {selectedChunk && (
          <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedChunk(null)}
          >
            <div
              className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="px-6 py-4 border-b border-slate-200/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-semibold text-slate-900">
                    {selectedChunk.index === -1 ? 'Web Result' : `Source ${selectedChunk.index}`}
                  </h3>
                  {selectedChunk.index === -1 && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Web</span>
                  )}
                </div>
                <button
                  onClick={() => setSelectedChunk(null)}
                  className="text-slate-500 hover:text-slate-700 transition-colors"
                >
                  ✕
                </button>
              </div>

              {/* Modal Content */}
              <div className="flex-1 overflow-y-auto p-6">
                <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                  {selectedChunk.content}
                </div>
              </div>

              {/* Modal Footer */}
              <div className="px-6 py-4 border-t border-slate-200/50 bg-slate-50 flex justify-end">
                <button
                  onClick={() => setSelectedChunk(null)}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg transition-colors text-sm font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
