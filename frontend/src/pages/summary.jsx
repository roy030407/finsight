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
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Plus, Search, X, Trash2, Calendar, Filter } from "lucide-react";
import { toast } from "sonner";
import api from "@/api/axios";
import useStore from "@/store";
import { formatCurrency, formatDate } from "@/utils/format";

const Summary = () => {
  const { user } = useStore((state) => state.auth);
  const queryClient = useQueryClient();
  
  // Set page title
  useEffect(() => {
    document.title = "FinSight | Summary";
  }, []);
  
  // State for filters and pagination
  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    type: "all",
    category: "",
    search: "",
  });
  const [page, setPage] = useState(1);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [transactionToDelete, setTransactionToDelete] = useState(null);
  const [newTransaction, setNewTransaction] = useState({
    amount: "",
    type: "expense",
    category: "",
    description: "",
    date: format(new Date(), "yyyy-MM-dd"),
    payment_mode: "",
  });
  const [searchDebounce, setSearchDebounce] = useState("");

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters(prev => ({ ...prev, search: searchDebounce }));
    }, 400);
    return () => clearTimeout(timer);
  }, [searchDebounce]);

  // Build query params
  const buildQueryParams = () => {
    const params = new URLSearchParams();
    params.set("limit", "20");
    params.set("offset", ((page - 1) * 20).toString());
    
    if (filters.type !== "all") params.set("type", filters.type);
    if (filters.start_date) params.set("start_date", filters.start_date);
    if (filters.end_date) params.set("end_date", filters.end_date);
    if (filters.category) params.set("category", filters.category);
    if (filters.search) params.set("search", filters.search);
    
    return params.toString();
  };

  // Fetch transactions
  const {
    data: transactionsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["transactions", page, filters],
    queryFn: async () => {
      try {
        const response = await api.get(`/transactions/?${buildQueryParams()}`);
        return response.data;
      } catch (error) {
        toast.error("Failed to load transactions");
        throw error;
      }
    },
  });

  // Add transaction mutation
  const addTransactionMutation = useMutation({
    mutationFn: async (transactionData) => {
      try {
        const response = await api.post("/transactions/", transactionData);
        return response.data;
      } catch (error) {
        toast.error("Failed to add transaction");
        throw error;
      }
    },
    onSuccess: () => {
      toast.success("Transaction added successfully");
      setShowAddModal(false);
      setNewTransaction({
        amount: "",
        type: "expense",
        category: "",
        description: "",
        date: format(new Date(), "yyyy-MM-dd"),
        payment_mode: "",
      });
      queryClient.invalidateQueries(["transactions"]);
    },
  });

  // Delete transaction mutation
  const deleteTransactionMutation = useMutation({
    mutationFn: async (id) => {
      try {
        await api.delete(`/transactions/${id}`);
        return id;
      } catch (error) {
        toast.error("Failed to delete transaction");
        throw error;
      }
    },
    onSuccess: () => {
      toast.success("Transaction deleted successfully");
      setShowDeleteDialog(false);
      setTransactionToDelete(null);
      queryClient.invalidateQueries(["transactions"]);
    },
  });

  const handleAddTransaction = (e) => {
    e.preventDefault();
    const transactionData = {
      amount: parseFloat(newTransaction.amount),
      transaction_type: newTransaction.type,
      category: newTransaction.category,
      description: newTransaction.description || null,
      transaction_date: newTransaction.date,
      payment_mode: newTransaction.payment_mode || null,
    };
    addTransactionMutation.mutate(transactionData);
  };

  const handleDeleteClick = (transaction) => {
    setTransactionToDelete(transaction);
    setShowDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    if (transactionToDelete) {
      deleteTransactionMutation.mutate(transactionToDelete.id);
    }
  };

  const clearFilters = () => {
    setFilters({
      start_date: "",
      end_date: "",
      type: "all",
      category: "",
      search: "",
    });
    setSearchDebounce("");
    setPage(1);
  };

  const transactions = Array.isArray(transactionsData) ? transactionsData : (transactionsData?.transactions || []);
  const totalCount = Array.isArray(transactionsData) ? transactionsData.length : (transactionsData?.total || 0);
  const totalPages = Math.ceil(totalCount / 20);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <p className="text-red-600">Failed to load transactions</p>
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
      {/* Filter Bar */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
            <div>
              <Label htmlFor="start_date">Start Date</Label>
              <Input
                id="start_date"
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters(prev => ({ ...prev, start_date: e.target.value }))}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="end_date">End Date</Label>
              <Input
                id="end_date"
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters(prev => ({ ...prev, end_date: e.target.value }))}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="type">Type</Label>
              <Select value={filters.type} onValueChange={(value) => setFilters(prev => ({ ...prev, type: value }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="income">Income</SelectItem>
                  <SelectItem value="expense">Expense</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="search">Search</Label>
              <div className="relative mt-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search description..."
                  value={searchDebounce}
                  onChange={(e) => setSearchDebounce(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex items-end gap-2">
              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
              <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Transaction
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add New Transaction</DialogTitle>
                    <DialogDescription>
                      Enter the details of your transaction
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleAddTransaction} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="amount">Amount *</Label>
                        <Input
                          id="amount"
                          type="number"
                          step="0.01"
                          required
                          value={newTransaction.amount}
                          onChange={(e) => setNewTransaction(prev => ({ ...prev, amount: e.target.value }))}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="type">Type *</Label>
                        <Select value={newTransaction.type} onValueChange={(value) => setNewTransaction(prev => ({ ...prev, type: value }))}>
                          <SelectTrigger className="mt-1">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="income">Income</SelectItem>
                            <SelectItem value="expense">Expense</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="category">Category *</Label>
                      <Input
                        id="category"
                        required
                        value={newTransaction.category}
                        onChange={(e) => setNewTransaction(prev => ({ ...prev, category: e.target.value }))}
                        placeholder="e.g., Food & Dining"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Input
                        id="description"
                        value={newTransaction.description}
                        onChange={(e) => setNewTransaction(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Optional description"
                        className="mt-1"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="date">Date *</Label>
                        <Input
                          id="date"
                          type="date"
                          required
                          value={newTransaction.date}
                          onChange={(e) => setNewTransaction(prev => ({ ...prev, date: e.target.value }))}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="payment_mode">Payment Mode</Label>
                        <Input
                          id="payment_mode"
                          value={newTransaction.payment_mode}
                          onChange={(e) => setNewTransaction(prev => ({ ...prev, payment_mode: e.target.value }))}
                          placeholder="e.g., Credit Card"
                          className="mt-1"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 pt-4">
                      <Button type="button" variant="outline" onClick={() => setShowAddModal(false)}>
                        Cancel
                      </Button>
                      <Button type="submit" disabled={addTransactionMutation.isPending}>
                        {addTransactionMutation.isPending ? "Adding..." : "Add Transaction"}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Transactions</CardTitle>
          <CardDescription>
            {totalCount > 0 ? `${totalCount} transaction${totalCount !== 1 ? 's' : ''} found` : "No transactions found"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(10)].map((_, i) => (
                <Skeleton key={i} className="h-12" />
              ))}
            </div>
          ) : transactions.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Date</th>
                      <th className="text-left p-2">Description</th>
                      <th className="text-left p-2">Category</th>
                      <th className="text-left p-2">Amount</th>
                      <th className="text-left p-2">Type</th>
                      <th className="text-left p-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((transaction) => (
                      <tr key={transaction.id} className="border-b hover:bg-muted/50">
                        <td className="p-2">
                          {format(new Date(transaction.transaction_date), "MMM d, yyyy")}
                        </td>
                        <td className="p-2">
                          {transaction.description || transaction.category}
                        </td>
                        <td className="p-2">{transaction.category}</td>
                        <td className={`p-2 font-bold ${
                          transaction.transaction_type === "income" ? "text-green-600" : "text-red-600"
                        }`}>
                          {transaction.transaction_type === "income" ? "+" : "-"}
                          {formatCurrency(transaction.amount)}
                        </td>
                        <td className="p-2">
                          <Badge
                            variant={transaction.transaction_type === "income" ? "default" : "destructive"}
                          >
                            {transaction.transaction_type}
                          </Badge>
                        </td>
                        <td className="p-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteClick(transaction)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">
                    Page {page} of {totalPages}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(prev => Math.max(1, prev - 1))}
                      disabled={page === 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
                      disabled={page === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">💰</div>
              <h3 className="text-lg font-semibold mb-2">No transactions yet</h3>
              <p className="text-muted-foreground mb-4">Add your first one to get started!</p>
              <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Transaction
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add New Transaction</DialogTitle>
                    <DialogDescription>
                      Enter the details of your transaction
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleAddTransaction} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="amount">Amount *</Label>
                        <Input
                          id="amount"
                          type="number"
                          step="0.01"
                          required
                          value={newTransaction.amount}
                          onChange={(e) => setNewTransaction(prev => ({ ...prev, amount: e.target.value }))}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="type">Type *</Label>
                        <Select value={newTransaction.type} onValueChange={(value) => setNewTransaction(prev => ({ ...prev, type: value }))}>
                          <SelectTrigger className="mt-1">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="income">Income</SelectItem>
                            <SelectItem value="expense">Expense</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="category">Category *</Label>
                      <Input
                        id="category"
                        required
                        value={newTransaction.category}
                        onChange={(e) => setNewTransaction(prev => ({ ...prev, category: e.target.value }))}
                        placeholder="e.g., Food & Dining"
                        className="mt-1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Input
                        id="description"
                        value={newTransaction.description}
                        onChange={(e) => setNewTransaction(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Optional description"
                        className="mt-1"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="date">Date *</Label>
                        <Input
                          id="date"
                          type="date"
                          required
                          value={newTransaction.date}
                          onChange={(e) => setNewTransaction(prev => ({ ...prev, date: e.target.value }))}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="payment_mode">Payment Mode</Label>
                        <Input
                          id="payment_mode"
                          value={newTransaction.payment_mode}
                          onChange={(e) => setNewTransaction(prev => ({ ...prev, payment_mode: e.target.value }))}
                          placeholder="e.g., Credit Card"
                          className="mt-1"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 pt-4">
                      <Button type="button" variant="outline" onClick={() => setShowAddModal(false)}>
                        Cancel
                      </Button>
                      <Button type="submit" disabled={addTransactionMutation.isPending}>
                        {addTransactionMutation.isPending ? "Adding..." : "Add Transaction"}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Delete</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this transaction? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          {transactionToDelete && (
            <div className="py-4">
              <div className="flex justify-between items-center p-3 border rounded">
                <div>
                  <p className="font-medium">{transactionToDelete.description || transactionToDelete.category}</p>
                  <p className="text-sm text-muted-foreground">
                    {format(new Date(transactionToDelete.date), "MMM d, yyyy")}
                  </p>
                </div>
                <div className={`font-bold ${
                  transactionToDelete.transaction_type === "income" ? "text-green-600" : "text-red-600"
                }`}>
                  {transactionToDelete.transaction_type === "income" ? "+" : "-"}
                  {formatCurrency(transactionToDelete.amount)}
                </div>
              </div>
            </div>
          )}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleteTransactionMutation.isPending}
            >
              {deleteTransactionMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Summary;
