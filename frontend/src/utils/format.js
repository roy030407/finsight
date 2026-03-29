import { format } from 'date-fns';

// Currency formatting for Indian Rupees
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

// Date formatting
export const formatDate = (date) => {
  if (!date) return 'N/A';
  return format(new Date(date), 'MMM d, yyyy');
};

// Percentage formatting
export const formatPercent = (value) => {
  return `${(value * 100).toFixed(1)}%`;
};

// Get transaction icon
export const getTransactionIcon = (category) => {
  const icons = {
    "Food & Dining": "🍔",
    "Transportation": "🚗", 
    "Shopping": "🛍️",
    "Entertainment": "🎬",
    "Bills & Utilities": "💡",
    "Healthcare": "🏥",
    "Education": "📚",
    "Travel": "✈️",
    "Investment": "📈",
    "Salary": "💰",
    "Freelance": "💻",
    "Other": "📝",
  };
  return icons[category] || "📝";
};

// Get user initials
export const getUserInitials = (name) => {
  if (!name) return "U";
  return name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
};
