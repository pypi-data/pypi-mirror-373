// 货币符号工具

const currencyMap: Record<string, string> = {
  USD: '$',
  CNY: '¥',
  RMB: '¥',
  HKD: 'HK$',
  TWD: 'NT$',
  GBP: '£',
  EUR: '€',
  JPY: '¥',
  KRW: '₩',
  AUD: 'A$',
  CAD: 'C$',
  SGD: 'S$',
  THB: '฿',
  INR: '₹',
}

export function getCurrencyCodeFromPricelocal(pricelocal?: string): string {
  if (!pricelocal || typeof pricelocal !== 'string') return 'CNY'
  const match = pricelocal.match(/currency=([A-Z]{3})/)
  return (match && match[1]) || 'CNY'
}

export function getSymbolByCode(code?: string): string {
  if (!code) return '¥'
  return currencyMap[code] || '¥'
}

export function getCurrencySymbol(pricelocal?: string): string {
  const code = getCurrencyCodeFromPricelocal(pricelocal)
  return getSymbolByCode(code)
}

export default {
  getCurrencyCodeFromPricelocal,
  getSymbolByCode,
  getCurrencySymbol,
}


