import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ArrowUp, ArrowDown, TrendingUp, Wallet, DollarSign } from "lucide-react";
import { toast } from "sonner";
import api from "@/api/axios";
import useStore from "@/store";
import { formatCurrency, formatDate, getTransactionIcon } from "@/utils/format";

const COLORS = {
  primary: "var(--color-chart-1)",
  success: "var(--color-chart-2)",
  danger: "var(--color-chart-4)",
  warning: "var(--color-chart-3)",
  info: "var(--color-chart-5)",
};

const CATEGORIES_COLORS = [
  "var(--color-chart-1)", "var(--color-chart-4)", "var(--color-chart-2)", "var(--color-chart-3)", "var(--color-chart-5)",
  "var(--color-sidebar-accent)", "var(--color-sidebar-primary)", "var(--color-chart-4)", "var(--color-chart-1)", "var(--color-chart-2)"
];

const Home = () => {
  const { user } = useStore((state) => state.auth);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Set page title
  useEffect(() => {
    document.title = "FinSight | Dashboard";
  }, []);

  // Time-based greeting
  const getTimeBasedGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  const greeting = getTimeBasedGreeting();
  const name = user?.full_name || user?.username || "there";

  // Fetch transaction summary
  const {
    data: summaryData,
    isLoading: summaryLoading,
    error: summaryError,
  } = useQuery({
    queryKey: ["transactions", "summary"],
    queryFn: async () => {
      try {
        const response = await api.get("/transactions/summary");
        return response.data;
      } catch (error) {
        toast.error("Failed to load transaction summary");
        throw error;
      }
    },
  });

  // Fetch recent transactions
  const {
    data: recentTransactions,
    isLoading: transactionsLoading,
    error: transactionsError,
  } = useQuery({
    queryKey: ["recent-transactions"],
    queryFn: async () => {
      try {
        const response = await api.get("/transactions/?limit=5");
        return response.data;
      } catch (error) {
        toast.error("Failed to load recent transactions");
        throw error;
      }
    },
  });

  const currentDate = format(new Date(), "EEEE, MMMM d, yyyy");

  const handleTransactionClick = (transaction) => {
    setSelectedTransaction(transaction);
    setShowDetailModal(true);
  };

  if (summaryError || transactionsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <p className="text-destructive">Failed to load dashboard data</p>
            <Button
              onClick={() => window.location.reload()}
              className="mt-4"
              variant="outline"
            >
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header Row */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            {greeting}, {name}
          </h1>
          <p className="text-muted-foreground">{currentDate}</p>
        </div>
        <Badge variant="secondary" className="text-lg px-3 py-1">
          INR
        </Badge>
      </div>

      {/* Balance Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {summaryLoading ? (
          <>
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </>
        ) : (
          <>
            {/* Total Balance */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
                <Wallet className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(summaryData?.net_cashflow || 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  All time income minus expenses
                </p>
              </CardContent>
            </Card>

            {/* This Month Income */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">This Month Income</CardTitle>
                <ArrowUp className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(
                    summaryData?.by_month?.[0]?.income || 0
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  +12% from last month
                </p>
              </CardContent>
            </Card>

            {/* This Month Expenses */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">This Month Expenses</CardTitle>
                <ArrowDown className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(
                    summaryData?.by_month?.[0]?.expenses || 0
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  +5% from last month
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Cashflow Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Cashflow Trend</CardTitle>
          <CardDescription>
            Income vs expenses over last 6 months
          </CardDescription>
        </CardHeader>
        <CardContent>
          {summaryLoading ? (
            <Skeleton className="h-64" />
          ) : summaryData?.by_month?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={summaryData.by_month}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 12 }}
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `₹${value / 1000}k`}
                />
                <Tooltip
                  formatter={(value, name) => [
                    formatCurrency(value),
                    name === "income" ? "Income" : "Expenses",
                  ]}
                />
                <Line
                  type="monotone"
                  dataKey="income"
                  stroke={COLORS.success}
                  strokeWidth={2}
                  dot={{ fill: COLORS.success, strokeWidth: 2, r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="expenses"
                  stroke={COLORS.danger}
                  strokeWidth={2}
                  dot={{ fill: COLORS.danger, strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-muted-foreground">
              No cashflow data available
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spending Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Spending by Category</CardTitle>
            <CardDescription>
              Where your money goes this month
            </CardDescription>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-64" />
            ) : summaryData?.by_category?.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={summaryData.by_category}
                  layout="horizontal"
                >
                  <XAxis type="number" tickFormatter={(value) => `₹${value}`} />
                  <YAxis
                    dataKey="category"
                    type="category"
                    width={80}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value) => [formatCurrency(value), "Amount"]}
                  />
                  <Bar dataKey="total_amount">
                    {summaryData.by_category.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={CATEGORIES_COLORS[index % CATEGORIES_COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No category data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>
              Your latest financial activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            {transactionsLoading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12" />
                ))}
              </div>
            ) : Array.isArray(recentTransactions) && recentTransactions.length > 0 ? (
              <div className="space-y-3">
                {recentTransactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                    onClick={() => handleTransactionClick(transaction)}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">
                        {getTransactionIcon(transaction.category)}
                      </span>
                      <div>
                        <p className="font-medium text-sm">
                          {transaction.description || transaction.category}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDate(new Date(transaction.transaction_date || transaction.date))}
                        </p>
                      </div>
                    </div>
                    <div
                      className={`font-bold ${
                        transaction.transaction_type === "income"
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {transaction.transaction_type === "income" ? "+" : "-"}
                      {formatCurrency(transaction.amount)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-muted-foreground">
                <DollarSign className="h-12 w-12 mb-4 opacity-50" />
                <p>No transactions yet</p>
                <p className="text-sm">
                  Start tracking your expenses to see them here
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Transaction Detail Modal */}
      <Dialog open={showDetailModal} onOpenChange={setShowDetailModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Transaction Details</DialogTitle>
            <DialogDescription>
              Full information about this transaction
            </DialogDescription>
          </DialogHeader>
          {selectedTransaction && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Category</p>
                  <p className="font-medium">
                    {getTransactionIcon(selectedTransaction.category)}{" "}
                    {selectedTransaction.category}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Amount</p>
                  <p
                    className={`font-bold text-lg ${
                      selectedTransaction.transaction_type === "income"
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {selectedTransaction.transaction_type === "income" ? "+" : "-"}
                    {formatCurrency(selectedTransaction.amount)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Date</p>
                  <p className="font-medium">
                    {formatDate(new Date(selectedTransaction.transaction_date || selectedTransaction.date))}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Type</p>
                  <Badge
                    variant={
                      selectedTransaction.transaction_type === "income"
                        ? "default"
                        : "destructive"
                    }
                  >
                    {selectedTransaction.transaction_type}
                  </Badge>
                </div>
              </div>
              {selectedTransaction.description && (
                <div>
                  <p className="text-sm text-muted-foreground">Description</p>
                  <p className="font-medium">{selectedTransaction.description}</p>
                </div>
              )}
              {selectedTransaction.payment_mode && (
                <div>
                  <p className="text-sm text-muted-foreground">Payment Mode</p>
                  <p className="font-medium">{selectedTransaction.payment_mode}</p>
                </div>
              )}
              {selectedTransaction.account && (
                <div>
                  <p className="text-sm text-muted-foreground">Account</p>
                  <p className="font-medium">{selectedTransaction.account}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Home;
