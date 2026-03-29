import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { formatCurrency, formatDate } from "@/utils/format";
import { 
  Plus, 
  Target, 
  TrendingUp, 
  TrendingDown, 
  AlertCircle, 
  DollarSign,
  X,
  Wallet,
  PiggyBank,
  Home,
  Car,
  Plane,
  GraduationCap
} from "lucide-react";
import { toast } from "sonner";
import api from "@/api/axios";
import useStore from "@/store";

const GOAL_ICONS = {
  "Emergency": <AlertCircle className="h-6 w-6" />,
  "Travel": <Plane className="h-6 w-6" />,
  "Education": <GraduationCap className="h-6 w-6" />,
  "Home": <Home className="h-6 w-6" />,
  "Car": <Car className="h-6 w-6" />,
  "General": <PiggyBank className="h-6 w-6" />,
};

const Grow = () => {
  const { user } = useStore((state) => state.auth);
  const queryClient = useQueryClient();
  
  // Set page title
  useEffect(() => {
    document.title = "FinSight | Grow";
  }, []);
  
  // Goals state
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [goalForm, setGoalForm] = useState({
    title: "",
    description: "",
    target_amount: "",
    current_amount: "",
    category: "General",
    deadline: ""
  });
  
  // Investments state
  const [showInvestmentModal, setShowInvestmentModal] = useState(false);
  const [investmentForm, setInvestmentForm] = useState({
    symbol: "",
    name: "",
    quantity: "",
    average_buy_price: ""
  });
  const [quickAddAmount, setQuickAddAmount] = useState("");

  // Fetch goals
  const {
    data: goalsData,
    isLoading: goalsLoading,
    error: goalsError,
  } = useQuery({
    queryKey: ["goals"],
    queryFn: async () => {
      try {
        const response = await api.get("/goals/");
        const data = response.data;
        // Ensure we always return an array
        return Array.isArray(data) ? data : [];
      } catch (error) {
        console.error("Failed to load goals:", error);
        toast.error("Failed to load goals");
        return []; // Return empty array on error
      }
    },
  });

  // Fetch portfolio
  const {
    data: portfolioData,
    isLoading: portfolioLoading,
    error: portfolioError,
  } = useQuery({
    queryKey: ["investments", "portfolio"],
    queryFn: async () => {
      try {
        const response = await api.get("/investments/portfolio-value");
        const data = response.data;
        // Ensure we have a valid structure with holdings array
        return {
          ...data,
          holdings: Array.isArray(data?.holdings) ? data.holdings : []
        };
      } catch (error) {
        console.error("Failed to load portfolio:", error);
        toast.error("Failed to load portfolio");
        // Return default structure on error
        return {
          total_value: 0,
          total_gain_loss: 0,
          total_gain_loss_pct: 0,
          holdings: [],
          live_data: false
        };
      }
    },
  });

  // Create goal mutation
  const createGoalMutation = useMutation({
    mutationFn: async (goalData) => {
      const response = await api.post("/goals/", goalData);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Goal created successfully");
      setShowGoalModal(false);
      setGoalForm({
        title: "",
        description: "",
        target_amount: "",
        current_amount: "",
        category: "General",
        deadline: ""
      });
      queryClient.invalidateQueries(["goals"]);
    },
    onError: (error) => {
      toast.error("Failed to create goal");
    },
  });

  // Update goal mutation
  const updateGoalMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await api.put(`/goals/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Goal updated successfully");
      queryClient.invalidateQueries(["goals"]);
    },
    onError: (error) => {
      toast.error("Failed to update goal");
    },
  });

  // Create investment mutation
  const createInvestmentMutation = useMutation({
    mutationFn: async (investmentData) => {
      const response = await api.post("/investments/", investmentData);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Investment added successfully");
      setShowInvestmentModal(false);
      setInvestmentForm({
        symbol: "",
        name: "",
        quantity: "",
        average_buy_price: ""
      });
      queryClient.invalidateQueries(["investments"]);
    },
    onError: (error) => {
      toast.error("Failed to add investment");
    },
  });

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
    }).format(amount);
  };

  const calculateDaysRemaining = (deadline) => {
    if (!deadline) return null;
    const today = new Date();
    const deadlineDate = new Date(deadline);
    const diffTime = deadlineDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const handleCreateGoal = () => {
    if (!goalForm.title || !goalForm.target_amount) {
      toast.error("Please fill in required fields");
      return;
    }

    createGoalMutation.mutate({
      title: goalForm.title,
      description: goalForm.description,
      target_amount: parseFloat(goalForm.target_amount),
      current_amount: parseFloat(goalForm.current_amount) || 0,
      category: goalForm.category,
      deadline: goalForm.deadline ? new Date(goalForm.deadline) : null
    });
  };

  const handleCreateInvestment = () => {
    if (!investmentForm.symbol || !investmentForm.quantity || !investmentForm.average_buy_price) {
      toast.error("Please fill in all fields");
      return;
    }

    createInvestmentMutation.mutate({
      symbol: investmentForm.symbol.toUpperCase(),
      name: investmentForm.name,
      quantity: parseFloat(investmentForm.quantity),
      average_buy_price: parseFloat(investmentForm.average_buy_price)
    });
  };

  const handleQuickAdd = (goalId, currentAmount) => {
    if (!quickAddAmount) {
      toast.error("Please enter an amount");
      return;
    }

    updateGoalMutation.mutate({
      id: goalId,
      data: {
        current_amount: currentAmount + parseFloat(quickAddAmount)
      }
    });
    setQuickAddAmount("");
  };

  if (goalsError || portfolioError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-8 w-8 text-red-600 mx-auto mb-4" />
            <p className="text-red-600">Failed to load data</p>
            <Button onClick={() => window.location.reload()} variant="outline">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Goals Section */}
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Financial Goals</h2>
          <Dialog open={showGoalModal} onOpenChange={setShowGoalModal}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Goal
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Goal</DialogTitle>
                <DialogDescription>
                  Set a new financial goal to track your progress
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    value={goalForm.title}
                    onChange={(e) => setGoalForm({ ...goalForm, title: e.target.value })}
                    placeholder="e.g., Emergency Fund"
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={goalForm.description}
                    onChange={(e) => setGoalForm({ ...goalForm, description: e.target.value })}
                    placeholder="Optional description"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="target_amount">Target Amount (₹) *</Label>
                    <Input
                      id="target_amount"
                      type="number"
                      value={goalForm.target_amount}
                      onChange={(e) => setGoalForm({ ...goalForm, target_amount: e.target.value })}
                      placeholder="10000"
                    />
                  </div>
                  <div>
                    <Label htmlFor="current_amount">Current Amount (₹)</Label>
                    <Input
                      id="current_amount"
                      type="number"
                      value={goalForm.current_amount}
                      onChange={(e) => setGoalForm({ ...goalForm, current_amount: e.target.value })}
                      placeholder="0"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="category">Category</Label>
                    <select
                      id="category"
                      value={goalForm.category}
                      onChange={(e) => setGoalForm({ ...goalForm, category: e.target.value })}
                      className="w-full p-2 border rounded-md"
                    >
                      <option value="General">General</option>
                      <option value="Emergency">Emergency</option>
                      <option value="Travel">Travel</option>
                      <option value="Education">Education</option>
                      <option value="Home">Home</option>
                      <option value="Car">Car</option>
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="deadline">Deadline</Label>
                    <Input
                      id="deadline"
                      type="date"
                      value={goalForm.deadline}
                      onChange={(e) => setGoalForm({ ...goalForm, deadline: e.target.value })}
                    />
                  </div>
                </div>
                <Button 
                  onClick={handleCreateGoal}
                  disabled={createGoalMutation.isPending}
                  className="w-full"
                >
                  {createGoalMutation.isPending ? "Creating..." : "Create Goal"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {goalsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-4 w-3/4 mb-2" />
                  <Skeleton className="h-8 w-full mb-4" />
                  <Skeleton className="h-2 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : Array.isArray(goalsData) && goalsData.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goalsData.map((goal) => {
              const daysRemaining = calculateDaysRemaining(goal.deadline);
              const isOverdue = daysRemaining !== null && daysRemaining < 0;
              const progress = goal.target_amount > 0 
                ? Math.min((goal.current_amount / goal.target_amount) * 100, 100) 
                : 0;
              
              return (
                <Card key={goal.id} className="relative">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        {GOAL_ICONS[goal.category] || GOAL_ICONS["General"]}
                        <h3 className="font-semibold">{goal.title}</h3>
                      </div>
                      {goal.is_completed && (
                        <Badge className="bg-green-100 text-green-800">Completed</Badge>
                      )}
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Progress</span>
                          <span>{Math.round(progress)}%</span>
                        </div>
                        <Progress value={progress} className="w-full" />
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span>Current: {formatCurrency(goal.current_amount)}</span>
                        <span>Target: {formatCurrency(goal.target_amount)}</span>
                      </div>
                      
                      {daysRemaining !== null && (
                        <div className="text-sm">
                          {isOverdue ? (
                            <span className="text-red-600 font-medium">Overdue</span>
                          ) : daysRemaining === 0 ? (
                            <span className="text-orange-600 font-medium">Due today</span>
                          ) : (
                            <span className="text-gray-600">{daysRemaining} days left</span>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-2 mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setQuickAddAmount("");
                          // In a real app, this would open a quick add modal
                        }}
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Add Money
                      </Button>
                      
                      {quickAddAmount && (
                        <div className="flex items-center gap-2">
                          <Input
                            type="number"
                            value={quickAddAmount}
                            onChange={(e) => setQuickAddAmount(e.target.value)}
                            placeholder="Amount"
                            className="w-24"
                          />
                          <Button
                            size="sm"
                            onClick={() => handleQuickAdd(goal.id, goal.current_amount)}
                            disabled={updateGoalMutation.isPending}
                          >
                            Add
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card>
            <CardContent className="text-center py-8">
              <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No goals yet. Add your first financial goal!</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Portfolio Section */}
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Investment Portfolio</h2>
          <Dialog open={showInvestmentModal} onOpenChange={setShowInvestmentModal}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Holding
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Investment</DialogTitle>
                <DialogDescription>
                  Add a new investment to your portfolio
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="symbol">Symbol *</Label>
                  <Input
                    id="symbol"
                    value={investmentForm.symbol}
                    onChange={(e) => setInvestmentForm({ ...investmentForm, symbol: e.target.value })}
                    placeholder="e.g., AAPL"
                  />
                </div>
                <div>
                  <Label htmlFor="name">Name *</Label>
                  <Input
                    id="name"
                    value={investmentForm.name}
                    onChange={(e) => setInvestmentForm({ ...investmentForm, name: e.target.value })}
                    placeholder="e.g., Apple Inc."
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="quantity">Quantity *</Label>
                    <Input
                      id="quantity"
                      type="number"
                      value={investmentForm.quantity}
                      onChange={(e) => setInvestmentForm({ ...investmentForm, quantity: e.target.value })}
                      placeholder="10"
                    />
                  </div>
                  <div>
                    <Label htmlFor="average_buy_price">Avg Buy Price (₹) *</Label>
                    <Input
                      id="average_buy_price"
                      type="number"
                      value={investmentForm.average_buy_price}
                      onChange={(e) => setInvestmentForm({ ...investmentForm, average_buy_price: e.target.value })}
                      placeholder="150.00"
                    />
                  </div>
                </div>
                <Button 
                  onClick={handleCreateInvestment}
                  disabled={createInvestmentMutation.isPending}
                  className="w-full"
                >
                  {createInvestmentMutation.isPending ? "Adding..." : "Add Investment"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {portfolioLoading ? (
          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-4 w-1/4 mb-4" />
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        ) : portfolioData && (
          <div>
            {!portfolioData.live_data && (
              <Alert className="mb-6 bg-yellow-50 border-yellow-200">
                <AlertDescription>
                  Prices are estimates - Live data unavailable
                </AlertDescription>
              </Alert>
            )}
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Portfolio Value</span>
                  <Badge variant="outline" className="text-lg">
                    {formatCurrency(portfolioData.total_value)}
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Total Gain/Loss: 
                  <span className={portfolioData.total_gain_loss >= 0 ? "text-green-600" : "text-red-600"}>
                    {formatCurrency(portfolioData.total_gain_loss)} 
                    ({portfolioData.total_gain_loss_pct >= 0 ? '+' : ''}{portfolioData.total_gain_loss_pct}%)
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Symbol</th>
                        <th className="text-left p-2">Name</th>
                        <th className="text-right p-2">Qty</th>
                        <th className="text-right p-2">Avg Buy</th>
                        <th className="text-right p-2">Current Price</th>
                        <th className="text-right p-2">Current Value</th>
                        <th className="text-right p-2">Gain/Loss %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolioData?.holdings?.map((holding) => (
                        <tr key={holding.id} className="border-b hover:bg-gray-50">
                          <td className="p-2 font-medium">{holding.symbol}</td>
                          <td className="p-2">{holding.name}</td>
                          <td className="p-2 text-right">{holding.quantity}</td>
                          <td className="p-2 text-right">{formatCurrency(holding.average_buy_price)}</td>
                          <td className="p-2 text-right">{formatCurrency(holding.current_price)}</td>
                          <td className="p-2 text-right font-medium">{formatCurrency(holding.current_value)}</td>
                          <td className="p-2 text-right">
                            <span className={holding.gain_loss_pct >= 0 ? "text-green-600" : "text-red-600"}>
                              {holding.gain_loss_pct >= 0 ? '+' : ''}{holding.gain_loss_pct}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Grow;
