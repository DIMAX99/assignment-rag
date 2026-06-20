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
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data,
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
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="p-6 flex justify-center">
        <div className="bg-white rounded-full shadow-lg px-8 py-4 border border-slate-200">
          <h1 className="text-2xl font-bold text-slate-800">ChatBot Assistant</h1>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl w-full mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden m-6">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto scrollbar-hide p-6 space-y-4 bg-gradient-to-b from-white to-slate-50">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center text-slate-400">
              <div className="text-center">
                <p className="text-lg">No messages yet. Start chatting!</p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-md rounded-2xl p-4 ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white rounded-br-none'
                    : 'bg-slate-200 text-slate-900 rounded-bl-none'
                }`}
              >
                {message.image && (
                  <div className="mb-2 rounded-lg overflow-hidden">
                    <img
                      src={message.image}
                      alt="User uploaded"
                      className="max-w-sm max-h-48 object-cover"
                    />
                  </div>
                )}
                <p className="text-sm">{message.text}</p>
                <span className="text-xs opacity-70 mt-1 block">
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
              <div className="bg-slate-200 text-slate-900 rounded-2xl rounded-bl-none p-4">
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
          <div className="px-6 pb-4">
            <div className="relative inline-block">
              <img
                src={imagePreview}
                alt="Selected"
                className="max-w-xs max-h-32 rounded-lg border-2 border-blue-400"
              />
              <button
                onClick={removeImage}
                className="absolute -top-3 -right-3 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold transition-colors"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-slate-200 p-4 bg-white">
          <div className="flex gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-full transition-colors flex items-center gap-2 font-medium"
              title="Attach image"
            >
              📎 Image
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
              placeholder="Type your message here..."
              className="flex-1 px-4 py-2 border border-slate-300 text-slate-800 rounded-full focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() && !selectedImage}
              className="px-6 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-300 text-white rounded-full transition-colors font-medium"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
