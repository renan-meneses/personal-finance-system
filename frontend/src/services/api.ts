import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

export interface DashboardSummary {
  total_income: number;
  total_expenses: number;
  net_savings: number;
  category_expenses: Record<string, number>;
  goals: Goal[];
  total_invested: number;
  current_investment_value: number;
  investment_return: number;
  upcoming_recurring: Transaction[];
}

export interface Goal {
  id: number;
  name: string;
  target_amount: string;
  current_amount: string;
  progress_percentage: number;
  is_completed: boolean;
}

export interface Transaction {
  _id: string;
  date: string;
  description: string;
  amount: number;
  type: "income" | "expense";
  category: string;
  is_recurring: boolean;
  next_execution_date: string | null;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  theme_preference: "light" | "dark";
  monthly_income: string;
}

export interface CashFlowProjection {
  days: number;
  current_balance: number;
  predicted_income: number;
  scheduled_expenses: number;
  projected_balance: number;
  daily_projections: { date: string; balance: number; income: number; expense: number }[];
}

export async function login(username: string, password: string): Promise<UserProfile> {
  const res = await api.post("/auth/login/", { username, password });
  return res.data;
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout/");
}

export async function getProfile(): Promise<UserProfile> {
  const res = await api.get("/profile/");
  return res.data;
}

export async function updateTheme(theme: "light" | "dark"): Promise<UserProfile> {
  const res = await api.patch("/profile/theme/", { theme_preference: theme });
  return res.data;
}

export async function getDashboard(): Promise<DashboardSummary> {
  const res = await api.get("/dashboard/");
  return res.data;
}

export async function getTransactions(params?: Record<string, string>): Promise<{ count: number; results: Transaction[] }> {
  const res = await api.get("/transactions/", { params });
  return res.data;
}

export async function uploadFile(file: File): Promise<{ imported: number; filename: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/transactions/upload/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function createTransaction(data: Partial<Transaction>): Promise<Transaction> {
  const res = await api.post("/transactions/", data);
  return res.data;
}

export async function getCashFlow(days: number = 30, balance: number = 0): Promise<CashFlowProjection> {
  const res = await api.get("/cash-flow/", { params: { days, current_balance: balance } });
  return res.data;
}

export async function getHealth(): Promise<{ status: string; databases: { postgresql: boolean; mongodb: boolean } }> {
  const res = await api.get("/health/");
  return res.data;
}

export default api;
