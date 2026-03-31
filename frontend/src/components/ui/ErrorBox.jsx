export default function ErrorBox({ error, fallback = 'Something went wrong' }) {
  if (!error) return null;
  const message = typeof error === 'string'
    ? error
    : error?.response?.data?.detail?.[0]?.msg
      || error?.response?.data?.detail
      || error?.message
      || fallback;
  return (
    <div className="text-sm text-danger rounded-xl bg-danger/5 border border-danger/20 px-3 py-2" role="alert">
      {message}
    </div>
  );
}
