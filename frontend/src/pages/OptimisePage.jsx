import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
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
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { X, TrendingUp, TrendingDown, Minus, Brain, Target, DollarSign, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import api from "@/api/axios";
import useStore from "@/store";

const COLORS = {
  primary: "#3b82f6",
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
};

const CATEGORY_ICONS = {
  "Food": "🍕",
  "Transport": "🚗",
  "Shopping": "🛍",
  "Utilities": "⚡",
  "Entertainment": "🎬",
  "Healthcare": "🏥",
  "Education": "📚",
  "Other": "📦",
};

const Optimise = () => {
  const { user } = useStore((state) => state.auth);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null);
  const [classificationLoading, setClassificationLoading] = useState(false);
  const [dismissedAlerts, setDismissedAlerts] = useState(new Set());
  const [description, setDescription] = useState("");

  const {
    data: insightsData,
    isLoading: insightsLoading,
    error: insightsError,
  } = useQuery({
    queryKey: ["analytics", "insights"],
    queryFn: async () => {
      try {
        const response = await api.get("/analytics/insights");
        return response.data;
      } catch (error) {
        toast.error("Failed to load analytics insights");
        throw error;
      }
    },
  });

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
    }).format(amount);
  };

  const handleClassify = async () => {
    if (!description.trim()) {
      toast.error("Please enter a transaction description");
      return;
    }
    setClassificationLoading(true);
    try {
      const response = await api.post("/analytics/classify", { description });
      setClassificationResult(response.data);
      toast.success(`Categorized as: ${response.data.category}`);
    } catch (error) {
      toast.error("Failed to categorize transaction");
    } finally {
      setClassificationLoading(false);
      setDescription("");
    }
  };

  const dismissAlert = (alertId) => {
    setDismissedAlerts(prev => new Set([...prev, alertId]));
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case "increasing":
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "decreasing":
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  if (insightsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-8 w-8 text-red-600 mx-auto mb-4" />
            <p className="text-red-600">Failed to load insights</p>
            <Button onClick={() => window.location.reload()} variant="outline">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (insightsLoading) {
    return (
      <div className="space-y-6 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-8 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const insights = insightsData || {};

  return (
    <div className="space-y-6 p-6">

      {/* Smart Insights Banner */}
      <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Target className="h-8 w-8 opacity-80" />
              </div>
              <div className="text-3xl font-bold">{Math.round(insights.savings_rate || 0)}%</div>
              <div className="text-sm opacity-80">Savings Rate</div>
              <div className="mt-2">
                <Progress value={insights.savings_rate || 0} className="w-full bg-white/20" />
              </div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                {getTrendIcon(insights.monthly_trend)}
              </div>
              <div className="text-3xl font-bold capitalize">{insights.monthly_trend || "Stable"}</div>
              <div className="text-sm opacity-80">Monthly Trend</div>
            </div>
            <div className="text-center">
              <div className="text-6xl font-bold mb-2">{CATEGORY_ICONS[insights.top_category] || "📦"}</div>
              <div className="text-sm opacity-80">{insights.top_category || "No Data"}</div>
              <div className="text-xs opacity-60">Top Category</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Anomaly Alerts */}
      {insights.unusual_transactions && insights.unusual_transactions.length > 0 && (
        <div className="space-y-3">
          {insights.unusual_transactions
            .filter(transaction => !dismissedAlerts.has(transaction.id))
            .map((transaction, index) => (
              <Alert key={index} className="border-yellow-200 bg-yellow-50">
                <AlertDescription className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-medium text-yellow-800">💡 Unusual Spending Alert</div>
                    <div className="text-sm text-yellow-700 mt-1">
                      {transaction.description} • {formatCurrency(transaction.amount)} is {transaction.unusual_factor}x your average {transaction.category} spend
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => dismissAlert(transaction.id)}
                    className="text-yellow-600 hover:text-yellow-800"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </AlertDescription>
              </Alert>
            ))}
        </div>
      )}

      {/* Auto-Categorize Tool */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            AI Transaction Categorizer
          </CardTitle>
          <CardDescription>
            Paste a transaction description and let our AI categorize it instantly
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="e.g., 'Swiggy order for biryani'"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={handleClassify}
              disabled={classificationLoading || !description.trim()}
              className="px-6"
            >
              {classificationLoading ? "Categorizing..." : (
                <>
                  <Target className="h-4 w-4 mr-2" />
                  Categorize
                </>
              )}
            </Button>
          </div>
          {classificationResult && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <div className="text-sm text-gray-600">Predicted Category</div>
                  <div className="text-lg font-semibold">{classificationResult.category}</div>
                </div>
                <Badge variant="outline" className="text-xs">
                  {Math.round(classificationResult.confidence * 100)}% confidence
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Spending by Category */}
      {insights.category_breakdown && Object.keys(insights.category_breakdown).length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Spending by Category</CardTitle>
            <CardDescription>
              {selectedCategory ? (
                <span>Filtered: <strong>{selectedCategory}</strong></span>
              ) : (
                "Click a category to filter"
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedCategory && (
              <div className="mb-4">
                <Button variant="outline" size="sm" onClick={() => setSelectedCategory(null)}>
                  Clear Filter
                </Button>
              </div>
            )}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {Object.entries(insights.category_breakdown)
                .filter(([cat]) => !selectedCategory || cat === selectedCategory)
                .map(([category, data], index) => (
                  <div
                    key={category}
                    className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                      selectedCategory === category
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                    onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="text-2xl">{CATEGORY_ICONS[category] || "📦"}</div>
                        <div>
                          <div className="font-semibold">{category}</div>
                          <div className="text-sm text-gray-600">{data.count} transactions</div>
                        </div>
                      </div>
                      <Badge variant={selectedCategory === category ? "default" : "secondary"}>
                        {Math.round((data.total_amount / (insights.total_expenses || 1)) * 100)}%
                      </Badge>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">
                      {formatCurrency(data.total_amount)}
                    </div>
                    <div className="text-sm text-gray-600">
                      Avg: {formatCurrency(data.average)}
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="text-center py-8">
            <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No spending data yet</p>
            <p className="text-sm text-gray-500">Add transactions to see insights</p>
          </CardContent>
        </Card>
      )}

    </div>
  );
};

export default Optimise;