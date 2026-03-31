export const formatPercent = (value = 0) => `${Number(value).toFixed(0)}%`;
export const formatNumber = (value = 0) => Number(value).toLocaleString();

export const normalizeToPercent = (items) => {
  const total = items.reduce((sum, item) => sum + (Number(item.value) || 0), 0) || 1;
  return items.map((item) => ({
    ...item,
    value: Number(((item.value / total) * 100).toFixed(1)),
  }));
};
