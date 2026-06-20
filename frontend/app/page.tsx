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
  const [loading, setLoading] = useState(false);
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
      const messageText = usedWebSearch 
        ? `${answer}\n\n📡 Used WebSearch` 
        : answer;

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
      <div className="flex-1 flex flex-col max-w-5xl w-full mx-auto bg-white overflow-hidden">
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
                className={`max-w-2xl rounded-2xl px-5 py-3.5 space-y-2 ${
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
    </div>
  );
}
