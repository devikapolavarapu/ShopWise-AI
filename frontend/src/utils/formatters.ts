export function formatCurrency(amount: number): string {
  if (isNaN(amount)) return '₹0';
  if (amount >= 100000) {
    return `₹${(amount / 100000.0).toFixed(2)}L`;
  }
  return `₹${Math.round(amount).toLocaleString()}`;
}

export function formatNumber(num: number): string {
  if (isNaN(num)) return '0';
  return Math.round(num).toLocaleString();
}

export function formatDays(days: number): string {
  if (isNaN(days)) return '0 days';
  return `${Number(days.toFixed(1))} days`;
}

export function formatPercentage(pct: number): string {
  if (isNaN(pct)) return '0.0%';
  return `${Number(pct.toFixed(1))}%`;
}
