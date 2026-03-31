export default function Tooltip({ label, children }) {
  return (
    <span title={label} className="inline-flex items-center">
      {children}
    </span>
  );
}
