import { StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import './index.css';

const Loader = () => (
  <div className="min-h-screen flex items-center justify-center bg-shell">
    <div className="h-12 w-12 rounded-full border-4 border-text-muted border-t-text-primary animate-spin" aria-label="Loading" />
  </div>
);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Suspense fallback={<Loader />}>
        <App />
      </Suspense>
    </BrowserRouter>
  </StrictMode>
);
