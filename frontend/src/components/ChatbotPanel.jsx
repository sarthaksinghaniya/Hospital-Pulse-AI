import { useEffect, useMemo, useRef, useState } from 'react';
import Card from './ui/Card.jsx';
import Button from './ui/Button.jsx';
import Skeleton from './ui/Skeleton.jsx';
import ErrorBox from './ui/ErrorBox.jsx';
import { getChatbotFeed, sendChatMessage } from '../services/api.js';

const formatBotResponse = (data) => {
  if (!data) return '🤖 Sorry, I couldn’t find relevant data. Try asking about system status or patient predictions.';

  // Normalize string payload
  if (typeof data === 'string') return data;

  const type = data.type;
  const msg = data.message;

  if (type === 'system_info' && data.system_status) {
    const components = data.system_status.components || {};
    return [
      `✅ ${msg || 'System status'}`,
      'Components:',
      `• Backend: ${components.backend ?? 'Unknown'}`,
      `• Database: ${components.database ?? 'Unknown'}`,
      `• ML Models: ${components.ml_models ?? 'Unknown'}`,
      `• APIs: ${components.api_endpoints ?? 'Unknown'}`,
    ].join('\n');
  }

  if (type === 'prediction') {
    return `📊 ${msg}${data.risk ? ` (${data.risk} risk)` : ''}`;
  }

  if (type === 'patient_info') {
    return `👤 ${msg}`;
  }

  if (type === 'text' || type === 'fallback') {
    return `🤖 ${msg || 'I can help with system status, patient predictions, and hospital analytics.'}`;
  }

  return msg || '🤖 Response received successfully';
};

const wsFromHttp = (url) => url?.replace('https://', 'wss://').replace('http://', 'ws://');

export default function ChatbotPanel({ baseUrl }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const listRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    getChatbotFeed({ limit: 10 })
      .then((res) => {
        if (cancelled) return;
        const feed = res?.data?.data?.messages || [];
        setMessages(feed);
      })
      .catch((err) => !cancelled && setError(err))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (!baseUrl) return;
    const wsUrl = wsFromHttp(baseUrl) + '/chatbot/ws';
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onmessage = (evt) => {
      try {
        const payload = JSON.parse(evt.data);
        if (payload?.data?.messages) {
          setMessages(payload.data.messages);
        } else if (payload?.data) {
          setMessages((prev) => [...prev, payload.data]);
        }
      } catch (e) {
        console.warn('WS parse error', e);
      }
    };
    ws.onerror = () => setError('Chat connection error');
    return () => ws.close();
  }, [baseUrl]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const content = input.trim();
    const userEntry = { content, role: 'user', timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userEntry]);
    setInput('');

    try {
      const res = await sendChatMessage(content);
      const botEntry = {
        role: 'assistant',
        content: res?.data,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botEntry]);
    } catch (err) {
      setError(err);
    }
  };

  const ordered = useMemo(() => messages.slice(-20), [messages]);

  return (
    <Card title="HopX Assistant" subtitle="OpenAI + rules-backed chatbot" className="space-y-3">
      {loading ? <Skeleton className="h-24 w-full" /> : null}
      <ErrorBox error={error} />

      <div ref={listRef} className="h-60 overflow-y-auto space-y-2 pr-1">
        {ordered.length === 0 && !loading && <p className="text-sm text-text-muted">No messages yet.</p>}
        {ordered.map((msg, idx) => {
          const raw = msg.content ?? msg.message ?? msg.data ?? msg;
          const text = formatBotResponse(raw);
          return (
            <div key={idx} className="rounded-xl p-3 border border-slate-100 bg-white shadow-soft space-y-1">
              <p className="text-xs text-text-muted">{msg.role || msg.type || 'assistant'}</p>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{text}</p>
            </div>
          );
        })}
      </div>

      <form className="flex items-center gap-2" onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
        <label htmlFor="chat-message" className="sr-only">Ask something</label>
        <input
          id="chat-message"
          name="chat-message"
          autoComplete="off"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Ask anything about operations..."
          className="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-text-primary/20"
        />
        <Button type="submit" onClick={sendMessage} className="px-4">Send</Button>
      </form>
    </Card>
  );
}
