import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useTheme } from "../../context/ThemeContext";

interface Props {
  income: number;
  expenses: number;
}

export default function IncomeExpenseBarChart({ income, expenses }: Props) {
  const { theme } = useTheme();
  const strokeColor = theme === "dark" ? "#9ca3af" : "#6b7280";

  const data = [
    { name: "Income", amount: income },
    { name: "Expenses", amount: expenses },
  ];

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={strokeColor} opacity={0.3} />
          <XAxis dataKey="name" stroke={strokeColor} />
          <YAxis stroke={strokeColor} />
          <Tooltip
            contentStyle={{
              backgroundColor: theme === "dark" ? "#1f2937" : "#fff",
              border: "1px solid #374151",
              color: theme === "dark" ? "#f9fafb" : "#111827",
            }}
          />
          <Bar dataKey="amount" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
