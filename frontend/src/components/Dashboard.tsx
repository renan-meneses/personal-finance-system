import { useEffect, useState } from "react";
import * as api from "../services/api";
import NetWorthChart from "./Charts/NetWorthChart";
import CategoryPieChart from "./Charts/CategoryPieChart";
import IncomeExpenseBarChart from "./Charts/IncomeExpenseBarChart";

export default function Dashboard() {
  const [dashboard, setDashboard] = useState<api.DashboardSummary | null>(null);
  const [cashFlow, setCashFlow] = useState<api.CashFlowProjection | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getDashboard(), api.getCashFlow(30, 0)])
      .then(([dash, cf]) => {
        setDashboard(dash);
        setCashFlow(cf);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  const categoryData = dashboard
    ? Object.entries(dashboard.category_expenses).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard
          title="Total Income"
          value={dashboard?.total_income ?? 0}
          color="text-green-600 dark:text-green-400"
        />
        <SummaryCard
          title="Total Expenses"
          value={dashboard?.total_expenses ?? 0}
          color="text-red-600 dark:text-red-400"
        />
        <SummaryCard
          title="Net Savings"
          value={dashboard?.net_savings ?? 0}
          color="text-blue-600 dark:text-blue-400"
        />
        <SummaryCard
          title="Investments"
          value={dashboard?.current_investment_value ?? 0}
          color="text-purple-600 dark:text-purple-400"
        />
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-4 text-lg font-semibold">Net Worth Evolution</h3>
          <NetWorthChart data={cashFlow?.daily_projections ?? []} />
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-4 text-lg font-semibold">Category Expenses</h3>
          <CategoryPieChart data={categoryData} />
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <h3 className="mb-4 text-lg font-semibold">Income vs Expenses</h3>
        <IncomeExpenseBarChart
          income={dashboard?.total_income ?? 0}
          expenses={dashboard?.total_expenses ?? 0}
        />
      </div>

      {/* Goals */}
      {dashboard && dashboard.goals.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-4 text-lg font-semibold">Financial Goals</h3>
          <div className="space-y-3">
            {dashboard.goals.map((goal) => (
              <div key={goal.id}>
                <div className="mb-1 flex justify-between text-sm">
                  <span>{goal.name}</span>
                  <span>{goal.progress_percentage.toFixed(0)}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                  <div
                    className="h-2 rounded-full bg-blue-500 transition-all"
                    style={{ width: `${Math.min(goal.progress_percentage, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Recurring */}
      {dashboard && dashboard.upcoming_recurring.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <h3 className="mb-4 text-lg font-semibold">Upcoming Recurring</h3>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {dashboard.upcoming_recurring.map((tx) => (
              <div
                key={tx._id}
                className="flex items-center justify-between py-2"
              >
                <div>
                  <p className="font-medium">{tx.description}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {tx.next_execution_date}
                  </p>
                </div>
                <span
                  className={`font-semibold ${
                    tx.type === "expense" ? "text-red-500" : "text-green-500"
                  }`}
                >
                  {tx.type === "expense" ? "-" : "+"}${tx.amount.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SummaryCard({
  title,
  value,
  color,
}: {
  title: string;
  value: number;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
      <p className={`text-2xl font-bold ${color}`}>
        ${value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
      </p>
    </div>
  );
}
